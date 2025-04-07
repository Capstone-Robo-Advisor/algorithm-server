from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.portfolio_service import PortfolioService

router = APIRouter()

class Stock(BaseModel):
    ticker: str
    shares: float
    purchase_price: float

class Portfolio(BaseModel):
    name: str
    stocks: List[Stock] = []

@router.post("/create")
def create_portfolio(portfolio: Portfolio):
    """
    새 포트폴리오를 생성합니다.
    """
    portfolio_dict = {
        "name": portfolio.name,
        "stocks": [{"ticker": s.ticker, "shares": s.shares, "purchase_price": s.purchase_price} for s in portfolio.stocks]
    }
    
    result = PortfolioService.create_portfolio(portfolio_dict)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"message": "Portfolio created successfully", "portfolio": result}

@router.get("/list")
def list_portfolios():
    """
    모든 포트폴리오 목록을 반환합니다.
    """
    return PortfolioService.get_all_portfolios()

@router.get("/{portfolio_name}")
def get_portfolio(portfolio_name: str):
    """
    이름으로 포트폴리오를 찾습니다.
    """
    portfolio = PortfolioService.get_portfolio_by_name(portfolio_name)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

@router.put("/{portfolio_name}")
def update_portfolio(portfolio_name: str, updated_portfolio: Portfolio):
    """
    기존 포트폴리오를 업데이트합니다.
    """
    portfolio_dict = {
        "name": updated_portfolio.name,
        "stocks": [{"ticker": s.ticker, "shares": s.shares, "purchase_price": s.purchase_price} for s in updated_portfolio.stocks]
    }
    
    result = PortfolioService.update_portfolio(portfolio_name, portfolio_dict)
    if not result:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return {"message": "Portfolio updated successfully", "portfolio": result}

@router.delete("/{portfolio_name}")
def delete_portfolio(portfolio_name: str):
    """
    포트폴리오를 삭제합니다.
    """
    success = PortfolioService.delete_portfolio(portfolio_name)
    if not success:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return {"message": "Portfolio deleted successfully"}

@router.get("/{portfolio_name}/performance")
def get_portfolio_performance(portfolio_name: str):
    """
    포트폴리오의 현재 성과를 계산합니다.
    """
    portfolio = PortfolioService.get_portfolio_by_name(portfolio_name)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    result = PortfolioService.calculate_portfolio_performance(portfolio)
    return result
