import json
import random
import threading
import uuid

import requests
from DB import *
from main import main
from bot import get_price, Bot_, get_value

# Ids_p = [1082603147391930480, 1068868803578052710, 1068911764776947722]
Ids = [, ]

def execute(rpc, private_key, address, token_address, value, stop_loss, take_profit):
    Bot_(rpc, private_key, address, token_address, value, stop_loss, take_profit).make_deal()


def make_request():

    headers = {
        'authorization': ''
    }

    while True:

        for Id in Ids:
            with requests.get(f'https://discord.com/api/v9/channels/{Id}/messages?limit=1', headers=headers) as resp:
                dd = resp.json()

                print(dd)
                # input()

                for post in dd:
                    contractAddress = post['embeds'][0]['description']
                    name = post['embeds'][0]['title']

                    Verified = None
                    Renounced = None

                    TaxBuy = None
                    TaxSell = None
                    TaxesParam = None

                    HoneypotBuy = None
                    HoneypotSell = None

                    Buys = None
                    Sells = None
                    BuySellParam = None

                    Volume = None

                    Liquidity = None

                    FDV = None

                    Price_5M = None
                    Price_1H = None

                    Uniq = None
                    Buys = None



                    for field in post['embeds'][0]['fields']:

                        if field['name'] == 'Verified | Renounced':
                            Verified = field['value'].split(' | ')[0].split(' ')[-1]
                            Renounced = field['value'].split(' | ')[1].split(' ')[-1]

                        elif field['name'] == 'Taxes':
                            TaxBuy = field['value'].split(' | ')[0].split(' ')[-1]
                            TaxSell = field['value'].split(' | ')[1].split(' ')[-1]

                            if '🟢' in field['value']:
                                TaxesParam = '🟢'
                            elif '🟡' in field['value']:
                                TaxesParam = '🟡'
                            elif '🔴' in field['value']:
                                TaxesParam = '🔴'

                        elif field['name'] == 'Honeypot':
                            HoneypotBuy = field['value'].split(' | ')[0].split(' ')[-1]
                            HoneypotSell = field['value'].split(' | ')[1].split(' ')[-1]

                        elif field['name'] == 'Buys | Sells':

                            if field['value'] == None:
                                break

                            Buys = field['value'].split(' | ')[0].split(' ')[-1]
                            Sells = field['value'].split(' | ')[1].split(' ')[-1]

                            if '🟢' in field['value']:
                                BuySellParam = '🟢'
                            elif '🟡' in field['value']:
                                BuySellParam = '🟡'
                            elif '🔴' in field['value']:
                                BuySellParam = '🔴'

                        elif field['name'] == 'Liquidity':
                            Liquidity = field['value'].replace(' ', '').replace('$', '')

                        elif field['name'] == 'Volume':
                            Volume = field['value'].replace(' ', '').replace('$', '')

                        elif field['name'] == 'FDV':
                            FDV = field['value'].replace(' ', '').replace('$', '')

                        elif field['name'] == 'Price m5':
                            Price_5M = field['value'].replace(' ', '').replace('%', '')

                        elif field['name'] == 'h1':
                            Price_1H = field['value'].replace(' ', '').replace('%', '')

                        elif field['name'] == 'Uniq':
                            Uniq = field['value'].replace(' ', '').replace('%', '')

                        elif field['name'] == 'Buys':
                            Buys = field['value'].replace(' ', '').replace('%', '')


                    if BuySellParam == None or HoneypotBuy == 'Honeypot' or BuySellParam == '🔴' or ( Verified == 'No' and Renounced == 'No' ):
                        continue

                    Session = sessionmaker(bind=engine)
                    session = Session()

                    wallets = session.query(Wallet).filter(Wallet.Status == 'Ready').all()

                    if len(wallets) == 0:
                        session.close()
                        continue

                    random_wallet = random.choice(wallets)

                    address = random_wallet.Address
                    private = random_wallet.Private

                    rpc = 'https://rpc.builder0x69.io'
                    private_key = private
                    token_address = contractAddress
                    value_percent = 30
                    stop_loss = 0.8
                    take_profit = 1.5
                    token_name = name

                    thread = threading.Thread(target=execute, args=(rpc, private_key, address, token_address, value_percent, stop_loss, take_profit, token_name))
                    thread.start()

                    # Bot_(rpc, private_key, address, token_address, value, stop_loss, take_profit).make_deal()

                    oper = Operation(id = uuid.uuid4(),
                                    Name = name,
                                    CoinAddress = contractAddress,
                                    BuyPrice = get_price(contractAddress, address, private),
                                    Value = get_value(address, private_key, value_percent))
                    random_wallet.Operations.append(oper)


                    session.commit()
                    session.close()




make_request()


