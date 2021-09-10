from dataclasses import field
from typing import Dict

from marshmallow_dataclass import dataclass

from src.core.datastructures.base import BaseDataStruct


@dataclass
class ContractInfo(BaseDataStruct):
    name: str = ""
    addr: str = ""
    genesis_block: int = 0


@dataclass
class Product(BaseDataStruct):
    name: str = ""
    contract: ContractInfo = ContractInfo()

    # todo: incorporate poolinfo
    token_contracts: Dict[str, ContractInfo] = field(
        default_factory=lambda: {"": ContractInfo()}
    )
    other_contracts: Dict[str, ContractInfo] = field(
        default_factory=lambda: {"": ContractInfo()}
    )


CURVE_CRYPTOSWAP = ContractInfo(
    name="Curve CryptoSwap",
    addr="0x331aF2E331bd619DefAa5DAc6c038f53FCF9F785",
)

TRICRYPTO_V2 = Product(
    name="TriCrypto V2",
    contract=ContractInfo(
        name="TriCrypto v2 Pool",
        addr="0xD51a44d3FaE010294C616388b506AcdA1bfAAE46",
        genesis_block=12821148,
    ),
    token_contracts={
        "crv3crypto": ContractInfo(
            name="crv3crypto Token",
            addr="0xc4AD29ba4B3c580e6D59105FFf484999997675Ff",
        ),
    },
    other_contracts={
        "curve_gauge": ContractInfo(
            name="TriCrypto v2 Curve Gauge",
            addr="0xDeFd8FdD20e0f34115C7018CCfb655796F6B2168",
        ),
        "convex_gauge": ContractInfo(
            name="TriCrypto v2 Convex Gauge",
            addr="0x9D5C5E364D81DaB193b72db9E9BE9D8ee669B652",
        ),  # No contracts yet
    },
)

cvxCRV_STAKING = Product(
    name="cvxCRV Staking",
    contract=ContractInfo(
        name="CRV Depositor", addr="0x8014595F2AB54cD7c604B00E9fb932176fDc86Ae"
    ),
    token_contracts={
        "CVX": ContractInfo(
            name="Convex Token",
            addr="0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B",
        ),
        "CRV": ContractInfo(
            name="Curve DAO Token",
            addr="0xD533a949740bb3306d119CC777fa900bA034cd52",
        ),
        "cvxCRV": ContractInfo(
            name="3crv Liquidity Pool Token",
            addr="0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490",
        ),
    },
    other_contracts={
        "cvxCRV_rewards": ContractInfo(
            name="cvxCRV Rewards",
            addr="0x3Fe65692bfCD0e6CF84cB1E7d24108E434A7587e",
        ),
        "CVX_rewards": ContractInfo(
            name="CVX Rewards",
            addr="0xCF50b810E57Ac33B91dCF525C6ddd9881B139332",
        ),
        "3CRV_rewards": ContractInfo(
            name="3CRV Rewards",
            addr="0x7091dbb7fcbA54569eF1387Ac89Eb2a5C9F6d2EA",
        ),
    },
)

CVX_STAKING = Product(
    name="CVX Staking",
    contract=ContractInfo(
        name="CVX Reward Pool",
        addr="0xCF50b810E57Ac33B91dCF525C6ddd9881B139332",
    ),
    other_contracts={
        "cvxCRV_rewards": ContractInfo(
            name="cvxCRV Rewards",
            addr="0x3Fe65692bfCD0e6CF84cB1E7d24108E434A7587e",
        ),
    },
)
