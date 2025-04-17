import logging

from typing import List, Dict, Any
from app.common.gpt.gpt_service import GPTService
from app.common.rag.rag_service import RagService

# 로거 객체 선언
logger = logging.getLogger(__name__)

class RecommendationService:
    @staticmethod
    async def generate_portfolio_recommendations(
            portfolio_count: int,
            stocks_per_portfolio: int,
            themes: List[str]
    ) -> List[Dict[str, Any]]:
        """포트폴리오 추천을 생성합니다.

        Args:
            portfolio_count: 생성할 포트폴리오 수
            stocks_per_portfolio: 각 포트폴리오당 주식 수
            theme: 투자 테마

        Returns:
            포트폴리오 추천 목록
        """
        # 1. 뉴스 데이터 가져오기
        rag_service = RagService()
        # 향상된 검색 품질을 위해 매개변수 추가
        news_articles = rag_service.get_news_data(
            categories=themes,
            n_results=5,  # 가져올 뉴스 수
            min_relevance_score=0.3  # 최소 관련성 점수
        )

        if not news_articles:
            logger.warning(f"⚠️'{themes}' 테마 관련 뉴스 기사를 찾을 수 없습니다.")
            news_articles = []

        # 2. GPT API를 사용하여 포트폴리오 추천 생성
        return await GPTService.generate_portfolio_recommendations(
            portfolio_count=portfolio_count,
            stocks_per_portfolio=stocks_per_portfolio,
            themes=themes,
            news_articles=news_articles
        )