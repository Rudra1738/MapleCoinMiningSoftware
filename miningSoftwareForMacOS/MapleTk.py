from tkinter import *
from tkinter.ttk import Style
#from PIL import ImageTk, Image
from copy import deepcopy
import json, threading, time
from tkinter import messagebox

def doNothing():
    return


"""
The CNF parameters to be used for each Tk object
"""
cnfParameters = {
    "Master": list(),
    "LabelFrame": ("bg", "bd", "cursor", "font", "height", "labelAnchor", "highlightbackground", "highlightcolor", "highlightthickness", "relief", "text", "width"),
    "Button": ("text", "activebackground", "activeforeground", "bd", "bg", "fg", "font", "height", "highlightcolor", "image", "justify", "padx", "pady", "relief", "state", "underline", "width", "wraplength", "command"),
    "Label": ("anchor", "bg", "bitmap", "bd", "cursor", "font", "fg", "height", "image", "justify", "padx", "pady", "relief", "text", "textvariable", "underline", "width", "wraplength"),
    "Entry": ("bg", "bd", "command", "cursor", "font", "exportselection", "fg", "highlightcolor", "justify", "relief", "selectbackground", "selectborderwidth", "selectforeground", "show", "state", "textvariable", "width", "xscrollcommand"),
    "Radiobutton": ("activebackground", "activeforeground", "anchor", "bg", "bitmap", "borderwidth", "command", "cursor", "font", "fg", "height", "highlightbackground", "highlightcolor", "image", "justify", "padx", "pady", "relief", "selectcolor", "selectimage", "state", "text", "textvariable", "underline", "value", "variable", "width", "wraplength"),
    "Message": ("anchor", "bg", "bitmap", "bd", "cursor", "font", "fg", "height", "image", "justify", "padx", "pady", "relief", "text", "textvariable", "underline", "width", "wraplength"),
    "Canvas": ("bd", "bg", "confine", "cursor", "height", "highlightcolor", "relief", "scrollregion", "width", "xscrollincrement", "xscrollcommand", "yscrollincrement", "yscrollcommand"),
    "Checkbutton": ("activebackground", "activeforeground", "bg", "bitmap", "bd", "command", "cursor", "disabledforeground", "font", "fg", "height", "highlightcolor", "image", "justify", "offvalue", "onvalue", "padx", "pady", "relief", "selectcolor", "selectimage", "state", "text", "underline", "variable", "width", "wraplength"),
    "Listbox": ("bg", "bd", "cursor", "font", "fg", "height", "highlightcolor", "highlightthickness", "relief", "selectbackground", "selectmode", "width", "xscrollcommand", "yscrollcommand"),
    "Menubutton": ("activebackground", "activeforeground", "anchor", "bg", "bitmap", "bd", "cursor", "direction", "disabledforeground", "fg", "height", "highlightcolor", "image", "justify", "menu", "padx", "pady", "relief", "state", "text", "textvariable", "underline", "width", "wraplength"),
    "Menu": ("activebackground", "activeborderwidth", "activeforeground", "bg", "bd", "cursor", "disabledforeground", "font", "fg", "postcommand", "relief", "image", "selectcolor", "tearoff", "title"),
    "Scale": ("activebackground", "bg", "bd", "command", "cursor", "digits", "font", "fg", "from_", "highlightbackground", "highlightcolor", "label", "length", "orient", "relief", "repeatdelay", "resolution", "showvalue", "sliderlength", "state", "takefocus", "tickinterval", "to", "troughcolor", "variable", "width"),
    "Scrollbar": ("activebackground", "bg", "bd", "command", "cursor", "elementborderwidth", "highlightbackground", "highlightcolor", "highlightthickness", "jump", "orient", "repeatdelay", "repeatinterval", "takefocus", "troughcolor", "width"),
    "Text": ("bg", "bd", "cursor", "exportselection", "font", "fg", "height", "highlightbackground", "highlightcolor", "highlightthickness", "insertbackground", "insertborderwidth", "insertofftime", "insertontime", "insertwidth", "padx", "pady", "relief", "selectbackground", "selectborderwidth", "spacing1", "spacing2", "spacing3", "state", "tabs", "width", "wrap", "xscrollcommand", "yscrollcommand"),
    "Spinbox": ("activebackground", "bg", "bd", "command", "cursor", "disabledbackground", "disabledforeground", "fg", "font", "format", "from_", "justify", "relief", "repeatdelay", "repeatinterval", "state", "textvariable", "to", "validate", "validatecommand", "values", "vcmd", "width", "wrap", "xscrollcommand"),
    "PanedWindow": ("bg", "bd", "borderwidth", "cursor", "handlepad", "handlesize", "height", "orient", "relief", "sashcursor", "sashrelief", "sashwidth", "showhandle", "width")
}


