# rag_integration_test.py
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import logging

# 환경 변수 로드 (먼저 .env 파일 로드)
load_dotenv()

# 프로젝트 루트 디렉토리 계산 (app/test에서 두 단계 상위)
project_root = Path(__file__).parent.parent
chroma_storage_path = str(project_root / "chroma_storage")

# 환경 변수 명시적 설정
os.environ["VECTOR_PERSIST_PATH"] = chroma_storage_path
print(f"벡터 DB 경로 설정: {chroma_storage_path}")


# RagService는 환경 변수 설정 후에 임포트
from app.common.rag.rag_service import RagService

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag_test")


async def test_rag_system():
    # 테스트 테마들
    test_themes = [
        ["반도체"],
        ["기술"],
        ["AI"],
        ["여행"],
        ["증권"],
        ["부동산"],
        ["반도체", "기술"],
        ["AI", "반도체"]
    ]

    # RAG 서비스 초기화
    rag_service = RagService()

    # 각 테마에 대해 테스트
    for themes in test_themes:
        logger.info(f"\n[테스트] 테마: {themes}")

        # 기본 임계값으로 테스트
        result_default = rag_service.get_news_data(
            categories=themes,
            n_results=3,
            min_relevance_score=0.6  # 기존 높은 임계값
        )

        # 낮은 임계값으로 테스트
        result_low = rag_service.get_news_data(
            categories=themes,
            n_results=3,
            min_relevance_score=0.15  # 낮은 임계값
        )

        # 결과 로깅
        logger.info(f"기본 임계값(0.6) 결과 수: {len(result_default)}")
        logger.info(f"낮은 임계값(0.15) 결과 수: {len(result_low)}")

        if result_low:
            # 첫 번째 결과 상세 정보
            first_result = result_low[0]
            logger.info(f"최상위 결과: {first_result.get('title', '제목 없음')}")
            logger.info(f"유사도 점수: {first_result.get('relevance_score', 'N/A')}")


# 테스트 실행
if __name__ == "__main__":
    asyncio.run(test_rag_system())