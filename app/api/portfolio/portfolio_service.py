import yfinance as yf
import logging
import pandas as pd

import os
import time
import requests

from diskcache import Cache
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from datetime import datetime, timedelta

from typing import List, Dict, Any, Optional
from pypfopt import EfficientFrontier, risk_models, expected_returns, objective_functions
from .dto.portfolio_dto import StockAllocationDTO, OptimizationResultDTO

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("portfolio_service")

# FMP API 키 가져오기
FMP_API_KEY = os.getenv("FMP_API_KEY")

# 캐시 설정
try:
    # 상대 경로로 캐시 디렉토리 설정 (개발 환경용)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cache_dir = os.path.join(base_dir, "cache", "financial_data")

    # 디렉토리가 없으면 생성
    os.makedirs(cache_dir, exist_ok=True)

    stock_cache = Cache(cache_dir)
    logger.info(f"캐시 디렉토리 설정: {cache_dir}")
except Exception as e:
    logger.warning(f"캐시 디렉토리 설정 실패, 임시 디렉토리 사용: {e}")
    # 임시 디렉토리 사용 (최후의 수단)
    import tempfile

    cache_dir = os.path.join(tempfile.gettempdir(), "financial_data_cache")
    os.makedirs(cache_dir, exist_ok=True)
    stock_cache = Cache(cache_dir)

