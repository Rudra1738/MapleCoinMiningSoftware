"""
Property of Maple Coin, Open source. 
To use any snippets of code or the entire script, you must mention appropriate credits for said script.
Developed by: Rudra Rupani, rudrarupani@maple-coin.com

///////////////////////////

Maple Coin Mining Software

//////////////////////////

"""



"""
Boiler Plate stuff 
"""

import hashlib, datetime, json, copy, os, pathlib, random, threading
import psutil, pebble, rsa, MapleTk, requests
from baseClasses import *

nonceStartBounds = (0, 10000000)
#global miner address
minerAddress = None

"""
End Boiler Plate stuff
"""



"""

Network

"""
class Network():
    """
    Network Class to handle all the network operations
    response can either be said response in comments or error
    """
    
    #Initializer Attributes
    networkSite = "http://maple-coin.com/"                              #For Deployement
    #networkSite = 'http://127.0.0.1:8000/'                             #For local server testing
    session = requests.sessions.Session()
    minuteCheck = 3

    @staticmethod
    def url(extension):
        """
        Gets the url with extentsion
        returns string (url)
        """

        return Network.networkSite + extension

    @staticmethod
    def post(extension, data):
        """
        Posts given data to said url with extension
        returns response
        """

        return Network.session.post(Network.url(extension), data)
    
    @staticmethod
    def get(extension):
        """
        Gets data from said url with extension
        returns response
        """

        return Network.session.get(Network.url(extension))

    @staticmethod
    def minerLogin(username, password):
        """
        Logs in using given username and password, sets global miner address
        returns response (minerAddress)
        """

        global minerAddress
        minerAddress = Network.post("minerLogin", {
            "username": username, 
            "password": password
        }).text

        return minerAddress

    @staticmethod
    def uploadBlock(data):
        """
        Uploads block to network using given data
        returns response (OK or BAD)
        """

        return Network.post("uploadBlock", data).text

    @staticmethod
    def getTransactions():
        """
        Gets all transactions from network
        returns response (dict of transactions)
        """
        return eval(Network.get("getTransactions").text)

    @staticmethod
    def getBlockChain():
        """
        Gets the blockchain from network
        returns response (dict of blockchain)
        """

        return eval(Network.get("getBlockChain").text)

    @staticmethod
    def newBlockInfo():
        """
        Gets data about the new block from network
        returns response (dict of new block info)
        """
        return eval(Network.get("getInfoForNewBlock").text)

    @staticmethod 
    def getPendingTransactions():
        """
        Gets the pending transactions in the network from the network
        returns response
        """
        return eval(Network.get("getPendingTransactions").text)

    @staticmethod
    def currentBlockSearchIndex():
        """
        Gets the current block's index (which is being searched)
        returns index
        """
        
        return int(Network.get('currentBlockSearchIndex').text)

    @staticmethod
    def newTransactions():
        """
        Parses pending transactions from network to Transaction Objects
        returns a list of transaction Objects
        """
        return [
            Transaction(
                transaction,
                data["sender"],
                data["reciever"],
                data["timeOfTransaction"],
                data["amount"],
                Network.post("getSignature", {"id": transaction}).content,
                data["publicKey"],
                data["exponent"]
            )

            for transaction, data in Network.getPendingTransactions().items()
        ]



"""

Miner

"""

