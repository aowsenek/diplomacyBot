# diplomacyBot
A slackbot for playing diplomacy!

Still in alpha. 

If you want to set up this project to work on your own slack channel:
1. Create a bot user and save the api key.
2. Create or designate a channel to run the bot in. It must be a public channel. Get the channel ID from the URL.
    It should look something like: `CB227T8EQ` 
    
3. Create a file in the diplomacybot directory named config.py.
4. Edit the config.py file to say:
```API_TOKEN = "your-api-token-here"
DIPLOMACY_CHANNEL = "your-diplomacy-channel-id-here"```
5. Save the file and run ./run.sh! Enjoy~
