"""检查仓库内Markdown相对链接，跳过URL、锚点与代码块中的示例文本。"""
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
errors = []
checked = 0
for path in sorted(ROOT.rglob('*.md')):
    if any(part in {'.git', '.venv', 'data', '.pytest_cache'} for part in path.relative_to(ROOT).parts):
        continue
    source = re.sub(r'```.*?```', '', path.read_text(encoding='utf-8'), flags=re.S)
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', source):
        target = target.strip().split(' "')[0].strip('<>')
        if target.startswith(('http://', 'https://', '#', 'mailto:')):
            continue
        local = unquote(target.split('#', 1)[0])
        if not local:
            continue
        checked += 1
        if not (path.parent / local).exists():
            errors.append(f'{path.relative_to(ROOT)} -> {target}')
if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print(f'{checked} relative Markdown links verified.')
