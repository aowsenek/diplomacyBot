from slackbot_settings import API_TOKEN
import time
import re
from slackclient import SlackClient


RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"



class diplomacyBot():
    def __init__(self):
        self.testChannel = "G1D5QB988"
        self.diplomacy = "CB227T8EQ"

        self.sc = SlackClient(API_TOKEN)
        self.bot_id = None
        self.current = None
        self.run()

    def send(self,message):
        self.sc.api_call(
                "chat.postMessage",
                channel=self.current,
                text=message)

    def start(self):
        try:
            info = self.sc.api_call("channels.info",channel=self.current)
            if(info['channel']['id'] == self.diplomacy):
                self.send("Starting Game....")
            else:
                self.send("This isn't the diplomacy channel")
        except:
            self.send("This isn't the diplomacy channel")































    def handle_command(self,command, channel):
        default_response = "I do not understand that command"
        response = None
        self.current = channel
        self.commands = {"start":self.start}
        iscommand = False

        for i in self.commands:
            if command.startswith(i):
                self.commands[i]()
                iscommand = True

        if(not iscommand):
            self.sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=default_response
            )

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
                    return message, event["channel"]
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
                command, channel = self.parse_bot_commands(self.sc.rtm_read())
                if command:
                     self.handle_command(command, channel)
                time.sleep(RTM_READ_DELAY)
        else:
            print("Connection failed. Exception traceback printed above.")


if __name__ == "__main__":
    bot = diplomacyBot()