class Miner(Network):
    """
    This class constructs the Miner object, where all the mining related stuff resides
    This object gets all the required data, constructs blocks and then mines for the nonce of said block
    It returns said block once mined
    """

    def __init__(self):
        """
        Initializing all the required data for Mining; Note that it does not have any dependencies on arguments and dereives
        the needed data solely from the Network class's static methods, due to this the object is pickle safe and can be used 
        in multiprocessing and multithreading more easily without needing any janky workarounds
        """

        #Getting Pending Transactions and all the needed info for the new block and parsing it
        self.pendingTransactions = Network.newTransactions()
        newBlockInfo = Network.newBlockInfo()
        self.previousBlockHash = newBlockInfo["previousBlockHash"]
        self.newBlockIndex = newBlockInfo["id"]
        self.hashPuzzle = newBlockInfo["hashPuzzle"]
        self.maxTransactions = newBlockInfo["maxTransactions"]

        #Verfiying and validating the transactions to be placed into the block, if transaction is not valid, ignore
        self.getValidTransactions = lambda transactions : [   
                transaction for transaction in transactions
                if rsa.verify(transaction.stringTransactions().encode('utf8'), transaction.signature, rsa.PublicKey(int(transaction.publicKey), int(transaction.exponent)))
        ]

        #Adhereing to the limit of transactions per block
        self.transactions = self.getValidTransactions(self.pendingTransactions)[0:self.maxTransactions]

        #Future block attribute
        self.block = None

    def calculateHash(self):
        """
        This instance method calulates the hash of the given block
        """

        #Forms the string represtation of the block according to Maple Coin Standard Specfications
        self.block.time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        stringBlock = (
            str(self.block.time) + 
            self.block.merkelRoot + 
            (self.block.previousBlockHash if self.block.previousBlockHash != "None" else "") + 
            str(self.block.newBlockIndex) + 
            str(self.block.nonce)
        )

        #Hashes the string block and returns it
        return hashlib.sha3_512(stringBlock.encode('utf8')).hexdigest()

    def mine(self):
        """
        This instance method is the mining algorithm for Maple Coin Blocks 
        It starts at a random nonce, and keeps incrementing from there
        Calculates hash for each said nonce, if hash meets the hash puzzle, it stops, else repeats
        Every said minutes, it checks if a block has already been discovered, if so it stops, else continues
        """

        #setting time to check for block discovery
        startTime, check= datetime.datetime.now(), False

        #setting initial block nonce and hash
        self.block.nonce = random.randint(*nonceStartBounds)
        self.block.hash = self.calculateHash()
        
        #while the hash puzzle is not solved
        while self.block.hash[0:len(self.hashPuzzle)] != self.hashPuzzle:

            #checking for block discovery once every said minutes
            if ((datetime.datetime.now().minute - startTime.minute) % Network.minuteCheck) == 0:    
                if not check:
                    if self.currentBlockSearchIndex() > int(self.block.newBlockIndex):
                        break
                check = True
            else:
                check = False

            #increment nonce and caculate new hash
            self.block.nonce += 1
            self.block.hash = self.calculateHash()

    def mineBlock(self):
        """
        This instance method constructs a block from precompiled data and then mines for it's nonce
        """

        #Construct block and mine nonce
        self.block = Block(self.transactions, self.newBlockIndex, self.previousBlockHash)
        self.mine()



"""

Interface

"""

