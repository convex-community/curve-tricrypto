from dataclasses import field
from datetime import datetime
from typing import List

import pytz as pytz
from marshmallow_dataclass import dataclass

from src.core.datastructures.base import BaseDataStruct
from src.core.datastructures.tokens import Token


@dataclass
class Rewards(BaseDataStruct):

    date: datetime = pytz.utc.localize(datetime.utcnow())
    tokens: List[Token] = field(default_factory=lambda: [Token()])
