from fastapi import APIRouter, Query, HTTPException
from app.legacy.stock.stock_service import StockService

router = APIRouter()

@router.get(
    "/fmp/search",
    summary="(레거시) FMP 주식 검색 API",
    description="현재 사용되지 않음. GPT 기반 추천 시스템으로 대체 예정",
    deprecated=True,
)
def search_stock_with_fmp(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50)):
    """
    FMP API를 통한 주식 검색 API
    """
    results = StockService.get_stocks_with_fmp(query=q, limit=limit)
    return results

@router.get(
    "/fmp/{ticker}",
    summary="(레거시) FMP 주식 검색 API",
    description="현재 사용되지 않음. GTP 기반 추천 시스템으로 대체 예정",
    deprecated=True,
)
def search_stock_details_with_fmp(ticker: str):
    """
    FMP API를 통한 주식 정보 API
    """
    try:
        return StockService.get_stock_details_with_fmp(ticker)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock not found: {str(e)}")