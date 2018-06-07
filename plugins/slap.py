import re
import json
import random
import logging
from datetime import datetime
from slackbot.bot import listen_to
from slackbot.bot import respond_to

@listen_to("!slap (.*)", re.IGNORECASE)
def break_(res, name):
    obj = ["an Alex","an Izzak","a chair","a fish","mjolnir","a dead hooker","a dildo","fire"]
    item = random.choice(obj)
    res.send("Bender slaps %s around with %s"%(name, item))
