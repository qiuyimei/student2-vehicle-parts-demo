import pytest
from ai.inputs import validate_external

@pytest.mark.parametrize('box',[[0,0,float('nan'),10],[0,0,float('inf'),10],[10,0,5,10],[-1,0,5,5],[0,0,101,5]])
def test_invalid_external_coordinates_rejected(box):
    with pytest.raises(ValueError):validate_external([{'bbox':box,'damageType':'dent'}],100,100)

def test_external_input_is_copied_not_mutated():
    damage={'bbox':[0,0,5,5],'damageType':'dent'}
    result=validate_external({'damages':[damage]},10,10)
    assert result[0]['confidence']==1 and 'confidence' not in damage
