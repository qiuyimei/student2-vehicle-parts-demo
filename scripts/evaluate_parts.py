"""在独立人工标注测试集上计算真实指标。当前无GT数据，未执行。"""
import argparse,json
from pathlib import Path
from ultralytics import YOLO
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--data',required=True)
    parser.add_argument('--model',required=True)
    parser.add_argument('--device',default='cpu')
    parser.add_argument('--output',default='results/model-metrics.json')
    args=parser.parse_args()
    metrics=YOLO(args.model).val(data=args.data,split='test',imgsz=640,device=args.device,workers=0)
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(metrics.results_dict,ensure_ascii=False,indent=2),encoding='utf-8')
    print(output)
