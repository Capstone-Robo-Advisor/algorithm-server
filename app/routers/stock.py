from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.services.stock_service import StockService

router = APIRouter()

@router.get("/search")
def search_stock(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50)):
    """
    주식 심볼 검색 API
    """
    results = StockService.search_stocks(query=q, limit=limit)
    return results

@router.get("/{ticker}")
def get_stock_details(ticker: str):
    """
    주식 상세 정보 API
    """
    try:
        return StockService.get_stock_details(ticker)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock not found: {str(e)}")

@router.get("/{ticker}/chart")
def get_stock_chart(ticker: str, period: str = "1y", interval: str = "1d"):
    """
    주식 차트 데이터 API
    """
    try:
        valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
        valid_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
        
        if period not in valid_periods:
            raise HTTPException(status_code=400, detail=f"Invalid period. Valid options are: {valid_periods}")
            
        if interval not in valid_intervals:
            raise HTTPException(status_code=400, detail=f"Invalid interval. Valid options are: {valid_intervals}")
        
        return StockService.get_chart_data(ticker, period, interval)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chart data: {str(e)}")
