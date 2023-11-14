import requests
from web3 import Web3
from config import inch_abi, erc20_abi


def get_api_call_data(url):
    try:
        call_data = requests.get(url)
    except Exception as e:
        print(f'Call data error: {e}')
        return get_api_call_data(url)
    try:
        api_data = call_data.json()
        return api_data
    except Exception as e:
        print(f'Call data error: {e}')


def inch_swap(web3, private_key, to_token_address, amount, from_token_address='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'):
    try:
        my_address = web3.eth.account.from_key(private_key).address
        nonce = web3.eth.get_transaction_count(my_address)

        contract = web3.eth.contract(from_token_address, abi=inch_abi)
        decimal = contract.functions.decimals().call()

        if from_token_address == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2':
            amount = int(amount * int("".join(["1"] + ["0"] * decimal)))

        url = f'https://api.1inch.io/v5.0/{web3.eth.chain_id}/swap?' \
              f'fromTokenAddress={from_token_address}&' \
              f'toTokenAddress={to_token_address}' \
              f'&amount={amount}' \
              f'&fromAddress={my_address}&slippage=1'

        json_data = get_api_call_data(url)
        tx = json_data['tx']
        tx['nonce'] = nonce
        tx['to'] = Web3.to_checksum_address(tx['to'])
        tx['gasPrice'] = int(tx['gasPrice'])
        tx['value'] = int(tx['value'])
        tx['chainId'] = web3.eth.chain_id

        signed_txn = web3.eth.account.sign_transaction(tx, private_key)
        txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return web3.to_hex(txn_hash)

    except Exception as e:
        print(f'Swap error: {e}')


def approve(web3, private_key, token_address):
    try:
        spender = '0x1111111254EEB25477B68fb85Ed929f73A960582'
        contract = web3.eth.contract(token_address,  abi=erc20_abi)
        my_address = web3.eth.account.from_key(private_key).address
        nonce = web3.eth.get_transaction_count(my_address)
        amount = 2 ** 256 - 1

        allowance = contract.functions.allowance(my_address, spender).call()

        if allowance == amount:
            return True

        contract_txn = contract.functions.approve(spender, amount).build_transaction({
            'from': my_address,
            'value': 0,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce,
        })

        signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key)
        txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return web3.to_hex(txn_hash)
    except Exception as e:
        print(f'Approve error: {e}')
