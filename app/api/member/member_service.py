# app/services/member_service.py
from sqlalchemy.orm import Session
from app.domain.member import Member
from typing import Optional, Type


class MemberService:
    """
    회원 정보 관련 서비스 클래스

    - 이 클래스는 데이터베이스에서 회원 정보를 조회하는 메서드를 제공
    - 모든 메서드는 정적 메서드 (staticmethod)로 구현되어 있어 인스턴스 생성 없이 직접 호출 가능
    """
    @staticmethod
    def get_member_by_id(db: Session, member_id: int) -> Optional[Member]:

        """ID 로 회원 정보를 조회
        :param db: SQLAlchemy 데이터베이스 세션
        :param member_id: 조회할 회원의 ID
        :return: Optional[Member] : 해당 ID의 회원이 존재하면 Member 객체, 없으면 None
        """

        return db.query(Member).filter(Member.id == member_id).first()

    @staticmethod
    def get_member_by_email(db: Session, email: str) -> Optional[Member]:

        """이메일로 회원 정보를 조회
        :param db: SQLAlchemy 데이터베이스 세션
        :param email: (str) 조회할 회원의 이메일 주소
        :return: Optional[Member] : 해당 이메일의 회원이 존재하면 Member, 없으면 None
        """

        return db.query(Member).filter(Member.email == email).first()

    # 명시적 변환 방법
    @staticmethod
    def get_all_members(db: Session, skip: int = 0, limit: int = 100) -> list[Type[Member]]:
        """모든 회원 정보를 페이지네이션하여 조회
        :param db: (Session) SQLAlchemy 데이터베이스 세션
        :param skip: (int, optional) 건너뛸 레코드 수, 기본값은 0
        :param limit: (int, optional) 최대 반영할 레코드 수, 기본값은 100
        :return: sequence[Memnber] : 조회된 회원 목록
        """

        result = db.query(Member).offset(skip).limit(limit).all()
        return list(result)  # 명시적으로 list로 변환

    @staticmethod
    def get_members_by_social_type(db: Session, social_type: str) -> list[Type[Member]]:
        return db.query(Member).filter(Member.social_type == social_type).all()