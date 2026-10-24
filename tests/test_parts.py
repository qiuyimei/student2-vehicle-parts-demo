import numpy as np
from ai.parts import merge_duplicate_parts

def test_same_region_conflicting_left_right_door_becomes_ambiguous():
    rows=[{'className':'front_left_door','bbox':[0,0,10,10],'confidence':0.8},{'className':'front_right_door','bbox':[0,0,10,10],'confidence':0.9}]
    masks=np.ones((2,10,10),bool)
    parts,pm=merge_duplicate_parts(rows,masks)
    assert len(parts)==1 and len(pm)==1
    assert parts[0]['className']=='front_door' and parts[0]['rawClass']=='front_right_door'
    assert parts[0]['labelStatus']=='ambiguous_label' and len(parts[0]['candidateClasses'])==2

def test_separate_same_class_wheels_are_preserved():
    rows=[{'className':'wheel','bbox':[0,0,3,3],'confidence':0.8},{'className':'wheel','bbox':[6,6,9,9],'confidence':0.9}]
    a=np.zeros((10,10),bool);a[:3,:3]=1
    b=np.zeros_like(a);b[6:9,6:9]=1
    parts,pm=merge_duplicate_parts(rows,np.array([a,b]))
    assert len(parts)==2

def test_overlapping_different_families_remain_separate():
    rows=[{'className':'hood','bbox':[0,0,10,10],'confidence':0.8},{'className':'front_bumper','bbox':[0,0,10,10],'confidence':0.9}]
    assert len(merge_duplicate_parts(rows,np.ones((2,10,10),bool))[0])==2
