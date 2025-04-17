import logging

from fastapi import FastAPI

from app.api.recommendation import recommendation_route
from app.api.stock import stock_router
from app.api.portfolio import portfolio_route
from app.api.member import member_route
from app.common.crawlers.daily_news_collector import DailyNewsCollector

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

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행될 이벤트"""
    # 로거 설정
    # logger.info("🚀 애플리케이션 시작 중...")

    # 뉴스 수집기 초기화
    collector = DailyNewsCollector.get_instance()
    await collector.collect_initial_data()


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행될 이벤트"""
    # 스케줄러 종료
    collector = DailyNewsCollector.get_instance()
    collector.shutdown()

# 라우터 등록
app.include_router(member_route.router, prefix="/api", tags=["Members"])
app.include_router(stock_router.router, prefix="/stocks", tags=["Stocks"])
app.include_router(portfolio_route.router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(recommendation_route.router, prefix="/api/recommendations", tags=["recommendations"])
