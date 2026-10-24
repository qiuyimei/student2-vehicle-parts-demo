import numpy as np
import pytest
from ai.matching import bbox_iou,match_damage

def part(code,box,instance='part-1'):
    return {'part':code,'partLabel':code,'bbox':box,'confidence':0.9,'instanceId':instance}

def test_small_damage_inside_large_part_is_not_rejected_by_low_iou():
    d={'bbox':[10,10,20,20]};p=part('door',[0,0,100,100])
    r=match_damage(d,[p])
    assert r['part']=='door' and r['matchCoverage']==1
    assert r['matchIou']==0.01 and r['damageRatio']==0.01

def test_disjoint_and_empty_parts_stay_unknown():
    d={'bbox':[10,10,20,20]}
    assert match_damage(d,[])['part']=='unknown'
    assert match_damage(d,[part('door',[50,50,100,100])])['damageRatio'] is None

def test_masks_override_misleading_bounding_boxes():
    dmask=np.zeros((10,10),bool);dmask[1:3,1:3]=True
    a=np.zeros_like(dmask);a[5:10,5:10]=True
    b=np.zeros_like(dmask);b[0:5,0:5]=True
    parts=[part('bumper',[0,0,10,10]),part('door',[0,0,5,5],'part-2')]
    r=match_damage({'bbox':[1,1,3,3]},parts,dmask,[a,b])
    assert r['part']=='door' and r['ratioMethod']=='mask_intersection'
    assert r['damageRatio']==0.16

def test_box_only_input_uses_part_mask_instead_of_part_bbox_area():
    pm=np.zeros((10,10),bool);pm[0:5,0:5]=True
    r=match_damage({'bbox':[1,1,3,3]},[part('door',[0,0,10,10])],part_masks=[pm])
    assert r['damageRatio']==0.16 and r['ratioMethod']=='bbox_mask_intersection'

def test_cross_boundary_damage_keeps_multiple_candidates():
    a=np.zeros((10,10),bool);a[:,:5]=True
    b=~a
    dm=np.zeros_like(a);dm[2:8,2:8]=True
    r=match_damage({'bbox':[2,2,8,8]},[part('door',[0,0,5,10]),part('bumper',[5,0,10,10],'part-2')],dm,[a,b])
    assert r['matchStatus']=='multiple_parts' and len(r['candidates'])==2
    assert r['matchCoverage']==0.5 and r['damageRatio']==0.36

def test_low_coverage_returns_unknown_instead_of_forcing_a_part():
    r=match_damage({'bbox':[0,0,10,10]},[part('door',[0,0,2,10])])
    assert r['matchCoverage']==0.2 and r['part']=='unknown'

def test_zero_area_damage_cannot_match():
    assert match_damage({'bbox':[1,1,1,1]},[part('door',[0,0,10,10])])['part']=='unknown'

def test_mismatched_mask_sizes_rejected():
    with pytest.raises(ValueError):match_damage({'bbox':[0,0,1,1]},[part('door',[0,0,1,1])],np.ones((2,2)),[np.ones((3,3))])

def test_iou_identical_and_disjoint():
    assert bbox_iou([0,0,10,10],[0,0,10,10])==1
    assert bbox_iou([0,0,10,10],[20,20,30,30])==0

def test_lamp_damage_cannot_be_matched_to_a_door():
    r=match_damage({'damageType':'lamp_broken','bbox':[1,1,3,3]},[part('front_door',[0,0,10,10])])
    assert r['part']=='unknown' and not r['candidates'][0]['semanticCompatible']

def test_semantic_constraint_keeps_overlapping_light_candidate():
    r=match_damage({'damageType':'lamp_broken','bbox':[1,1,3,3]},[part('front_door',[0,0,10,10]),part('front_left_light',[0,0,5,5],'part-2')])
    assert r['part']=='front_left_light' and r['matchStatus']=='matched'
