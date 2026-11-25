import os
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .db import User, get_db

hasher=PasswordHasher(time_cost=2,memory_cost=19456,parallelism=2)
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/api/auth/login')

def secret():
    key=os.getenv('JWT_SECRET','')
    if len(key)<32:raise RuntimeError('JWT_SECRET environment variable must be at least 32 characters')
    return key

def hash_password(password):return hasher.hash(password)

def verify_password(plain,hashval):
    try:return hasher.verify(hashval,plain)
    except (VerifyMismatchError,VerificationError,InvalidHashError):return False

def create_token(subject):
    payload={'sub':str(subject),'exp':datetime.now(timezone.utc)+timedelta(hours=4)}
    return jwt.encode(payload,secret(),algorithm='HS256')

def current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    try:
        data=jwt.decode(token,secret(),algorithms=['HS256'])
        from uuid import UUID
        user=db.get(User,UUID(str(data['sub'])))
        if user:return user
    except (InvalidTokenError,ValueError,KeyError,TypeError):pass
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Geçersiz veya süresi dolmuş oturum',headers={'WWW-Authenticate':'Bearer'})
