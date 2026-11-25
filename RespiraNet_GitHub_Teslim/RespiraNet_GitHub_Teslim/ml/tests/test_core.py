import io
import wave
import numpy as np
import pytest
from ml.core import group_split,label_from_flags,add_noise,metrics_four_class

def test_labels():
    assert [label_from_flags(c,w) for c,w in [(0,0),(1,0),(0,1),(1,1)]]==['normal','crackle','wheeze','both']
    with pytest.raises(ValueError):label_from_flags(3,0)

def test_patient_split_disjoint():
    rows=[{'patient_id':str(p),'cycle_id':f'{p}-{i}','label':'normal'} for p in range(100,125) for i in range(3)]
    a=group_split(rows,seed=42);b=group_split(rows,seed=42)
    assert a==b
    groups=[{r['patient_id'] for r in a if r['split']==x} for x in ['train','validation','test']]
    assert not any(groups[i]&groups[j] for i in range(3) for j in range(i+1,3))
    assert sum(len(v) for v in groups)==25

def test_deterministic_snr():
    y=np.sin(np.linspace(0,50,16000)).astype(np.float32)*0.2
    a=add_noise(y,10,'101:1',seed=42);b=add_noise(y,10,'101:1',seed=42)
    assert np.allclose(a,b)
    assert not np.allclose(a,y)

def test_four_classes_metric():
    labels=['normal','crackle','wheeze','both']
    m=metrics_four_class(labels,labels)
    assert m['macro_f1']==1 and m['sensitivity']==1 and m['specificity']==1
    assert m['icbhi_score']==1
