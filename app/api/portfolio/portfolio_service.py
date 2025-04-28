import yfinance as yf
import logging
import pandas as pd

from typing import List, Dict, Any, Optional
from pypfopt import EfficientFrontier, risk_models, expected_returns
from .dto.portfolio_dto import StockAllocationDTO, OptimizationResultDTO

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("portfolio_service")

class PortfolioService:
    @staticmethod
    def optimize_portfolio(tickers: List[str], names: List[str],
                           allocations: Optional[List[float]] = None,
                           period: str = "2y", risk_free_rate: float = 0.02) -> OptimizationResultDTO:
        """
        PyPortfolioOpt를 사용하여 포트폴리오 최적화
        """
        try:
            # 주가 데이터 가져오기
            prices_df = yf.download(tickers, period=period)

            # 데이터 구조 확인 로깅
            logger.info(f"Data columns : {prices_df.columns}")

            # 🔥 MultiIndex 처리 바로 추가
            if isinstance(prices_df.columns, pd.MultiIndex):
                if 'Adj Close' in prices_df.columns.get_level_values(0):
                    prices_df = prices_df['Adj Close']
                elif 'Close' in prices_df.columns.get_level_values(0):
                    prices_df = prices_df['Close']
                else:
                    raise ValueError("다운로드한 데이터에 'Close' 또는 'Adj Close' 가격 정보가 없습니다.")
            else:
                if 'Adj Close' in prices_df.columns:
                    prices_df = prices_df['Adj Close']
                elif 'Close' in prices_df.columns:
                    prices_df = prices_df['Close']
                else:
                    raise ValueError("다운로드한 데이터에 'Close' 또는 'Adj Close' 가격 정보가 없습니다.")

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
                            allocation=round(weight, 4)
                        )
                    )

            return OptimizationResultDTO(
                expected_return=round(expected_return, 4),
                annual_volatility=round(annual_volatility, 4),
                sharpe_ratio=round(sharpe_ratio, 2),
                optimized_allocations=sorted(optimized_allocations, key=lambda x: x.allocation, reverse=True)
            )

        except ValueError as ve:
            raise ve

        except Exception as e:
            logger.exception("Unexpected error occurred during portfolio optimization.")
            raise ValueError(f"포트폴리오 최적화 중 오류: {str(e)}")