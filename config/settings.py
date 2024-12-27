from dataclasses import dataclass
from typing import List, Tuple
import os
from dotenv import load_dotenv

@dataclass
class Settings:
    notion_token: str
    notion_database_id: str
    trading212_api_token: str
    trading212_api_url: str
    debank_sources: List[Tuple[str, str]]
    binance_api_key: str
    binance_api_secret: str

    @classmethod
    def load_from_env(cls) -> 'Settings':
        load_dotenv()
        
        return cls(
            notion_token=os.getenv('NOTION_TOKEN'),
            notion_database_id=os.getenv('NOTION_DATABASE_ID'),
            trading212_api_token=os.getenv('TRADING212_API_TOKEN'),
            trading212_api_url= "https://live.trading212.com/api/v0/equity/portfolio",
            debank_sources=[
                ("https://debank.com/profile/0x6fc703151a658b58458917bd4099a0bd319d7681?chain=cro", "Cronos DeFi"),
                ("https://debank.com/profile/0x5d1c953d6b07c7fbc6541139cc1293408d58854e?chain=bsc", "BNB DeFi")
            ],
            binance_api_key=os.getenv('BINANCE_API_KEY'),
            binance_api_secret=os.getenv('BINANCE_API_SECRET')
        )