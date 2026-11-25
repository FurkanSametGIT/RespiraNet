import io
import os
import sys
import wave
from pathlib import Path
import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ['JWT_SECRET']='test-secret-do-not-use-outside-tests-1234567890'
os.environ['DATABASE_URL']='sqlite://'
os.environ['AUTO_CREATE_TABLES']='false'
from app.db import Base,get_db
from app.main import app
import app.main as app_module

@pytest.fixture
def client(tmp_path,monkeypatch):
    dbengine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
    Base.metadata.create_all(dbengine)
    factory=sessionmaker(bind=dbengine,autoflush=False)
    def dep():
        with factory() as db:yield db
    app.dependency_overrides[get_db]=dep
    monkeypatch.setattr(app_module,'UPLOAD_DIR',tmp_path/'private')
    with TestClient(app) as tc:yield tc
    app.dependency_overrides.clear()
    dbengine.dispose()

@pytest.fixture
def wav_bytes():
    samples=(0.25*np.sin(np.arange(16000)*2*np.pi*440/16000)*32767).astype('<i2')
    buf=io.BytesIO()
    with wave.open(buf,'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(16000);wav.writeframes(samples.tobytes())
    return buf.getvalue()

def login(client,email='demo@example.com',pwd='VeryStrongDemo123!'):
    r=client.post('/api/auth/register',json={'full_name':'Test Student','email':email,'password':pwd})
    assert r.status_code==201,r.text
    token=client.post('/api/auth/login',data={'username':email,'password':pwd})
    assert token.status_code==200,token.text
    return {'Authorization':'Bearer '+token.json()['access_token']}
