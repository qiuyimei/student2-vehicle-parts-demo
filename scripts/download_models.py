import hashlib,pathlib,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
MODELS=[('parts.pt','https://huggingface.co/Majorburn/yolov11-carparts-seg/resolve/main/best.pt','6759cf983e0bdefaa95d2d3fc6b37f89d3718a319c08617c3c7a339e18fdc3cd'),('damage.pt','https://huggingface.co/abdullahg7/cardd-yolov8s/resolve/main/v2.0/best.pt','529602f6390c6f7016dd2ef9e3465a2923cf744589868278fb08b10464c35698')]
(ROOT/'models').mkdir(exist_ok=True)
for name,url,expected in MODELS:
    path=ROOT/'models'/name
    if not path.exists():
        temporary=path.with_suffix('.partial')
        with urllib.request.urlopen(url,timeout=180) as source,temporary.open('wb') as dest:
            while chunk:=source.read(1024*1024):dest.write(chunk)
        temporary.replace(path)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise RuntimeError(f'Checksum mismatch: {path}')
    print(name,'SHA256 verified')
