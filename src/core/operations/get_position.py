import logging
from datetime import datetime
from typing import Optional

import pytz
from brownie import web3

from src.core.datastructures.current_position import Position
from src.core.datastructures.tokens import Token
from src.core.products_factory import Product
from src.core.sanity_check.check_value import is_dust
from src.utils.contract_utils import init_contract

logging.getLogger(__name__)


class CurvePositionCalculator:
    def __init__(
        self,
        product: Product,
    ):

        logging.info("Initialising Position Calculator ...")

        # todo: initialise using poolinfo or pool config yaml file

        self.pool_contract = init_contract(product.contract.addr)

        # initialise pool token contracts
        if len(product.token_contracts.items()) != 1:
            raise  # there should only be 1 token contract
        self.pool_token_contract = {}
        for token_name, info in product.token_contracts.items():

            token_contract = init_contract(info.addr)
            self.pool_token_contract = {
                "contract": token_contract,
                "decimals": token_contract.decimals(),
            }

        # initialise underlying assets info
        self.lp_assets = []
        for i in range(100):
            try:
                asset_addr = self.pool_contract.coins(i)
                asset_contract = init_contract(asset_addr)
                asset_decimals = asset_contract.decimals()
                asset_name = asset_contract.name()
                self.lp_assets.append(
                    {
                        "name": asset_name,
                        "contract": asset_contract,
                        "decimals": asset_decimals,
                    }
                )
            except ValueError:  # max index reached
                break

        # initialise auxiliary contracts:
        # NOTE: gauge tokens have the same decimals as lp tokens
        self.gauge_contracts = {}
        for contract_name, contract in product.other_contracts.items():

            contract_name: str = contract_name
            gauge_contract = None
            decimals = None
            if contract.addr:
                gauge_contract = init_contract(contract.addr)
                decimals = self.pool_token_contract["decimals"]

            gauge = {"contract": gauge_contract, "decimals": decimals}

            self.gauge_contracts[contract_name] = gauge

        logging.info("... done!")

    def get_token_and_gauge_bal(
        self, user_address: str, block_number: int
    ) -> dict:
        """We calculate position on the following token balance:
        (tokens in gauge + free lp tokens)

        :param block_number:
        :param user_address: web3 address of the user
        :return:
        """
        token_balances = {}

        # liquidity pool token balances

        try:
            pool_token_balance = self.pool_token_contract[
                "contract"
            ].balanceOf(user_address, block_identifier=block_number)
            if is_dust(
                pool_token_balance, self.pool_token_contract["decimals"]
            ):
                pool_token_balance = 0
        except ValueError:
            pool_token_balance = 0

        token_balances["liquidity_pool"] = pool_token_balance

        # gauge token balances
        for name, gauge in self.gauge_contracts.items():
            if not gauge["contract"]:
                continue
            try:
                token_balance = gauge["contract"].balanceOf(
                    user_address, block_identifier=block_number
                )
                if is_dust(token_balance, gauge["decimals"]):
                    token_balance = 0
            except ValueError:
                token_balance = 0
            token_balances[name] = token_balance

        return token_balances

    def get_position(
        self,
        user_address: str,
        block_number: Optional[int],
    ) -> Position:

        platform_token_balances = self.get_token_and_gauge_bal(
            user_address=user_address, block_number=block_number
        )
        token_balance_to_calc_on = sum(platform_token_balances.values())

        if not token_balance_to_calc_on:
            return Position(block_number=block_number)

        current_position_of_tokens = []
        for asset_idx, asset in enumerate(self.lp_assets):

            # calculate how many tokens the user would get if they withdrew
            # all of their liquidity in a single coin.
            num_tokens = self.pool_contract.calc_withdraw_one_coin(
                token_balance_to_calc_on,
                asset_idx,
                block_identifier=block_number,
            )

            num_tokens_float = num_tokens / 10 ** asset["decimals"]

            current_position_of_tokens.append(
                Token(
                    name=asset["name"],
                    address=asset["contract"].address,
                    num_tokens=num_tokens_float,
                ),
            )

        platform_token_balances.update(
            (x, y / 10 ** self.pool_token_contract["decimals"])
            for x, y in platform_token_balances.items()
        )
        position_data = Position(
            block_number=block_number,
            token_balances=platform_token_balances,
            tokens=current_position_of_tokens,
        )

        return position_data
