from .conftest import login

def test_health(client):
    res=client.get('/api/health');assert res.status_code==200;assert res.json()['research_only']

def test_auth_and_recording_crud(client,wav_bytes):
    headers=login(client)
    assert client.get('/api/auth/me',headers=headers).json()['email']=='demo@example.com'
    upload=client.post('/api/recordings',headers=headers,files={'file':('breathing.wav',wav_bytes,'audio/wav')})
    assert upload.status_code==201,upload.text
    rec=upload.json(); assert rec['quality']['status']=='accepted'
    assert rec['prediction_status']=='not_available_for_external_upload'
    rid=rec['id']
    assert len(client.get('/api/recordings',headers=headers).json())==1
    updated=client.patch('/api/recordings/'+rid,headers=headers,json={'notes':'Deneme kaydı'})
    assert updated.status_code==200
    assert updated.json()['notes']=='Deneme kaydı'
    assert client.get('/api/recordings/'+rid,headers=headers).status_code==200
    assert client.delete('/api/recordings/'+rid,headers=headers).status_code==204
    assert client.get('/api/recordings/'+rid,headers=headers).status_code==404

def test_user_isolation(client,wav_bytes):
    a=login(client,'a@example.com')
    rid=client.post('/api/recordings',headers=a,files={'file':('test.wav',wav_bytes,'audio/wav')}).json()['id']
    b=login(client,'b@example.com')
    assert client.get('/api/recordings/'+rid,headers=b).status_code==404
    assert client.patch('/api/recordings/'+rid,headers=b,json={'notes':'x'}).status_code==404
    assert client.delete('/api/recordings/'+rid,headers=b).status_code==404
    assert client.get('/api/recordings',headers=b).json()==[]

def test_invalid_file_rejected(client):
    h=login(client)
    resp=client.post('/api/recordings',headers=h,files={'file':('not_audio.wav',b'not-a-wav','audio/wav')})
    assert resp.status_code==422

def test_silence_logged_as_rejected(client):
    import io,wave
    b=io.BytesIO()
    with wave.open(b,'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(b'\0\0'*16000)
    h=login(client)
    r=client.post('/api/recordings',headers=h,files={'file':('silent.wav',b.getvalue(),'audio/wav')})
    assert r.status_code==201
    assert r.json()['quality']['status']=='rejected'
    assert 'SILENCE_OR_TOO_QUIET' in r.json()['quality']['reason_codes']

def test_experiments_never_make_up_numbers(client):
    import app.main as mod
    h=login(client)
    original=mod.REPORT_FILE
    mod.REPORT_FILE=mod.REPORT_FILE.with_name('___non_existing_file___')
    try:
        r=client.get('/api/experiments',headers=h)
        assert r.status_code==200
        assert r.json()['results']==[]
        assert r.json()['status']=='awaiting_dataset_and_training'
    finally:mod.REPORT_FILE=original
