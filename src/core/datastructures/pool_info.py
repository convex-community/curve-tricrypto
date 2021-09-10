from marshmallow_dataclass import dataclass

from src.core.datastructures.base import BaseDataStruct
from src.core.products_factory import ContractInfo


@dataclass
class ConvexPoolInfo(BaseDataStruct):

    name: str = ""
    curve_pool_token: ContractInfo = ContractInfo()
    convex_pool_token: ContractInfo = ContractInfo()
    curve_gauge: ContractInfo = ContractInfo()
    crv_rewards: ContractInfo = ContractInfo()
    cvx_token: ContractInfo = ContractInfo(
        name="CVX", addr="0x4e3fbd56cd56c3e72c1403e103b45db9da5b9d2b"
    )
    stash: ContractInfo = ContractInfo()
    shutdown: bool = False
