from pydantic import BaseModel
from typing import List, Dict, Optional

class StockAllocationDTO(BaseModel):
    """ 각 종목(주식)에 대한 정보를 담는 DTO
    field
    - ticker : 주식 티커 (예 : "AAPL")
    - name : 주식 이름 (예 : "Apple Inc.")
    - allocation : 해당 종목에 할당된 비율 (예 : 0.25 = 25%)
    정리 : "한 종목당 (티커, 이름, 비율)" 을 담는 작은 단위
    """
    ticker: str
    name: str
    allocation: float

class OptimizationRequestDTO(BaseModel):
    """ 최적화 요청을 할 때 보내는 데이터
    field
    - tickers : 최적화 대상 종목들의 티커 리스트
    - names : 최적화 대상 종목들의 이름 리스트
    - allocations: 초기 비율 리스트 (선택사항, 없으면 무시)
    - period : 수익률/리스크 계산에 사용할 기간(기본 2년)
    - risk_free_rate : 무위험 수익률 (Sharpe Ratio 계산에 필요)
    정리 : "어떤 종목을, 어떤 이름으로, 몇 년치 데이터를, 어떤 무위험 수익률로" 최적화할지 요청하는 구조
    """
    tickers: List[str]
    names: List[str]
    allocations: Optional[List[float]] = None
    period: str = "2y"
    risk_free_rate: float = 0.02

class OptimizationResultDTO(BaseModel):
    """최적화 결과를 반환할 때 사용하는 데이터
    field
    - expected_return : 최적화된 포트폴리오의 연간 예상 수익률
    - annual_volatility: 연간 변동성(위험도)
    - sharpe_ratio : 샤프 비율(수익 대비 위험도 비율)
    - optimized_allocations: 최적화된 종목별 비율 리스트
    정리 : 최적화 후 예상 성과 지표 + 각 종목별 최적화 비율을 응답하는 구조
    """
    expected_return: float
    annual_volatility: float
    sharpe_ratio: float
    optimized_allocations: List[StockAllocationDTO]