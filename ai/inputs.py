import math

def validate_external(items,width,height):
    if isinstance(items,dict):items=items['damages']
    if not isinstance(items,list) or len(items)>100:raise ValueError('需要不超过100项的损伤数组')
    validated=[]
    for item in items:
        if not isinstance(item,dict):raise ValueError('每项损伤必须是对象')
        row=dict(item);box=row['bbox']
        if not isinstance(box,(list,tuple)) or len(box)!=4 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in box):raise ValueError('bbox必须有4个有限数值')
        x1,y1,x2,y2=box
        if not (0<=x1<x2<=width and 0<=y1<y2<=height):raise ValueError('bbox必须在EXIF纠正后原图范围内，且x1<x2、y1<y2')
        if not isinstance(row['damageType'],str) or not row['damageType']:raise ValueError('damageType不能为空')
        if isinstance(row.get('confidence'),bool):raise ValueError('confidence必须是数值')
        row['confidence']=float(row.get('confidence',1))
        if not 0<=row['confidence']<=1:raise ValueError('confidence必须在0至1之间')
        validated.append(row)
    return validated
