import json
import pytest
from fastapi.testclient import TestClient
from ai.server import app
from ai.pipeline import ROOT

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as connection:yield connection

def sample():return (ROOT/'samples/damage-4.jpg').read_bytes()

def test_corrupt_image_returns_explanation(client):
    response=client.post('/api/predict',files={'file':('bad.jpg',b'not an image','image/jpeg')})
    assert response.status_code==422 and '无法读取' in response.json()['detail']

def test_out_of_range_threshold_rejected(client):
    response=client.post('/api/predict',files={'file':('car.jpg',sample(),'image/jpeg')},data={'partConfidence':'1.5'})
    assert response.status_code==422

def test_external_outside_image_rejected(client):
    damages=[{'damageType':'dent','bbox':[0,0,9999,9999]}]
    response=client.post('/api/predict',files={'file':('car.jpg',sample(),'image/jpeg')},data={'mode':'external','damagesJson':json.dumps(damages)})
    assert response.status_code==422 and '原图范围' in response.json()['detail']

def test_student1_external_damage_can_be_matched_without_damage_model(client):
    damages=[{'damageType':'dent','confidence':0.9,'bbox':[390,335,510,440]}]
    response=client.post('/api/predict',files={'file':('car.jpg',sample(),'image/jpeg')},data={'mode':'external','damagesJson':json.dumps(damages)})
    assert response.status_code==200
    result=response.json()
    assert result['width']==791 and result['height']==592
    assert result['damages'][0]['part']=='front_bumper'
    assert result['damages'][0]['ratioMethod']=='bbox_mask_intersection'
    assert result['damages'][0]['damageRatio']>0
    assert '显式输入' in result['damageOrigin']

def test_parts_only_contains_no_damage_predictions(client):
    response=client.post('/api/predict',files={'file':('car.jpg',sample(),'image/jpeg')},data={'mode':'parts'})
    assert response.status_code==200
    result=response.json()
    assert len(result['parts'])>0 and result['damages']==[]
    assert all(p['part']!='object' for p in result['parts'])

def test_explicit_model_path_is_reported_without_claiming_reference_origin(tmp_path):
    import shutil
    from ai.pipeline import Pipeline
    custom=tmp_path/'my-part-model.pt'
    shutil.copyfile(ROOT/'models/parts.pt',custom)
    metadata=Pipeline(parts_model=custom).metadata()
    assert metadata['partsModelFile']=='my-part-model.pt'
    assert '用户指定' in metadata['partsSource']
    assert metadata['moduleId']=='student2-vehicle-parts-demo'
