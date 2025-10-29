import os
import nasdaqdatalink
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
from alpha_vantage.fundamentaldata import FundamentalData
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class NasdaqDataService:
    def __init__(self):
        self.api_key = os.getenv('NASDAQ_DATA_LINK_API_KEY')
        if self.api_key:
            nasdaqdatalink.ApiConfig.api_key = self.api_key
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.fd = FundamentalData(key=self.alpha_vantage_key, output_format='pandas') if self.alpha_vantage_key else None
    
    async def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Obtener información básica de la empresa"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap'),
                'employees': info.get('fullTimeEmployees'),
                'description': info.get('longBusinessSummary', ''),
                'website': info.get('website', '')
            }
        except Exception as e:
            logger.error(f"Error getting company info for {symbol}: {e}")
            return {}
    
    async def get_stock_data(self, symbol: str, period: str = "1mo") -> Dict[str, Any]:
        """Obtener datos de precios de acciones"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return {}
            
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100
            
            return {
                'symbol': symbol,
                'current_price': round(current_price, 2),
                'previous_close': round(previous_close, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': int(hist['Volume'].iloc[-1]),
                'data_date': hist.index[-1].strftime('%Y-%m-%d')
            }
        except Exception as e:
            logger.error(f"Error getting stock data for {symbol}: {e}")
            return {}
    
    async def get_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """Obtener datos fundamentales"""
        try:
            if not self.fd:
                return {}
            
            # Obtener balance sheet
            balance_sheet, _ = self.fd.get_balance_sheet_annual(symbol)
            income_statement, _ = self.fd.get_income_statement_annual(symbol)
            cash_flow, _ = self.fd.get_cash_flow_annual(symbol)
            
            fundamentals = {
                'symbol': symbol,
                'balance_sheet': balance_sheet.to_dict() if not balance_sheet.empty else {},
                'income_statement': income_statement.to_dict() if not income_statement.empty else {},
                'cash_flow': cash_flow.to_dict() if not cash_flow.empty else {}
            }
            
            return fundamentals
        except Exception as e:
            logger.error(f"Error getting fundamental data for {symbol}: {e}")
            return {}
    
    async def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Obtener datos históricos"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                return {}
            
            return {
                'symbol': symbol,
                'historical_data': hist.reset_index().to_dict('records'),
                'period': f"{start_date} to {end_date}"
            }
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return {}