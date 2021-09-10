import web3
from brownie import network
from brownie._config import CONFIG


def connect(node_provider_https: str, network_name: str = "mainnet") -> None:
    # change network provider to user specified
    CONFIG.networks[network_name]["host"] = node_provider_https
    CONFIG.networks[network_name]["name"] = "Ethereum mainnet"

    # connect to mainnet
    network.connect("mainnet")


def get_http_provider(node_provider_https: str):
    return web3.Web3(web3.Web3.HTTPProvider(node_provider_https))


def get_websocket_provider(node_provider_websocket: str):
    return web3.Web3(web3.Web3.WebsocketProvider(node_provider_websocket))
