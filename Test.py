import uuid



from DB import *

def CheckDB():
    Session = sessionmaker(bind=engine)
    session = Session()

    addresses = session.query(Wallet).all()

    for i in addresses:
        print(i.PrivateKey)

    session.close()

def AddWallet(address, private):

    Session = sessionmaker(bind=engine)
    session = Session()

    wallet = Wallet(id=str(uuid.uuid4()),
            PrivateKey=private,
            Address=address,
            Status='Ready')

    session.add(wallet)
    session.commit()
    session.close()
CheckDB()






