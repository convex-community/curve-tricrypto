import argparse
import logging
import os
import time
from datetime import datetime
from typing import Optional

import brownie.network
from brownie.network.contract import Contract
from eth_abi.exceptions import InsufficientDataBytes
from pandas import DataFrame

from src.core.operations.current_block import get_block_info
from src.core.operations.get_position_multicall import (
    CurvePositionCalculatorMultiCall,
)
from src.core.operations.get_user_lp_tokens import (
    get_liquidity_positions_for_participants,
)
from src.core.operations.get_user_lp_tokens import get_lp_tokens_of_users
from src.core.products_factory import TRICRYPTO_V2
from src.utils.cache_utils import cache_object_to_json
from src.utils.contract_utils import get_all_txes
from src.utils.network_utils import connect


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d-4s %(levelname)-4s [%(filename)s %(module)s:%(lineno)d] :: %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
)

SLEEP_TIME = 1800


def parse_args():

    parser = argparse.ArgumentParser(
        description="Get current Pool Liquidity Providers."
    )
    parser.add_argument(
        "--cache-dir",
        dest="cache_dir",
        type=str,
        default="../data/block_positions_for_amount",
    )
    parser.add_argument(
        "--node-provider-https",
        dest="node_provider_https",
        help="Node provider API. It must have Archive Node access (Alchemy). "
        "Go to: https://alchemy.com/?r=0f41076514343f84 to get $100 of "
        "credits. They also have a free tier with archival node access. "
        "After you make an account, you can fetch your api key and enter "
        "it in this parameter, "
        "e.g. https://eth-mainnet.alchemyapi.io/v2/API_KEY",
        type=str,
    )
    parser.add_argument(
        "--block-steps",
        dest="block_steps",
        type=int,
        default=1000,
    )
    parser.add_argument(
        "--lp-amount",
        dest="lp_amount",
        type=int,
        default=100,
    )
    return parser.parse_args()


def get_eth_tricrypto_positions(
    cache_dir: str,
    node_provider_https: str,
    block_steps: int,
    lp_amount: Optional[int] = None,
):

    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    # connect to custom note provider in args
    connect(node_provider_https)

    staking_contracts = [
        Contract(TRICRYPTO_V2.token_contracts["crv3crypto"].addr),
        Contract(TRICRYPTO_V2.other_contracts["curve_gauge"].addr),
        Contract(TRICRYPTO_V2.other_contracts["convex_gauge"].addr),
    ]

    # initialise tricrypto
    tricrypto_calculator = CurvePositionCalculatorMultiCall(TRICRYPTO_V2)
    from_block = TRICRYPTO_V2.contract.genesis_block

    steps = block_steps
    to_block = from_block + steps  # initialisation
    extra_steps_if_error = 100
    sleep_time = 0

    while True:

        cache_filename = os.path.join(
            cache_dir, f"block_{to_block}_lp_amount_{lp_amount}.csv"
        )
        if os.path.exists(cache_filename):
            # cache already exists. moving on...
            to_block += +steps
            continue

        # get block number (this uses a free api). can do with brownie but
        # why rpc call when you can avoid it?
        current_block = int(get_block_info()["height"])
        logging.info(f"Current block: {current_block}")

        # set longer sleep time if reached current block
        if to_block > current_block:
            logging.info(f"Reached max block height {current_block}")
            to_block = current_block
            sleep_time = SLEEP_TIME  # longer sleep time.

        # get addresses of active participants
        logging.info(f"Fetching Txes between {from_block} : {current_block}")
        historical_txes = get_all_txes(
            address=TRICRYPTO_V2.token_contracts["crv3crypto"].addr,
        )
        logging.info(f"... done! Num lp token txes: {len(historical_txes)}")
        from_addresses = [i["from"] for i in historical_txes]
        to_addresses = [i["to"] for i in historical_txes]
        all_addreses = from_addresses + to_addresses
        all_unique_participants = list(set(all_addreses))

        # remove zero addr
        current_liquidity_providers = list(
            filter(None, all_unique_participants)
        )

        # connect to brownie if not connected
        if not brownie.network.is_connected():
            connect(node_provider_https)

        # get active balances
        logging.info("Fetching active balances")
        while True:

            try:

                active_balances = get_lp_tokens_of_users(
                    participating_addrs=current_liquidity_providers,
                    staking_contracts=staking_contracts,
                    block_identifier=to_block,
                )
                break

            except InsufficientDataBytes:

                logging.warning(
                    f"InsufficientDataBytes encountered: "
                    f"retrying with {extra_steps_if_error} block steps ahead"
                )
                to_block = to_block + steps + extra_steps_if_error

                continue

        # aggregate positions to get total lp tokens
        logging.info("aggregating positions")
        aggregated_positions_all = get_liquidity_positions_for_participants(
            active_balances
        )

        addr_and_positions_to_calculate_on = aggregated_positions_all
        if lp_amount:
            # only select participants with at least 100 lp tokens
            # also, only calculate for args.lp_tokens number of tokens
            addr_and_positions_to_calculate_on = {}
            for key, value in aggregated_positions_all.items():
                if value > lp_amount * 1e18:
                    addr_and_positions_to_calculate_on[key] = lp_amount * 1e18

            if not addr_and_positions_to_calculate_on:
                # no addresses cross the threshold, so then we just move on.
                to_block += steps
                continue

        # get block positions
        logging.info("calculating underlying tokens")
        start_time = datetime.now()
        block_position = tricrypto_calculator.get_position(
            lp_balances=addr_and_positions_to_calculate_on,
            block_identifier=to_block,
        )
        logging.info(f"time taken: {datetime.now() - start_time}")

        # format block_position data for influxdb
        block_position_df = DataFrame(block_position).T
        block_position_df.index.name = "addr"
        block_position_df.reset_index(inplace=True)
        block_position_df.index = [
            datetime.fromtimestamp(
                brownie.web3.eth.get_block(to_block).timestamp
            )
        ] * block_position_df.shape[0]
        block_position_df["block_number"] = to_block

        # cache positions for block
        logging.info("cacheing output")
        block_position_df.to_csv(cache_filename)

        # disconnect_brownie
        brownie.network.disconnect()

        # all steps succeeded! we can step up now
        to_block += steps

        logging.info(f"sleeping for {sleep_time} seconds \n")
        time.sleep(sleep_time)


def main():

    args = parse_args()
    get_eth_tricrypto_positions(
        node_provider_https=args.node_provider_https,
        cache_dir=args.cache_dir,
        block_steps=args.block_steps,
        lp_amount=args.lp_amount,
    )


if __name__ == "__main__":
    main()
