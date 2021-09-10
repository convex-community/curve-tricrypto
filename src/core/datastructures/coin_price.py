from datetime import datetime

import pytz as pytz
from marshmallow_dataclass import dataclass

from src.core.datastructures.base import BaseDataStruct


@dataclass
class CoinPrice(BaseDataStruct):

    time: datetime = pytz.utc.localize(datetime.utcnow())
    currency: str = ""
    quote: float = 0
