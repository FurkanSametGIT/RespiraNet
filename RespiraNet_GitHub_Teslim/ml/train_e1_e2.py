"""Paired E1/E2 MobileNetV3-Small on Log-Mel with identical initialization.

This file does NOT contain precomputed results; run it only after acquiring ICBHI.
"""
import argparse
import hashlib
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

from ml.core import TARGET_SR, LABELS, read_audio_cycle, add_noise, logmel_image, metrics_four_class, patient_bootstrap_delta


def train(cycles: Path, out: Path, epochs=5, batch_size=16, lr=1e-3, seed=42, device='auto'):
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, Dataset
    from torchvision.models import mobilenet_v3_small

    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=pd.read_csv(cycles,dtype={'patient_id':'str'}).to_dict('records')
    by_split={part:[r for r in rows if r['split']==part] for part in ('train','validation','test')}
    if not all(by_split.values()):raise ValueError('Train/val/test split must all have cycles')
    all_labeled=set(r['label'] for r in by_split['train'])
    if len(all_labeled)<2:raise ValueError('Need >=2 training classes')
    device='cuda' if device=='auto' and torch.cuda.is_available() else ('cpu' if device=='auto' else device)
    torch.manual_seed(seed);np.random.seed(seed);random.seed(seed)
    if device=='cuda':torch.backends.cudnn.deterministic=True;torch.backends.cudnn.benchmark=False
    class SpectrogramDataset(Dataset):
        def __init__(self, examples, condition, snr=None, epoch=0):
            self.examples=examples;self.condition=condition;self.snr=snr;self.epoch=epoch
        def __len__(self):return len(self.examples)
        def __getitem__(self,i):
            r=self.examples[i]
            y=read_audio_cycle(r)
            if self.snr is not None:
                y=add_noise(y,self.snr,r['cycle_id'],seed)
            elif self.condition=='E2':
                digest=hashlib.sha256(f"{seed}-{self.epoch}-{r['cycle_id']}".encode()).digest()
                chosen=[5,10,20][int.from_bytes(digest[:2],'big')%3]
                y=add_noise(y,chosen,r['cycle_id']+':train:'+str(self.epoch),seed)
            im=logmel_image(y)
            return torch.from_numpy(im), LABELS.index(r['label'])

    def mk_model():
        torch.manual_seed(seed)
        model=mobilenet_v3_small(weights=None, num_classes=4)
        return model.to(device)

    results={}
    raw_predictions={}
    counts=np.array([sum(r['label']==label for r in by_split['train']) for label in LABELS]);weights=counts.sum()/(4*np.maximum(counts,1))
    class_weights=torch.as_tensor(weights,dtype=torch.float32,device=device)
    for cond in ('E1','E2'):
        random.seed(seed);np.random.seed(seed)
        model=mk_model()
        opt=torch.optim.AdamW(model.parameters(),lr=lr,weight_decay=1e-4)
        lossfn=nn.CrossEntropyLoss(weight=class_weights)
        history=[]
        for epoch in range(epochs):
            model.train();ds=SpectrogramDataset(by_split['train'],cond,epoch=epoch)
            gen=torch.Generator().manual_seed(seed+epoch)
            loader=DataLoader(ds,batch_size=batch_size,shuffle=True,generator=gen,num_workers=0)
            totals=[]
            for xb,yb in loader:
                xb=xb.to(device);yb=yb.to(device);opt.zero_grad()
                loss=lossfn(model(xb),yb);loss.backward();opt.step();totals.append(float(loss.item()))
            model.eval();valid_preds=[]
            with torch.no_grad():
                for xb,_ in DataLoader(SpectrogramDataset(by_split['validation'],'E1'),batch_size=batch_size):
                    valid_preds.extend(model(xb.to(device)).argmax(1).cpu().tolist())
            vm=metrics_four_class([r['label'] for r in by_split['validation']],[LABELS[p] for p in valid_preds])
            history.append({'epoch':epoch+1,'train_loss':float(np.mean(totals)),'validation_macro_f1':vm['macro_f1']})
            print(cond,'epoch',epoch+1,'train_loss',history[-1]['train_loss'],'val_f1',vm['macro_f1'])
        torch.save({'state_dict':model.cpu().state_dict(),'classes':LABELS,'seed':seed,'epochs':epochs,'condition':cond},out/f'{cond}_mobilenetv3.pt')
        model=model.to(device);model.eval()
        result={'experiment':cond,'model':'MobileNetV3-Small + Log-Mel','status':'measured',
          'seed':seed,'epochs':epochs,'batch_size':batch_size,'learning_rate':lr,
          'n_train':len(by_split['train']),'n_validation':len(by_split['validation']),'n_test':len(by_split['test']),
          'patient_count_test':len({r['patient_id'] for r in by_split['test']}),
          'history':history,'test':{}}
        for snr in (None,20,10):
            preds=[];key='clean' if snr is None else f'{snr}db'
            with torch.no_grad():
                for xb,_ in DataLoader(SpectrogramDataset(by_split['test'],'E1',snr=snr),batch_size=batch_size):
                    preds.extend(model(xb.to(device)).argmax(1).cpu().tolist())
            predicted=[LABELS[p] for p in preds]
            raw_predictions[(cond,key)]=predicted
            result['test'][key]=metrics_four_class([r['label'] for r in by_split['test']],predicted)
            (out/f'{cond}_predictions_{key}.json').write_text(json.dumps([
              {'cycle_id':r['cycle_id'],'patient_id':r['patient_id'],'truth':r['label'],'prediction':pr}
              for r,pr in zip(by_split['test'],predicted)],indent=2),encoding='utf-8')
        (out/f'{cond}_metrics.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
        results[cond]=result
    ci=patient_bootstrap_delta(by_split['test'],raw_predictions['E1','10db'],raw_predictions['E2','10db'],seed=seed)
    (out/'E2_minus_E1_10db_patient_bootstrap.json').write_text(json.dumps({'status':'measured','delta_sensitivity':
        results['E2']['test']['10db']['sensitivity']-results['E1']['test']['10db']['sensitivity'] if (
          results['E2']['test']['10db']['sensitivity'] is not None and results['E1']['test']['10db']['sensitivity'] is not None) else None,
        'confidence_interval_95':ci},indent=2),encoding='utf-8')
    print('Paired 10 dB patient bootstrap confidence interval:',ci)
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cycles',type=Path,default=Path('ml/outputs/cycles.csv'));p.add_argument('--out',type=Path,default=Path('ml/outputs/mobile'))
    p.add_argument('--epochs',type=int,default=5);p.add_argument('--batch-size',type=int,default=16);p.add_argument('--lr',type=float,default=1e-3);p.add_argument('--seed',type=int,default=42)
    p.add_argument('--device',default='auto');a=p.parse_args()
    train(a.cycles,a.out,epochs=a.epochs,batch_size=a.batch_size,lr=a.lr,seed=a.seed,device=a.device)
