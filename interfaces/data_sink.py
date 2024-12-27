from abc import ABC, abstractmethod
from typing import List
from models.position import Position

class DataSink(ABC):
    @abstractmethod
    def save_positions(self, positions: List[Position]) -> None:
        """Save positions to the data sink"""
        pass