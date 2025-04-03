from fastapi import FastAPI
from app.routers import stock, portfolio

app = FastAPI()

# 라우터 등록
app.include_router(stock.router, prefix="/stocks", tags=["Stocks"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])