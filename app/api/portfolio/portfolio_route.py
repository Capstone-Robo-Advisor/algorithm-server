from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from app.api.portfolio.dto.portfolio_dto import OptimizationRequestDTO, OptimizationResultDTO
from app.api.portfolio.portfolio_service import PortfolioService

router = APIRouter()

@router.post(
    "/optimize",
    summary="레거시(현재 사용되지 않으나 혹시 몰라서 놔둠",
    response_model=OptimizationResultDTO,
    description="티커, 종목명, 배분 비율 배열을 사용한 포트폴리오 최적화",
    deprecated=True,
)
async def optimize_portfolio(request: OptimizationRequestDTO):
    """포트폴리오 최적화 (PyPortfolio 를 사용)

    - 주어진 티커 목록의 초적 배분 비율 계산
    - 예상 수익률, 변동성, 샤프 비율 계산

    :param
    - tickers: 티커 목록 (예 : ["AAPL", "MSFT", "GOOGL"])
    - names: 회사명 목록 (예: ["Apple Inc", "Microsoft Corp", "Alphabet Inc"])
    - allocations: (선택) 초기 배분 비율 (예: [0.3, 0.2, 0.5])
    - period: 데이터 수집 기간 (기본값: "2y")
    - risk_free_rate: 무위험 수익률 (기본값: 0.02)
    :return:
    """
    try:
        result = PortfolioService.optimize_portfolio(
            tickers=request.tickers,
            names=request.names,
            allocations=request.allocations,
            period=request.period,
            risk_free_rate=request.risk_free_rate
        )
        return result
    except ValueError as e:
        # 입력값 문제 또는 최적화 계산 문제
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 서버 문제 또는 예상치 못한 오류
        raise HTTPException(status_code=500, detail=f"최적화 중 오류 발생: {str(e)}")


@router.post(
    "/optimize-gpt-recommendation",
    summary="GPT API 응답을 그대로 다시 PyPortfolio 로 전달",
    response_model=OptimizationResultDTO,
    description="GPT API가 추천한 포트폴리오를 최적화"
)
async def optimize_gpt_portfolio(portfolio: Dict[str, Any] = Body(..., example={
    "name": "포트폴리오 2",
    "stocks": [
        {"ticker": "TSLA", "name": "Tesla", "allocation": 30},
        {"ticker": "CVX", "name": "Chevron", "allocation": 20}
    ],
    "description": "다양한 산업 전반에 걸쳐..."
})):
    """GPT 추천 포트폴리오 최적화

    GPT API 가 생성한 포트폴리오 추천 형식을 그대로 받아 최적화합니다.
    :param portfolio:
    :return:
    """
    try:
        # GPT 응답에서 데이터 추출
        tickers = [stock["ticker"] for stock in portfolio["stocks"]]
        names = [stock["name"] for stock in portfolio["stocks"]]

        # 정수 퍼센트를 소수로 변환 (30% -> 0.3)
        allocations = [stock["allocation"] / 100 for stock in portfolio["stocks"]]

        # 기존 최적화 서비스 활용
        result = PortfolioService.optimize_portfolio(
            tickers=tickers,
            names=names,
            allocations=allocations,
        )
        return result
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"잘못된 포트폴리오 형식: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Rate Limit 오류 처리 (추가)
        error_msg = str(e)
        if "Rate limited" in error_msg or "Too Many Requests" in error_msg:
            raise HTTPException(
                status_code=429,  # Too Many Requests
                detail="주가 데이터 API 요청 제한에 도달했습니다. 관리자에게 문의 주세요."
            )
        # 기타 예상치 못한 오류
        raise HTTPException(status_code=500, detail=f"포트폴리오 최적화 중 오류 발생: {error_msg}")