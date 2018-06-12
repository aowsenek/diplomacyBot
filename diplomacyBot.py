import re
import time
import random
from diplomacyMap import Map
from slackclient import SlackClient
from slackbot_settings import API_TOKEN

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
class Command:
    def __init__(self):
        self.cmd = 'H'
        self.target = None
        self.atk = []
        self.sup = []

    def __repr__(self):
        return '%s (%s vs %s)' % (self.cmd, self.atk, self.sup)

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

    def showMap(self, player, mapname):
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
            self.map = Map()
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
            self.springFall()

            for i in self.players:
                ctry = self.players[i][1]
                self.im(i,"Your country is "+str(self.countries[ctry]))
                unitLocs = "Your units are: "+ "".join([str(j[0])+", " for j in self.map.getUnitsByCountry(ctry)])
                #send map
                #self.showMap(i, "diplomacy_map.png")
                self.im(i,unitLocs[:-2])
                self.im(i,"Send orders here, so they are private.\n Valid orders are in form [unit type] [location of unit] [action] [location of action or second unit] [second unit action] [location of second unit action]")

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
#============================== Needs Work
    def show(self, opt = None):#needs to implement map generation with the map library
        if(opt): self.command = opt
        if(self.command[1] == "HELP"):
            self.im(self.current, "Type \"show unit map\" or \"show labeled map\"") #Outdated)
        elif(self.command[1][0] == "M" or self.command[1][0] == "U"):
            self.map.getMap()
            self.map.saveMap("current_units.png")
            self.showMap(self.current, "current_units.png")
        elif(self.command[1][0] == "L"):
            self.showMap(self.current, "labeledMap.png")
        else:
            self.map.getMap()
            self.map.saveMap("current_units.png")
            self.showMap(self.current, "current_units.png")

    def win(self): #ties not implemented yet
        for i in self.players:
            ctry = self.players[i][1]
            if(self.supplyDepots[ctry] >= 18):
                self.running = False
                self.send("Game Over! The winner is "+self.countries[ctry])
                return
#============================== Game movement interface
    def standardizeOrder(self, cmd):
            typ = cmd[0][0]
            loc1 = cmd[1]
            act1 = cmd[2][0]
            loc2 = act2 = loc3 = None
            try:
                loc2 = cmd[3]
                act2 = cmd[4][0]
                loc3 = cmd[5]
            except IndexError: pass
            if(act1 == "M" or act1 == "A"):
                act1 = "-"
            if(act2 == "M" or act2 == "A"):
                act2 = "-"
            return list(filter(None,[typ,loc1,act1,loc2,act2,loc3]))

    def ordered(self):
        ctry = self.players[self.sender][1]
        idx = 0
        for i in self.orders[ctry]:
            if(i[1] == self.command[1]):
                del self.orders[ctry][idx]
            idx += 1
        self.command = self.standardizeOrder(self.command)
        self.orders[ctry].append(self.command[:])
        print(self.orders[ctry])
        self.send("Added standardized order: "+" ".join(self.command))

    def verify(self):
        ctry = self.players[self.sender][1]
        ordrs = "Your entered orders are:\n "+"\n".join(self.orders[ctry])
        self.im(self.sender, ordrs[:-1])

    def springFall(self):
        if(self.resolving == False):
            self.send("The "+self.season.lower()+" season is starting")
            self.send("Send in your movement orders at this time.")
        else:
            self.show(opt = "map")
            self.send("The "+self.season.lower()+" season is resolving.")
            self.send("Please send in your retreat orders at this time.")
            #for i in self.retreatingUnits:
            #   self.im(self.map.getUnitByProvince(i).controllerID,"Your unit at "+i+" needs to retreat")

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

