"""可脱离网页单独运行学生2模块，生成JSON和标注图。"""
import argparse,json,sys
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from ai.pipeline import Pipeline,MEDIA

def main():
    parser=argparse.ArgumentParser(description='学生2车辆部件识别与匹配Demo')
    parser.add_argument('--image',default=str(ROOT/'samples/damage-4.jpg'))
    parser.add_argument('--mode',choices=['parts','auto','external'],default='auto')
    parser.add_argument('--damages-json',help='外部损伤数组或包含damages字段的JSON文件')
    parser.add_argument('--output',default=str(ROOT/'results'))
    parser.add_argument('--part-confidence',type=float,default=0.25,help='部件检测置信度阈值')
    parser.add_argument('--damage-confidence',type=float,default=0.25,help='auto模式损伤置信度阈值')
    parser.add_argument('--min-coverage',type=float,default=0.35,help='接受匹配的最低损伤覆盖率')
    parser.add_argument('--parts-model',help='可选：指定自己验证过的YOLO部件分割权重')
    args=parser.parse_args()
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    external=None
    if args.mode=='external':
        if not args.damages_json:parser.error('external模式必须传入--damages-json')
        external=json.loads(Path(args.damages_json).read_text(encoding='utf-8'))
        if isinstance(external,dict):external=external['damages']
    with Image.open(args.image) as image:
        result=Pipeline(parts_model=args.parts_model).predict(ImageOps.exif_transpose(image).convert('RGB'),args.mode,part_conf=args.part_confidence,damage_conf=args.damage_confidence,external=external,min_coverage=args.min_coverage)
    stem=Path(args.image).stem
    result_file=output/f'{stem}-{args.mode}.json'
    result_file.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    for key,suffix in [('originalImageUrl','original'),('partsImageUrl','parts'),('matchingImageUrl','matching')]:
        data=(MEDIA/Path(result[key]).name).read_bytes()
        (output/f'{stem}-{suffix}.jpg').write_bytes(data)
    print(f"部件 {len(result['parts'])} 个，损伤 {len(result['damages'])} 处，耗时 {result['elapsedMs']} ms")
    print(result_file)

if __name__=='__main__':main()
