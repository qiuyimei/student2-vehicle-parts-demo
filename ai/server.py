import io,json,math,os
from contextlib import asynccontextmanager
from PIL import Image,ImageOps,UnidentifiedImageError
from fastapi import FastAPI,UploadFile,File,Form,HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .pipeline import Pipeline,MEDIA,ROOT

pipeline=None
@asynccontextmanager
async def lifespan(app):
    global pipeline
    pipeline=Pipeline()
    yield

app=FastAPI(title='学生2 · 车辆部件识别与损伤定位',version='1.0.0',lifespan=lifespan)
app.mount('/media',StaticFiles(directory=str(MEDIA)),name='media')
app.mount('/samples',StaticFiles(directory=str(ROOT/'samples')),name='samples')
app.mount('/static',StaticFiles(directory=str(ROOT/'web')),name='web')

@app.get('/')
def index():return FileResponse(ROOT/'web/index.html')

@app.get('/api/health')
def health():return {'status':'ok','serverPid':os.getpid(),**pipeline.metadata()}

@app.get('/api/samples')
def samples():return [{'name':p.stem,'url':f'/samples/{p.name}','kind':'部件示例' if p.stem.startswith('parts') else '损伤示例'} for p in sorted((ROOT/'samples').glob('*.jpg'))]

@app.post('/api/predict')
def predict(file:UploadFile=File(...),mode:str=Form('parts'),partConfidence:float=Form(0.25),damageConfidence:float=Form(0.25),minCoverage:float=Form(0.35),damagesJson:str=Form('')):
    if mode not in ('parts','auto','external'):raise HTTPException(422,'不支持的模式')
    if not all(0.05<=v<=0.95 for v in (partConfidence,damageConfidence,minCoverage)):raise HTTPException(422,'阈值必须在0.05到0.95之间')
    data=file.file.read(12*1024*1024+1)
    if len(data)>12*1024*1024:raise HTTPException(413,'图片不能超过12MB')
    try:
        with Image.open(io.BytesIO(data)) as source:
            if source.width*source.height>8_000_000:raise HTTPException(413,'图片像素不能超过800万，请先缩小图片')
            image=ImageOps.exif_transpose(source).convert('RGB')
    except (UnidentifiedImageError,OSError,Image.DecompressionBombError):raise HTTPException(422,'无法读取图片，请上传JPEG、PNG或WebP')
    external=None
    if mode=='external':
        try:
            external=json.loads(damagesJson)
            if isinstance(external,dict):external=external['damages']
            if not isinstance(external,list) or len(external)>100:raise ValueError('需要不超过100项的损伤数组')
            for d in external:
                box=d['bbox']
                if len(box)!=4 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in box):raise ValueError('bbox必须有4个有限数值')
                x1,y1,x2,y2=box
                if not (0<=x1<x2<=image.width and 0<=y1<y2<=image.height):raise ValueError('bbox必须在EXIF纠正后原图范围内，且x1<x2、y1<y2')
                if not isinstance(d['damageType'],str) or not d['damageType']:raise ValueError('damageType不能为空')
                d['confidence']=float(d.get('confidence',1))
                if not 0<=d['confidence']<=1:raise ValueError('confidence必须在0至1之间')
        except (ValueError,TypeError,KeyError) as error:raise HTTPException(422,f'损伤JSON无效：{error}')
    return pipeline.predict(image,mode,partConfidence,damageConfidence,external,minCoverage)
