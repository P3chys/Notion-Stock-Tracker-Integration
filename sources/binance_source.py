from typing import List
from decimal import Decimal
import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode
from models.position import Position
from interfaces.data_source import DataSource
from config.settings import Settings

class BinanceSource(DataSource):
    def __init__(self, settings: Settings):
        self.api_key = settings.binance_api_key
        self.api_secret = settings.binance_api_secret
        self.base_url = "https://api.binance.com"
        
    def fetch_positions(self) -> List[Position]:
        """Fetch all wallet positions from Binance"""
        try:
            # Get account information including balances
            account_info = self._get_account_info()
            
            # Get current price information for all assets
            prices = self._get_ticker_prices()
            
            # Filter non-zero balances and calculate worth
            positions = []
            for balance in account_info['balances']:
                asset = balance['asset']
                free_amount = Decimal(balance['free'])
                locked_amount = Decimal(balance['locked'])
                total_amount = free_amount + locked_amount
                
                if total_amount > Decimal('0'):
                    try:
                        # Calculate worth in USD
                        worth = Decimal('0')
                        if asset == 'USDT':
                            worth = total_amount
                        elif asset == 'USDC':
                            worth = total_amount
                        elif f"{self._clean_asset_name(asset)}USDT" in prices:
                            worth = total_amount * Decimal(str(prices[f"{self._clean_asset_name(asset)}USDT"]))
                        
                        if worth >= Decimal('5'):  # Only include positions worth $5 or more
                            cleaned_name = self._clean_asset_name(asset)
                            positions.append(Position(
                                name=cleaned_name,
                                worth=worth,
                                platform="Binance"
                            ))
                    except (KeyError, ValueError, TypeError) as e:
                        print(f"Skipping {asset} due to pricing error: {e}")
            
            return positions
        except Exception as e:
            print(f"Error fetching Binance positions: {e}")
            return []
    
    def _get_account_info(self) -> dict:
        """Get account information from Binance API"""
        endpoint = "/api/v3/account"
        return self._signed_request("GET", endpoint)
    
    def _get_ticker_prices(self) -> dict:
        """Get current prices for all trading pairs"""
        endpoint = "/api/v3/ticker/price"
        response = requests.get(f"{self.base_url}{endpoint}")
        response.raise_for_status()
        
        return {item['symbol']: item['price'] for item in response.json()}
    
    def _signed_request(self, method: str, endpoint: str, params: dict = None) -> dict:
        """Make a signed request to Binance API"""
        if params is None:
            params = {}
            
        timestamp = int(time.time() * 1000)
        params['timestamp'] = timestamp
        
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
        headers = {'X-MBX-APIKEY': self.api_key}
        
        response = requests.request(method, url, headers=headers)
        response.raise_for_status()
        
        return response.json()
        
    @staticmethod
    def _clean_asset_name(asset_name: str) -> str:
        """Remove 'LD' prefix from asset names if present."""
        if asset_name.startswith('LD'):
            return asset_name[2:]
        return asset_name