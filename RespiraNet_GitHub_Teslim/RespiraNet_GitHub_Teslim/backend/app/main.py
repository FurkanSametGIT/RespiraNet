"""Week 4/5 API: auth + private WAV quality CRUD + measured experiment reporting.

External/mobile WAV files NEVER receive ICBHI four-class predictions.
"""
from __future__ import annotations
from contextlib import asynccontextmanager
import json
import os
import re
import uuid
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import Base, engine, get_db, User, Recording, QualityCheck
from .security import current_user, hash_password, verify_password, create_token
from .audio import validate_wav, MAX_BYTES

@asynccontextmanager
async def lifespan(app:FastAPI):
    if os.getenv('AUTO_CREATE_TABLES','false').lower()=='true':
        Base.metadata.create_all(bind=engine) # SQLite demo; PostgreSQL uses schema + migration
    UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
    yield

app=FastAPI(title='RespiraNet Araştırma API',version='0.5.0',description='ICBHI 2017 araştırma prototipi. Tanı aracı değildir.',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=os.getenv('CORS_ORIGINS','http://localhost:5173').split(','),allow_credentials=False,allow_methods=['GET','POST','PATCH','DELETE'],allow_headers=['Authorization','Content-Type'])
UPLOAD_DIR=Path(os.getenv('UPLOAD_DIR','./private_uploads')).resolve()
REPORT_FILE=Path(os.getenv('REPORT_FILE','../experiments/comparison.json'))

class Register(BaseModel):
    full_name:str=Field(min_length=2,max_length=120)
    email:EmailStr
    password:str=Field(min_length=10,max_length=128)

class NotePatch(BaseModel):
    notes:str=Field(max_length=1000)

def serialize(rec:Recording):
    return {'id':str(rec.id),'filename':rec.original_filename,'source_type':rec.source_type,
       'notes':rec.notes or '', 'created_at':rec.created_at.isoformat() if rec.created_at else None,
       'duration_ms':rec.duration_ms,'sample_rate_hz':rec.sample_rate_hz,
       'quality':({'status':rec.quality.status,'reason_codes':rec.quality.reason_codes,
                   'metrics':rec.quality.metrics} if rec.quality else None),
       'prediction_status':'not_available_for_external_upload',
       'medical_disclaimer':'Bu analiz yalnız dosya kalitesi içindir; tıbbi tanı değildir.'}

@app.get('/api/health')
def health():return {'status':'ok','research_only':True}

@app.post('/api/auth/register',status_code=201)
def register(data:Register,db:Session=Depends(get_db)):
    email=str(data.email).lower()
    if db.scalar(select(User.id).where(User.email==email)):
        raise HTTPException(status_code=409,detail='Bu e-posta zaten kayıtlı')
    user=User(full_name=data.full_name,email=email,password_hash=hash_password(data.password))
    db.add(user)
    try:db.commit()
    except Exception:
        db.rollback();raise HTTPException(status_code=409,detail='Bu e-posta zaten kayıtlı')
    db.refresh(user)
    return {'id':str(user.id),'email':user.email,'full_name':user.full_name}

@app.post('/api/auth/login')
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==form.username.lower()))
    if not user or not verify_password(form.password,user.password_hash):
        raise HTTPException(status_code=401,detail='E-posta veya parola hatalı')
    return {'access_token':create_token(user.id),'token_type':'bearer'}

@app.get('/api/auth/me')
def me(user:User=Depends(current_user)):
    return {'id':str(user.id),'full_name':user.full_name,'email':user.email,'role':user.role}

@app.post('/api/recordings',status_code=201)
async def upload_recording(file:UploadFile=File(...),user:User=Depends(current_user),db:Session=Depends(get_db)):
    if len(file.filename or '')>255:raise HTTPException(status_code=422,detail='Dosya adı çok uzun')
    content=await file.read(MAX_BYTES+1)
    quality=validate_wav(content,file.filename or '')
    rec_id=uuid.uuid4()
    storage_key=f'{user.id}/{rec_id}.wav'
    path=(UPLOAD_DIR/storage_key).resolve()
    if not path.is_relative_to(UPLOAD_DIR):raise HTTPException(status_code=400,detail='Geçersiz dosya konumu')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(content)
    rec=Recording(id=rec_id,user_id=user.id,reference_sample_id=None,source_type='external_upload',
                  original_filename=Path(file.filename).name,file_storage_key=storage_key,mime_type='audio/wav',
                  file_size_bytes=len(content),duration_ms=quality['duration_ms'],sample_rate_hz=quality['sample_rate_hz'],notes='')
    rec.quality=QualityCheck(status=quality['status'],reason_codes=quality['reason_codes'],metrics=quality['metrics'])
    db.add(rec)
    try:db.commit();db.refresh(rec)
    except Exception:
        db.rollback();path.unlink(missing_ok=True);raise
    return serialize(rec)

@app.get('/api/recordings')
def list_recordings(user:User=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(Recording).where(Recording.user_id==user.id).order_by(Recording.created_at.desc())).all()
    return [serialize(r) for r in rows]

def owned_recording(rid:uuid.UUID,user:User,db:Session):
    row=db.get(Recording,rid)
    if not row or row.user_id!=user.id:raise HTTPException(status_code=404,detail='Kayıt bulunamadı')
    return row

@app.get('/api/recordings/{recording_id}')
def get_recording(recording_id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    return serialize(owned_recording(recording_id,user,db))

@app.patch('/api/recordings/{recording_id}')
def update_recording(recording_id:uuid.UUID,patch:NotePatch,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=owned_recording(recording_id,user,db);row.notes=patch.notes;db.commit();db.refresh(row);return serialize(row)

@app.delete('/api/recordings/{recording_id}',status_code=204)
def delete_recording(recording_id:uuid.UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=owned_recording(recording_id,user,db)
    path=(UPLOAD_DIR/row.file_storage_key).resolve() if row.file_storage_key else None
    if path is not None and not path.is_relative_to(UPLOAD_DIR):raise HTTPException(status_code=400,detail='Geçersiz dosya yolu')
    db.delete(row);db.commit()
    if path:path.unlink(missing_ok=True)
    return None

@app.get('/api/experiments')
def experiments(user:User=Depends(current_user)):
    if not REPORT_FILE.is_file():
        return {'status':'awaiting_dataset_and_training','results':[],
          'missing_experiments':['E0','E1','E2'],'disclaimer':'Gerçek ICBHI verisiyle deney henüz çalıştırılmadı.'}
    try:return json.loads(REPORT_FILE.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError):raise HTTPException(status_code=503,detail='Deney raporu okunamadı')
