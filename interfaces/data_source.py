from abc import ABC, abstractmethod
from typing import List
from models.position import Position

class DataSource(ABC):
    @abstractmethod
    def fetch_positions(self) -> List[Position]:
        """Fetch positions from the data source"""
        pass