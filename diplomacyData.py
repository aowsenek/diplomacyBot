import threading
from diplomacyMap import Map

class ddata():
    def __init__(self):
        self.season = "SPRING"
        self.date = 1901
        self.resolving = False
        self.players={}
        self.countries = {1: "Russia",
                          2: "England",
                          3: "Germany",
                          4: "France",
                          5: "Austria",
                          6: "Italy",
                          7: "Turkey"}

        self.orders = { 1:[],2:[],3:[],4:[],5:[],6:[],7:[]}
        self.retreats = []
        self.ready = {}
        self.numBuild = {1:0,2:0,3:0,4:0,5:0,6:0,7:0}
        self.map = Map()
    def getSeason(self):
        return self.season
    def getDate(self):
        return self.date
    def getResolving(self):
        return self.resolving
    def getPlayers(self):
        return self.players
    def getPID(self,countryID):
        return self.players[countryID][0]
    def getPCountries(self):
        return self.players.keys()
    def getCountrybyPID(self,pid):
        for c in self.getPCountries():
            if(pid == self.players[c])
                return c
    def countries(self,countryID):
        return self.countries[countryID]
    def getOrders(self):
        return self.orders
    def getNumBuild(self,countryID):
        return self.numBuild[countryID]
    def getOrdersbyCID(self,countryID):
        return self.orders[countryID]
    def getRetreats(self):
        return self.retreats
    def isReady(self):
        return all(ready == True for ready in self.ready.values())
    #==============Needs to be locked for Threading============
    def map(self):
        return self.map
    def changeSeason(self):
        if(self.season == "SPRING"): self.season = "FALL"
        elif(self.season == "FALL"): self.season = "WINTER"
        else: self.season = "SPRING"
    def incrementDate(self):
        self.date += 1
    def setResolving(self,state):
        self.resolving = state
    def addPlayer(self,countryID,uid):
        self.players[countryID] = uid
    def addOrder(self,countryID,order):
        idx = 0
        for i in self.orders[countryID]:
            if(i[1] == order[1]):
                del self.orders[countryID][idx]
            idx += 1
        self.orders[countryID.append(order)
    def addReady(self,countryID):
        self.ready[countryID] = True
    def addRetreat(self,unit,prevLoc):
        self.retreats.append((unit,prevLoc))
    def setNumBuild(self,countryID,toBuild):
        self.numBuild[countryID] = toBuild
    def reset(self):
        self.ready = dict.fromkeys(self.ready,False)
        self.orders = { 1:[],2:[],3:[],4:[],5:[],6:[],7:[]}

