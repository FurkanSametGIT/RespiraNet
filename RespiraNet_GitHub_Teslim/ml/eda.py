"""EDA: counts, coverage, cycle-duration distribution, patient-level leakage audit."""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from ml.core import LABELS

def run(path:Path,out:Path):
    df=pd.read_csv(path,dtype={'patient_id':'str'});out.mkdir(parents=True,exist_ok=True)
    overlap={a+'_'+b:len(set(df[df.split==a].patient_id)&set(df[df.split==b].patient_id)) for a,b in [('train','validation'),('train','test'),('validation','test')]}
    if any(overlap.values()):raise ValueError(f'PATIENT LEAKAGE: {overlap}')
    table=pd.crosstab(df['split'],df['label']).reindex(index=['train','validation','test'],columns=LABELS,fill_value=0)
    table.to_csv(out/'class_distribution.csv')
    ax=table.plot.bar(figsize=(8,5),rot=0);ax.set_title('ICBHI — cycle labels by patient-disjoint split');ax.set_ylabel('Cycles');plt.tight_layout();plt.savefig(out/'class_distribution.png',dpi=150);plt.close()
    plt.figure(figsize=(8,4));plt.hist(df.duration_s,bins=35);plt.title('Respiratory cycle durations');plt.xlabel('Seconds');plt.ylabel('Count');plt.tight_layout();plt.savefig(out/'cycle_duration.png',dpi=150);plt.close()
    summary={'source':'actual local ICBHI cycles.csv','patients':int(df.patient_id.nunique()),'recordings':int(df.recording.nunique()),'cycles':len(df),
             'split_patients':{x:int(df[df.split==x].patient_id.nunique()) for x in ['train','validation','test']},'patient_overlap':overlap,
             'labels':{x:int((df.label==x).sum()) for x in LABELS},'cycle_duration_median_seconds':float(df.duration_s.median())}
    (out/'eda.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2));return summary
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cycles',type=Path,default=Path('ml/outputs/cycles.csv'));p.add_argument('--out',type=Path,default=Path('ml/outputs/eda'));a=p.parse_args();run(a.cycles,a.out)