class Interface(Network):
    """
    This class constructs the Interface Object which is built upon foundations provided by MapleTk
    It runs on the main thread of the python interpreter

    Warning: DO NOT CALL MAINLOOP INSIDE INITIALIZER OR ANYWHERE ELSE EXCEPT __name__ == __main__
    Failing to do so may spawn in infinite Tk windows, freeze said window(s) or crash the interpreter

    Warning: DO NOT SET AUTOUPDATER ON DURING DEPLOYMENT
    Failing to do so may ruin the interface and user experience
    """

    def __init__(self, jsonPath, autoUpdater=False):
        """
        Initializing MapleTk, The Tkinter API that the entire interface is built on.
        Intializing required attributes for the interface
        """

        #MapleTk
        self.interface = MapleTk.intializer(jsonPath=jsonPath)
        self.interface.initialize()
        #AutoUpdater to be used only in developement, not deployment
        if autoUpdater:
            MapleTk.autoUpdater(jsonPath, self.interface).jsonFileUpdateEventListener(refreshRate= autoUpdater)

    
        #For easier access to interface class and objects
        self.interfaceClass = self.interface.masterData["Interface"]
        self.interfaceObjects = self.interface.masterData["Interface"].rootDictionary
        
        #initializing font and assigning login button
        self.fontInit()
        self.interfaceObjects["Button"]["loginButton"].config(command= self.login)

        #initializing other stuff
        self.cpusInterface = {}


    """
    Helper Funcs
    """
    def fontInit(self):
        """
        This instance method initializes the fonts for all the widgets
        """

        #initializing widget fonts
        self.interfaceObjects["Label"]["loginTitle"].config(font=("TimesNewRoman", 50))
        self.interfaceObjects["Label"]["usernameLabel"].config(font=("TimesNewRoman", 18))
        self.interfaceObjects["Entry"]["usernameInput"].config(font=("TimesNewRoman", 18))
        self.interfaceObjects["Entry"]["passwordInput"].config(font=("TimesNewRoman", 18), show= "●")
        self.interfaceObjects["Label"]["passwordLabel"].config(font=("TimesNewRoman", 18))
        self.interfaceObjects["Label"]["errorLabel"].config(font=("TimesNewRoman", 23))
        self.interfaceObjects["Button"]["loginButton"].config(font=("TimesNewRoman", 23))
        self.interfaceObjects["Label"]["welcomeLabel"].config(font=("TimesNewRoman", 27))
        self.interfaceObjects["Label"]["mineBlocksLabel"].config(font=("TimesNewRoman", 16))
        self.interfaceObjects["Label"]["mineBlocksRejectLabel"].config(font=("TimesNewRoman", 16))
        self.interfaceObjects["Label"]["transactionsLabel"].config(font=("TimesNewRoman", 23))
        self.interfaceObjects["Label"]["blockChainLabel"].config(font=("TimesNewRoman", 23))
        self.interfaceObjects["Listbox"]["transactions"].config(font=("TimesNewRoman", 16))
        self.interfaceObjects["Listbox"]["blockChain"].config(font=("TimesNewRoman", 16))

    def cpusInit(self):
        """
        This instnace mehtod intializes the CPU interface
        """

        #Getting the cpu count for the given device
        cpus = os.cpu_count()

        #calculating and setting sizes for each cpu interface block according to the amount of cpu
        sizeCalc, startCalc= lambda x : 20 if x <= 8 else 18 if x <= 16 else 12, lambda x: 0.04 if x <= 8 else 0.011
        size, start = sizeCalc(cpus), startCalc(cpus)

        #for all cpus
        for i in range(cpus):

            #Initialize containers for a CPU label, a button to control said CPU and result label to display the results from said CPU
            self.interfaceObjects["Label"]["cpu" + str(i)], self.interfaceObjects["Button"]["cpu" + str(i)], self.interfaceObjects["Label"]["result" + str(i)] = None, None, None
            label, button, result= self.interfaceObjects["Label"]["cpu" + str(i)], self.interfaceObjects["Button"]["cpu" + str(i)], self.interfaceObjects["Label"]["result" + str(i)]

            #Initialize the objects said above and placing them in their respective containers
            label = MapleTk.Label(master=self.interfaceObjects["LabelFrame"]["CPUFrame"], text= "CPU " + str(i) + ": ", bg= "#e7b309", font=("TimesNewRoman", size))
            button = MapleTk.Button(master=self.interfaceObjects["LabelFrame"]["CPUFrame"], text= "Unavailable")
            result = MapleTk.Label(master=self.interfaceObjects["LabelFrame"]["CPUFrame"], text= "Not Started", bg= "grey", font=("TimesNewRoman", size))

            #Giving easy reference to said objects for future
            self.cpusInterface[i] = {"Label": label, "Button": button, "result": result}

            #Place CPU interface objects
            label.place(relx= 0.02, rely= start + (i/cpus))
            button.place(relx= 0.32, rely= start + (i/cpus))
            result.place(relx= 0.65, rely= start + (i/cpus))

    def initializeMining(self):
        """
        This instance method creates a seperate thread and initializes the Mining Handler object onto the said thread
        to avoid freezing of the interface during operation and mining
        """
        
        #Creating a new thread with target Mining Handler and starting it
        thread = threading.Thread(target=MiningHandler, args=[
            self.cpusInterface, 
            minerAddress, 
            self.interfaceObjects["Button"]["refreshCPUs"], 
            self.interfaceObjects["Label"]["mineBlocksLabel"],
            self.interfaceObjects["Label"]["mineBlocksRejectLabel"]
        ])
        thread.start()
    
    def resetListBox(self, listBox):
        listboxSize = listBox.size()
        for i in range(listboxSize):
            listBox.delete(i)

    def renderTransactionsBox(self):
        """
        This instance method gets all the transactions from the network and 
        displays them to the user in the interface
        """

        #Getting the transactions and reversing them to see the latest ones first
        transactions = dict(list(self.getTransactions().items())[::-1])
        
        #Deleting all Enteries in the list box (Resetting)
        self.resetListBox(self.interfaceObjects["Listbox"]["transactions"])

        #Displaying transaction data
        i = 1
        self.interfaceObjects["Listbox"]["transactions"].insert(0, '  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ')
        for c in transactions:

            transaction = transactions[c]
            itemsToInsert = (
                f'  Index: {c}',
                f'  Sender: {transaction["sender"]}',
                f'  Reciever: {transaction["reciever"]}',
                f'  Amount: {transaction["amount"]};        Time Of Transaction: {transaction["timeOfTransaction"]}',
                f'  Public Key: {transaction["publicKey"]};         Exponent: {transaction["exponent"]}',
                '  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- '
            )

            #inserting each line into list box
            for item in itemsToInsert:
                self.interfaceObjects["Listbox"]["transactions"].insert(i, item)
                i +=1
    
    def renderBlockChainBox(self):
        """
        This instance method gets the block chain from the network and 
        displays them to the user in the interface
        """

        #Getting the blockchain and then reversing it to see the latest blocks first
        blockChain = dict(list(self.getBlockChain().items())[::-1])
    
        #Deleting all Enteries in the list box (Resetting)
        self.resetListBox(self.interfaceObjects["Listbox"]["blockChain"])

        #Displaying the blockchain
        i = 1 
        self.interfaceObjects["Listbox"]["blockChain"].insert(0, '  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ')
        for c in blockChain:

            block = blockChain[c]
            itemsToInsert = (
                f'  Index: {c}',
                f'  Previous Block Hash: {block["previousBlockHash"]}',
                f'  Merkel Root: {block["merkelRoot"]};',
                f'  Nonce: {block["nonce"]};        Block Time: {block["blockTime"]}',
                f'  Block Hash: {block["blockHash"]}',
                f'  Miner: {block["miner"]}',
                '  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- '
            )

            #inserting each line into the list box
            for item in itemsToInsert:
                self.interfaceObjects["Listbox"]["blockChain"].insert(i, item)
                i +=1   

    """
    Helper Funcs end
    """

    def showMiningScreen(self):
        """
        This instance method displays the mining screen to the user
        and allows user to mine and read data
        """
        
        #Destroy login frame and make the screen big
        self.interfaceObjects["LabelFrame"]["loginFrame"].destroy()
        self.interfaceObjects["Master"].geometry("1700x1000")

        #Show the Mining Screen Widgets
        widgetsToShow = ("navigationFrame", "welcomeLabel", "transactionsLabel", "mineBlocksLabel", "blockChainLabel", "transactions", "blockChain", "mineBlocksRejectLabel", "CPUFrame", "refreshCPUs", "refreshData")
        for widget in widgetsToShow:
            self.interfaceClass.screenData[widget]["display"] = "True"
            self.interfaceClass.renderWidget(widget)

        #Bugged in Tk, will fix with a workaround in the future
        self.interfaceObjects["Button"]["refreshData"].config(state= MapleTk.DISABLED)

        #Render in the transactions box and Block Chain box
        self.renderTransactionsBox()
        self.renderBlockChainBox()

        #Initialize the Mining Handler(Seperate Thread) and the CPU interface
        self.cpusInit()
        self.initializeMining()
    
    def login(self):
        """
        This instance method displays the login screen to the user
        and allows user to log in
        """

        #Get the username and password
        username = self.interfaceObjects["Entry"]["usernameInput"].get()
        password = self.interfaceObjects["Entry"]["passwordInput"].get()

        #Log into the network and get response
        response = Network.minerLogin(username, password)

        #if user is valid then show the show the mining screen
        if response != "BAD":
            try:
                self.interfaceObjects["Label"]["errorLabel"].destroy()
            except: 
                ""
            self.showMiningScreen()

        #No user found (user enter invalid credential methods)
        else:
            self.interfaceObjects["Label"]["errorLabel"].place(relx= 0.422, rely= 0.8)



