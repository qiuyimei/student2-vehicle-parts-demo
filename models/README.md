# 模型文件说明

Git仓库提供下载脚本和校验值，模型二进制文件放在GitHub Release的离线源码包里。首次克隆仓库后执行：

```powershell
.venv/Scripts/python.exe scripts/download_models.py
```

正确结果应有两行 `SHA256 verified`：

| 文件 | 用途 | 大小 |
| --- | --- | --- |
| parts.pt | 学生2的车辆部件分割模型 | 6,016,100字节 |
| damage.pt | 自动联调时提供损伤输入 | 23,882,275字节 |

部件模型来源：[Majorburn/yolov11-carparts-seg](https://huggingface.co/Majorburn/yolov11-carparts-seg)。SHA256：`6759cf983e0bdefaa95d2d3fc6b37f89d3718a319c08617c3c7a339e18fdc3cd`。

损伤模型来源：[abdullahg7/cardd-yolov8s](https://huggingface.co/abdullahg7/cardd-yolov8s)。SHA256：`529602f6390c6f7016dd2ef9e3465a2923cf744589868278fb08b10464c35698`。

只运行学生2的部件识别或外部损伤框匹配时，算法只使用parts.pt；auto模式才加载damage.pt。当前自动下载脚本会准备两份文件，便于复现全部演示模式。两份权重均为公开预训练模型，来源与许可见[第三方说明](../THIRD_PARTY_NOTICES.md)。
