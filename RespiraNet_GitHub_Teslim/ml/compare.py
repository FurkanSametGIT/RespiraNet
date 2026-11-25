"""Create honest benchmark table from existing real evaluation JSON, without fabricated numbers."""
import argparse
import csv
import json
from pathlib import Path

def build(root: Path,out: Path):
    files={'E0':root/'E0'/'E0_metrics.json','E1':root/'mobile'/'E1_metrics.json','E2':root/'mobile'/'E2_metrics.json'}
    records=[];missing=[]
    for condition,path in files.items():
        if not path.exists():
            missing.append(condition)
            continue
        payload=json.loads(path.read_text(encoding='utf-8'))
        if payload.get('status')!='measured':raise ValueError(f'Unmeasured result marked as benchmark: {path}')
        for test,metrics in payload['test'].items():
            records.append({'model':condition,'snr':test,'n_test_cycles':metrics['n_cycles'],
                            'n_test_patients':payload['patient_count_test'], 'macro_f1':metrics['macro_f1'],
                            'sensitivity':metrics['sensitivity'], 'specificity':metrics['specificity'],
                            'icbhi_score':metrics['icbhi_score']})
    out.mkdir(parents=True,exist_ok=True)
    columns=['model','snr','n_test_cycles','n_test_patients','macro_f1','sensitivity','specificity','icbhi_score']
    with (out/'comparison.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(records)
    summary={'status':'measured_partial' if records else 'awaiting_dataset_and_training', 'missing_experiments':missing,'results':records,
             'disclaimer':'Same test cycles under clean/20 dB/10 dB are paired observations; not independent samples.'}
    (out/'comparison.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# RespiraNet deney karşılaştırması','',f"Durum: **{summary['status']}**",'',
           'Bu tabloda yalnızca gerçek veriyle çalıştırılmış deneyler yer alır.']
    lines+=['','| Model | SNR | Döngü | Hasta | Macro-F1 | Se | Sp | ICBHI |','|---|---|---:|---:|---:|---:|---:|---:|']
    for r in records:
        def fmt(x):return f'{x:.3f}' if x is not None else '—'
        lines.append(f"| {r['model']} | {r['snr']} | {r['n_test_cycles']} | {r['n_test_patients']} | {fmt(r['macro_f1'])} | {fmt(r['sensitivity'])} | {fmt(r['specificity'])} | {fmt(r['icbhi_score'])} |")
    if missing:lines+=['',f"Henüz ölçülmeyen deneyler: {', '.join(missing)}."]
    lines+=['','SNR kopyaları bağımsız hasta/döngü olarak sayılmaz.','']
    (out/'comparison.md').write_text('\n'.join(lines),encoding='utf-8')
    print(f'Wrote comparison files; measured experiments={len(files)-len(missing)}; missing={missing}')
    return summary
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('ml/outputs'));p.add_argument('--out',type=Path,default=Path('experiments'));a=p.parse_args();build(a.root,a.out)
