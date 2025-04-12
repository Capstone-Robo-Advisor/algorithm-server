from pydantic import BaseModel, Field
from typing import List, Optional

class PortfolioRequestDTO(BaseModel):
    """포트폴리오 추천 요청 DTO"""
    portfolio_count: int = Field(3, ge=1, le=5, description="생성할 포트폴리오 수")
    stocks_per_portfolio: int = Field(5, ge=3, le=10, description="각 포트폴리오당 주식 수")
    theme: str = Field("기술", description="투자 테마 (예: 에너지, 반도체, 기술, 원자재)")

class StockAllocationDTO(BaseModel):
    """주식 할당 DTO"""
    ticker: str
    name: str
    allocation: float

class PortfolioDTO(BaseModel):
    """포트폴리오 DTO"""
    name: str
    stocks: List[StockAllocationDTO]
    description: str