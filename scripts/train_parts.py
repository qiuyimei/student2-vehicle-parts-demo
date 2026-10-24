"""可选后续训练入口。未执行训练；需要自行合法获取并标注部件数据。"""
import argparse
from pathlib import Path
from ultralytics import YOLO
if __name__=='__main__':
    parser=argparse.ArgumentParser(description='训练学生2自己的部件分割模型')
    parser.add_argument('--data',required=True,help='YOLO分割数据集YAML，明确train/val/test')
    parser.add_argument('--epochs',type=int,default=50)
    parser.add_argument('--device',default='cpu')
    parser.add_argument('--model',default=str(Path(__file__).resolve().parents[1]/'models/parts.pt'))
    parser.add_argument('--output',default='runs/student2-parts')
    args=parser.parse_args()
    YOLO(args.model).train(data=args.data,epochs=args.epochs,imgsz=640,batch=4,device=args.device,workers=0,project=args.output,name='train',seed=42)
