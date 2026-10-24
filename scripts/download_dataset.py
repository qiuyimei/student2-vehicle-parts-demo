"""下载并校验本次复现采用的Carparts-seg快照，可仅解压test划分。"""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://github.com/ultralytics/assets/releases/download/v0.0.0/carparts-seg.zip'
SHA256 = 'e2eea20030d02366b07174bcdbcc843f63791bdd53962a83e00636d15e78e41f'
EXPECTED = {'train': 3156, 'val': 401, 'test': 276}


def validate_archive(archive, output):
    """提取前检查每一个归档路径，防止文件越出目标目录。"""
    output = Path(output).resolve()
    for name in archive.namelist():
        if not (output / name).resolve().is_relative_to(output):
            raise ValueError(f'归档路径超出目标目录：{name}')


def extract_dataset(zip_path, output, subset='test'):
    if subset not in ('test', 'all'):
        raise ValueError('subset应为test或all')
    zip_path = Path(zip_path)
    output = Path(output).resolve()
    if hashlib.sha256(zip_path.read_bytes()).hexdigest() != SHA256:
        raise ValueError('数据包SHA256不符；不要跳过校验，请核对下载版本')
    splits = ['test'] if subset == 'test' else ['train', 'val', 'test']
    with zipfile.ZipFile(zip_path) as archive:
        validate_archive(archive, output)
        members = [n for n in archive.namelist() if not n.endswith('/') and any(n.startswith(f'{kind}/{split}/') for kind in ('images', 'labels') for split in splits)]
        for split in splits:
            count = sum(n.startswith(f'images/{split}/') for n in members)
            if count != EXPECTED[split]:
                raise ValueError(f'{split}图片数异常：{count}')
        # 只写入已校验快照中明确的图像与标签路径。
        archive.extractall(output, members=members)
    summary = {'source': URL, 'sha256': SHA256, 'subset': subset, 'splits': {s: EXPECTED[s] for s in splits}}
    output.mkdir(parents=True, exist_ok=True)
    (output / f'download-{subset}-manifest.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--subset', choices=['test', 'all'], default='test')
    parser.add_argument('--output', default=str(ROOT / 'data/datasets/carparts-seg'))
    parser.add_argument('--source-zip', help='已有官方ZIP时指定该文件，可完全离线提取')
    args = parser.parse_args()
    archive = Path(args.source_zip) if args.source_zip else ROOT / 'data/downloads/carparts-seg.zip'
    if not archive.exists():
        if args.source_zip:
            raise FileNotFoundError(archive)
        archive.parent.mkdir(parents=True, exist_ok=True)
        temporary = archive.with_suffix('.partial')
        print('Downloading official dataset...', flush=True)
        with urllib.request.urlopen(URL, timeout=180) as source, temporary.open('wb') as dest:
            while chunk := source.read(1024 * 1024):
                dest.write(chunk)
        temporary.replace(archive)
    print(json.dumps(extract_dataset(archive, args.output, args.subset), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
