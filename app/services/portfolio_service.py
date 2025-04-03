from typing import List, Dict, Any, Optional
import yfinance as yf
from datetime import datetime

# 포트폴리오 데이터 모델 (실제 DB 연동 시 수정 필요)
portfolios = []

class PortfolioService:
    @staticmethod
    def create_portfolio(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        새 포트폴리오를 생성합니다.
        """
        # 중복 확인
        for p in portfolios:
            if p["name"] == portfolio_data["name"]:
                return {"error": "Portfolio with this name already exists"}
        
        # 생성 시간 추가
        portfolio_data["created_at"] = datetime.now().isoformat()
        portfolio_data["last_updated"] = datetime.now().isoformat()
        
        portfolios.append(portfolio_data)
        return portfolio_data
    
    @staticmethod
    def get_all_portfolios() -> List[Dict[str, Any]]:
        """
        모든 포트폴리오 목록을 반환합니다.
        """
        return portfolios
    
    @staticmethod
    def get_portfolio_by_name(name: str) -> Optional[Dict[str, Any]]:
        """
        이름으로 포트폴리오를 찾습니다.
        """
        for p in portfolios:
            if p["name"] == name:
                return p
        return None
    
    @staticmethod
    def update_portfolio(name: str, updated_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        기존 포트폴리오를 업데이트합니다.
        """
        for i, p in enumerate(portfolios):
            if p["name"] == name:
                # 기존 데이터 유지하면서 업데이트
                portfolios[i].update(updated_data)
                portfolios[i]["last_updated"] = datetime.now().isoformat()
                return portfolios[i]
        return None
    
    @staticmethod
    def delete_portfolio(name: str) -> bool:
        """
        포트폴리오를 삭제합니다.
        """
        for i, p in enumerate(portfolios):
            if p["name"] == name:
                portfolios.pop(i)
                return True
        return False
    
    @staticmethod
    def calculate_portfolio_performance(portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """
        포트폴리오의 현재 가치와 수익률을 계산합니다.
        """
        total_value = 0.0
        total_cost = 0.0
        stocks_data = []
        
        for stock in portfolio.get("stocks", []):
            ticker = stock["ticker"]
            shares = float(stock["shares"])
            purchase_price = float(stock["purchase_price"])
            
            try:
                # 현재 가격 조회
                yf_ticker = yf.Ticker(ticker)
                hist = yf_ticker.history(period="1d")
                
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    current_value = shares * current_price
                    cost_basis = shares * purchase_price
                    profit_loss = current_value - cost_basis
                    profit_loss_percent = (profit_loss / cost_basis) * 100 if cost_basis > 0 else 0.0
                    
                    # 종목별 성과 추가
                    stocks_data.append({
                        "ticker": ticker,
                        "shares": shares,
                        "purchase_price": round(purchase_price, 2),
                        "current_price": round(current_price, 2),
                        "current_value": round(current_value, 2),
                        "profit_loss": round(profit_loss, 2),
                        "profit_loss_percent": round(profit_loss_percent, 2)
                    })
                    
                    total_value += current_value
                    total_cost += cost_basis
            except Exception:
                # 에러 발생 시 해당 종목 건너뛰기
                continue
        
        # 포트폴리오 전체 성과
        total_profit_loss = total_value - total_cost
        total_profit_loss_percent = (total_profit_loss / total_cost) * 100 if total_cost > 0 else 0.0
        
        return {
            "name": portfolio["name"],
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_profit_loss": round(total_profit_loss, 2),
            "total_profit_loss_percent": round(total_profit_loss_percent, 2),
            "stocks": stocks_data
        }
