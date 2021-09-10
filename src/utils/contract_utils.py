import os
import re
from typing import List
from typing import Optional

from brownie.network.contract import Contract
from etherscan.accounts import Account
from etherscan.client import Client
from etherscan.client import EmptyResponse
from web3 import Web3


def init_contract(address: str) -> Optional[Contract]:

    if not Web3.isAddress(address):
        return None

    try:
        contract = Contract(address_or_alias=address)
    except Exception as e:
        print(e)
        contract = Contract.from_explorer(address=address)

    return contract


class TransactionScraper(Account):
    def __init__(self, address=Client.dao_address, api_key="YourApiKey"):
        Account.__init__(self, address=address, api_key=api_key)
        self.url_dict[self.MODULE] = "account"

    def get_tx_with(
        self,
        addr: str,
        start_block: int = 0,
        end_block: int = -1,
        sort: str = "asc",
    ):

        self.url_dict[self.ACTION] = "txlist"
        self.url_dict[self.SORT] = sort
        self.url_dict[self.START_BLOCK] = str(start_block)
        self.url_dict[self.END_BLOCK] = str(end_block)
        if int(end_block) == -1:
            self.url_dict[self.END_BLOCK] = "latest"

        self.build_url()
        req = self.connect()
        relevant_txes = []
        for tx in req["result"]:
            if tx["from"] in [
                addr,
                addr.lower(),
                Web3.toChecksumAddress(addr),
            ]:
                relevant_txes.append(tx)

        return

    def get_tx(self, offset=10000, sort="asc") -> list:

        self.url_dict[self.ACTION] = "txlist"
        self.url_dict[self.PAGE] = str(1)
        self.url_dict[self.OFFSET] = str(offset)
        self.url_dict[self.SORT] = sort
        self.build_url()

        trans_list = []
        while True:
            self.build_url()

            try:

                req = self.connect()
                if "No transactions found" in req["message"]:
                    return trans_list

                else:

                    trans_list += req["result"]
                    # Find any character block that is a integer of any length
                    page_number = re.findall(
                        Account.PAGE_NUM_PATTERN, self.url_dict[self.PAGE]
                    )
                    self.url_dict[self.PAGE] = str(int(page_number[0]) + 1)

            except EmptyResponse:

                return trans_list


def get_all_txes(
    address: str,
) -> List:

    tx_scraper = TransactionScraper(
        address=address, api_key=os.environ["ETHERSCAN_API_KEY"]
    )
    txes = tx_scraper.get_tx()

    return txes
