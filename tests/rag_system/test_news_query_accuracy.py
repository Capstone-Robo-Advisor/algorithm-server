# tests/rag_system/test_news_query_accuracy.py

import os
import logging

from pathlib import Path

# 경로 설정 확인 - 절대 경로 사용
project_root = Path(__file__).parent.parent.parent
chroma_storage_path = str(project_root / "chroma_storage")
os.environ["VECTOR_PERSIST_PATH"] = chroma_storage_path  # 중요: 환경변수 설정

from app.common.rag.rag_service import RagService

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_news_query_relevance():
    # RagService 초기화 (환경 변수 경로 사용)
    rag = RagService()

    # 실제 서비스와 동일학 테마 설정
    themes = ["반도체", "AI"]

    # 최소 유사도 점수 설정
    articles = rag.get_news_data(
        categories=themes,
        n_results=5,
        min_relevance_score=0.7,
        add_diversity=True   # 다양한 쿼리 활성화
    )

    # DB 내용 확인 출력
    logger.info(f"✅ 벡터 DB 경로: {os.environ.get('VECTOR_PERSIST_PATH')}")

    # 컬렉션 문서 수 확인
    count = rag.collection.count()
    logger.info(f"✅ 벡터 DB 총 문서 수: {count}")

    # 결과 출력
    if not articles:
        logger.info("❌ 뉴스 검색 결과가 없습니다.")

        #  검색 과정 디버깅
        logger.info("🔍 검색 쿼리 디버깅:")
        enriched_queries = []
        for category in themes:
            if "반도체" in category:
                enriched_queries.append(f"반도체 산업 관점에서 {category}")
            elif "기술" in category or "AI" in category:
                enriched_queries.append(f"기술 산업 관점에서 {category}")
            else:
                enriched_queries.append(category)
        query = f"{', '.join(enriched_queries)} 관련 산업 동향 및 뉴스 기사"
        logger.info(f"  실제 검색 쿼리: '{query}'")
        return

    logger.info(f"\n✅ 테마 관련 뉴스 검색 결과 ({len(articles)}개):")
    for i, article in enumerate(articles, 1):
        score = article['relevance_score']
        title = article['title']
        logger.info(f"{i}. (유사도: {score:.3f}) 제목: {title}")

        if themes[0] not in article['title'] and themes[0] not in article['summary']:
            logger.warning("⚠️ 관련성 낮은 기사 포함 가능성 있음.")

if __name__ == "__main__":
    test_news_query_relevance()
