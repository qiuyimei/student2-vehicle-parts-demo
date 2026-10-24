"""离线检查复现条件，不运行模型推理，也不上传本机信息。"""
import argparse
import hashlib
from importlib import metadata
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MODELS = {
    'parts.pt': '6759cf983e0bdefaa95d2d3fc6b37f89d3718a319c08617c3c7a339e18fdc3cd',
    'damage.pt': '529602f6390c6f7016dd2ef9e3465a2923cf744589868278fb08b10464c35698',
}
PACKAGES = ['torch', 'torchvision', 'ultralytics', 'fastapi', 'uvicorn', 'python-multipart', 'numpy', 'pillow', 'opencv-python', 'requests', 'pytest']


def inspect():
    packages = {}
    for package in PACKAGES:
        try:
            packages[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            packages[package] = None
    models = {}
    for name, expected in EXPECTED_MODELS.items():
        path = ROOT / 'models' / name
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        models[name] = {'exists': path.exists(), 'sha256': digest, 'verified': digest == expected}
    return {
        'pythonVersion': sys.version.split()[0],
        'python312': sys.version_info[:2] == (3, 12),
        'packages': packages,
        'models': models,
        'sampleCount': len(list((ROOT / 'samples').glob('*.jpg'))),
        'readyForAllDemos': all(packages.values()) and all(m['verified'] for m in models.values()),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='检查Python依赖、权重和样例')
    parser.add_argument('--strict', action='store_true', help='缺依赖或模型校验失败时返回非零状态码')
    args = parser.parse_args()
    report = inspect()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.strict and not report['readyForAllDemos']:
        raise SystemExit(1)
