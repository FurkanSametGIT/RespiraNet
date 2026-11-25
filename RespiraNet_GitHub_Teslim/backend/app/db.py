from __future__ import annotations
import os
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, BigInteger, DateTime, ForeignKey, JSON, Uuid, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

DATABASE_URL=os.getenv('DATABASE_URL','sqlite:///./respiranet-dev.db')
args={'check_same_thread':False} if DATABASE_URL.startswith('sqlite') else {}
engine=create_engine(DATABASE_URL,connect_args=args,pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)

class Base(DeclarativeBase): pass

def now():return datetime.now(timezone.utc)

class User(Base):
    __tablename__='users'
    id:Mapped[uuid.UUID]=mapped_column(Uuid(as_uuid=True),primary_key=True,default=uuid.uuid4)
    full_name:Mapped[str]=mapped_column(String(120))
    email:Mapped[str]=mapped_column(String(320),unique=True,index=True)
    password_hash:Mapped[str]=mapped_column(Text)
    role:Mapped[str]=mapped_column(String(16),default='user')
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)

class Recording(Base):
    __tablename__='recordings'
    id:Mapped[uuid.UUID]=mapped_column(Uuid(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id:Mapped[uuid.UUID]=mapped_column(Uuid(as_uuid=True),ForeignKey('users.id',ondelete='CASCADE'),index=True)
    reference_sample_id:Mapped[uuid.UUID|None]=mapped_column(Uuid(as_uuid=True),nullable=True)
    source_type:Mapped[str]=mapped_column(String(24),default='external_upload')
    original_filename:Mapped[str]=mapped_column(String(255))
    file_storage_key:Mapped[str|None]=mapped_column(Text,nullable=True)
    mime_type:Mapped[str]=mapped_column(String(80),default='audio/wav')
    file_size_bytes:Mapped[int|None]=mapped_column(BigInteger,nullable=True)
    duration_ms:Mapped[int|None]=mapped_column(Integer,nullable=True)
    sample_rate_hz:Mapped[int|None]=mapped_column(Integer,nullable=True)
    notes:Mapped[str]=mapped_column(Text,default='')   # added in migration 001
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    quality:Mapped['QualityCheck|None']=relationship(back_populates='recording',uselist=False,cascade='all, delete-orphan')

class QualityCheck(Base):
    __tablename__='quality_checks'
    id:Mapped[uuid.UUID]=mapped_column(Uuid(as_uuid=True),primary_key=True,default=uuid.uuid4)
    recording_id:Mapped[uuid.UUID]=mapped_column(Uuid(as_uuid=True),ForeignKey('recordings.id',ondelete='CASCADE'),unique=True)
    status:Mapped[str]=mapped_column(String(16))
    reason_codes:Mapped[list]=mapped_column(JSON,default=list)
    metrics:Mapped[dict]=mapped_column(JSON,default=dict)
    checked_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    recording:Mapped[Recording]=relationship(back_populates='quality')

def get_db():
    db=SessionLocal()
    try:yield db
    finally:db.close()
