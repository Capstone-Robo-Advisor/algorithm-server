# app/models/member.py
from sqlalchemy import Column, BigInteger, String, DateTime, Enum, func
from app.db.database import Base

class Member(Base):
    """Member 데이터베이스 모델

    'members' 테이블과 매핑되는 SQLAlchemy ORM 모델 클래스
    사용자 계정 정보와 관련된 속성들을 포함
    """
    __tablename__ = "members"  # 데이터베이스 테이블 이름

    # 회원 고유 식별자 (기본 키)
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # 회원 이메일 주소 (고유 값, 인덱스 생성, NULL 허용)
    email = Column(String(255), unique=True, index=True, nullable=True)

    # 회원 닉네임 (NULL 허용 안 함)
    nickname = Column(String(255), nullable=False)

    # 회원 역할 (ENUM 타입, ROLE_USER만 허용)
    # 인증 및 권한 관리에 사용됨
    role = Column(Enum('ROLE_USER'), nullable=False)

    # 소셜 로그인 타입 (ENUM 타입, GOOGLE 또는 NAVER 허용)
    # 소셜 로그인 제공자를 구분하는 데 사용됨
    social_type = Column(Enum('GOOGLE', 'NAVER'), nullable=False)

    # 회원 생성 일시 (자동으로 현재 시간 설정)
    # 정밀도 6의 DateTime 타입 사용
    created_at = Column(DateTime(6), nullable=False, default=func.now())

    # 회원 정보 마지막 수정 일시 (생성 시 현재 시간, 업데이트 시 자동 갱신)
    # 정밀도 6의 DateTime 타입 사용
    update_at = Column(DateTime(6), nullable=False, default=func.now(), onupdate=func.now())

    def __repr__(self):
        """
        객체의 문자열 표현을 반환합니다.
        디버깅 및 로깅에 유용합니다.
        """
        return f"<Member(id={self.id}, email='{self.email}', nickname='{self.nickname}')>"