"""学生2：独立损伤与部件匹配模块。输入框坐标为原图像素xyxy。"""
import numpy as np


def bbox_iou(a,b):
    area_a=max(0,a[2]-a[0])*max(0,a[3]-a[1])
    area_b=max(0,b[2]-b[0])*max(0,b[3]-b[1])
    intersection=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    union=area_a+area_b-intersection
    return intersection/union if union>0 else 0


def match_damage(damage,parts,damage_mask=None,part_masks=None,min_coverage=0.35):
    if not 0<min_coverage<=1:
        raise ValueError('覆盖率阈值必须大于0且不超过1')
    if part_masks is not None and len(part_masks)!=len(parts):
        raise ValueError('部件掩膜数量与部件数量不一致')
    from_box=False
    if damage_mask is None and part_masks is not None and len(part_masks):
        height,width=part_masks[0].shape
        damage_mask=np.zeros((height,width),dtype=bool)
        x1,y1,x2,y2=damage['bbox']
        damage_mask[max(0,int(np.floor(y1))):min(height,int(np.ceil(y2))),max(0,int(np.floor(x1))):min(width,int(np.ceil(x2)))]=True
        from_box=True
    candidates=[]
    for i,part in enumerate(parts):
        iou=bbox_iou(damage['bbox'],part['bbox'])
        if damage_mask is not None and part_masks is not None:
            dm,pm=np.asarray(damage_mask,dtype=bool),np.asarray(part_masks[i],dtype=bool)
            if dm.shape!=pm.shape:
                raise ValueError('损伤与部件掩膜尺寸不一致')
            intersection=int(np.logical_and(dm,pm).sum())
            damage_area=int(dm.sum());part_area=int(pm.sum())
            coverage=intersection/max(1,damage_area)
            ratio=intersection/max(1,part_area)
            method='bbox_mask_intersection' if from_box else 'mask_intersection'
        else:
            a,b=damage['bbox'],part['bbox']
            intersection=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
            coverage=intersection/max(1,(a[2]-a[0])*(a[3]-a[1]))
            ratio=intersection/max(1,(b[2]-b[0])*(b[3]-b[1]))
            method='bbox_intersection'
        expected={'lamp_broken':'light','glass_shatter':'glass','tire_flat':'wheel'}.get(damage.get('damageType'))
        compatible=expected is None or expected in part['part']
        candidates.append({'part':part['part'],'partLabel':part['partLabel'],'instanceId':part.get('instanceId',f'part-{i+1}'),'coverage':round(coverage,5),'iou':round(iou,5),'damageRatio':round(min(1,ratio),5),'confidence':part['confidence'],'method':method,'semanticCompatible':compatible})
    candidates.sort(key=lambda p:(p['coverage'],p['iou'],p['confidence']),reverse=True)
    compatible=[c for c in candidates if c['semanticCompatible']]
    best=compatible[0] if compatible else None
    displayed=[c for c in candidates if c['coverage']>0]
    if not best or best['coverage']<min_coverage:
        return {'part':'unknown','partLabel':'部位待确认','partInstanceId':None,'partConfidence':None,'damageRatio':None,'matchCoverage':best['coverage'] if best else 0,'matchIou':best['iou'] if best else 0,'matchStatus':'unmatched','ratioMethod':'unmatched','candidates':displayed,'matchReason':'没有足够且类型相容的部件覆盖，保留未匹配结果。'}
    multi=len(compatible)>1 and compatible[1]['coverage']>=min_coverage
    return {'part':best['part'],'partLabel':best['partLabel'],'partInstanceId':best['instanceId'],'partConfidence':best['confidence'],'damageRatio':best['damageRatio'],'matchCoverage':best['coverage'],'matchIou':best['iou'],'matchStatus':'multiple_parts' if multi else 'matched','ratioMethod':best['method'],'candidates':displayed,'matchReason':'存在多个候选部件，请复核主部件。' if multi else '按部件覆盖损伤的比例匹配，IoU用于次级排序。'}
