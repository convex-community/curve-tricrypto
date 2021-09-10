from src.core.datastructures.pool_info import ConvexPoolInfo
from src.utils.contract_utils import init_contract


CONVEX_BOOSTER_ADDRESS = "0xF403C135812408BFbE8713b5A23a04b3D48AAE31"


def get_pool_info(pool_index: int = 0) -> ConvexPoolInfo:

    contract = init_contract(CONVEX_BOOSTER_ADDRESS)
    pool_info_tuple = contract.poolInfo(pool_index)

    pool_token = init_contract(pool_info_tuple[0])
    pool_name = pool_token.name()

    pool_info = ConvexPoolInfo(
        name=pool_name,
        curve_pool_token=pool_info_tuple[0],
        convex_pool_token=pool_info_tuple[1],
        curve_gauge=pool_info_tuple[2],
        crv_rewards=pool_info_tuple[3],
        stash=pool_info_tuple[4],
        shutdown=pool_info_tuple[5],
    )

    return pool_info


def main():
    from brownie.network import disconnect

    import json
    import os
    from src.utils.network_utils import connect

    connect(os.environ["node_provider"])
    pool_info = get_pool_info(pool_index=0)

    print(json.dumps(pool_info.__dict__, indent=4, default=str))

    disconnect()


if __name__ == "__main__":
    main()
