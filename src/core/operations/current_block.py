from typing import Dict

import requests


def get_block_info() -> Dict:

    block_info_response = requests.get(
        "https://api.blockcypher.com/v1/eth/main",
    )

    return block_info_response.json()


def main():
    import json

    block_info = get_block_info()
    print(json.dumps(block_info, indent=4))


if __name__ == "__main__":
    main()
