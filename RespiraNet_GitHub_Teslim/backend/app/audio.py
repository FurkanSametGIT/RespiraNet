"""A conservative WAV admission/quality check (not a diagnostic model)."""
import io
import wave
import numpy as np
from fastapi import HTTPException
MAX_BYTES=12*1024*1024
MIN_SECONDS=1.0
MAX_SECONDS=30.0

def validate_wav(content: bytes, filename: str) -> dict:
    if not filename.lower().endswith('.wav'):
        raise HTTPException(status_code=415,detail='Yalnızca WAV dosyası destekleniyor')
    if len(content)>MAX_BYTES:
        raise HTTPException(status_code=413,detail='Dosya 12 MB sınırını aşıyor')
    if len(content)<44 or content[:4]!=b'RIFF' or content[8:12]!=b'WAVE':
        raise HTTPException(status_code=422,detail='Geçersiz WAV içeriği')
    try:
        with wave.open(io.BytesIO(content),'rb') as wav:
            nch=wav.getnchannels();sr=wav.getframerate();width=wav.getsampwidth()
            frames=wav.getnframes(); compression=wav.getcomptype()
            if not (nch in (1,2) and 8000<=sr<=48000 and width==2 and compression=='NONE'):
                raise HTTPException(status_code=415,detail='PCM16 WAV; mono/stereo ve 8-48 kHz desteklenir')
            data=wav.readframes(frames)
        if len(data)<frames*nch*2:raise ValueError('truncated audio')
    except HTTPException:raise
    except (wave.Error,EOFError,ValueError) as ex:
        raise HTTPException(status_code=422,detail='WAV çözümlenemedi') from ex
    duration=frames/sr
    samples=np.frombuffer(data,dtype='<i2').astype(np.float32)/32768.0
    rms=float(np.sqrt(np.mean(samples**2))) if len(samples) else 0.0
    clipping=float(np.mean(np.abs(samples)>=0.999)) if len(samples) else 0.0
    reasons=[]
    if duration<MIN_SECONDS:reasons.append('TOO_SHORT')
    if duration>MAX_SECONDS:reasons.append('TOO_LONG')
    if rms<0.002:reasons.append('SILENCE_OR_TOO_QUIET')
    if clipping>0.10:reasons.append('CLIPPING')
    return {'status':'rejected' if reasons else 'accepted','reason_codes':reasons,'metrics':
      {'duration_s':round(duration,3),'sample_rate_hz':sr,'channels':nch,'rms':round(rms,6),'clip_fraction':round(clipping,6)},
      'duration_ms':int(duration*1000),'sample_rate_hz':sr}
