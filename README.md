# curve-tricrypto

This is a python repo that parses the ethereum blockchain to get data on a liquidity provider's underlying tokens in a
liquidity pool. The pool contracts in this repo are in curve, with staking contracts in curve and convex (soon other staking contracts). This repo focuses on tricrypto.

## Installation

```bash
python3 -m venv venv
source ./venv/bin/activate
pip install --upgrade pip
pip install -r ./requirements.txt
```

## Usage

The notebook impermanent_loss_analysis.ipynb uses the ethereum blockchain scraper (at certain block steps) from a curve
liquidity pool contract's genesis till the current block; the scraper is in src/get_block_positions.py.

The user needs access to an archive node. Alchemy is preferred. The example is also in the notebook. Furthermore, the user
needs Etherscan api token in their environment, as Brownie (the web3py wrapper) uses it to fetch contract ABI from the explorer.

Have fun!

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
