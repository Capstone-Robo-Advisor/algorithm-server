from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
from app.services.stock_service import StockService

router = APIRouter()

@router.get("/fmp/search")
def search_stock_with_fmp(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50)):
    """
    FMP API를 통한 주식 검색 API
    """
    results = StockService.search_stocks_with_fmp(query=q, limit=limit)
    return results

@router.get("/fmp/{ticker}")
def get_stock_details_with_fmp(ticker: str):
    """
    FMP API를 통한 주식 정보 API
    """
    try:
        return StockService.get_stock_details(ticker)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock not found: {str(e)}")