"""
Critical Gobal Function to allow for safe pickling and multiprocessing
"""

def mine(minerAddress, cpuid):
    """
    This is a critical gobal function, proceed with care and do not modify anything unless familiar with
    pickling in multiprocessing and multiprocessing, multithreading in general

    This function does the necessary steps for mining outside cpu object for each process and is safe

    Uploads block to network and returns response to schedule/submit process callback 
    (schedule for pebble.ProcessPool or submit for concurrents.futures.ProcessPoolExecutor/Mutliprocessing process pool and its said executors)
    """

    #Intialize the pickle safe and multiprocessing safe miner object
    miner = Miner()

    #Mine the block of the miner object for its nonce
    miner.mineBlock()

    #get the block and assign it miner from global of the thread on which Mining Handler object is runnning
    block = miner.block
    block.miner = minerAddress
    
    #Upload the block with the necessary data from block object
    return Network.uploadBlock({
        "index": block.newBlockIndex,
        "previousBlockHash": block.previousBlockHash,
        "transactions": str([transaction.id for transaction in block.transactions]),
        "merkelRoot": block.merkelRoot,
        "nonce": block.nonce,
        "hash": block.hash,
        "miner": block.miner,
        "time": block.time
    })

"""
Critical Gobal Function End 
"""



"""

Mining Handler and CPU

"""

