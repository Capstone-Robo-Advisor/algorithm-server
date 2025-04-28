from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.api.portfolio.dto.portfolio_dto import OptimizationRequestDTO, OptimizationResultDTO
from app.api.portfolio.portfolio_service import PortfolioService

router = APIRouter()

@router.post("/optimize", response_model=OptimizationResultDTO)
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

