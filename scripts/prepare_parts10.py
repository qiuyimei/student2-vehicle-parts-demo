"""将Carparts-seg原始23类标签转换为项目10类，保留官方数据划分。"""
import argparse,json,shutil
from pathlib import Path

NAMES=['front_bumper','back_bumper','hood','trunk','door','front_light','back_light','glass','mirror','wheel']
CLASS_MAP={0:1,1:4,2:7,3:4,4:6,5:6,6:4,7:6,8:0,9:4,10:7,11:4,12:5,13:5,14:4,15:5,16:2,17:8,19:8,20:3,21:3,22:9}

def convert(source,dest):
    source=source.resolve();dest=dest.resolve()
    if dest.exists():raise ValueError('输出目录已存在，请选择新的目录以避免覆盖')
    if dest==source or source in dest.parents:raise ValueError('输出目录不能位于原始数据集中')
    for split in ('train','val','test'):
        if not (source/'images'/split).is_dir() or not (source/'labels'/split).is_dir():raise ValueError(f'缺少{split}图片或标签目录')
    manifest={'source':str(source),'output':str(dest),'names':NAMES,'splits':{},'excludedClass':18}
    for split in ('train','val','test'):
        counts=[0]*10;images=0;excluded=0
        for image in sorted((source/'images'/split).iterdir()):
            if image.suffix.lower() not in ('.jpg','.jpeg','.png','.bmp','.webp'):continue
            label=source/'labels'/split/(image.stem+'.txt')
            if not label.exists():raise ValueError(f'缺少标签：{label}，不将未标注图片当作负样本')
            output_lines=[]
            for line in label.read_text(encoding='utf-8').splitlines():
                values=line.split()
                if not values:continue
                if len(values)<7 or len(values)%2!=1:raise ValueError(f'不是YOLO多边形分割标签：{label}')
                code=int(values[0]);coords=[float(v) for v in values[1:]]
                if any(not 0<=v<=1 for v in coords):raise ValueError(f'坐标不在0至1之间：{label}')
                if code==18:excluded+=1;continue
                if code not in CLASS_MAP:raise ValueError(f'未知原始类别ID {code}')
                target=CLASS_MAP[code];counts[target]+=1
                output_lines.append(str(target)+' '+' '.join(values[1:]))
            target_image=dest/'images'/split/image.name;target_image.parent.mkdir(parents=True,exist_ok=True)
            target_label=dest/'labels'/split/label.name;target_label.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(image,target_image)
            target_label.write_text('\n'.join(output_lines)+'\n' if output_lines else '',encoding='utf-8')
            images+=1
        manifest['splits'][split]={'images':images,'classInstanceCounts':dict(zip(NAMES,counts)),'excludedObjectInstances':excluded}
    yaml='path: '+json.dumps(str(dest).replace('\\','/'))+'\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n'+''.join(f'  {i}: {name}\n' for i,name in enumerate(NAMES))
    (dest/'parts10.yaml').write_text(yaml,encoding='utf-8')
    (dest/'conversion-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    print(json.dumps(convert(Path(args.source),Path(args.output)),ensure_ascii=False,indent=2))