class cpu(Network):
    """
    This class constructs a cpu object which handles the mining process, updating the mining handler
    and handles the interface
    """

    def __init__(self):
        """
        Initializer attributes
        """

        #Intializer attributes
        self.id = None

        self._state = None
        self._active = False 
        self._status = None
        self.process= None

        self._interfaceObject = None
        self.blocksMined = None

    def updateInterface(self):
        """
        This instance method updates the interface according to the current instance attributes
        """

        #If Button is not disabled
        if self._state is not None:
            self._interfaceObject["Button"].config(text= "Mine", state= "normal")
            self._interfaceObject["Button"].place(relx= 0.32)

            #If button is active
            if self._active == True:
                self._interfaceObject["Button"].config(text= "Kill", command= lambda : MiningHandler.killCPU(self.id), padx= 25, pady= 3)
                self._interfaceObject["Label"].config(bg= "green")
                self._interfaceObject["result"].config(text="Mining.....", bg= "#e7b309")

            #If button is Inactive
            elif self._active == False: 
                self._interfaceObject["Button"].config(text= "Mine", command= lambda : MiningHandler.mine(self.id), padx= 20, pady= 3)
                self._interfaceObject["Label"].config(bg= "#e7b309")

                #If the CPU has been used for mining atleast once
                if self.blocksMined is not None:

                    #show mined blocks by said cpu
                    if self.blocksMined > 0:
                        self._interfaceObject["result"].config(text="Mined: " + str(self.blocksMined), bg= "green")
                    else:
                        self._interfaceObject["result"].config(text="Mined: " + str(0), bg= "red")
                
                #CPU has not been used for mining even once
                else:
                    self._interfaceObject["result"].config(text="Not Started", bg= "grey")

        #Button is disabled
        else:
            self._interfaceObject["Button"].config(text= "Unavailable", padx= 0, pady= 3)
            self._interfaceObject["Button"].config(state= MapleTk.DISABLED)
            self._interfaceObject["result"].config(text= "Unavailabe", bg= "grey")
            self._active = False
            self._status = None

       

    def callBack(self, fn):
        """
        This is the callback method that the mining process calls when its Either:
            1: Done mining
                i: Block Accepted
                ii: Block Rejected
            2: Block already discovered
            3: Process Killed by user
        """

        #If the process was not killed by the user
        if not fn.cancelled():

            #Set the self status to result and update the interface accordingly
            self._status = fn.result()

            #Update interface according to status
            if self._status == "OK":
                self.blocksMined +=1
                MiningHandler.blocksMined +=1
                blocksMinedLabel.config(text= "Blocks Mined in current session: " + str(MiningHandler.blocksMined))

            else:
                MiningHandler.blocksRejected +=1
                blocksRejectedLabel.config(text= "Blocks Rejected in current session: " + str(MiningHandler.blocksRejected))

            #for every cpu in mining handler
            for cpuid in MiningHandler.cpus.keys():
                currentCpu = MiningHandler.cpus[cpuid]

                #Resart mining for every CPU as it is already known that block found
                if currentCpu.state is not None and currentCpu.active == True:
                    MiningHandler.killCPU(cpuid)
                    MiningHandler.mine(cpuid)

            #update the interface after everything is done
            self.updateInterface()

    def mineBlock(self, minerAddress):
        """
        This instance method schedules/submits a process to mine a block if there is no ongoing process already 
        schedule for pebble.ProcessPoolExecutor or submit for concurrent.futures.ProcessPoolExecutor
        """ 

        #Starting to use CPU for mining
        if self.blocksMined is None:
            self.blocksMined = 0

        #Start a mining process if there is no ongoing process already
        if self.process is None:

            #CPU is active, update interface
            self._active = True
            self.updateInterface()

            #Start the mining process (schedule/submit it) and then add a done callback to it to recieve result asynchronously
            self.process= MiningHandler.executor.schedule(mine, args=[minerAddress, self.id])
            self.process.add_done_callback(self.callBack)

    def kill(self):
        """
        This instance method kills the ongoing process in the CPU if there is one
        """

        #If there's an ongoing process, kill it and update interface
        if self.process is not None:
            self.process.cancel()
            self.process = None
            self._active = False
            self._status = None
            self.updateInterface()

    #read state
    @property
    def state(self):
        return self._state

    #write state, update interface
    @state.setter
    def state(self, value):
        self._state = value
        self.updateInterface()

    #read cpu activity
    @property
    def active(self):
        return self._active

    #write cpu activity, update interface
    @active.setter
    def active(self, value):
        self._active = value
        self.updateInterface()

    #read interface objects
    @property
    def interfaceObject(self):
        return self._interfaceObject
    
    #Set interface object, intialize it, update interface
    @interfaceObject.setter
    def interfaceObject(self, value):
        self._interfaceObject = value
        self._interfaceObject["Button"].config(command= lambda: MiningHandler.mine(self.id))
        self.updateInterface()
    
    #status read
    @property
    def status(self):
        return self._status

    #status write, update interface
    @status.setter
    def status(self, value):
        self._status = value
        self.updateInterface()

