# app/models/member.py
from sqlalchemy import Column, BigInteger, String, DateTime, Enum, func
from app.db.database import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    nickname = Column(String(255), nullable=False)
    role = Column(Enum('ROLE_USER'), nullable=False)
    social_type = Column(Enum('GOOGLE', 'NAVER'), nullable=False)
    created_at = Column(DateTime(6), nullable=False, default=func.now())
    update_at = Column(DateTime(6), nullable=False, default=func.now(), onupdate=func.now())