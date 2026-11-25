"""Build immutable cycle/patient split manifest from locally downloaded ICBHI data."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from ml.core import collect_cycles, group_split, LABELS


def prepare(source: Path, out: Path, seed: int=42):
    rows, excluded=collect_cycles(source)
    rows=group_split(rows,seed)
    out.mkdir(parents=True,exist_ok=True)
    fields=list(rows[0].keys())
    with (out/'cycles.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    with (out/'excluded.json').open('w',encoding='utf-8') as f:json.dump(excluded,f,ensure_ascii=False,indent=2)
    split={s:{'patients':len({r['patient_id'] for r in rows if r['split']==s}),
              'cycles':sum(r['split']==s for r in rows),
              'labels':dict(Counter(r['label'] for r in rows if r['split']==s))}
           for s in ['train','validation','test']}
    sha=hashlib.sha256((out/'cycles.csv').read_bytes()).hexdigest()
    summary={'source':'ICBHI 2017 (local user-provided download)', 'seed':seed,'wav_count':len({r['wav_path'] for r in rows}),
             'patients':len({r['patient_id'] for r in rows}),'cycles':len(rows),'excluded_count':len(excluded),
             'split':split,'manifest_sha256':sha,'status':'observed'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    for s,counts in split.items():
        absent=[label for label in LABELS if counts['labels'].get(label,0)==0]
        if absent: print(f"WARNING: {s} split lacks classes {absent}; interpret metrics cautiously")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,default=Path('ml/outputs'))
    p.add_argument('--seed',type=int,default=42);a=p.parse_args();prepare(a.data,a.out,a.seed)
