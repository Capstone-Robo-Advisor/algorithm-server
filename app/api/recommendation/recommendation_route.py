from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.recommendation.dto.recommendation_dto import PortfolioRequestDTO, PortfolioDTO
from app.api.recommendation.recommendation_service import RecommendationService

router = APIRouter(tags=["recommendations"])


@router.post("", response_model=List[PortfolioDTO])
async def generate_portfolio_recommendations(request: PortfolioRequestDTO):
    """
    투자 테마와 포트폴리오 구성 요청에 따라 포트폴리오 추천을 생성합니다.
    """
    try:
        portfolios = await RecommendationService.generate_portfolio_recommendations(
            portfolio_count=request.portfolio_count,
            stocks_per_portfolio=request.stocks_per_portfolio,
            themes=request.theme
        )

        if not portfolios:
            raise HTTPException(status_code=500, detail="포트폴리오 추천을 생성하지 못했습니다.")

        return portfolios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"포트폴리오 추천 생성 실패: {str(e)}")