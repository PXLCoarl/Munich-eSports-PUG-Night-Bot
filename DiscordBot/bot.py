import discord, os
from discord import Intents, CustomActivity
from discord.ext import commands
from utilities import logger



class CustomHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        ctx = self.context
        await ctx.message.delete()
        bot = ctx.bot
        command_list = [
            f'`/{command.name}` - {command.description}' + 
            (' - (needs Staff!)' if command.checks else '')
            for cog in bot.cogs.values()
            for command in cog.get_app_commands()
        ]
        await ctx.send('\n'.join(command_list))
        return



class PugBot(commands.Bot):
    def __init__(self, *, intents: Intents, activity: CustomActivity, help_command: commands.HelpCommand):
        super().__init__(command_prefix='#', intents=intents, activity=activity, help_command=help_command, status=discord.Status.online)
        
    async def on_ready(self):
        files = [filename for filename in os.listdir('DiscordBot/cogs') if filename.endswith('.py')]
        for filename in files:
            try:
                await self.load_extension(f'DiscordBot.cogs.{filename[:-3]}')
                logger.info(f'Loaded extension: {filename[:-3]}')
            except Exception as e:
                logger.error(f'Failed to load extension {filename[:-3]}: {e}')
        logger.info(f'Started bot as {self.user}')