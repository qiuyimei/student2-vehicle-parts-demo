"""从文件调用学生2服务，避免PowerShell不同版本的multipart差异。"""
import argparse
import json
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8765')
    parser.add_argument('--image', default=str(ROOT / 'samples/damage-4.jpg'))
    parser.add_argument('--mode', choices=['parts', 'auto', 'external'], default='external')
    parser.add_argument('--damages-json', default=str(ROOT / 'config/student1-example.json'))
    parser.add_argument('--output', default=str(ROOT / 'results/tutorial-runs/api-result.json'))
    args = parser.parse_args()
    data = {'mode': args.mode, 'partConfidence': 0.25, 'damageConfidence': 0.25, 'minCoverage': 0.35}
    if args.mode == 'external':
        data['damagesJson'] = Path(args.damages_json).read_text(encoding='utf-8')
    with Path(args.image).open('rb') as image:
        response = requests.post(args.url.rstrip('/') + '/api/predict', data=data, files={'file': (Path(args.image).name, image, 'image/jpeg')}, timeout=120)
    if not response.ok:
        raise SystemExit(f'HTTP {response.status_code}: {response.text}')
    result = response.json()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"parts={len(result['parts'])}, damages={len(result['damages'])}")
    print(output)