class baseWidgetsClass():
    """
    A base class for all widgets, to handle them, to store them and to give easy access.
    This only operates for a single screen
    """

    def __init__(self, allFunctions= dict(), screenData= dict(), masterScreenForTop= None):
        """
        Initialize all the properties and make the master if it exists otherwise use own
        """

        # A datastructure to store all the objects on the master screen
        self.rootDictionary = { 
            "Master": Toplevel,
            "LabelFrame": dict(),
            "Button": dict(),
            "Label": dict(),
            "Entry": dict(),
            "Radiobutton": dict(),
            "Message": dict(),
            "Canvas": dict(),
            "Checkbutton": dict(),
            "Listbox": dict(),
            "Menubutton": dict(),
            "Menu": dict(),
            "Scale": dict(),
            "Scrollbar": dict(),
            "Text": dict(),
            "Spinbox": dict(),
            "PannedWindow": dict()
        }
        self.cnfParameters = cnfParameters
        self.allFunctions = allFunctions
        self.screenData = screenData
        self.masterScreenForTop = masterScreenForTop

        #master handling
        for key, value in screenData.items():
            if key == "Master":
                keys = value.keys()
                try:
                    self.rootDictionary["Master"] = (Toplevel if value["type"] == "TopLevel" else Tk) if "type" in keys and "master" in keys else Tk
                    localType = ("Toplevel" if value["type"] == "TopLevel" else "Tk") if "type" in keys and "master" in keys else "Tk"
                except:
                    self.rootDictionary["Master"] == Tk
                    localType = "Tk"
                if "display" in keys:
                    if value["display"] == "True":
                        self.rootDictionary["Master"] = self.rootDictionary["Master"]() if localType == "Tk" else self.rootDictionary["Master"](master= self.masterScreenForTop)
                        if "title" in keys:
                            self.rootDictionary["Master"].title(value["title"])
                        if "geometry" in keys:
                            self.rootDictionary["Master"].geometry(value["geometry"])
                        if "icon" in keys:
                            self.rootDictionary["Master"].iconbitmap(value["icon"])
                else:
                    self.rootDictionary["Master"] = self.rootDictionary["Master"]() if localType == "Tk" else self.rootDictionary["Master"](master= self.masterScreenForTop)
                    if "title" in keys:
                        self.rootDictionary["Master"].title(value["title"])
                    if "geometry" in keys:
                        self.rootDictionary["Master"].geometry(value["geometry"])
                    if "icon" in keys:
                        self.rootDictionary["Master"].iconbitmap(value["icon"])

                break


    def findWidgetByID(self, widgetID):
        """
        Search the entire datastructure for the widget with the input id and return it
        """

        for typeOfWidgets, widgets in self.rootDictionary.items():
            if typeOfWidgets != "Master":
                for key, widget in widgets.items():
                    if widgetID == key:
                        return widget
        return self.rootDictionary["Master"]


    def defineScreen(self, screenData= None):
        """
        Initialize the screen
        """

        screenData = self.screenData if screenData is None else screenData

        """
        Make and store a widget object for each entry in the screen data according to
        the parameters specified in screen data
        """
        for key, value in screenData.items():

            keys = value.keys()

            masterScreen = self.findWidgetByID(value["master"]) if "master" in keys else self.rootDictionary["Master"]

            if value["type"] == "LabelFrame":

                self.rootDictionary["LabelFrame"][key] = LabelFrame(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items() if cnfKey in self.cnfParameters["LabelFrame"]
                    }
                )

            elif value["type"] == "Button":

                self.rootDictionary["Button"][key] = Button(
                    master= masterScreen,
                    cnf= {
                        cnfKey: (cnfValue if cnfKey != "command" else self.allFunctions[cnfValue] if cnfValue in self.allFunctions.keys() else doNothing)
                        for cnfKey, cnfValue in value.items() if cnfKey in self.cnfParameters["Button"]
                        
                    }
                )

            elif value["type"] == "Label":

                self.rootDictionary["Label"][key] = Label(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Label"]
                    }
                )

            elif value["type"] == "Entry":

                self.rootDictionary["Entry"][key] = Entry(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Entry"]
                    }
                )
            
            elif value["type"] == "Canvas":
                
                self.rootDictionary["Canvas"][key] = Canvas(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Canvas"]
                    }
                )

            elif value["type"] == "Checkbutton":

                self.rootDictionary["Checkbutton"][key] = Checkbutton(
                    master= masterScreen,
                    cnf= {
                        cnfKey: (cnfValue if cnfKey != "command" else self.allFunctions[cnfValue] if cnfValue in self.allFunctions.keys() else doNothing)
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Checkbutton"]
                    }
                )

            elif value["type"] == "Listbox":

                self.rootDictionary["Listbox"][key] = Listbox(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Listbox"]
                    }
                )

            elif value["type"] == "Menubutton":

                self.rootDictionary["Menubutton"][key] = Menubutton(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Menubutton"]
                    }
                )

            elif value["type"] == "Menu":

                self.rootDictionary["Menu"][key] = Menu(
                    master= masterScreen,
                    cnf= {
                        cnfKey: (cnfValue if cnfKey != "command" else self.allFunctions[cnfValue] if cnfValue in self.allFunctions.keys() else doNothing)
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Menu"]
                    }
                )

            elif value["type"] == "Message":

                self.rootDictionary["Message"][key] = Message(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Message"]
                    }
                )

            elif value["type"] == "Canvas":

                self.rootDictionary["Canvas"][key] = Canvas(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Canvas"]
                    }
                )
            
            elif value["type"] == "Checkbutton":

                self.rootDictionary["Checkbutton"][key] = Checkbutton(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Checkbutton"]
                    }
                )

            elif value["type"] == "Listbox":

                self.rootDictionary["Listbox"][key] = Listbox(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Listbox"]
                    }
                )
            
            elif value["type"] == "Menubutton":

                self.rootDictionary["Menubutton"][key] = Menubutton(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Menubutton"]
                    }
                )

            elif value["type"] == "Menu":

                self.rootDictionary["Menu"][key] = Menu(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Menu"]
                    }
                )
            
            elif value["type"] == "Scale":

                self.rootDictionary["Scale"][key] = Scale(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Scale"]
                    }
                )

            elif value["type"] == "Scrollbar":

                self.rootDictionary["Scrollbar"][key] = Scrollbar(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Scrollbar"]
                    }
                )
            
            elif value["type"] == "Text":

                self.rootDictionary["Text"][key] = Text(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Text"]
                    }
                )
            
            elif value["type"] == "Spinbox":

                self.rootDictionary["Spinbox"][key] = Spinbox(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["Spinbox"]
                    }
                )

            elif value["type"] == "PanedWindow":

                self.rootDictionary["PanedWindow"][key] = PanedWindow(
                    master= masterScreen,
                    cnf= {
                        cnfKey: cnfValue 
                        for cnfKey, cnfValue in value.items()  if cnfKey in self.cnfParameters["PanedWindow"]
                    }
                )

        if screenData != self.screenData:
            self.screenData.update(screenData)

    def runStaticScreen(self):
        """
        Run the initial static screen
        """

        #show all the Label Frames
        for key, frame in self.rootDictionary["LabelFrame"].items():
            if "display" in self.screenData[key].keys() and not frame.winfo_ismapped():
                if self.screenData[key]["display"] == "True":
                    if "place" in self.screenData[key].keys():
                        frame.place(relx= self.screenData[key]["place"]["x"], rely= self.screenData[key]["place"]["y"])
                    else:
                        frame.pack()
            else:
                if "place" in self.screenData[key].keys():
                    frame.place(relx= self.screenData[key]["place"]["x"], rely= self.screenData[key]["place"]["y"])
                else:
                    frame.pack()
        
            frame.pack_propagate(self.screenData[key]["propogate"] if "propogate" in self.screenData[key].keys() else 0)
        
        #show all the widgets
        for typeOfWidget, widgetPack in self.rootDictionary.items():
            if typeOfWidget != "LabelFrame" and typeOfWidget != "Master":
                for key, widget in widgetPack.items():
                    if not widget.winfo_ismapped():
                        if "display" in self.screenData[key].keys():
                            if self.screenData[key]["display"] == "True":
                                if "place" in self.screenData[key].keys():
                                    widget.place(relx= self.screenData[key]["place"]["x"], rely= self.screenData[key]["place"]["y"])
                                else:
                                    widget.pack()
                        else:
                                if "place" in self.screenData[key].keys():
                                    widget.place(relx= self.screenData[key]["place"]["x"], rely= self.screenData[key]["place"]["y"])
                                else:
                                    widget.pack()

    def hideFrame(self, frameID):

        for key, value in self.screenData:
            if value["master"] == frameID and self.rootDictionary[value["type"]][key].winfo_ismapped():
                self.rootDictionary[value["type"]][key].pack_forget()

        if self.rootDictionary["LabelFrame"][frameID].winfo_ismapped():
            self.rootDictionary["LabelFrame"][frameID].pack_forget()
    
    def showFrame(self, frameID):

        for key, value in self.screenData:
            if value["master"] == frameID and not self.rootDictionary[value["type"]][key].winfo_ismapped():
                self.rootDictionary[value["type"]][key].pack()

        if not self.rootDictionary["LabelFrame"][frameID].winfo_ismapped():
            self.rootDictionary["LabelFrame"][frameID].pack()

    def hideWidget(self, widgetId):

        for _, widgetPack in self.rootDictionary.items():
            for key, widget in widgetPack.items():
                if key == widgetId and widget.winfo_ismapped():
                    widget.pack_forget()
            
    def showWidget(self, widgetID):

        for _, widgetPack in self.rootDictionary.items():
            for key, widget in widgetPack.items():
                if key == widgetID and not widget.winfo_ismapped():
                    widget.pack()

    def renderWidget(self, widgetID):

        for typeOfWidget, widgetPack in self.rootDictionary.items():
            if typeOfWidget != "Master":
                for key, widget in widgetPack.items():
                    if key == widgetID and not widget.winfo_ismapped():
                        if "display" in self.screenData[key].keys():
                            if self.screenData[key]["display"] == "True":
                                if "place" in self.screenData[key].keys():
                                    widget.place(relx= self.screenData[key]["place"]["x"], rely= self.screenData[key]["place"]["y"])
                                else:
                                    widget.pack()
                        else:
                            if "place" in self.screenData[key].keys():
                                widget.place(relx= self.screenData[key]["place"]["x"], rely= self.screenData[key]["place"]["y"])
                            else:
                                widget.pack()
                        break

