# app/schemas/member_dto.py
'''
1. 데이터 검증
API 를 통해 받거나 반환하는 Member 데이터의 형식과 타입을 검증한다.
예를 들어, Email 필드는 EmailStr 타입이어야 하며, 유효한 이메일 형식인지 자동으로 검증한다.

2. API 문서화
FastAPI 의 자동 문서화 시스템(Swagger/OpenAPI)에서 API 요청/응답의 스키마를 생성한다.

3. 데이터 반환
데이터베이스 모델 (SQLAlchemy)과 API 요청/응답 사이의 데이터 변환을 담당한다.
'''
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class MemberBase(BaseModel):
    email: EmailStr
    nickname: str
    role: str
    social_type: str

class MemberCreate(MemberBase):
    pass

class Member(MemberBase):
    id: int
    created_at: datetime
    update_at: datetime

    class Config:
        orm_mode = True