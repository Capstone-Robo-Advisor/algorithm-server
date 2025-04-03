import yfinance as yf
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

class StockService:
    @staticmethod
    def search_stocks(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        검색어와 일치하는 주식 심볼을 찾아 기본 정보를 반환합니다.
        """
        # 실제 구현에서는 보다 완전한 심볼 DB를 사용해야 함
        all_tickers = ["QQQ", "TQQQ", "QQQW", "AAPL", "TSLA", "GOOGL", "MSFT", "AMZN", "META", "NVDA", "NFLX"]
        matched = [t for t in all_tickers if query.upper() in t][:limit]
        
        results = []
        for ticker in matched:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2d")
                
                if hist.empty or len(hist) < 2:
                    continue
                    
                close = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                diff = close - prev
                percent = (diff / prev) * 100
                
                # 기업 정보 추가
                info = stock.info
                name = info.get("shortName", ticker)
                
                # NumPy boolean을 Python boolean으로 변환
                is_positive = bool(diff > 0)
                
                results.append({
                    "ticker": ticker,
                    "name": name,
                    "close_price": round(float(close), 2),
                    "diff": round(float(diff), 2),
                    "percent": round(float(percent), 2),
                    "is_positive": is_positive
                })
            except Exception:
                # 에러 발생 시 해당 종목 건너뛰기
                continue
                
        return results
    
    @staticmethod
    def get_stock_details(ticker: str) -> Dict[str, Any]:
        """
        특정 주식의 상세 정보를 가져옵니다.
        """
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # 주요 지표 계산
        hist = stock.history(period="1mo")
        if not hist.empty:
            current_price = float(hist['Close'].iloc[-1])
            ma_50 = float(hist['Close'].rolling(window=50).mean().iloc[-1]) if len(hist) >= 50 else None
            ma_200 = float(hist['Close'].rolling(window=200).mean().iloc[-1]) if len(hist) >= 200 else None
        else:
            current_price = float(info.get("currentPrice", 0))
            ma_50 = None
            ma_200 = None
        
        # NumPy 타입 변환 확인
        return {
            "ticker": ticker,
            "name": info.get("shortName", "Unknown"),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "country": info.get("country", "Unknown"),
            "price": round(current_price, 2),
            "market_cap": int(info.get("marketCap", 0)) if info.get("marketCap") else 0,
            "pe_ratio": float(info.get("trailingPE", 0)) if info.get("trailingPE") else 0,
            "eps": float(info.get("trailingEps", 0)) if info.get("trailingEps") else 0,
            "dividend_yield": round(float(info.get("dividendYield", 0) * 100), 2) if info.get("dividendYield") else 0,
            "52_week_high": float(info.get("fiftyTwoWeekHigh", 0)) if info.get("fiftyTwoWeekHigh") else 0,
            "52_week_low": float(info.get("fiftyTwoWeekLow", 0)) if info.get("fiftyTwoWeekLow") else 0,
            "ma_50": round(ma_50, 2) if ma_50 is not None else None,
            "ma_200": round(ma_200, 2) if ma_200 is not None else None,
            "description": info.get("longBusinessSummary", "No description available.")
        }
    
    @staticmethod
    def get_chart_data(ticker: str, period: str = "1y", interval: str = "1d") -> List[Dict[str, Any]]:
        """
        특정 주식의 차트 데이터를 가져옵니다.
        """
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        
        if hist.empty:
            return []
        
        # DataFrame을 JSON 형식으로 변환
        result = []
        for index, row in hist.iterrows():
            result.append({
                "date": index.strftime('%Y-%m-%d %H:%M:%S'),
                "open": float(round(row["Open"], 2)) if not pd.isna(row["Open"]) else None,
                "high": float(round(row["High"], 2)) if not pd.isna(row["High"]) else None,
                "low": float(round(row["Low"], 2)) if not pd.isna(row["Low"]) else None,
                "close": float(round(row["Close"], 2)) if not pd.isna(row["Close"]) else None,
                "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else 0
            })
            
        return result
