"""E0 MFCC + SVM. Uses held-out validation only for model choice, tests once."""
import argparse
import json
from pathlib import Path
from collections import Counter
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import f1_score
from ml.core import read_audio_cycle, extract_mfcc, add_noise, metrics_four_class, LABELS

def run(cycles, out, seed=42):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(cycles,dtype={'patient_id':'str'}).to_dict('records')
    data={}
    for split in ('train','validation','test'):
        rows=[r for r in df if r['split']==split]
        if not rows:raise ValueError(f'{split} split empty')
        X=[]
        for r in rows:X.append(extract_mfcc(read_audio_cycle(r)))
        data[split]=(rows,np.stack(X))
    train, X_train=data['train']; val,X_val=data['validation']; test,_=data['test']
    y_train=[r['label'] for r in train]; y_val=[r['label'] for r in val]
    candidates=[]
    for c in (0.1,1.0,10.0):
        model=Pipeline([('scale',StandardScaler()),('svm',SVC(C=c,kernel='rbf',class_weight='balanced',probability=True,random_state=seed))])
        model.fit(X_train,y_train)
        score=float(f1_score(y_val,model.predict(X_val),labels=LABELS,average='macro',zero_division=0))
        candidates.append((score,c,model))
    candidates.sort(key=lambda x:(-x[0],x[1]))
    _,best_c,model=candidates[0];joblib.dump(model,out/'E0_mfcc_svm.joblib')
    result={'experiment':'E0','model':'MFCC + SVM','status':'measured','seed':seed,'chosen_C':best_c,
            'n_train':len(train),'n_validation':len(val),'n_test':len(test),
            'patient_count_test':len(set(r['patient_id'] for r in test)),'validation_macro_f1':candidates[0][0], 'test':{}}
    for snr in (None,20,10):
        X=np.stack([extract_mfcc(add_noise(read_audio_cycle(r),snr,r['cycle_id'],seed)) for r in test])
        preds=model.predict(X).tolist();metrics=metrics_four_class([r['label'] for r in test],preds)
        key='clean' if snr is None else f'{snr}db';result['test'][key]=metrics
        (out/f'E0_predictions_{key}.json').write_text(json.dumps([
            {'cycle_id':r['cycle_id'],'patient_id':r['patient_id'],'truth':r['label'],'prediction':p}
            for r,p in zip(test,preds)],indent=2),encoding='utf-8')
    (out/'E0_metrics.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cycles',type=Path,default=Path('ml/outputs/cycles.csv'));p.add_argument('--out',type=Path,default=Path('ml/outputs/E0'));p.add_argument('--seed',type=int,default=42);a=p.parse_args();run(a.cycles,a.out,a.seed)
