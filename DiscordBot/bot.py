from discord.ext import commands
import discord, os
from utilities import logger, DBOps

class CustomHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        ctx = self.context
        await ctx.message.delete()
        bot = ctx.bot
        command_list = [
            f'`/{command.name}` - {command.description}' + 
            (' - (requires a privileged Role!)' if command.checks else '')
            for cog in bot.cogs.values()
            for command in cog.get_app_commands()
        ]                
        await ctx.send('\n'.join(command_list))


class PugBot(commands.Bot):
    def __init__(self,intents:discord.Intents, activity, help_command:commands.HelpCommand):
        super().__init__(command_prefix="#", intents=intents, activity=activity, help_command=help_command, status=discord.Status.dnd)
    
    async def on_ready(self):
        async def load():
            for filename in os.listdir("DiscordBot/cogs"):
                if filename.endswith("py"):
                    await self.load_extension(f"DiscordBot.cogs.{filename[:-3]}")
                    
        logger.info(f'Started Bot as: {self.user}')
        await load()

intents = discord.Intents.all()
activity = discord.CustomActivity(name='Use /help for more information')
bot = PugBot(intents=intents, activity=activity, help_command=CustomHelp())



# Custom Events:

@bot.event
async def on_api_call(data: dict) -> None:
    '''
    Very much work in Progress, 
    since matchZy's implementation does not work yet
    I also have not worked on this.
    '''
    event: str = data.get("event")
    match_id: int = int(data.get("matchid"))
    _: list[int] = await DBOps.get_message_id(query_value=match_id)
    message_id: int = _[0]
    match event:
        case "series_start":
            logger.info(f"{event} received")
        case "map_result":
            logger.info(f"{event} received")
        case "series_end":
            logger.info(f"{event} received")
        case "going_live":
            logger.info(f'{event} received')