class autoUpdater():

    def __init__(self, jsonFile, intializerInstance):

        self.jsonFile = jsonFile
        self.intializerInstance = intializerInstance

        self.originalData = intializerInstance.screenData
    
    def jsonFileUpdateEventListener(self, refreshRate= 0.001):

        with open(self.jsonFile) as jFile:

            try:
                newData= json.load(jFile)

            except:
                newData = self.originalData
                
            if newData != self.originalData and newData != dict():

                for screenName, data in newData.items():
                
                    if screenName not in self.originalData.keys():
                        self.intializerInstance.addNewScreen(screenName, deepcopy(data))
                    else:
                        if data != self.originalData[screenName] and "Master" in data.keys():
                            if data["Master"] != dict():
                                newScreenCreated = False
                                if data["Master"] != self.originalData[screenName]["Master"]:
                                    newScreenCreated = self.configureScreen(newData= deepcopy(data), oldData= deepcopy(self.originalData[screenName]), baseWidgetsClassInstance= self.intializerInstance.masterData[screenName] if screenName in self.intializerInstance.masterData.keys() else None, screenName= screenName)
                                
                                if not newScreenCreated and screenName in self.intializerInstance.masterData.keys():
                                    if self.intializerInstance.display[screenName] == True:
                                        self.processScreen(newData= deepcopy(data), oldData= deepcopy(self.originalData[screenName]), baseWidgetsClassInstance= self.intializerInstance.masterData[screenName], screenName= screenName)

                for screenName in self.originalData.keys():
                    if screenName not in newData.keys():
                        self.intializerInstance.destroyScreen(screenName)
                    
                self.originalData = deepcopy(newData)
            
        threading.Timer(refreshRate, self.jsonFileUpdateEventListener).start()
    
    def distinguishNewData(self, newData, oldData):

        newWidgets = {
            key: value for key, value in newData.items() if key not in oldData.keys() and key != "Master"
        }

        removeWidgets = {
            key: value for key, value in oldData.items() if key not in newData.keys() and key != "Master"
        }

        configureWidgetsAdd = {
            key: value for key, value in newData.items() 
            if key in oldData.keys() if value != oldData[key] and value != dict() and key != "Master"
        }

        configureWidgetsRemove = {
            key: newData[key] for key, value in oldData.items() if key in newData.keys()
            if (len([propertyValue for propertyValue in value if propertyValue not in newData[key].keys()]) != 0) 
            and key != "Master"
        }

        configureWidgetsRemove.update({
            key: value for key, value in newData.items() 
            if key in oldData.keys() if value != oldData[key] and value != dict() if "master" in value.keys()
            and key != "Master"
        })

        return newWidgets, removeWidgets, configureWidgetsAdd, configureWidgetsRemove
    
    def processScreen(self, newData, oldData, baseWidgetsClassInstance, screenName):

        rootDictionary = baseWidgetsClassInstance.rootDictionary

        newWidgets, removeWidgets, configureWidgetsAdd, configureWidgetsRemove = self.distinguishNewData(newData, oldData)

        removeWidgets.update(configureWidgetsRemove)
        newWidgets.update(configureWidgetsRemove)

        for typeOfWidget, widgets in rootDictionary.items():
            for key in removeWidgets.keys():
                if key in widgets.keys() and key != "Master":
                    try:
                        rootDictionary[typeOfWidget][key].destroy()
                        rootDictionary[typeOfWidget].pop(key)
                    except: 
                        pass

        baseWidgetsClassInstance.defineScreen(newWidgets)

        for key in newWidgets.keys():
            if key != "Master":
                try:
                    baseWidgetsClassInstance.renderWidget(key)
                except: 
                    pass
        
        for typeOfWidget, widgets in rootDictionary.items():
            for key, propertyValue in configureWidgetsAdd.items():
                if key in widgets.keys() and key != "Master":
                    try:
                        widget = rootDictionary[typeOfWidget][key]

                        cnfs = {
                            cnfKey: (cnfValue if cnfKey != "command" else baseWidgetsClassInstance.allFunctions[cnfValue] if cnfValue in baseWidgetsClassInstance.allFunctions.keys() else doNothing)
                            for cnfKey, cnfValue in propertyValue.items() if cnfKey in baseWidgetsClassInstance.cnfParameters[typeOfWidget]
                        }

                        for cnfKey, cnfValue in cnfs.items():
                            try:
                                print({cnfKey: cnfValue})
                                widget.config({cnfKey: cnfValue})
                            except:
                                pass

                        for propertyKey, data in propertyValue.items():
                            if propertyKey == "place":
                                if not bool(widget.winfo_ismapped()):
                                    widget.place(relx= data["x"], rely= data["y"])
                                else:
                                    widget.pack_forget()
                                    widget.place(relx= data["x"], rely= data["y"])
                            elif propertyKey == "display":
                                if data != "True" and bool(widget.winfo_ismapped()):
                                    widget.pack_forget()
                                elif data == "True" and not bool(widget.winfo_ismapped()):
                                    self.complexObjectsInstance.showWidget(key)
                    except: 
                        pass

                    if "place" not in propertyValue.keys():
                        try:
                            widget = rootDictionary[typeOfWidget][key]
                            if not bool(widget.winfo_ismapped()):
                                widget.pack()
                            else:
                                widget.pack_forget()
                                widget.pack()
                        except: 
                            pass

    
    def configureScreen(self, newData, oldData, baseWidgetsClassInstance, screenName):

        #display
        if "display" in newData["Master"].keys():

            if newData["Master"]["display"] != oldData["Master"]["display"] if "display" in oldData["Master"].keys() else True:
                if newData["Master"]["display"] == "True":
                    if screenName in self.intializerInstance.display.keys():
                        if self.intializerInstance.display[screenName] == False:
                            self.intializerInstance.addNewScreen(screenName, deepcopy(newData))
                            return True
                    else:
                        self.intializerInstance.addNewScreen(screenName, deepcopy(newData))
                        return True
                elif newData["Master"]["display"] == "False":
                    if screenName in self.intializerInstance.display.keys():
                        if self.intializerInstance.display[screenName] == True:
                            self.intializerInstance.destroyScreen(screenName)
                            return True
        
        elif "display" not in newData["Master"].keys() and "display" in oldData["Master"].keys():

            if oldData["Master"]["display"] == "False":
                if screenName in self.intializerInstance.display.keys():
                        if self.intializerInstance.display[screenName] == False:
                            self.intializerInstance.addNewScreen(screenName, deepcopy(newData))
                            return True
                else:
                    self.intializerInstance.addNewScreen(screenName, deepcopy(newData))
                    return True

        #title
        if "title" in newData["Master"].keys() and "title" in oldData["Master"].keys():

            if newData["Master"]["title"] != oldData["Master"]["title"]:
                baseWidgetsClassInstance.rootDictionary["Master"].title(newData["Master"]["title"])
                return False

        elif "title" in newData["Master"].keys() and "title" not in oldData["Master"].keys():

            baseWidgetsClassInstance.rootDictionary["Master"].title(newData["Master"]["title"])
            return False

        elif "title" not in newData["Master"].keys() and "title" in oldData["Master"].keys():

            baseWidgetsClassInstance.rootDictionary["Master"].title(None)
            return False

        #geometry
        if "geometry" in newData["Master"].keys() and "geometry" in oldData["Master"].keys():

            if newData["Master"]["geometry"] != oldData["Master"]["geometry"]:

                baseWidgetsClassInstance.rootDictionary["Master"].geometry(newData["Master"]["geometry"])
                return False

        elif "geometry" in newData["Master"].keys() and "geometry" not in oldData["Master"].keys():

            baseWidgetsClassInstance.rootDictionary["Master"].geometry(newData["Master"]["geometry"])
            return False

        elif "geometry" not in newData["Master"].keys() and "geometry" in oldData["Master"].keys():

            baseWidgetsClassInstance.rootDictionary["Master"].geometry(None)
            return False

        return False
            
