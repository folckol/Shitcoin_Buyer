import time
import uuid

from web3 import Web3
from uniswap import Uniswap
import one_inch
from config import erc20_abi
from DB import *

def get_price(token_address, address, private_key):

    rpc = 'https://rpc.builder0x69.io'

    web3 = Web3(Web3.HTTPProvider(rpc))

    contract = web3.eth.contract(token_address, abi=erc20_abi)
    decimal = contract.functions.decimals().call()

    weth_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    uniswap = Uniswap(address=address, private_key=private_key, version=2, provider=rpc)

    price_gwei = uniswap.get_price_output(weth_address, token_address, 1_000 * 10 ** decimal)
    price = int(price_gwei) / int("".join((["1"] + ["0"] * 18)))

    return price

def get_value(address, private_key, value):
    rpc = 'https://rpc.builder0x69.io'
    uniswap = Uniswap(address=address, private_key=private_key, version=2, provider=rpc)
    weth_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

    return uniswap.get_token_balance(weth_address) * value / 100

class Bot_:

    def __init__(self, rpc, private_key, address, token_address, value, stop_loss, take_profit, token_name):
        self.token_name = token_name
        self.private_key = private_key
        self.address = address
        self.token_address = token_address

        self.stop_loss = stop_loss
        self.take_profit = take_profit

        self.weth_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

        self.web3 = Web3(Web3.HTTPProvider(rpc))
        self.uniswap = Uniswap(address=address, private_key=private_key, version=2, provider=rpc)

        self.value = self.uniswap.get_token_balance(self.weth_address) * value/100



    def make_deal(self):
        if self.swap('buy'):



            bought_price = self.value / self.uniswap.get_token_balance(self.token_address)
            self.track_price(bought_price)

    def track_price(self, bought_price):
        price = self.get_price()
        while bought_price * self.stop_loss > price < bought_price * self.take_profit:
            price = self.get_price()

        weth_balance_before = self.uniswap.get_token_balance(self.weth_address)
        self.swap('sell')
        weth_balance_after = self.uniswap.get_token_balance(self.weth_address)
        result = weth_balance_after - weth_balance_before

        print(f'Result: {result}')

    def get_price(self):
        contract = self.web3.eth.contract(self.token_address, abi=erc20_abi)
        decimal = contract.functions.decimals().call()

        price_gwei = self.uniswap.get_price_output(self.weth_address, self.token_address, 1_000 * 10 ** decimal)
        price = int(price_gwei) / int("".join((["1"] + ["0"] * 18)))

        return price

    def swap(self, type):
        if type == 'buy':
            one_inch.approve(self.web3, self.private_key, self.weth_address)
            tx_hash = one_inch.inch_swap(self.web3, self.private_key, self.token_address, self.value)
            return self.check_txn(tx_hash, type)
        elif type == 'sell':
            tx_hash = one_inch.approve(self.web3, self.private_key, self.token_address)
            value = self.uniswap.get_token_balance(self.token_address)
            if tx_hash == True or self.check_txn(tx_hash, 'approve'):
                tx_hash = one_inch.inch_swap(self.web3, self.private_key, self.weth_address, value, self.token_address)
                return self.check_txn(tx_hash, type)

    def check_txn(self, tx_hash, type):
        if tx_hash:
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            if tx_receipt['status'] == 1:
                if type == 'approve':
                    pass
                else:
                    print(f'{type.capitalize()} succesful: https://etherscan.io/tx/{tx_hash}\n'
                          f'Token address: {self.token_address}')

                    if type == 'buy':
                        Session = sessionmaker(bind=engine)
                        session = Session()

                        operation = Operation(id=str(uuid.uuid4()),
                                              Name=self.token_name,
                                              CoinAddress=self.token_address,
                                              BuyPrice=self.get_price(),
                                              Value = self.value,
                                              TimeStamp=int(time.time())
                                              )

                        addr = session.query(Wallet).filter(Wallet.Address == self.address).first()
                        addr.Operations.append(operation)

                        session.commit()

                        session.add(Notification(id = uuid.uuid4(),
                                                 text = 'Произведена покупка монеты\n\n'
                                                        f'Кошелек: {self.address}\n'
                                                        f'Адресс монеты: {self.token_address}\n'
                                                        f'Сумма: {self.value} WETH\n'
                                                        f'Цена покупки: {self.get_price()}\n'
                                                        f'Хэш:\n https://etherscan.io/tx/{tx_hash}'))

                        session.commit()
                        session.close()

                    if type == 'sell':
                        Session = sessionmaker(bind=engine)
                        session = Session()

                        addr = session.query(Wallet).filter(Wallet.Address == self.address).first()

                        for operation in addr.Operations:
                            if operation.SellPrice == None:
                                break


                        operation.SellPrice = self.get_price()

                        session.commit()

                        session.add(Notification(id=uuid.uuid4(),
                                                 text='Произведена продажа монеты\n\n'
                                                      f'Кошелек: {self.address}\n'
                                                      f'Адресс монеты: {self.token_address}\n'
                                                      f'Сумма: {self.value} WETH\n'
                                                      f'Цена покупки: {self.get_price()}\n'
                                                      f'Хэш:\n https://etherscan.io/tx/{tx_hash}'))

                        session.commit()
                        session.close()

                return True
            else:
                print(f'{type.capitalize()} transaction failed: https://etherscan.io/tx/{tx_hash}\n'
                      f'Token address: {self.token_address}')

                Session = sessionmaker(bind=engine)
                session = Session()

                session.add(Notification(id=uuid.uuid4(),
                                         text='Покупка монеты не удалась\n\n'
                                              f'Кошелек: {self.address}\n'
                                              f'Адресс монеты: {self.token_address}\n'
                                              f'Хэш:\n https://etherscan.io/tx/{tx_hash}'))

                session.commit()
                session.close()


                return False
