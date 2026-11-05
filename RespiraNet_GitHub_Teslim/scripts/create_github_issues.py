#!/usr/bin/env python3
"""issues.json içindeki taslakları GitHub'a aktarır.
Güvenli varsayılan: yalnız önizleme. Gerçek işlem için --apply gerekir.
Gereksinimler: GitHub CLI (gh) + gh auth login, repo erişim yetkisi.
"""
import argparse,json,subprocess,shutil,sys
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--repo',required=True,help='owner/repo örn. kullanici/RespiraNet')
p.add_argument('--apply',action='store_true',help='GitHub üzerinde issue aç')
args=p.parse_args()
if '/' not in args.repo:sys.exit('Geçersiz repo, owner/repo biçimi gerekli.')
items=json.loads((Path(__file__).parent.parent/'issues.json').read_text(encoding='utf-8'))
print('Repo:',args.repo,'İş sayısı:',len(items),'Mod:',('YAZMA' if args.apply else 'ÖNİZLEME'))
if not args.apply:
 for i in items:print(i['title'])
 sys.exit(0)
if not shutil.which('gh'):sys.exit('gh bulunamadı. GitHub CLI kur ve gh auth login çalıştır.')
def gh(*argv):
 return subprocess.run(['gh',*argv],text=True,capture_output=True,check=True)
try:
 auth=gh('auth','status')
 current=json.loads(gh('issue','list','--repo',args.repo,'--state','all','--limit','1000','--json','title').stdout)
 existing={x['title'] for x in current}
 labels=sorted({label for item in items for label in item['labels']})
 for lab in labels:
  subprocess.run(['gh','label','create',lab,'--repo',args.repo,'--color','BFD9E3','--force'],capture_output=True,text=True,check=True)
 for item in items:
  if item['title'] in existing:print('SKIP (zaten var)',item['title']);continue
  cmd=['gh','issue','create','--repo',args.repo,'--title',item['title'],'--body',item['body']]
  for label in item['labels']:cmd+=['--label',label]
  res=subprocess.run(cmd,text=True,capture_output=True,check=True)
  print('CREATED',item['title'],res.stdout.strip())
except subprocess.CalledProcessError as err:
 print('GitHub işlemi başarısız:',err.stderr or str(err),file=sys.stderr)
 sys.exit(2)
