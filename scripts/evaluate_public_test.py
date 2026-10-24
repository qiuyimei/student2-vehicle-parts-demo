"""复现本次原始23类公开模型精度验证。输入官方Carparts-seg目录。"""
import argparse,json,time
from pathlib import Path
import torch
from ultralytics import YOLO

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--dataset',required=True,help='官方数据目录，含images/test与labels/test')
    parser.add_argument('--device',default='cpu')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];dataset=Path(args.dataset).resolve()
    if not (dataset/'images/test').is_dir() or not (dataset/'labels/test').is_dir():raise ValueError('缺少测试图片或标签')
    torch.set_num_threads(4)
    model=YOLO(str(root/'models/parts.pt'))
    config=root/'data/public-test-only.yaml';config.parent.mkdir(exist_ok=True)
    # YOLO验证器需要train/val字段；此配置仅用于split=test，不能用于训练。
    yaml='# Evaluation only. Never train with this YAML.\npath: '+json.dumps(str(dataset).replace('\\','/'))+'\ntrain: images/test\nval: images/test\ntest: images/test\nnames:\n'+''.join(f'  {i}: {name}\n' for i,name in model.names.items())
    config.write_text(yaml,encoding='utf-8')
    start=time.perf_counter()
    metrics=model.val(data=str(config),split='test',imgsz=640,batch=4,device=args.device,workers=0,plots=True,verbose=False,project=str(root/'results'),name='public-model-eval',exist_ok=True)
    report={'evaluationType':'公开原始23类部件模型，仅test划分，不含10类归并与匹配后处理','images':len(list((dataset/'images/test').glob('*.jpg'))),'metrics':{k:float(v) for k,v in metrics.results_dict.items()},'perClass':[{'classId':i,'name':model.names[i],'boxMap50_95':float(metrics.box.maps[i]),'maskMap50_95':float(metrics.seg.maps[i])} for i in range(len(model.names))],'elapsedSeconds':round(time.perf_counter()-start,2)}
    path=root/'results/public-model-metrics-rerun.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(path)

if __name__=='__main__':main()
