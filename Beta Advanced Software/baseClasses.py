import hashlib

class Block():

    def __init__(self, transactions, index, previousBlockHash):
        self.newBlockIndex = index
        self.transactions = transactions
        self.previousBlockHash = previousBlockHash
        self.nonce = None
        self.hash = None
        self.merkelRoot = (
            self.getMerkelRoot(self.transactions) if len(self.transactions) > 1 
            else (hashlib.sha3_512(str(self.transactions[0]).encode('utf8')).hexdigest() if len(self.transactions) == 1 
            else "")
        )
        self.miner = None
    
    @staticmethod
    def getMerkelRoot(items):
        if len(items) == 1:
            return items[0]

        items = [hashlib.sha3_512(str(item).encode('utf8')).hexdigest() for item in items]
        newItems, temp = [], ""
        for index in range(len(items)):
            if index % 2 == 0:
                temp = items[index]
            else:
                newItems.append(temp + items[index])
                temp = ""
        return Block.getMerkelRoot(newItems)
    
    def __eq__(self, other):
        return isinstance(other, type(self)) and self.newBlockIndex == other.newBlockIndex and self.transactions == other.transactions and all([self.transactions[index] == other.transactions[index] for index in range(len(self.transactions))]) and self.nonce == other.nonce and self.hash == other.hash and self.merkelRoot == other.merkelRoot

class Transaction():
    
    def __init__(self, tid, sender, reciever, time, amount, signature, publicKey, exponent):
        self.id = tid
        self.sender = sender
        self.reciever = reciever
        self.amount = str(amount)
        self.timeOfTransaction = time
        self.signature = signature
        self.publicKey = publicKey
        self.exponent = exponent
        self.stringTransactions = lambda : self.sender + self.reciever + str(self.amount) + str(self.timeOfTransaction)

    def readText(self):
        return f'Sender: {self.sender}; Reciever: {self.reciever}; Amount: {self.amount}; Time: {self.timeOfTransaction}'

    def __repr__(self):
        return self.stringTransactions()

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.sender == other.sender and self.reciever == other.reciever and self.amount == other.amount and self.timeOfTransaction == other.timeOfTransaction and self.signature == other.signature