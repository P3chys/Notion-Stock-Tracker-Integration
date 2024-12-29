import requests
from decimal import Decimal
from typing import List
from app.models.position import Position
from app.interfaces.data_source import DataSource
from config.settings import Settings

class Trading212Source(DataSource):
    def __init__(self, settings: Settings):
        self.api_url = settings.trading212_api_url
        self.api_token = settings.trading212_api_token

    def fetch_positions(self) -> List[Position]:

        headers = {
        "Authorization": self.api_token
        }
        response = requests.get(self.api_url, headers=headers)
        response.raise_for_status()
        
        portfolio_data = response.json()
        return [
            Position(
                name=position.get('ticker', ''),
                worth=Decimal(str(float(position.get('currentPrice', 0)) * float(position.get('quantity', 0)))),
                platform="Trading212"
            )
            for position in portfolio_data
        ]
