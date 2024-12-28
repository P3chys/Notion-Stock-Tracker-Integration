from typing import List
from models.position import Position
from sources.trading212_source import Trading212Source
from sources.debank_source import DebankSource
from sinks.notion_sink import NotionSink
from services.web_driver_service import WebDriverService
from config.settings import Settings
from sources.binance_source import BinanceSource
from sources.cryptocom_source import CryptoComSource

class PortfolioTracker:
    def __init__(self, settings: Settings):
        self.web_driver_service = WebDriverService()
        self.sources = [
            #Trading212Source(settings),
            #DebankSource(settings, self.web_driver_service),
            #BinanceSource(settings),
            CryptoComSource(settings)
        ]
        self.sink = NotionSink(settings)

    def run(self) -> None:
        all_positions: List[Position] = []
        
        for source in self.sources:
            try:
                positions = source.fetch_positions()
                all_positions.extend(positions)
            except Exception as e:
                print(f"Error fetching positions from {source.__class__.__name__}: {e}")

        if all_positions:
            try:
                self.sink.save_positions(all_positions)
            except Exception as e:
                print(f"Error saving positions to Notion: {e}")

if __name__ == "__main__":
    settings = Settings.load_from_env()
    tracker = PortfolioTracker(settings)
    tracker.run()