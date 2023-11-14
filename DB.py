from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table, Boolean, Float
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///SHitCoin.db',pool_size=30, max_overflow=0)
Base = declarative_base()

# Association table between User and Raffle


class ShitCoin(Base):
    __tablename__ = 'ShitCoins'

    id = Column(String, primary_key=True, unique=True)
    contractAddress = Column(String)
    name = Column(String)
    Verified = Column(Boolean)
    Renounced = Column(Boolean)
    TaxBuy = Column(Integer)
    TaxSell = Column(Integer)
    TaxesParam = Column(String)
    HoneypotBuy = Column(Boolean)
    HoneypotSell = Column(Boolean)
    Buys = Column(Integer)
    Sells = Column(Integer)
    BuySellParam = Column(String)
    Volume = Column(Integer)
    Liquidity = Column(Integer)
    FDV = Column(Integer)
    Price_5M = Column(Integer)
    Price_1H = Column(Integer)
    Uniq = Column(Integer)
    Buys = Column(Integer)
    TimeStamp = Column(Integer)



class Wallet(Base):
    __tablename__ = 'Wallets'

    id = Column(String, primary_key=True, unique=True)
    PrivateKey = Column(String)
    Address = Column(String)
    Status = Column(String)
    Balance = Column(Float)

    Operations = relationship('Operation', backref='Wallet', cascade='all, delete-orphan')

class Notification(Base):
    __tablename__ = 'Notifications'

    id = Column(String, primary_key=True, unique=True)
    text = Column(String)


class Operation(Base):
    __tablename__ = 'Operations'

    id = Column(String, primary_key=True, unique=True)

    Name = Column(String)
    CoinAddress = Column(String)
    BuyPrice = Column(Float)
    SellPrice = Column(Float)
    Value = Column(Float)
    TimeStamp = Column(Integer)


    Operation_Id = Column(String, ForeignKey('Wallets.id'))




Base.metadata.create_all(engine)
