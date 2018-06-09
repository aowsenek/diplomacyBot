import re
import time
import random
from diplomacyMap import *
from slackclient import SlackClient
from slackbot_settings import API_TOKEN


RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"



class diplomacyBot():
    def __init__(self):
        self.diplomacy = "CB227T8EQ"

        self.sc = SlackClient(API_TOKEN)
        self.bot_id = None
        self.current = None
        self.starting = False
        self.running = False
        self.season = "SPRING"
        self.resolving = False
        self.players={}
        self.run()
#============================= Messaging
    def send(self,message):
        self.sc.api_call(
                "chat.postMessage",
                channel=self.current,
                text=message,
                as_user="true")

    def im(self, player, message):
        self.sc.api_call(
                "conversations.open",
                users=player,
                return_im="true")
        self.sc.api_call(
                "chat.postMessage",
                channel=player,
                text=message,
                as_user="true")

    def map(self, player, mapname):
        self.sc.api_call(
                  "files.upload",
                   channels=player,
                   as_user="true",
                   filename=mapname,
                   file=open(mapname, 'rb'))
#============================= User Interface
    def start(self):
        try:
            info = self.sc.api_call("channels.info",channel=self.current)
            if(info['channel']['id'] == self.diplomacy):
                pass
            else:
                self.send("This isn't the diplomacy channel")
                return
        except KeyError:
            self.send("This isn't the diplomacy channel")
            return
        if(self.starting == False):
            self.send("@channel A new game of Diplomacy is starting...")
            self.send("Message \"@bender add me\" if you want to join the game")
            self.send("Message \"@bender Start\" when all members have registered and you are ready to play")
            self.starting = True
            self.addPlayer()
        else:
            self.starting = False
            self.running = True
            self.send("Starting Game...")
            if(len(self.players) > 7):
                self.send("Too many players for this game. Quitting...")
                self.starting = False
                self.running = False
                return
            playerstr = "Players are "+"".join([str(self.players[i][0])+", " for i in self.players])
            self.send(playerstr[:-2])
            self.randomizeCountries()

            for i in self.players:
                ctry = self.players[i][1]
                self.im(i,"Your country is "+str(self.countries[ctry]))
                unitLocs = "Your units are: "+
                            "".join([str(j[1])+", " for j in getUnitsByCountry(ctry)])
                #send map
                #self.map(i, "diplomacy_map.png")
                self.im(i,unitLocs[:-2])
                self.im(i,"Send orders here, so they are private.\n
                        Valid orders are in form [unit type] [location of unit]
                        [action] [location of action or second unit]
                        [second unit action] [location of second unit action]")

    def addPlayer(self):
        info = self.sc.api_call("users.info",user=self.sender)
        if(self.sender not in self.players):
            self.players[self.sender] = [str(info['user']['name']),""]
            self.send("Added player: "+str(info['user']['name']))
        else:
            self.send("You cannot be in the same game twice")

    def randomizeCountries(self):
        self.countries = {1: "Russia",
                          2: "England",
                          3: "Germany",
                          4: "France",
                          5: "Austria",
                          6: "Italy",
                          7: "Turkey"}

        self.orders = { 1:[],2:[],3:[],4:[],5:[],6:[],7:[]}
        self.supplyDepots = {1:4,2:3,3:3,4:3,5:3,6:3,7:3}

        assign = random.sample(range(1,8),len(self.players))
        it = 0
        for i in self.players:
            self.players[i][1] = assign[it]
            it += 1
        print(self.players)

    def ordered(self):
        ctry = self.players[self.sender][1]
        idx = 0
        for i in self.orders[ctry]:
            if(i[1] == self.command[1]):
                del self.orders[ctry][idx]
            idx += 1
        self.orders[ctry].append(self.command[:])
        print(self.orders[ctry])
        self.send("Added order: "+" ".join(self.command))

    def verify(self):
        ctry = self.players[self.sender][1]
        ordrs = "Your entered orders are:\n "+"\n".join(self.orders[ctry])
        self.im(self.sender, ordrs[:-1])

#============================== Needs Work
    def show(self):#needs to implement map generation with the map library
        try:
            if(self.command[1] == "HELP"):
                self.im(self.current, "Type \"show current map\" or \"show arrow map\"")
            elif(self.command[1][0] == "C"):
                self.map(self.current, "diplomacy_map.png")
            else:
                self.im(self.current, "That hasn't been implemented yet")
        except:
            self.map(self.current, "diplomacy_map.png")

    def win(self): #ties not implemented yet
        for i in self.players:
            ctry = self.players[i][1]
            if(self.supplyDepots[ctry] >= 18):
                self.running = False
                self.send("Game Over! The winner is "+self.countries[ctry])
                return

    def winter(self):
        self.send("The Winter Season is starting.")
        for i in self.players:
            ctry = self.players[i][1]
            if(self.unitsToBuild[ctry] > 0):
                self.im(i,"You need to build "+str(self.unitsToBuild[ctry])+" units. You can only build them on your home supply depots.")
                self.im(i,"Type [unit type] [spawn location] to order unit creation. The spawn location must be unoccupied.")
            elif(self.unitsToBuild[ctry] == 0):
                self.im(i,"You have no units to build or destroy.")
            else:
                self.im(i,"You need to destroy "+str(-1*self.unitsToBuild[ctry])+" units.")
                self.im(i,"Type [unit type] [location] to order unit destruction.")

#=============================== Game Logic
    def resolveWinterOrders(self):
        for i in self.players:
            ctry = self.players[i][1]
            if(self.unitsToBuild[ctry] > 0): #Build Units
                unitsBuilt = 0
                for i in self.orders:
                    if(unitsBuilt < self.unitsToBuild[ctry]):
                        placeUnit(i[0],ctry,i[1])
                        unitsBuilt += 1
            elif(self.unitsToBuild[ctry] < 0): #Delete Units
                if(self.orders[ctry] == self.unitsToBuild[ctry]):
                    for i in self.orders[ctry]:
                        deleteUnit(i[1])
                elif(self.orders[ctry] > self.unitsToBuild[ctry]):
                    unitsRemoved = 0
                    for i in self.orders[ctry]:
                        if(unitsRemoved < self.unitsToBuild[ctry]):
                            deleteUnit(i[1])
                            unitsRemoved += 1
                else:
                    unitsRemoved = 0
                    units = getUnitsByCountry(ctry)
                    for i in self.orders[ctry]:
                        if(unitsRemoved < self.unitsToBuild[ctry]):
                            deleteUnit(i[1])
                            unitsRemoved += 1
                    for i in units:
                        if(unitsRemoved < self.unitsToBuild[ctry]):
                            deleteUnit(i[1])
                            unitsRemoved += 1
            else: pass #No units to remove or add

    def isValidCommand(self, cmd):
        if(self.command[2][0] == "H"): #holding
            return True
        elif(self.command[2][0] == "-" or self.command[2][0] == "A"):#attacking
            if(adjacent(self.command[1], self.command[3])):
                return True
            return False
        elif(self.command[2][0] == "S"): #supporting
            if(adjacent(self.command[1],self.command[5])):
                if(adjacent(self.command[3],self.command[5])):
                    return True
            return False
        elif(self.command[2][0] == "C"): #convoying
            if(adjacent(self.command[1],self.command[5])):
                if(adjacent(self.command[3],self.command[5])):
                    return True
            return False

    def build(self):
        self.unitsToBuild = {1:0,2:0,3:0,4:0,5:0,6:0,7:0}
        for i in self.players:
            ctry = self.players[i][1]
            supplyDepots = 0
            units = getUnitsByCountry(ctry)
            for t,loc in units:
                if(isSupplyDepot(loc)):
                    supplyDepots += 1
                changeOwner(loc,ctry)
            self.unitsToBuild[ctry] =  supplyDepots - len(units)
            self.supplyDepots[ctry] = supplyDepots
            self.win()
        self.winter()
#self.command[Type, location1, action1, location2, action2, location3]
#=============================== In Progress
    def adjudicate(self):
        if(self.season == "SPRING"):
            if(self.resolving == True):
                self.resolving = False
                self.season = "FALL"
                return
            self.resolving = True
        elif(self.season == "FALL"):
            if(self.resolving == True):
                self.resolving = False
                self.season = "WINTER"
                return
            self.resolving = True
        elif(self.season == "WINTER"):
            if(self.resolving == True):
                self.resolveWinterOrders()
                self.resolving = False
                self.season = "SPRING"
                return
            self.build()
            self.resolving = True




    def move(self):
        pass
    def retreat(self):
        pass








#=============================== Event Loop and Bones
    def handle_command(self,cmd, channel, sender):
        default_response = "I do not understand that command"
        self.viableCommands = {
                "START":self.start,
                "ADD ME":self.addPlayer,
                "F ":self.ordered,
                "A ":self.ordered,
                "ADJUDICATE":self.adjudicate,
                "VERIFY",self.verify,
                "SHOW":self.show}#list of commands
        iscommand = False
        #variables needed for functions that can't be passed with the dictionary
        self.current = channel
        self.sender = sender
        self.command = cmd.upper().split()
        #executes proper code for given command
        for i in self.viableCommands:
            if cmd.upper().startswith(i):
                if(self.starting == True or self.running == True or i == "START"):
                    print("command detected: ",i)
                    self.viableCommands[i]()
                    iscommand = True
                else:
                    self.send("A game is not currently starting")

        if(not iscommand):
            self.send(default_response)

    def parse_bot_commands(self,slack_events):
        for event in slack_events:
            if event["type"] == "message" and not "subtype" in event:
                user_id, message = self.parse_direct_mention(event["text"])
                if user_id == self.bot_id:
                    return message, event["channel"], event["user"]
                elif event["channel"][0] == "D" and self.bot_id != event["user"]:
                    print("DM'ed")
                    return event["text"], event["channel"], event["user"]
        return None, None, None

    def parse_direct_mention(self,message_text):
        matches = re.search(MENTION_REGEX, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def run(self):
        if self.sc.rtm_connect(with_team_state=False):
            print("Starter Bot connected and running!")
            self.bot_id = self.sc.api_call("auth.test")["user_id"]
            while True:
                command, channel, user = self.parse_bot_commands(self.sc.rtm_read())
                if command:
                     self.handle_command(command, channel, user)
                time.sleep(RTM_READ_DELAY)
        else:
            print("Connection failed. Exception traceback printed above.")


if __name__ == "__main__":
    bot = diplomacyBot()
