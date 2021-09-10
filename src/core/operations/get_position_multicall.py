import logging
from datetime import datetime
from typing import Any
from typing import Dict

import brownie
from brownie.network.contract import Contract

from src.core.products_factory import Product
from src.utils.misc_utils import chunk_dict

logging.getLogger(__name__)


class CurvePositionCalculatorMultiCall:
    def __init__(
        self,
        product: Product,
    ):

        with brownie.multicall:
            logging.info("Initialising Position Calculator ...")

            # todo: initialise using poolinfo or pool config yaml file

            self.pool_contract = Contract(product.contract.addr)

            # initialise pool token contracts
            if len(product.token_contracts.items()) != 1:
                raise  # there should only be 1 token contract
            self.pool_token_contract = {}
            for token_name, info in product.token_contracts.items():

                token_contract = Contract(info.addr)
                self.pool_token_contract = {
                    "contract": token_contract,
                    "decimals": token_contract.decimals(),
                }

            # initialise underlying assets info
            self.lp_assets = []

            asset_addrs = [self.pool_contract.coins(i) for i in range(10)]
            asset_addrs = [i for i in asset_addrs if i]
            for asset_addr in asset_addrs:
                asset_contract = Contract(asset_addr)
                asset_decimals = asset_contract.decimals()
                asset_name = asset_contract.name()
                self.lp_assets.append(
                    {
                        "name": str(asset_name),
                        "contract": asset_contract,
                        "decimals": int(asset_decimals),
                    }
                )

            # initialise auxiliary contracts:
            # NOTE: gauge tokens have the same decimals as lp tokens
            self.gauge_contracts = {}
            for contract_name, contract in product.other_contracts.items():

                contract_name: str = contract_name
                gauge_contract = None
                decimals = None
                if contract.addr:
                    gauge_contract = Contract(contract.addr)
                    decimals = self.pool_token_contract["decimals"]

                gauge = {"contract": gauge_contract, "decimals": decimals}

                self.gauge_contracts[contract_name] = gauge

        logging.info("... done!")

    def get_position(self, lp_balances: dict, block_identifier: int) -> dict:

        current_position_of_tokens = {}
        for asset_idx, asset in enumerate(self.lp_assets):

            # calculate how many tokens the user would get if they withdrew
            # all of their liquidity in a single coin.
            time_start = datetime.now()
            num_tokens = []
            for chunk in chunk_dict(lp_balances):  # chunk to avoid OOG errors
                with brownie.multicall(
                    block_identifier=block_identifier,
                ):
                    for idx, (addr, lp_balance) in enumerate(chunk.items()):
                        num_tokens.append(
                            self.pool_contract.calc_withdraw_one_coin(
                                lp_balance,
                                asset_idx,
                            )
                        )

            logging.info(f"Time elapsed: {datetime.now()-time_start}")

            num_tokens_float = [
                int(num_tokens_user) / 10 ** asset["decimals"]
                if num_tokens_user
                else "Error"  # something went wrong so we explicitly store error
                for num_tokens_user in num_tokens
            ]
            current_position_of_tokens[asset["name"]] = num_tokens_float

        current_position_of_tokens["lp_balances"] = list(lp_balances.values())
        block_positions = self.__groom_user_positions(
            user_addrs=lp_balances.keys(),
            current_positions=current_position_of_tokens,
        )

        return block_positions

    def get_oracle_prices_dict(self, block_identifier: int):

        oracle_prices_dict = {}
        n_coin = 0
        n_coins_query = []
        for asset in self.lp_assets:
            if asset["name"] == "Tether USD":
                oracle_prices_dict[asset["asset"]] = 1
                continue
            oracle_prices_dict[asset["name"]] = None
            n_coin.append(n_coin)
            n_coin += 1

        with brownie.multicall(
            block_identifier=block_identifier,
        ):
            oracle_prices = [
                self.pool_contract.price_oracle(coin_index) / 10 ** 18
                for coin_index in n_coins_query
            ]

        n_coin = 0
        for key in oracle_prices_dict.keys():

            if not oracle_prices_dict[key]:
                continue

            oracle_prices_dict[key] = oracle_prices[n_coin]
            n_coin += 1

        return oracle_prices_dict

    @staticmethod
    def __groom_user_positions(
        user_addrs: Any, current_positions: Dict
    ) -> Dict:

        user_positions = {}
        for idx, addr in enumerate(user_addrs):
            user_position = {}
            for asset, positions in current_positions.items():
                user_position[asset] = positions[idx]

            user_positions[addr] = user_position

        return user_positions
