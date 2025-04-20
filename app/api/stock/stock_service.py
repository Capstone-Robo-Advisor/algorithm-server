"""
FMP API 의 경우 하루 API 호출 제한이 250 번이라 yfinance 도 일단 넣었습니다.
만약에 FMP API 호출 제한 걸리면 stock_router.py 에서 yfinance 함수 호출로 변경하면 됩니다.
ㅅㅂ 허리 개아프다
"""

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
    def get_stocks_with_yf(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """yfinance를 사용하여 주식 검색
        :param query: 검색할 주식 심볼
        :param limit: 반환할 최대 결과 수
        :return: 검색된 주식 정보 목록
        """
        try:
            # Yahoo Finance의 자동완성 API를 사용한 검색을 구현할 수도 있지만,
            # 여기서는 단순히 검색어를 ticker로 간주하고 정보를 가져오는 방식으로 구현
            ticker = yf.Ticker(query)
            info = ticker.info

            # 유효한 주식 정보인지 확인
            if not info or "symbol" not in info:
                return []

            # 주식 가격 데이터 가져오기
            hist = ticker.history(period="2d")

            if hist.empty or len(hist) < 2:
                return []

            close = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-2])
            diff = close - prev
            percent = (diff / prev) * 100

            result = [{
                "ticker": str(info.get("symbol")),
                "name": str(info.get("shortName", info.get("symbol"))),
                "price": round(float(close), 2),
                "change": round(float(diff), 2),
                "change_percent": round(float(percent), 2),
                "is_positive": bool(diff) > 0
            }]

            # 관련 주식 검색 결과도 포함하려면 추가 로직이 필요
            # (yfinance에는 직접적인 검색 기능이 없어 구현이 복잡함)

            return result

        except Exception as e:
            print(f"주식 검색 실패: {str(e)}")
            return []

    @staticmethod
    def get_stock_details_with_yf(ticker: str) -> Dict[str, Any]:
        """
        yfinance를 통하여 특정 주식의 상세 정보를 가져옵니다.
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
    def get_stocks_with_fmp(query: str, limit: int = 10) -> List[Dict[str, Any]]:
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
        """FMP API를 사용하여 특정 주식의 상세 정보 가져오기
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

            # 회사 프로필 정보 가져오기
            profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
            profile_response = requests.get(profile_url)

            profile = {}
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                if profile_data:
                    profile = profile_data[0]

            # 기술적 지표 가져오기 (이동평균선)
            ma_url = f"https://financialmodelingprep.com/api/v3/technical_indicator/daily/{ticker}?period=200&type=sma&apikey={FMP_API_KEY}"
            ma_response = requests.get(ma_url)

            ma_50 = None
            ma_200 = None

            if ma_response.status_code == 200:
                ma_data = ma_response.json()
                if ma_data:
                    # 가장 최근 데이터 사용
                    latest = ma_data[0]
                    # 50일 이동평균선은 별도 API 호출 필요할 수 있음
                    ma_200 = float(latest.get("value", 0))
            
            # 필요한 정보만 반환
            return {
                "ticker": ticker,
                "name": profile.get("companyName", quote.get("name", "")),
                "sector": profile.get("sector", "Unknown"),
                "industry": profile.get("industry", "Unknown"),
                "country": profile.get("country", "Unknown"),
                "price": float(quote.get("price", 0)),
                "market_cap": int(float(quote.get("marketCap", 0))),
                "pe_ratio": float(quote.get("pe", 0)) if quote.get("pe") else 0,
                "eps": float(quote.get("eps", 0)) if quote.get("eps") else 0,
                "dividend_yield": round(float(quote.get("dividend", 0) * 100), 2),
                "52_week_high": float(quote.get("yearHigh", 0)),
                "52_week_low": float(quote.get("yearLow", 0)),
                "ma_50": None,  # FMP API에서는 별도 호출 필요
                "ma_200": ma_200,
                "description": profile.get("description", "No description available."),
                "is_positive": bool(float(quote.get("change", 0)) > 0)
            }

        except Exception as e:
            print(f"주식 {ticker} 정보 가져오기 실패: {str(e)}")
            raise Exception(f"주식 정보를 가져오는 중 오류 발생: {str(e)}")