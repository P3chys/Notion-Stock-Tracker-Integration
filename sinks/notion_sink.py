from typing import List
from datetime import datetime
from notion_client import Client
from models.position import Position
from interfaces.data_sink import DataSink
from config.settings import Settings

class NotionSink(DataSink):
    def __init__(self, settings: Settings):
        self.client = Client(auth=settings.notion_token)
        self.database_id = settings.notion_database_id

    def save_positions(self, positions: List[Position]) -> None:
        current_date = datetime.now().date().isoformat()
        
        for position in positions:
            page_data = self._create_page_data(position, current_date)
            try:
                self.client.pages.create(**page_data)
                print(f"Successfully imported {position.name} from {position.platform}")
            except Exception as e:
                print(f"Error importing {position.name}: {e}")

    def _create_page_data(self, position: Position, current_date: str) -> dict:
        return {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Date": {
                    "date": {
                        "start": current_date
                    }
                },
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": position.name
                            }
                        }
                    ]
                },
                "Worth": {
                    "number": float(position.worth)
                },
                "Platform": {
                    "select": {
                        "name": position.platform
                    }
                }
            }
        }
        