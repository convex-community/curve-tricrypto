import argparse

from src.core.operations.get_lp_txes import get_mint_or_burn_txs
from src.core.operations.read_liquidity_transaction import (
    get_liquidity_moved_for_tx,
)
from src.utils.network_utils import connect


def parse_args():
    parser = argparse.ArgumentParser(
        description="Get TriCrypto positions and deposit info for address."
    )
    parser.add_argument(
        "--address",
        dest="address",
        help="Address to fetch info for.",
        type=str,
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

    return parser.parse_args()


def main():
    from src.core.products_factory import TRICRYPTO_V2
    import json

    args = parse_args()

    # connect to custom note provider in args
    connect(args.node_provider_https)

    added_liquidity_txes = get_mint_or_burn_txs(
        user_address=args.address,
        token_addr=TRICRYPTO_V2.token_contracts["crv3crypto"].addr,
        from_block=TRICRYPTO_V2.contract.genesis_block,
        tx_type="mint",
    )

    if not added_liquidity_txes:
        pass

    added_liquidity = []
    for tx in added_liquidity_txes:
        parsed_tx = get_liquidity_moved_for_tx(
            tx_hash=tx["hash"][2:], currency="usd"
        )
        added_liquidity.append(parsed_tx)
        print(json.dumps(parsed_tx.__dict__, indent=4, default=str))


if __name__ == "__main__":
    main()