class PortfolioService:

    @staticmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def get_stock_data_from_fmp(tickers: List[str], period: str = "2y") -> pd.DataFrame:
        """FMP API 를 통한 주가 데이터 가져오기"""

        # 캐시 키 생성
        cache_key = f"fmp_stocks_{'_'.join(sorted(tickers))}_{period}"

        # 캐시에서 확인
        cached_data = stock_cache.get(cache_key)
        if cached_data is not None and not cached_data.empty:
            logger.info(f"캐시에서 {len(tickers)}개 종목 데이터 로드")
            return cached_data

        # 기간을 날짜로 변환
        end_date = datetime.now()
        if period.endswith('y'):
            years = int(period.replace('y', ''))
            start_date = end_date - timedelta(days=365 * years)
        elif period.endswith('m'):
            months = int(period.replace('m', ''))
            start_date = end_date - timedelta(days=30 * months)
        else:
            # 기본값 2년
            start_date = end_date - timedelta(days=365 * 2)

        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        logger.info(f"FMP API 에서 {len(tickers)}개 종목 데이터 다운로드 중 : {start_str} ~ {end_str}")

        # 모든 종목 데이터를 저장할 딕셔너리
        price_data = {}
        all_dates = set()

        for ticker in tickers:
            try:
                url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}"
                params = {
                    'from' : start_str,
                    'to' : end_str,
                    'apikey' : FMP_API_KEY,
                }

                response = requests.get(url, params=params)

                if response.status_code != 200:
                    logger.warning(f"FMP API 응답 오류 ({ticker}): {response.status_code}")
                    continue

                data = response.json()

                if 'historical' not in data:
                    logger.warning(f"FMP API 데이터 없음 ({ticker})")
                    continue

                # 일별 데이터 추출
                ticker_data = {}
                for day in data['historical']:
                    date_str = day['date']
                    ticker_data[date_str] = day['close']
                    all_dates.add(date_str)

                price_data[ticker] = ticker_data
                logger.info(f"FMP API: {ticker} 데이터 {len(ticker_data)}개 로드 완료")

                # API 요청 간 간격 두기
                time.sleep(0.2)

            except Exception as e:
                logger.error(f"FMP API 오류 ({ticker}): {str(e)}")

        # 날짜 정렬
        all_dates = sorted(list(all_dates))

        if not all_dates:
            logger.error("FMP API : 데이터를 가져오지 못했습니다.")

            # 캐시에 백업 데이터가 있는지 확인
            backup_data = stock_cache.get(cache_key, default=None, read=True)

            if backup_data is not None and not backup_data.empty:
                logger.info("이전 캐시 데이터 사용")
                return backup_data
            return pd.DataFrame()  # 빈 데이터프레임 반환

        # 데이터프레임 생성
        df_data = []
        for date in all_dates:
            row = {'date': date}
            for ticker in tickers:
                if ticker in price_data and date in price_data[ticker]:
                    row[ticker] = price_data[ticker][date]
            df_data.append(row)

        # 데이터프레임으로 변환
        df = pd.DataFrame(df_data)
        df['data'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)

        # 결측치 처리
        df = df.fillna(method='ffill').fillna(method='bfill')

        # yfinance와 호환되는 멀티인덱스 형식으로 변환
        multi_df = pd.DataFrame()

        # 사용 가능한 티커만 선택
        available_tickers = [t for t in tickers if t in df.columns]

        if not available_tickers:
            logger.error("FMP API: 사용 가능한 티커가 없습니다")
            return pd.DataFrame()

        # Adj Close와 Close 열 추가 (yfinance 호환)
        for ticker in available_tickers:
            multi_df[('Adj Close', ticker)] = df[ticker]
            multi_df[('Close', ticker)] = df[ticker]

        # 멀티 인덱스 명시적으로 지정
        multi_df.columns = pd.MultiIndex.from_tuples(multi_df.columns, names=["Price Type", "Ticker"])

        # 캐시에 저장 (12시간 유효)
        stock_cache.set(cache_key, multi_df, expire=43200)

        return multi_df


    # 추가: 캐싱을 적용한 주가 데이터 다운로드 함수
    @staticmethod
    @retry(
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def get_stock_data(tickers: List[str], period: str = "2y") -> pd.DataFrame:
        """캐싱이 적용된 주가 데이터 다운로드 함수"""
        # 캐시 키 생성
        cache_key = f"stocks_{'_'.join(sorted(tickers))}_{period}"

        # 캐시에서 확인
        cached_data = stock_cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"캐시에서 {len(tickers)}개 종목 데이터 로드")
            return cached_data

        # 캐시에 없으면 다운로드
        logger.info(f"yfinance에서 {len(tickers)}개 종목 데이터 다운로드")
        try:
            # 1초 대기 추가 (Rate Limit 방지)
            time.sleep(1)

            # 다운로드 시도
            data = yf.download(tickers, period=period)

            # 데이터 유효성 검사
            if data.empty:
                logger.warning("다운로드된 데이터가 비어 있습니다. Rate Limit 의심")

                # 백업 캐시 확인
                backup_data = stock_cache.get(cache_key, default=None, read=True)
                if backup_data is not None and not backup_data.empty:
                    logger.info("기존 캐시 데이터 사용")
                    return backup_data

                # Rate Limit으로 간주하고 예외 발생
                raise Exception("Rate limited: 데이터가 비어 있습니다")

            # 캐시에 저장 (12시간 유효)
            stock_cache.set(cache_key, data, expire=43200)
            return data

        except Exception as e:
            error_msg = str(e)

            # Rate Limit 예외 처리
            if "Rate limited" in error_msg or "Too Many Requests" in error_msg:
                logger.warning(f"Rate Limit 발생: {error_msg}")

                # 캐시에 백업 데이터가 있는지 확인 (만료 무시)
                backup_data = stock_cache.get(cache_key, default=None, read=True)
                if backup_data is not None and not backup_data.empty:
                    logger.warning("Rate limit 발생, 캐시의 만료된 데이터 사용")
                    return backup_data

                # 없으면 재시도를 위해 예외 전파
                logger.error(f"Rate limit 발생 & 캐시 데이터 없음: {e}")
                raise Exception(f"Rate limited: {error_msg}")

            # 그 외 예외는 그대로 전파
            raise

    @staticmethod
    def optimize_portfolio(tickers: List[str], names: List[str],
                           allocations: Optional[List[float]] = None,
                           period: str = "2y", risk_free_rate: float = 0.02) -> OptimizationResultDTO:
        """po
        PyPortfolioOpt를 사용하여 포트폴리오 최적화
        """
        try:
            # 주가 데이터 가져오기
            prices_df = PortfolioService.get_stock_data_from_fmp(tickers, period=period)

            # 데이터 구조 확인 로깅
            logger.info(f"Data columns : {prices_df.columns}")

            # MultiIndex 처리 바로 추가
            if isinstance(prices_df.columns, pd.MultiIndex):
                # 로깅 추가
                logger.info(f"MultiIndex 열 이름: {[col for col in prices_df.columns.get_level_values(0).unique()]}")

                # 대소문자 구분 없이 검색
                price_cols = [col.lower() for col in prices_df.columns.get_level_values(0).unique()]

                if 'adj close' in price_cols:
                    adj_close_col = [col for col in prices_df.columns.get_level_values(0).unique()
                                     if col.lower() == 'adj close'][0]
                    prices_df = prices_df[adj_close_col]
                elif 'close' in price_cols:
                    close_col = [col for col in prices_df.columns.get_level_values(0).unique()
                                 if col.lower() == 'close'][0]
                    prices_df = prices_df[close_col]
                else:
                    # 모든 열 접두사 출력
                    logger.error(f"사용 가능한 열: {prices_df.columns.get_level_values(0).unique()}")
                    # 첫 번째 레벨 그냥 사용
                    prices_df = prices_df[prices_df.columns.get_level_values(0)[0]]
                    logger.warning(f"가격 데이터 열을 찾지 못해 첫 번째 열 {prices_df.columns.get_level_values(0)[0]} 사용")
            else:
                logger.info(f"일반 열 이름: {prices_df.columns.tolist()}")

            # DataFrame 또는 Series 여부에 따라 dropna 분기 처리
            if isinstance(prices_df, pd.DataFrame):
                prices_df = prices_df.dropna(axis=1, how='all')
            else:
                prices_df = prices_df.dropna()

                # 표준 DataFrame 처리
                if 'Adj Close' in prices_df.columns:
                    prices_df = prices_df['Adj Close']
                elif 'Close' in prices_df.columns:
                    prices_df = prices_df['Close']
                else:
                    # 가능한 경우 그냥 첫 번째 열 사용
                    logger.warning(f"가격 데이터 열을 찾지 못해 첫 번째 열 {prices_df.columns[0]} 사용")
                    prices_df = prices_df[prices_df.columns[0]]

            # 결측치 처리
            prices_df = prices_df.dropna(axis=1, how='all')
            available_tickers = list(prices_df.columns)

            # 사용 가능한 티커만 필터링
            valid_indices = [i for i, t in enumerate(tickers) if t in available_tickers]
            valid_tickers = [tickers[i] for i in valid_indices]
            valid_names = [names[i] for i in valid_indices]

            if len(valid_tickers) < 2:
                raise ValueError("최적화에 필요한 충분한 종목이 없습니다.")

            # 예상 수익률과 공분산 행렬 계산
            mu = expected_returns.mean_historical_return(prices_df)
            S = risk_models.sample_cov(prices_df)

            # 최적화 수행
            ef = EfficientFrontier(mu, S, weight_bounds=(0, 1))

            # soft 제약 : 너무 한 종목에 치우치지 않도록 L2 정규화 추가
            ef.add_objective(objective_functions.L2_reg, gamma=0.1)

            # Hard 제약 : 각 종목 최대 40% 까지만 투자
            ef.add_constraint(lambda w: w<=0.4)

            # 최대 샤프 비율 포트폴리오 계산
            weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
            cleaned_weights = ef.clean_weights()

            # 성과 지표 계산
            expected_return, annual_volatility, sharpe_ratio = ef.portfolio_performance(risk_free_rate=risk_free_rate)

            # 최적화된 비율 구성
            ticker_to_name = {t: n for t, n in zip(valid_tickers, valid_names)}
            optimized_allocations = []

            for ticker, weight in cleaned_weights.items():
                if weight > 0.01:  # 1% 이상인 종목만 포함
                    optimized_allocations.append(
                        StockAllocationDTO(
                            ticker=ticker,
                            name=ticker_to_name.get(ticker, ticker),
                            allocation=round(weight, 4) * 100
                        )
                    )

            return OptimizationResultDTO(
                expected_return=round(expected_return, 4),
                annual_volatility=round(annual_volatility, 4),
                sharpe_ratio=round(sharpe_ratio, 2),
                optimized_allocations=sorted(optimized_allocations, key=lambda x: x.allocation, reverse=True)
            )

        except ValueError as ve:
            logger.warning(f"Value Error: {ve}")
            raise ve


        except Exception as e:
            logger.exception("Unexpected error occurred during portfolio optimization.")

            # 예외 메시지에 Rate Limit 관련 내용이 있는지 확인
            if "Rate limited" in str(e) or "Too Many Requests" in str(e):
                # Rate Limit 예외는 그대로 전파 (route에서 429로 처리)
                raise Exception(f"Rate limited: {str(e)}")

            # 그 외 예외는 ValueError로 변환
            raise ValueError(f"포트폴리오 최적화 중 오류: {str(e)}")