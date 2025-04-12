from typing import List, Dict, Any
from app.api.news.news_service import NewsService
from app.common.gpt.gpt_service import GPTService


class RecommendationService:
    @staticmethod
    async def generate_portfolio_recommendations(
            portfolio_count: int,
            stocks_per_portfolio: int,
            theme: str
    ) -> List[Dict[str, Any]]:
        """
        포트폴리오 추천을 생성합니다.

        Args:
            portfolio_count: 생성할 포트폴리오 수
            stocks_per_portfolio: 각 포트폴리오당 주식 수
            theme: 투자 테마

        Returns:
            포트폴리오 추천 목록
        """
        # 1. 뉴스 데이터 가져오기
        news_articles = NewsService.get_recent_news(limit=10, theme=theme)

        if not news_articles:
            print(f"경고: '{theme}' 테마 관련 뉴스 기사를 찾을 수 없습니다.")

        # 2. GPT API를 사용하여 포트폴리오 추천 생성
        return await GPTService.generate_portfolio_recommendations(
            portfolio_count=portfolio_count,
            stocks_per_portfolio=stocks_per_portfolio,
            theme=theme,
            news_articles=news_articles
        )