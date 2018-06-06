from slackbot_settings import API_TOKEN
from slackclient import SlackClient

sc = SlackClient(API_TOKEN)
testChannel = "G1D5QB988"
diplomacy = "CB227T8EQ"


def main():
    sc.api_call(
            "chat.postMessage",
            channel=testChannel,
            text="Suck a butt")
    info = sc.api_call("channels.info",channel=diplomacy)
    if(info['channel']['id'] == diplomacy):
        print("wrong channel")







if __name__ == "__main__":
    main()



