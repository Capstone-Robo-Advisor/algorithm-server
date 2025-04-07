from fastapi import FastAPI
from app.routers import member_route, stock_router, portfolio_route

app = FastAPI()

# 라우터 등록
app.include_router(member_route.router, prefix="/api", tags=["Members"])
app.include_router(stock_router.router, prefix="/stocks", tags=["Stocks"])
app.include_router(portfolio_route.router, prefix="/portfolio", tags=["Portfolio"])
