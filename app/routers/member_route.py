# app/routers/member.py
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List
from enum import Enum

from app.db.database import get_db
from app.services.member_service import MemberService
from app.schemas.member_sch import Member as MemberSchema

router = APIRouter()

# ENUM 검증을 위한 클래스
class RoleEnum(str, Enum):
    ROLE_USER = "ROLE_USER"

class SocialTypeEnum(str, Enum):
    GOOGLE = "GOOGLE"
    NAVER = "NAVER"

@router.get("/members/", response_model = List[MemberSchema])
def read_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    members = MemberService.get_all_members(db, skip=skip, limit=limit)
    return members

@router.get("/members/{member_id}", response_model=MemberSchema)
def read_member(member_id: int, db: Session = Depends(get_db)):
    db_member = MemberService.get_member_by_id(db, member_id=member_id)

    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

# @router.get("/members/role/{role}", response_model=List[MemberSchema])
# def read_members_by_role(role: str, db: Session = Depends(get_db)):
#     members = MemberService.get_members_by_role(db, role=role)
#     return members

# 더 구체적인 경로부터 정의
@router.get("/members/email/{email}", response_model=MemberSchema)
def read_member_by_email(
    email: str = Path(..., description="회원 이메일 주소"),
    db: Session = Depends(get_db)
):
    db_member = MemberService.get_member_by_email(db, email=email)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member
