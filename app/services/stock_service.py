import yfinance as yf
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

import requests
import os
from dotenv import load_dotenv

# 환경 변수에서 API 키 로드
load_dotenv()
FMP_API_KEY = os.getenv("FMP_API_KEY")

class StockService:
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

    @staticmethod
    def search_stocks_with_fmp(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """FMP API를 사용하여 주식 검색
        :param query: 검색할 주식 심볼 또는 회사명
        :param limit: 반환할 최대 결과 수
        :return: 검색된 주식 정보 목록
        """
        try:
            # FMP API 호출로 주식 검색
            url = f"https://financialmodelingprep.com/api/v3/search?query={query}&limit={limit}&apikey={FMP_API_KEY}"
            response = requests.get(url)

            if response.status_code != 200:
                print(f"FMP API 호출 실패: {response.status_code}")
                return []

            data = response.json()

            # 검색 결과가 없으면 빈 리스트 반환
            if not data:
                return []

            results = []

            # 각 검색 결과에 대해 필요한 정보만 가져오기
            for item in data:
                ticker = item.get("symbol")

                # 실시간 시세 정보 가져오기
                try:
                    quote_url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={FMP_API_KEY}"
                    quote_response = requests.get(quote_url)

                    if quote_response.status_code == 200:
                        quote_data = quote_response.json()
                        if quote_data:
                            quote = quote_data[0]
                            price = quote.get("price", 0)
                            change = quote.get("change", 0)

                            # UI에 필요한 정보만 포함
                            results.append({
                                "ticker": ticker,
                                "name": item.get("name", ""),
                                "price": round(float(price), 2),
                                "change": round(float(change), 2),
                                "change_percent": round(float(quote.get("changesPercentage", 0)), 2),
                                "is_positive": change > 0
                            })
                except Exception as e:
                    print(f"주식 {ticker}의 시세 정보 가져오기 실패: {str(e)}")

            return results

        except Exception as e:
            print(f"FMP API를 통한 주식 검색 실패: {str(e)}")
            return []

    @staticmethod
    def get_stock_details_with_fmp(ticker: str) -> Dict[str, Any]:
        """FMP API를 사용하여 특정 주식의 정보 가져오기
        :param ticker: 주식 심볼
        :return: 주식 정보
        """
        try:
            # 시세 정보 가져오기
            quote_url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={FMP_API_KEY}"
            quote_response = requests.get(quote_url)

            if quote_response.status_code != 200:
                raise Exception(f"API 호출 실패: {quote_response.status_code}")
                
            quote_data = quote_response.json()
            
            if not quote_data:
                raise Exception("주식 정보를 찾을 수 없습니다.")
                
            quote = quote_data[0]
            
            # 필요한 정보만 반환
            return {
                "ticker": ticker,
                "name": quote.get("name", ""),
                "price": quote.get("price", 0),
                "change": quote.get("change", 0),
                "change_percent": quote.get("changesPercentage", 0),
                "is_positive": quote.get("change", 0) > 0
            }

        except Exception as e:
            print(f"주식 {ticker} 정보 가져오기 실패: {str(e)}")
            raise Exception(f"주식 정보를 가져오는 중 오류 발생: {str(e)}")