"""9张公开样例的真实推理烟测。没有GT，因此不计算或声称mAP。"""
import csv,json,sys,shutil
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from ai.pipeline import Pipeline,MEDIA

output=ROOT/'results';output.mkdir(exist_ok=True)
pipeline=Pipeline();rows=[]
for path in sorted((ROOT/'samples').glob('*.jpg')):
    with Image.open(path) as image:
        result=pipeline.predict(ImageOps.exif_transpose(image).convert('RGB'),'auto')
    (output/f'{path.stem}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    for key,suffix in [('partsImageUrl','parts'),('matchingImageUrl','matching')]:
        shutil.copyfile(MEDIA/Path(result[key]).name,output/f'{path.stem}-{suffix}.jpg')
    row={'image':path.name,'parts':len(result['parts']),'damageInputs':len(result['damages']),'matched':sum(d['matchStatus']!='unmatched' for d in result['damages']),'multipleCandidates':sum(d['matchStatus']=='multiple_parts' for d in result['damages']),'elapsedMs':result['elapsedMs'],'partLabels':' / '.join(p['partLabel'] for p in result['parts']),'matches':' / '.join(d['damageLabel']+'→'+d['partLabel'] for d in result['damages'])}
    rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
with (output/'batch-results.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
(output/'batch-summary.json').write_text(json.dumps({'images':len(rows),'partInstances':sum(r['parts'] for r in rows),'damageInputs':sum(r['damageInputs'] for r in rows),'matchedInputs':sum(r['matched'] for r in rows),'metricType':'运行烟测；无人工GT，不是准确率评估','rows':rows},ensure_ascii=False,indent=2),encoding='utf-8')
