"""
Property of Maple Coin, Open source. 
To use any snippets of code or the entire script, you must mention appropriate credits for said script.

///////////////////////////

Maple Coin Mining Software

//////////////////////////

"""

import hashlib, datetime, rsa, json, copy, requests, MapleTk, os, pathlib, random
from baseClasses import *

class Miner():

    def __init__(self, previousBlockHash, newBlockIndex, hashPuzzle, pendingTransactions, minerAddress, maxTransactions = 200):
        
        self.pendingTransactions = pendingTransactions
        self.previousBlockHash = previousBlockHash
        self.newBlockIndex = newBlockIndex
        self.hashPuzzle = hashPuzzle

        self.maxTransactions = maxTransactions

        self.minerAddress = minerAddress

        self.getValidTransactions = lambda transactions : [   
                transaction for transaction in transactions
                if rsa.verify(transaction.stringTransactions().encode('utf8'), transaction.signature, rsa.PublicKey(int(transaction.publicKey), int(transaction.exponent)))
        ]
        self.transactions = self.getValidTransactions(self.pendingTransactions)[0:maxTransactions]
        self.block = None

    def calculateHash(self, block):
        block.time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        stringTransactions = (
            str(block.time) + 
            block.merkelRoot + 
            (block.previousBlockHash if block.previousBlockHash != "None" else "") + 
            str(block.newBlockIndex) + 
            str(block.nonce)
        )
        return hashlib.sha3_512(stringTransactions.encode('utf8')).hexdigest()

    def mine(self, block, hashPuzzle):
        startTime, check= datetime.datetime.now(), False
        block.nonce = random.randint(0, 10000000)
        block.hash = self.calculateHash(block)
        while block.hash[0:len(hashPuzzle)] != hashPuzzle:
            if ((datetime.datetime.now().minute - startTime.minute) % 5) == 0:         
                if not check:
                    if int(session.get(url('currentBlockSearchIndex')).text) > int(self.block.newBlockIndex):
                        break
                check = True
            else:
                check = False

            block.nonce += 1
            block.hash = self.calculateHash(block)

    def mineBlock(self):
        self.block = Block(self.transactions, self.newBlockIndex, self.previousBlockHash)
        self.mine(self.block, self.hashPuzzle)

        self.block.miner = self.minerAddress
        return self.block

