"""人为构造的教学输入，用于理解匹配公式；不是模型预测或准确率评估。"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ai.matching import match_damage

door = {'part': 'front_door', 'partLabel': '前车门', 'bbox': [0, 0, 100, 100], 'confidence': 0.9, 'instanceId': 'part-1'}
cases = {
    '小损伤位于大车门内部': {'damageType': 'dent', 'bbox': [10, 10, 20, 20]},
    '损伤与车门完全分离': {'damageType': 'scratch', 'bbox': [150, 150, 160, 160]},
    '车灯破损不能匹配给车门': {'damageType': 'lamp_broken', 'bbox': [10, 10, 20, 20]},
}
for title, damage in cases.items():
    result = match_damage(damage, [door])
    print(title)
    print(json.dumps({key: result[key] for key in ['part', 'matchCoverage', 'matchIou', 'damageRatio', 'matchStatus']}, ensure_ascii=False, indent=2))
