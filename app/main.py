from fastapi import FastAPI
from app.routers import member_route, stock, portfolio

app = FastAPI()

# 라우터 등록
app.include_router(member_route.router, prefix="/api", tags=["Members"])
app.include_router(stock.router, prefix="/stocks", tags=["Stocks"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
