"""学生2：部件实例分割与损伤关联。检测来自公开模型或显式输入。"""
import os
from pathlib import Path
import threading
import time
import uuid
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from ultralytics import YOLO
import torch
from .matching import match_damage
from .parts import merge_duplicate_parts
from .inputs import validate_external

ROOT=Path(__file__).resolve().parents[1]
MEDIA=ROOT/'data'/'media'
MEDIA.mkdir(parents=True,exist_ok=True)
PART_LABELS={
    'back_bumper':'后保险杠','front_bumper':'前保险杠','hood':'引擎盖','trunk':'后备箱盖','tailgate':'尾门',
    'front_door':'前车门（侧别未确定）','back_door':'后车门（侧别未确定）',
    'front_left_door':'左前车门','front_right_door':'右前车门','back_left_door':'左后车门','back_right_door':'右后车门',
    'front_left_light':'左前车灯','front_right_light':'右前车灯','back_left_light':'左后车灯','back_right_light':'右后车灯',
    'front_light':'前车灯（侧别未确定）','back_light':'后车灯（侧别未确定）',
    'front_glass':'前挡风玻璃','back_glass':'后挡风玻璃','left_mirror':'左后视镜','right_mirror':'右后视镜','wheel':'车轮',
    'door':'车门（细分类待确认）','mirror':'后视镜（侧别待确认）','glass':'玻璃（位置待确认）'}
GROUPS={'front_bumper':'前保险杠','back_bumper':'后保险杠','hood':'引擎盖','trunk':'后备箱 / 尾门','door':'车门','front_light':'前车灯','back_light':'后车灯','glass':'挡风玻璃','mirror':'后视镜','wheel':'车轮'}
DAMAGE_LABELS={'dent':'凹陷','scratch':'划痕','crack':'裂纹','glass_shatter':'玻璃破碎','lamp_broken':'车灯破损','tire_flat':'轮胎异常'}
NOTICE='本Demo默认使用公开预训练模型，识别与匹配结果需要人工复核。'


def group_for(part):
    for group in ('door','mirror','glass'):
        if group in part:return group
    if 'light' in part:return 'front_light' if part.startswith('front') else 'back_light'
    return 'trunk' if part=='tailgate' else part