class MiningHandler(Network):
    """
    This class creates a Mining Handler Object which handles the CPU objects, assigns critical gobals
    and provides static methods for cpus to communicate with each other and stay in sync all the time

    Warning: This is a critical class, do not modiy it unless familiar with pickling, multiprocessing
    and multithreading
    """

    #Make the CPU objects and the process pool executor object
    cpuCount = os.cpu_count()
    cpus = {i: cpu() for i in range(cpuCount)}
    executor = pebble.ProcessPool()

    #class attributes for all cpus to report to
    blocksMined = 0
    blocksRejected = 0

    def __init__(self, interfaceObjects, minerAddressin, cpuButton, mineLabel, rejectLabel, interval= 1):
        """
        Initializer for Mining Handler Object
        Declare critical globals, assign each cpu objects its respective attributes, 
        ensure cpu availibility and other stuff
        """
        #Button for refresh cpu availibility and interval for cpu percent list
        self.cpuButton, self.interval = cpuButton, interval

        #declaring critical gobals to be used by all the cpus, to report to and stay in sync with
        global minerAddress, blocksMinedLabel, blocksRejectedLabel
        minerAddress = minerAddressin
        blocksMinedLabel = mineLabel
        blocksRejectedLabel = rejectLabel

        #Assigning each CPU object its respective attributes
        for i, cpu in self.cpus.items():
            cpu.interfaceObject, cpu.id, cpu.executor= interfaceObjects[i], i, self.executor

        #Check for CPU availibility
        self.refreshCpuAvailibility()
        
        cpuButton.config(command= self.refreshCpuAvailibility)
 
    def refreshCpuAvailibility(self):
        """
        This instance method checks for CPU availibility and assigns each cpu its availibility attribute respectively
        """

        #Kill all CPUs whose processes are from this script to get accurate readings
        for i in self.cpus.keys():
            self.killCPU(i)
        
        #Get CPU percent list using psutil percent list
        cpuPercentList = self.cpuPercentList

        #for each cpu
        for i, cpu in self.cpus.items():
            #disable cpu if its usage is more than 50% (incapable for efficient mining)
            cpu.state, cpu.active = None if cpuPercentList[i] > 50 else True, False

    @staticmethod
    def mine(cpuid):
        """
        This static method is to provide a consisently synced way for CPUs to call their mining methods
        """

        #Mine
        MiningHandler.cpus[cpuid].mineBlock(minerAddress)
 
    @staticmethod
    def killCPU(cpuid):
        """
        This static method is to provide a consistently synced way for CPUs to kill their processes
        """

        #Kill
        MiningHandler.cpus[cpuid].kill()

    #CPU percent list from psutil
    @property
    def cpuPercentList(self):
        return psutil.cpu_percent(interval= self.interval, percpu= True)



if __name__ == "__main__":
    """
    Main

    Warning: Do not initiaize interface anywhere else, The new spawned thread and its processes
    will spawn in more Tk windows
    """
    
    #Interface and mainloop
    Interface(
        jsonPath= str(pathlib.Path(__file__).parent.absolute()) + os.sep + "screenData.json"
    )
    MapleTk.mainloop()



"""

End

"""