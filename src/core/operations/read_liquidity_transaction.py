import logging
from datetime import datetime
from typing import Tuple

import pytz
from brownie import ZERO_ADDRESS
from brownie.network import transaction
from brownie.network.event import EventDict

from src.core.datastructures.pool_transactions import LiquidityTransaction
from src.core.datastructures.tokens import Token
from src.utils.coin_prices import get_historical_price_coingecko
from src.utils.contract_utils import init_contract

logging.getLogger(__name__)


def get_liquidity_moved_for_tx(tx_hash: str, currency: str = "usd"):

    tx_receipt = transaction.TransactionReceipt(tx_hash)
    date = pytz.utc.localize(datetime.utcfromtimestamp(tx_receipt.timestamp))
    contract_function = tx_receipt.fn_name

    events: EventDict = tx_receipt.events

    if contract_function == "add_liquidity":
        lp_tokens = get_minted_tokens(events)
    elif contract_function == "remove_liquidity":
        lp_tokens = get_burned_tokens(events)
    elif contract_function == "remove_liquidity_one_coin":
        lp_tokens = get_burned_tokens(events)
    else:
        return LiquidityTransaction()

    return LiquidityTransaction(
        date=date,
        contract_function=contract_function,
        transaction_hash=tx_hash,
        lp_tokens=lp_tokens,
        block_number=tx_receipt.block_number,
        transaction_fees_eth=tx_receipt.gas_used
        * 1e-18
        * tx_receipt.gas_price,
    )


def get_minted_tokens(events: EventDict) -> int:

    for event in events:
        if "_from" in event.keys() and event["_from"] == ZERO_ADDRESS:
            minted_tokens = event["_value"]  # ZERO_ADDRESS mints lp tokens
            return minted_tokens
    return 0


def get_burned_tokens(events: EventDict) -> int:

    for event in events:
        if "_to" in event.keys() and event["_to"] == ZERO_ADDRESS:
            burned_tokens = event["_value"]  # ZERO_ADDRESS mints lp tokens
            return burned_tokens
    return 0


def get_added_tokens(events: EventDict) -> Tuple:

    for event in events:
        if event.name == "AddLiquidity":
            tokens_added = event["token_amounts"]
            return tokens_added


def get_removed_tokens(events: EventDict) -> Tuple:

    for event in events:
        if event.name == "RemoveLiquidity":
            tokens_removed = event["token_amounts"]
            return tokens_removed


def get_removed_tokens_one(events: EventDict) -> Tuple:
    liquidity_pool_transaction_index = None
    for event_id, event in enumerate(events):
        if "_to" in event.keys() and event["_to"] == ZERO_ADDRESS:
            # after the lp token is burnt, the pool transfer contract is
            # called.
            liquidity_pool_transaction_index = event_id + 1

    if not liquidity_pool_transaction_index:
        return ()  # TODO: might be a source of error

    liquidity_pool_addr = events[liquidity_pool_transaction_index]["from"]
    liquidity_pool_contract = init_contract(liquidity_pool_addr)

    # we need the number of underlying coins
    num_underlying_tokens: int = 0
    for i in range(100):
        try:
            liquidity_pool_contract.coins(i)
            num_underlying_tokens += 1
        except ValueError:  # max index reached, hence count is num tokens
            break

    token_amount = 0
    token_index = None
    for event in events:
        if event.name == "RemoveLiquidityOne":
            token_amount = event["token_amount"]
            token_index = event["coin_index"]

    if not token_index:
        return ()  # TODO: might be a source of error

    # create an empty tuple and fill in tokens_removed at token_index
    tokens_removed = []
    for i in range(num_underlying_tokens):
        if i == token_index:
            tokens_removed.append(token_amount)
        else:
            tokens_removed.append(0)

    return tokens_removed
