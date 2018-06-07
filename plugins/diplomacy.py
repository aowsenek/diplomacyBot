import re
import random
import logging
from slackbot.bot import listen_to
from slackbot.bot import respond_to
from slackbot_settings import API_TOKEN
from slackclient import SlackClient

sc = SlackClient(API_TOKEN)
testChannel = "G1D5QB988"
diplomacy = "CB227T8EQ"

def start(res):

    sc.api_call(
            "chat.postMessage",
            channel=testChannel,
            text="Suck a butt")
    info = sc.api_call("channels.info",channel=current)
    if(info['channel']['id'] == diplomacy):
        res.send("Starting Game....")
    else:
        res.send("This isn't the diplomacy channel")