#self.command[Type, location1, action1, location2, action2, location3]
    def adjudicate(self):
        if(self.current != self.diplomacy):
            self.send("Adjudication must happen in the diplomacy channel.")
            return
        if(self.season == "SPRING"):
            if(self.resolving == False):
                self.move()
                self.resolving = True
                if(self.fails == []):
                    self.resolving = False
                    self.season = "WINTER"
                self.springFall()
            else:
                self.retreat()
                self.season = "WINTER"
                self.resolving = False
                self.springFall()
        elif(self.season == "FALL"):
            if(self.resolving == False):
                self.move()
                self.resolving = True
                if(self.fails == []):
                    self.resolving = False
                    self.season = "WINTER"
                self.springFall()
            else:
                self.retreat()
                self.season = "WINTER"
                self.resolving = False
                self.springFall()
        elif(self.season == "WINTER"):
            if(self.resolving == False):
                self.build()
                self.resolving = True
            else:
                self.resolveWinterOrders()
                self.season = "SPRING"
                self.resolving = False
                self.springFall()


    def move(self):
        q = { n: Command() for n, p in self.map.provinces.items() if p.unit != None }
        orders = []
        for i in self.countries:
            orders = orders + self.orders[i]
        for command in orders:
            print(command)
            if command[2] == '-':
                _, f,a,t = command
                q[f].cmd = '-'
                q[f].target = t
                if t in q:
                    q[t].atk.append(f)
            elif command[2] == 'S':
                try:
                    _, lc1, s, f,a,t = command
                except IndexError:
                    _, lc1, s, f,a = command

                q[s].cmd = 'S'
                q[t].atk.append(s)
                q[f].sup.append(s)
            elif command[2] == 'H':
                pass
        self.success = []
        self.fails = []
        for p in q.keys():
            if self.succeeds(p,q):
                if(q[p].cmd == '-'):
                    try:
                        self.map.moveUnit(p,q[p].target)
                        self.success.append(p)
                    except AssertionError:
                        self.fails.append(p)
                else:
                    self.success.append(p)
            else:
                self.fails.append(p)
        print(q)
        print(self.success)
        print(self.fails)

        #start = q.keys()[0]
        #solve(start)

    def active(self,p,q):
        if p not in q:
            return False
        c = q[p]
        if c.cmd == 'S':
            if any([x for x in c.atk if self.active(x,q)]):
                return False
        return True

    def support(self,p,q):
        return sum([1 for x in q[p].sup if self.active(x,q)])

    def succeeds(self,p,q):
        c = q[p]
        if c.cmd == 'H':
            if not c.atk:
                return True
            return max([self.support(x,q) for x in c.atk]) <= self.support(p,q)
        if c.cmd == '-':
            if not self.active(c.target,q) or (q[c.target].cmd == '-' and self.succeeds(c.target,q)):
                return True
            return self.support(p,q) > self.support(c.target,q)
        if c.cmd == 'S':
            return not self.active(p,q)



    def retreat(self):
        pass

    def build(self):
        self.unitsToBuild = {1:0,2:0,3:0,4:0,5:0,6:0,7:0}
        for i in self.players:
            ctry = self.players[i][1]
            supplyDepots = 0
            units = self.map.getUnitsByCountry(ctry)
            for t,loc in units:
                if(self.map.isSupplyDepot(loc)):
                    supplyDepots += 1
                self.map.changeController(loc,ctry)
            self.unitsToBuild[ctry] =  supplyDepots - len(units)
            self.supplyDepots[ctry] = supplyDepots
            self.win()
        self.winter()
    def resolveWinterOrders(self):
        for i in self.players:
            ctry = self.players[i][1]
            if(self.unitsToBuild[ctry] > 0): #Build Units
                unitsBuilt = 0
                for i in self.orders[ctry]:
                    if(unitsBuilt < self.unitsToBuild[ctry]):
                        self.map.placeUnit(i[0],ctry,i[1])
                        unitsBuilt += 1
            elif(self.unitsToBuild[ctry] < 0): #Delete Units
                if(self.orders[ctry] >= self.unitsToBuild[ctry]):
                    unitsRemoved = 0
                    for i in self.orders[ctry]:
                        if(unitsRemoved < self.unitsToBuild[ctry]):
                            self.map.deleteUnit(i[1])
                            unitsRemoved += 1
                else:
                    unitsRemoved = 0
                    units = self.map.getUnitsByCountry(ctry)
                    for i in self.orders[ctry]:
                        if(unitsRemoved < self.unitsToBuild[ctry]):
                            self.map.deleteUnit(i[1])
                            unitsRemoved += 1
                    for i in units:
                        if(unitsRemoved < self.unitsToBuild[ctry]):
                            self.map.deleteUnit(i[1])
                            unitsRemoved += 1
            else: pass #No units to remove or add

#=============================== Event Loop and Bones
    def handle_command(self,cmd, channel, sender):
        default_response = "I do not understand that command"
        self.viableCommands = {
                "START":self.start,
                "ADD ME":self.addPlayer,
                "F ":self.ordered,
                "A ":self.ordered,
                "ADJUDICATE":self.adjudicate,
                "VERIFY":self.verify,
                "SHOW":self.show}#list of commands
        iscommand = False
        #variables needed for functions that can't be passed with the dictionary
        self.current = channel
        self.sender = sender
        self.command = cmd.upper().split()
        #executes proper code for given command
        for i in self.viableCommands:
            if cmd.upper().startswith(i):
                if((self.starting == True and ((i == "START") or (i == "ADD ME"))) or self.running == True or i == "START"):
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