class intializer():

    def __init__(self, allFunctions= dict(), screenData= None, jsonPath= None):

        self.allFunctions = allFunctions
        self.screenData = screenData
        self.masterData = None

        self.display = dict()

        if screenData is None: 
            with open(jsonPath) as jsonFile:
               self.screenData = json.load(jsonFile)

    def loadFromJson(self, jsonPath):
        
        with open(jsonPath) as jsonFile:
            self.screenData = json.load(jsonFile)
            return self.screenData
    
    def initialize(self):

        Tks = {
            screenName : baseWidgetsClass(
                allFunctions= self.allFunctions[screenName] if screenName in self.allFunctions.keys() else dict(),
                screenData= data
            )
            for screenName, data in self.screenData.items()
            if any([True for key, value in data.items() if key == "Master" and value["type"] == "Tk"])
        }

        TopLevels = {
            screenName : baseWidgetsClass(
                allFunctions= self.allFunctions[screenName] if screenName in self.allFunctions.keys() else dict(),
                screenData= data,
                masterScreenForTop= Tks[data["Master"]["master"]].rootDictionary["Master"] if "master" in data["Master"].keys() else None
            )
            for screenName, data in self.screenData.items()
            if any([True for key, value in data.items() if key == "Master" and value["type"] == "TopLevel"])
        }

        Tks.update(TopLevels)

        self.display = {screenName: False for screenName in Tks.keys()}

        self.masterData = Tks

        for screenID, data in self.screenData.items():
            if "display" in data["Master"].keys():
                if data["Master"]["display"] == "True" and self.display[screenID] == False:
                    self.masterData[screenID].defineScreen()
                    self.masterData[screenID].runStaticScreen()
                    self.display[screenID] = True
            else:
                self.masterData[screenID].defineScreen()
                self.masterData[screenID].runStaticScreen()
                self.display[screenID] = True


    def addNewScreen(self, screenName, screenData):

        self.masterData[screenName] = baseWidgetsClass(
                allFunctions= self.allFunctions[screenName] if screenName in self.allFunctions.keys() else dict(),
                screenData= screenData,
                masterScreenForTop= self.masterData[screenData["Master"]["master"]].rootDictionary["Master"] if "master" in screenData["Master"].keys() else None
            )

        self.display[screenName] = False

        if "display" in screenData["Master"].keys():
            if screenData["Master"]["display"] == "True" and self.display[screenName] == False:
                self.masterData[screenName].defineScreen()
                self.masterData[screenName].runStaticScreen()
                self.display[screenName] = True
        else:
            self.masterData[screenName].defineScreen()
            self.masterData[screenName].runStaticScreen()
            self.display[screenName] = True

    def destroyScreen(self, screenName):

        if self.display[screenName] == True:
            self.masterData.pop(screenName).rootDictionary["Master"].destroy()
            self.display.pop(screenName)
