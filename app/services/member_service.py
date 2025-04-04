# app/services/member_service.py
from sqlalchemy.orm import Session
from app.models.member import Member
from typing import Optional, Type


class MemberService:
    @staticmethod
    def get_member_by_id(db: Session, member_id: int) -> Optional[Member]:
        return db.query(Member).filter(Member.id == member_id).first()

    @staticmethod
    def get_member_by_email(db: Session, email: str) -> Optional[Member]:
        return db.query(Member).filter(Member.email == email).first()

    # 명시적 변환 방법
    @staticmethod
    def get_all_members(db: Session, skip: int = 0, limit: int = 100) -> list[Type[Member]]:
        result = db.query(Member).offset(skip).limit(limit).all()
        return list(result)  # 명시적으로 list로 변환

    # @staticmethod
    # def get_members_by_role(db: Session, role: str) -> list[Type[Member]]:
    #     return db.query(Member).filter(Member.role == role).all()

    @staticmethod
    def get_members_by_social_type(db: Session, social_type: str) -> list[Type[Member]]:
        return db.query(Member).filter(Member.social_type == social_type).all()