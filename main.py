from dotenv import load_dotenv
from DiscordBot import PugBot, CustomHelp
from discord import Intents, CustomActivity
import os, json, logging, sys



if os.path.exists('.env'):
    load_dotenv()
else:
    with open('.env', 'w') as file:
        file.write('DISCORD_TOKEN =\n')
        file.write('FACEIT_TOKEN =\n')
        file.write('DB_URI = sqlite:///Munich-eSports-Puggers.db\n')
        file.write('APP_SETTINGS = appsettings.json\n')
    from utilities import logger
    logger.warning(f'.env was created, please adjust it according to your needs and then restart the program.')
    logger.warning('Exiting now ...')
    sys.exit(1)
    
if not os.path.exists(os.getenv('APP_SETTINGS')):
    from utilities import logger
    with open(f'{os.getenv('APP_SETTINGS')}', 'w') as file:
        data = {"Settings":{'priv_roles':[], 'guilds':[], 'matches_url': None}, "Servers":[{"Id":1, "IP":"example.com", "Port":27015, "RconPort":27015, "Password":"example", "RconPassword":"different_example"}]}
        json.dump(data, file, indent=4)
    logger.warning(f'{os.getenv('APP_SETTINGS')} was created, please adjust it according to your needs and then restart the program.')
    logger.warning('Exiting now ...')
    sys.exit(1)



if __name__ == '__main__':
    bot = PugBot(intents=Intents.all(), activity=CustomActivity(name='test'), help_command=CustomHelp())
    TOKEN = os.getenv('TOKEN')
    bot.run(token=TOKEN, log_handler=None)