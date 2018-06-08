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
                print(i, self.players[i])
                self.im(i,"Your country is "+str(self.players[i][1]))
                #send map
                self.im(i,"Send orders in this chat. Valid orders are [unit] ATK [country]")

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
        assign = random.sample(range(1,8),len(self.players))
        it = 0
        for i in self.players:
            self.players[i][1] = self.countries[assign[it]]
            it += 1
        print(self.players)

    def takeOrders(self):
        pass


    def adjudicate(self):
        pass
    def resolve(self):
        pass
    def addUnits(self):
        pass








    def handle_command(self,command, channel, sender):
        default_response = "I do not understand that command"
        self.commands = {"start":self.start,"add me":self.addPlayer,"orders":self.takeOrders}#list of commands
        iscommand = False
        #variables needed for functions that can't be passed with the dictionary
        self.current = channel
        self.sender = sender
        self.command = command
        #executes proper code for given command
        for i in self.commands:
            if command.lower().startswith(i):
                self.commands[i]()
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

