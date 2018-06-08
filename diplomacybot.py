from slackbot_settings import API_TOKEN
import time
import re
import random
from slackclient import SlackClient


RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"



class diplomacyBot():
    def __init__(self):
        self.diplomacy = "CB227T8EQ"

        self.sc = SlackClient(API_TOKEN)
        self.bot_id = None
        self.current = None
        self.starting=False
        self.running = False
        self.players={}
        self.run()

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
    def start(self):
        try:
            info = self.sc.api_call("channels.info",channel=self.current)
            if(info['channel']['id'] == self.diplomacy):
                pass
            else:
                self.send("This isn't the diplomacy channel")
                return
        except:
            self.send("This isn't the diplomacy channel")
            return
        if(self.starting == False):
            self.send("@channel A new game of Diplomacy is starting...")
            self.send("Message \"@bender add me\" if you want to join the game")
            self.send("Message \"@bender Start\" when all members have registered and you are ready to play")
            self.starting = True
            #self.addPlayer()
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
                unitLocs = "Your units are: "+"".join([str(j[0])+", " for j in self.unitList[ctry]])
                #send map
                #self.map(i, "diplomacy_map.png")
                self.im(i,unitLocs[:-2])
                self.im(i,"Send orders here, so they are private.\n Valid orders are in form [unit type] [location of unit] [action] [location of action or second unit] [second unit action] [location of second unit action]")

    def addPlayer(self):
        if(self.starting == True):
            info = self.sc.api_call("users.info",user=self.sender)
            if(self.sender not in self.players):
                self.players[self.sender] = [str(info['user']['name']),""]
                self.send("Added player: "+str(info['user']['name']))
            else:
                self.send("You cannot be in the same game twice")
        else:
            self.send("A game is not currently starting")

    def randomizeCountries(self):
        self.countries = {1: "Russia", 2: "England", 3: "Germany", 4: "France", 5: "Austria", 6: "Italy", 7: "Turkey"}
        self.unitList = {1:[["stp","f",True],["mos","a",True],["sev","f",True],["war","a",True]],
                        2:[["edi","f",True],["lvp","a",True],["lon","f",True]],
                        3:[["kie","f",True],["ber","a",True],["mun","a",True]],
                        4:[["edi","f",True],["lvp","a",True],["lon","f",True]],
                        5:[["tri","f",True],["bud","a",True],["vie","a",True]],
                        6:[["nap","f",True],["rom","a",True],["ven","a",True]],
                        7:[["ank","f",True],["smy","a",True],["con","a",True]]}
        self.orders = { 1:[],2:[],3:[],4:[],5:[],6:[],7:[]}

                        #country: [[unit location, type, on a supplydept]]
        assign = random.sample(range(1,8),len(self.players))
        it = 0
        for i in self.players:
            self.players[i][1] = assign[it]
            it += 1
        print(self.players)

    def orders(self):
        print("Order Input")
        ctry = self.players[player][1]
        self.orders[ctry].append(self.command[:])
        self.send("Added order: "+" ".join(self.command))



    def retreat(self):
        pass
    def build(self):
        pass
    def adjudicate(self):
        unitType = self.command[0]
        loc1 = self.command[1]
        act1 = self.command[2]
        loc2 = act2 = loc3 = None
        units=["a","army","f","fleet"]
        vc = ["atk","attack","mov","move","-","h","hold","s","support","c","cvy","convoy"]
        vc = ["a","-","h","s","c"]
        try:
            loc2 = self.command[3]
            act2 = self.command[4]
            loc3 = self.command[5]
        except: pass
        if(act1[0] == vc[2]): #hold
            pass
        elif(act1[0] == vc[0] or act1[0] == vc[1]): #attack/move
            pass
        elif(act1[0] == vc[3]): #support
            pass
        elif(unitType == (units[2] or units[3]) and act1[0] == vc[4]): #convoy
            pass
        else:
            self.im(self.sender," ".join(self.command)+" is not a valid command.")
    def show(self):
        pass







    def handle_command(self,cmd, channel, sender):
        default_response = "I do not understand that command"
        self.viableCommands = {"start":self.start,"add me":self.addPlayer,"f ":self.orders,"a ":self.orders,"adjudicate":self.adjudicate}#list of commands
        iscommand = False
        #variables needed for functions that can't be passed with the dictionary
        self.current = channel
        self.sender = sender
        self.command = cmd.lower().split()
        #executes proper code for given command
        for i in self.viableCommands:
            if cmd.lower().startswith(i):
                print("command detected: ",i)
                self.viableCommands[i]()
                iscommand = True

        if(not iscommand):
            self.send(default_reponse)

    def parse_bot_commands(self,slack_events):
        """
            Parses a list of events coming from the Slack RTM API to find bot commands.
            If a bot command is found, this function returns a tuple of command and channel.
            If its not found, then this function returns None, None.
        """
        for event in slack_events:
            if event["type"] == "message" and not "subtype" in event:
                user_id, message = self.parse_direct_mention(event["text"])
                if user_id == self.bot_id:
                    return message, event["channel"], event["user"]
                elif event["channel"][0] == "D":
                    print("DM'ed")
                    return event["text"], event["channel"], event["user"]
        return None, None

    def parse_direct_mention(self,message_text):
        """
            Finds a direct mention (a mention that is at the beginning) in message text
            and returns the user ID which was mentioned. If there is no direct mention, returns None
        """
        matches = re.search(MENTION_REGEX, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def run(self):
        if self.sc.rtm_connect(with_team_state=False):
            print("Starter Bot connected and running!")
            self.bot_id = self.sc.api_call("auth.test")["user_id"]
            while True:
                try:
                    command, channel, user = self.parse_bot_commands(self.sc.rtm_read())
                    if command:
                         self.handle_command(command, channel, user)
                except: pass
                time.sleep(RTM_READ_DELAY)
        else:
            print("Connection failed. Exception traceback printed above.")


if __name__ == "__main__":
    bot = diplomacyBot()

