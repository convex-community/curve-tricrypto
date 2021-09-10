from marshmallow_dataclass import dataclass

from src.core.datastructures.base import BaseDataStruct


@dataclass
class PoolFees(BaseDataStruct):

    accrued_fees: float = 0
    block_start: int = 0
    block_end: int = 0