class Pipeline:
    def __init__(self,parts_model=None):
        torch.set_num_threads(min(4,os.cpu_count() or 2))
        self.parts_path=Path(parts_model or os.environ.get('STUDENT2_PARTS_MODEL') or ROOT/'models/parts.pt').resolve()
        self.reference_parts=self.parts_path==(ROOT/'models/parts.pt').resolve()
        self.parts=YOLO(str(self.parts_path))
        self.damage=None
        self.lock=threading.Lock()

    def metadata(self):
        return {'moduleId':'student2-vehicle-parts-demo','partsModel':'YOLO11n · 车辆部件实例分割' if self.reference_parts else '用户指定YOLO部件模型','partsSource':'https://huggingface.co/Majorburn/yolov11-carparts-seg' if self.reference_parts else '用户指定权重，来源需自行记录','partsModelFile':self.parts_path.name,'damageModel':'CarDD YOLOv8s-seg v2.0 · 可选联调输入','damageSource':'https://huggingface.co/abdullahg7/cardd-yolov8s','device':'CPU','partClasses':[{'code':k,'label':v,'group':group_for(k)} for k,v in PART_LABELS.items()],'nativeModelClasses':list(self.parts.names.values()),'focusGroups':GROUPS,'excludedClasses':['object'],'weightsOrigin':'公开预训练模型，非学生自行训练' if self.reference_parts else '部件使用用户指定权重；自动损伤输入仍来自公开模型','matchingMethod':'优先分割区域交集；外部损伤框采用框内部件像素覆盖率。IoU作为次级排序依据。车灯/玻璃/轮胎损伤附加类别相容检查。','deduplication':'同类部件Mask IoU≥0.65合并，冲突标签保留待确认','notice':NOTICE}

    def _run(self,model,image,conf):
        result=model.predict(image,conf=conf,imgsz=640,device='cpu',verbose=False,retina_masks=True)[0]
        boxes=result.boxes.xyxy.cpu().numpy() if result.boxes is not None else []
        scores=result.boxes.conf.cpu().numpy() if result.boxes is not None else []
        classes=result.boxes.cls.cpu().numpy() if result.boxes is not None else []
        masks=result.masks.data.cpu().numpy().astype(bool) if result.masks is not None else None
        rows=[{'className':str(result.names[int(cls)]).lower().replace(' ','_'),'confidence':round(float(score),4),'bbox':[round(float(x),2) for x in box]} for box,score,cls in zip(boxes,scores,classes)]
        return rows,masks

    def predict(self,image,mode='parts',part_conf=0.25,damage_conf=0.25,external=None,min_coverage=0.35):
        if mode not in ('parts','auto','external'):raise ValueError('不支持的模式')
        if mode=='external':external=validate_external(external if external is not None else [],image.width,image.height)
        started=time.perf_counter()
        array=cv2.cvtColor(np.array(image),cv2.COLOR_RGB2BGR)
        with self.lock:
            parts,pm=self._run(self.parts,array,part_conf)
            keep=[i for i,p in enumerate(parts) if p['className'] in PART_LABELS]
            parts=[parts[i] for i in keep]
            pm=pm[keep] if pm is not None and keep else None
            parts,pm=merge_duplicate_parts(parts,pm)
            if mode=='auto':
                if self.damage is None:self.damage=YOLO(str(ROOT/'models/damage.pt'))
                damages,dm=self._run(self.damage,array,damage_conf)
                origin='公开CarDD模型预测（仅供学生2联调）'
            elif mode=='external':
                damages,dm=[dict(x) for x in (external or [])],None
                origin='用户显式输入 / 学生1接口结果'
            else:damages,dm,origin=[],None,'未运行损伤检测'
        for i,p in enumerate(parts):
            p['part']=p.pop('className');p['partLabel']=PART_LABELS[p['part']]
            p['group']=group_for(p['part']);p['groupLabel']=GROUPS[p['group']]
            p['instanceId']=f'part-{i+1}'
            p['areaPixels']=int(pm[i].sum()) if pm is not None else int((p['bbox'][2]-p['bbox'][0])*(p['bbox'][3]-p['bbox'][1]))
            if pm is not None:
                contours,_=cv2.findContours(pm[i].astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                p['polygons']=[cv2.approxPolyDP(c,2,True).reshape(-1,2).tolist() for c in contours if cv2.contourArea(c)>10]
        for i,d in enumerate(damages):
            d['damageType']=d.pop('className',d.get('damageType','unknown'))
            d['damageLabel']=DAMAGE_LABELS.get(d['damageType'],d['damageType']);d['damageId']=f'damage-{i+1}'
            d.update(match_damage(d,parts,dm[i] if dm is not None else None,pm,min_coverage))
        asset_id=uuid.uuid4().hex
        image.save(MEDIA/f'{asset_id}.jpg',quality=94)
        self.annotate(image,parts,pm,damages,False).save(MEDIA/f'{asset_id}-parts.jpg',quality=94)
        self.annotate(image,parts,pm,damages,True).save(MEDIA/f'{asset_id}-match.jpg',quality=94)
        return {'runId':asset_id,'originalImageUrl':f'/media/{asset_id}.jpg','partsImageUrl':f'/media/{asset_id}-parts.jpg','matchingImageUrl':f'/media/{asset_id}-match.jpg','width':image.width,'height':image.height,'coordinateSpace':'EXIF纠正后原图，像素坐标xyxy','parts':parts,'damages':damages,'damageOrigin':origin,'elapsedMs':round((time.perf_counter()-started)*1000),'mode':mode,'thresholds':{'partConfidence':part_conf,'damageConfidence':damage_conf,'minCoverage':min_coverage},'model':self.metadata(),'notice':NOTICE}

    def annotate(self,image,parts,pm,damages,matching):
        canvas=image.copy().convert('RGBA');overlay=Image.new('RGBA',image.size)
        palette=[(13,148,136),(37,99,235),(124,58,237),(180,83,9),(190,24,93),(5,150,105)]
        for i,p in enumerate(parts):
            color=palette[i%len(palette)]
            if pm is not None:
                layer=Image.new('RGBA',image.size,(*color,0));layer.putalpha(Image.fromarray(pm[i].astype('uint8')*(30 if matching else 70)))
                overlay=Image.alpha_composite(overlay,layer)
            ImageDraw.Draw(overlay).rectangle(p['bbox'],outline=(*color,200),width=max(2,image.width//300))
        canvas=Image.alpha_composite(canvas,overlay).convert('RGB');draw=ImageDraw.Draw(canvas)
        font_path=Path('C:/Windows/Fonts/msyh.ttc')
        font=ImageFont.truetype(str(font_path),max(13,image.width//55)) if font_path.exists() else ImageFont.load_default()
        def label(row,text,color):
            x,y=int(row['bbox'][0]),max(0,int(row['bbox'][1])-font.size-9)
            bounds=draw.textbbox((0,0),text,font=font);x=min(x,max(0,image.width-(bounds[2]+10)))
            draw.rectangle((x,y,x+bounds[2]+9,y+font.size+8),fill=color);draw.text((x+4,y+1),text,font=font,fill='white')
        if not matching:
            for i,p in enumerate(parts):label(p,f"P{i+1} {p['partLabel']} {p['confidence']:.0%}",palette[i%len(palette)])
        else:
            for i,d in enumerate(damages):
                draw.rectangle(d['bbox'],outline='#ef5f36',width=max(3,image.width//180))
                label(d,f"D{i+1} {d['damageLabel']} → {d['partLabel']}",'#d94e26')
                if d['partInstanceId']:
                    p=next(p for p in parts if p['instanceId']==d['partInstanceId'])
                    a=((d['bbox'][0]+d['bbox'][2])/2,(d['bbox'][1]+d['bbox'][3])/2);b=((p['bbox'][0]+p['bbox'][2])/2,(p['bbox'][1]+p['bbox'][3])/2)
                    draw.line((a,b),fill='#ef5f36',width=3);draw.ellipse((b[0]-4,b[1]-4,b[0]+4,b[1]+4),fill='#ef5f36')
        return canvas
