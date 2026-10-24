# 第三方模型与数据来源

本工程复现公开模型，并添加学生2模块所需的识别包装、类别归并、重复区域处理、损伤匹配、页面与测试。第三方权重不应归为学生自主训练成果。

| 资源 | 来源 | 许可或使用记录 |
| --- | --- | --- |
| 部件模型parts.pt | [Majorburn/yolov11-carparts-seg](https://huggingface.co/Majorburn/yolov11-carparts-seg) | 模型卡标注AGPL-3.0 |
| 可选损伤模型damage.pt | [abdullahg7/cardd-yolov8s](https://huggingface.co/abdullahg7/cardd-yolov8s) | 模型卡标注AGPL-3.0，仅用于生成联调输入 |
| YOLO推理框架 | [Ultralytics](https://github.com/ultralytics/ultralytics) | AGPL-3.0；随附LICENSE文本 |
| 9张演示图片 | [Thanaphit公开演示空间](https://huggingface.co/spaces/Thanaphit/yolov8-car-parts-and-damage-segmentation/tree/main/sample) | 来自公开样例，保留原来源；本次用于本地学习测试，没有确认独立图片授权 |
| 公开部件测试集 | [Carparts-seg官方说明](https://docs.ultralytics.com/datasets/segment/carparts-seg/) | 数据下载保留在工作目录，不随源码压缩包重复分发 |

部件模型SHA256：`6759cf983e0bdefaa95d2d3fc6b37f89d3718a319c08617c3c7a339e18fdc3cd`。

损伤模型SHA256：`529602f6390c6f7016dd2ef9e3465a2923cf744589868278fb08b10464c35698`。

`asset-manifest.json`记录已下载权重和样例的地址、大小与SHA256。源码压缩包中的模型来源与许可记录应随工程保留。模型卡中的作者指标不作为本次测试结果引用。