class Interface():

    def __init__(self, jsonPath, autoUpdater=False):
        self.miner = None
        self.minerAddress = None
        self.userName = None

        self.interface = MapleTk.intializer(jsonPath=jsonPath)
        self.interface.initialize()
        if autoUpdater:
            MapleTk.autoUpdater(jsonPath, self.interface).jsonFileUpdateEventListener(refreshRate= autoUpdater)

        self.navObjects = self.interface.masterData["Nav"].rootDictionary
        self.fontInit()
        self.assignButtons()

        self.blocksMinedInSession = 0

        MapleTk.mainloop()

    def fontInit(self):
        self.navObjects["Label"]["loginTitle"].config(font=("TimesNewRoman", 50))
        self.navObjects["Label"]["usernameLabel"].config(font=("TimesNewRoman", 18))
        self.navObjects["Entry"]["usernameInput"].config(font=("TimesNewRoman", 18))
        self.navObjects["Entry"]["passwordInput"].config(font=("TimesNewRoman", 18))
        self.navObjects["Label"]["passwordLabel"].config(font=("TimesNewRoman", 18))
        self.navObjects["Label"]["errorLabel"].config(font=("TimesNewRoman", 23))
        self.navObjects["Button"]["loginButton"].config(font=("TimesNewRoman", 23))
        self.navObjects["Button"]["mineButton"].config(font=("TimesNewRoman", 18))
        self.navObjects["Button"]["autoMineButton"].config(font=("TimesNewRoman", 18))
        self.navObjects["Label"]["welcomeLabel"].config(font=("TimesNewRoman", 17)) #from 23
        self.navObjects["Label"]["successLabel"].config(font=("TimesNewRoman", 18))
        self.navObjects["Label"]["mineBlocksLabel"].config(font=("TimesNewRoman", 13)) #from 15
        self.navObjects["Label"]["transactionsLabel"].config(font=("TimesNewRoman", 23))
        self.navObjects["Label"]["blockChainLabel"].config(font=("TimesNewRoman", 23))
        self.navObjects["Listbox"]["transactions"].config(font=("TimesNewRoman", 16))
        self.navObjects["Listbox"]["blockChain"].config(font=("TimesNewRoman", 16))
        self.navObjects["Label"]["autoMineLabel"].config(font=("TimesNewRoman", 13)) #from 15
        self.navObjects["Entry"]["autoMineHours"].config(font=("TimesNewRoman", 15))
    
    def showMiningPage(self):
        self.navObjects["LabelFrame"]["loginFrame"].destroy()
        self.navObjects["Master"].geometry("1300x700")
        self.navObjects["LabelFrame"]["navigationFrame"].place(relx= 0, rely= 0)
        self.navObjects["Button"]["mineButton"].place(relx= 0.14, rely= 0.4) #from x=0.22
        self.navObjects["Label"]["autoMineLabel"].place(relx= 0.03, rely= 0.25) #from x=0.05
        self.navObjects["Entry"]["autoMineHours"].place(relx= 0.48, rely= 0.248) #from x= 0.53
        self.navObjects["Entry"]["autoMineHours"].insert(0, 1)
        self.navObjects["Button"]["autoMineButton"].place(relx= 0.18, rely= 0.29) #from x=0.24
        self.navObjects["Label"]["welcomeLabel"].place(relx= 0.05, rely= 0.02)
        self.navObjects["Label"]["transactionsLabel"].place(relx= 0.223, rely= 0.03)
        self.navObjects["Label"]["mineBlocksLabel"].place(relx= 0.04, rely= 0.53)
        self.navObjects["Label"]["blockChainLabel"].place(relx= 0.223, rely= 0.53)
        self.navObjects["Listbox"]["transactions"].place(relx= 0.225, rely= 0.09)
        self.navObjects["Listbox"]["blockChain"].place(relx= 0.225, rely= 0.59)

    def assignButtons(self):
        self.navObjects["Button"]["loginButton"].config(command= self.getMinerAddress)
        self.navObjects["Button"]["mineButton"].config(command= self.mineBlock)
        self.navObjects["Button"]["autoMineButton"].config(command= self.autoMine)


    def renderTransactionsBox(self):
        transactions =  eval(session.get(url("getTransactions")).text)
        for i, c in enumerate(transactions):
            try:
                self.navObjects["Listbox"]["transactions"].delete(i)
            except:
                continue
            transaction = transactions[c]
            self.navObjects["Listbox"]["transactions"].insert(i, f'  Index: {c};     Sender: {transaction["sender"]};    Reciever: {transaction["reciever"]};    Amount: {transaction["amount"]};    Time Of Transaction: {transaction["timeOfTransaction"]};    Public Key: {transaction["publicKey"]};     Exponent: {transaction["exponent"]}')

    def renderBlockChainBox(self):
        blockChain = eval(session.get(url("getBlockChain")).text)
        for i, c in enumerate(blockChain):
            try:
                self.navObjects["Listbox"]["blockChain"].delete(i)
            except:
                continue
            block = blockChain[c]
            self.navObjects["Listbox"]["blockChain"].insert(i, f'    Index: {c};     Previous Block Hash: {block["previousBlockHash"]};      Merkel Root: {block["merkelRoot"]};     nonce: {block["nonce"]};       Block Hash: {block["blockHash"]};    Block Time: {block["blockTime"]};      Miner: {block["miner"]}')

    
    def getMinerAddress(self):
        self.userName = self.navObjects["Entry"]["usernameInput"].get()

        self.minerAddress = session.post(url("minerLogin"), {
            "username": self.userName, 
            "password": self.navObjects["Entry"]["passwordInput"].get()
        }).text

        if self.minerAddress != "BAD":
            try:
                self.navObjects["Label"]["errorLabel"].destroy()
            except: 
                ""
            self.showMiningPage()
            self.navObjects["Label"]["welcomeLabel"].config(text= f"Welcome, {self.userName}!")
            self.renderTransactionsBox()
            self.renderBlockChainBox()
        else:
            self.navObjects["Label"]["errorLabel"].place(relx= 0.422, rely= 0.8)

    def mineBlock(self):
        self.navObjects["Master"].iconify()

        pendingTransactions = eval(session.get(url("getPendingTransactions")).text)

        newBlockInfo = eval(session.get(url("getInfoForNewBlock")).text)

        newTransactions = [
            Transaction(
                transaction,
                pendingTransactions[transaction]["sender"],
                pendingTransactions[transaction]["reciever"],
                pendingTransactions[transaction]["timeOfTransaction"],
                pendingTransactions[transaction]["amount"],
                session.post(url("getSignature"), {"id": transaction}).content,
                pendingTransactions[transaction]["publicKey"],
                pendingTransactions[transaction]["exponent"]
            )

            for transaction in pendingTransactions.keys()
        ]
        self.miner = Miner(newBlockInfo["previousBlockHash"], newBlockInfo["id"], newBlockInfo["hashPuzzle"], newTransactions, self.minerAddress, newBlockInfo["maxTransactions"])
        self.miner.mineBlock()
        block = self.miner.block

        networkResponse = session.post(url("uploadBlock"), {
            "index": block.newBlockIndex,
            "previousBlockHash": newBlockInfo["previousBlockHash"],
            "transactions": str([transaction.id for transaction in block.transactions]),
            "merkelRoot": block.merkelRoot,
            "nonce": block.nonce,
            "hash": block.hash,
            "miner": block.miner,
            "time": block.time
        }).text

        self.navObjects["Master"].deiconify()
        
        self.renderTransactionsBox()
        self.renderBlockChainBox()

        if networkResponse == "OK":
            self.navObjects["Label"]["successLabel"].place(relx= 0.1, rely= 0.1)
            self.blocksMinedInSession +=1
            self.navObjects["Label"]["mineBlocksLabel"].config(text= ("Blocks mined in current session: " + str(self.blocksMinedInSession)))
        else:
            print(networkResponse)
            self.navObjects["Label"]["successLabel"].place(relx= 0.1, rely= 0.1)
            self.navObjects["Label"]["successLabel"].config(text= "Block Rejected", bg="red")
    
    def autoMine(self):
        startTime = datetime.datetime.now()
        hours = 1
        try: 
            hours = int(self.navObjects["Entry"]["autoMineHours"].get())
        except:
            hours = 1
        while (datetime.datetime.now().hour - startTime.hour) <= hours:
            self.mineBlock()


session = requests.sessions.Session()
networkSite = "http://maple-coin.com/"              #For Deployment and Deployment test runs
#networkSite = 'http://127.0.0.1:8000/'             #Only for local server test runs
url = lambda x : networkSite + x

Interface(
    jsonPath= str(pathlib.Path(__file__).parent.absolute()) + os.sep + "screenData.json"
)
