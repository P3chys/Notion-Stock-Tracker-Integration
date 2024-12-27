from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

@dataclass
class Position:
    name: str
    worth: Decimal
    platform: str
    timestamp: datetime = datetime.now()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "worth": str(self.worth),
            "platform": self.platform
        }