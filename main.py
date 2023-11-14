import threading
from web3 import Web3

from bot import Bot_


def execute(rpc, private_key, address, token_address, value, stop_loss, take_profit):
    Bot_(rpc, private_key, address, token_address, value, stop_loss, take_profit).make_deal()


def main(rpc, private_key, address, token_address, value, stop_loss, take_profit):
    thread = threading.Thread(target=execute, args=(rpc, private_key, address, token_address, value, stop_loss, take_profit))
    thread.start()


if __name__ == "__main__":

    private_key = ''
    address = Web3.to_checksum_address('')
    rpc = 'https://rpc.builder0x69.io'

    token_address = Web3.to_checksum_address('')
    value = 0.04
    stop_loss = 0.8
    take_profit = 1.5

    main(rpc, private_key, address, token_address, value, stop_loss, take_profit)
