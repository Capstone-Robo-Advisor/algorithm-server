# app/routers/member.py
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List
from enum import Enum

from app.common.db.database import get_db
from app.api.member.member_service import MemberService
from app.api.member.dto.member_dto import Member as MemberSchema

router = APIRouter()

# ENUM 검증을 위한 클래스
class RoleEnum(str, Enum):
    ROLE_USER = "ROLE_USER"

class SocialTypeEnum(str, Enum):
    GOOGLE = "GOOGLE"
    NAVER = "NAVER"

@router.get("/members/", response_model = List[MemberSchema])
def read_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """전체 회원 목록 조회 API
    :param skip: 건너뛸 레코드 수 (기본값 : 0)
    :param limit: 최대 반환할 레코드 수 (기본값 : 100)
    :param db: 데이터베이스 세션 (의존성 주입)
    :return: List[MemberSchema] : 회원 객체 목록
    """
    members = MemberService.get_all_members(db, skip=skip, limit=limit)
    return members

@router.get("/members/{member_id}", response_model=MemberSchema)
def read_member(member_id: int, db: Session = Depends(get_db)):
    """특정 ID의 회원 정보 조회 API
    :param member_id: (int) 조회할 회원의 ID
    :param db: 데이터베이스 세션 (의존성 주입)
    :return: MemberScheman : 회원 객체
    :raise HTTPException: 회원을 찾을 수 없는 경우 404 에러 발생
    """
    db_member = MemberService.get_member_by_id(db, member_id=member_id)

    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

# 더 구체적인 경로부터 정의
@router.get("/members/email/{email}", response_model=MemberSchema)
def read_member_by_email(
    email: str = Path(..., description="회원 이메일 주소"),
    db: Session = Depends(get_db)
):
    """이메일로 회원 정보 조회 API
    :param email: (str) 조회할 회원의 이메일 주소
    :param db: 데이터베이스 세션(의존성 주입)
    :return: MemberSchema: 회원 객체
    :raise: HTTPException : 회원을 찾을 수 없는 경우 404 에러 발생
    """
    db_member = MemberService.get_member_by_email(db, email=email)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member
