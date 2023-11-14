
import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from bot import *
from DB import *

key = ''

logging.basicConfig(level=logging.INFO)

# Создаем бота и диспетчер
bot = Bot(token=key)
dp = Dispatcher(bot, storage=MemoryStorage())

valid_ids = [199804475,649811235,733000248]

# Обрабатываем команду /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):

    if message.from_user.id not in valid_ids:
        return


    await message.answer('Саламчик, команды вот:\n\n'
                         '/active - Активные сделки\n'
                         '/balance - Баланс\n'
                         '/history - История')


@dp.message_handler(commands=['active'])
async def active(message: types.Message):

    if message.from_user.id not in valid_ids:
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    addresses = session.query(Wallet).filter(Wallet.Status == 'Active').all()

    for address in addresses:
        operations = address.Operations
        for operation in operations:
            if operation.SellPrice == None:

                PriceNow = get_price(operation.CoinAddress, address.Address, address.PrivateKey)

                await message.answer(f'Кошелек: {address.Address}\n\n'
                                     f'Монета: {operation.Name} | {operation.CoinAddress}\n'
                                     f'Цена покупки: {operation.BuyPrice} WETH/{operation.Name}\n'
                                     f'Цена сейчас: {PriceNow} WETH/{operation.Name}\n'
                                     f'Изменение: {(PriceNow-operation.BuyPrice)/operation.BuyPrice * 100}%')

                break

    session.close()

@dp.message_handler(commands=['balance'])
async def balance(message: types.Message):

    if message.from_user.id not in valid_ids:
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    addresses = session.query(Wallet).all()

    text = ''

    for address in addresses:
        text += address.Address + '-' + address.Balance + 'WETH\n'

    await message.answer(text)

    session.close()

@dp.message_handler(commands=['history'])
async def history(message: types.Message):

    if message.from_user.id not in valid_ids:
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    addresses = session.query(Wallet).all()

    text = ''

    for address in addresses:

        operations = address.Operations

        count = 0

        for operation in operations:
            if operation.SellPrice == None:
                continue
            else:
                count+=1

        text += f'/history_of_{address.Address}' + '-' + count

    await message.answer(text)

    session.close()


@dp.message_handler(lambda message: message.text.startswith('/history_of_'))
async def history_(message: types.Message):

    if message.from_user.id not in valid_ids:
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    address = session.query(Wallet).filter(Wallet.Address == message.text.replace('/history_of_', '')).first()


    operations = address.Operations

    count = 0

    for operation in operations:

        if operation.SellPrice == None:
            continue

        await message.answer(f'Название - {operation.Name}\n'
                             f'Адресс - {operation.CoinAddress}\n'
                             f'Цена покупки - {operation.BuyPrice} WETH/{operation.Name}\n'
                             f'Цена продажи - {operation.SellPrice} WETH/{operation.Name}\n'
                             f'Профит - {operation.SellPrice*operation.Value-operation.BuyPrice*operation.Value} WETH')

    session.close()

async def scheduled(wait_for):
    while True:
        Session = sessionmaker(bind=engine)
        session = Session()

        notifications = session.query(Notification).all()

        for notification in notifications:
            for id_ in valid_ids:
                await bot.send_message(id_, notification.text)
                await asyncio.sleep(0.3)

                session.query(Notification).filter(Notification.id == notification.id).delete()
                session.commit()

        session.close()


        await asyncio.sleep(wait_for)


# Запускаем бота
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(1))
    executor.start_polling(dp, loop=loop)



