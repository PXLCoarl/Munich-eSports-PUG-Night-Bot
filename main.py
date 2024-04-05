from dotenv import load_dotenv
load_dotenv()
from DiscordBot import PugBot, CustomHelp
from discord import Intents, CustomActivity
from utilities import appsettings, RconUtils, logger
from icecream import ic
import os




if __name__ == '__main__':
    bot = PugBot(intents=Intents.all(), activity=CustomActivity(name='test'), help_command=CustomHelp())
    TOKEN = os.getenv('TOKEN')
    bot.run(token=TOKEN, log_handler=None)