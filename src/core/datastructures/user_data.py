from typing import Optional

from marshmallow_dataclass import dataclass

from src.core.datastructures.base import BaseDataStruct
from src.core.datastructures.pool_transactions import HistoricalTransactions
from src.core.datastructures.pools import Pools


@dataclass
class UserData(BaseDataStruct):

    address: str = ""
    current_liquidity: Pools = Pools()
    historical_liquidity_transactions: HistoricalTransactions = (
        HistoricalTransactions()
    )


def main():

    user_data = UserData()
    print(user_data)


if __name__ == "__main__":
    main()
