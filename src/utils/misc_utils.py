import os
from itertools import islice

import web3

w3_infura = web3.Web3(
    web3.Web3.HTTPProvider(
        f"https://mainnet.infura.io/v3/{os.environ['WEB3_INFURA_PROJECT_ID']}",
    ),
)


def to_dict(dict_to_parse: dict):
    # convert any 'AttributeDict' type found to 'dict'

    parsed_dict = dict(dict_to_parse)
    for key, val in parsed_dict.items():
        if "list" in str(type(val)):
            parsed_dict[key] = [parse_value(x) for x in val]
        else:
            parsed_dict[key] = parse_value(val)
    return parsed_dict


def parse_value(val):
    # check for nested dict structures to iterate through
    if "dict" in str(type(val)).lower():
        parsed_val = {}
        for key, _val in val.items():
            if "list" in str(type(_val)).lower():
                parsed_val[key] = [parse_value(x) for x in _val]
                continue
            parsed_val[key] = parse_value(_val)
        return parsed_val
    # convert 'HexBytes' type to 'str'
    elif "HexBytes" in str(type(val)):
        return val.hex()
    else:
        return val


def chunk_list(data, SIZE=1000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield [k for k in islice(it, SIZE)]


def chunk_dict(data, SIZE=1000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k: data[k] for k in islice(it, SIZE)}
