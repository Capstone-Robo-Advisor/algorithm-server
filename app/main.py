import logging

from fastapi import FastAPI

from app.api.recommendation import recommendation_route
from app.legacy.stock import stock_router
from app.api.portfolio import portfolio_route
from app.api.member import member_route

# 전역 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI(
    title="AI-Based Portfolio Builder",
    openapi_tags=[
        {
            "name" : "Stocks",
            "description" : "주식 검색 API (일부는 레거시입니다)"
        }
    ]
)

# 라우터 등록
app.include_router(member_route.router, prefix="/api", tags=["Members"])
app.include_router(stock_router.router, prefix="/stocks", tags=["Stocks"])
app.include_router(portfolio_route.router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(recommendation_route.router, prefix="/api/recommendations", tags=["recommendations"])
