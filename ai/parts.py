"""合并同一实体的重复分割，并显式保留原模型的侧别冲突。"""
import numpy as np
from .matching import bbox_iou

def family(code):
    if 'door' in code:return 'door'
    if 'light' in code:return 'front_light' if code.startswith('front') else 'back_light'
    if 'mirror' in code:return 'mirror'
    if 'glass' in code:return 'glass'
    if code in ('trunk','tailgate'):return 'trunk'
    return code

def ambiguous_code(codes,group):
    if group=='door':
        if all(c.startswith('front') for c in codes):return 'front_door'
        if all(c.startswith('back') for c in codes):return 'back_door'
        return 'door'
    return group

def merge_duplicate_parts(parts,masks=None,threshold=0.65):
    keep=[];kept_masks=[]
    for index in sorted(range(len(parts)),key=lambda i:parts[i]['confidence'],reverse=True):
        row=dict(parts[index]);row['rawClass']=row['className']
        row['candidateClasses']=[row['className']];row['labelStatus']='model_prediction'
        group=family(row['className']);duplicate=None
        for j,previous in enumerate(keep):
            if family(previous['className'])!=group:continue
            if masks is not None:
                a,b=np.asarray(masks[index],bool),np.asarray(kept_masks[j],bool)
                union=np.logical_or(a,b).sum()
                overlap=np.logical_and(a,b).sum()/max(1,union)
            else:overlap=bbox_iou(row['bbox'],previous['bbox'])
            if overlap>=threshold:
                duplicate=j;break
        if duplicate is None:
            keep.append(row)
            if masks is not None:kept_masks.append(masks[index])
        else:
            previous=keep[duplicate]
            codes=sorted(set(previous['candidateClasses']+[row['className']]))
            previous['candidateClasses']=codes
            previous['mergedDetections']=previous.get('mergedDetections',1)+1
            if len(codes)>1:
                previous['className']=ambiguous_code(codes,group)
                previous['labelStatus']='ambiguous_label'
                previous['labelReason']='同一区域出现互相矛盾的类别，合并重复检测并保留侧别或细分类待确认。'
    return keep,np.array(kept_masks,dtype=bool) if masks is not None and kept_masks else None
