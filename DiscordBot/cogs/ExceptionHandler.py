from discord import app_commands, Interaction
from DiscordBot import EmbedBuilder
from discord.ext import commands
from utilities import logger

class ExceptionHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.tree.error(coro=self.__dispatch_to_app_command_handler)
        
    async def __dispatch_to_app_command_handler(self, interaction:Interaction, error:app_commands.AppCommandError):
        self.bot.dispatch("app_command_error", interaction, error)
        
    @commands.Cog.listener("on_app_command_error")
    async def get_app_command_error(self, interaction: Interaction, error: app_commands.AppCommandError):        
        logger.error(f"An error has occured within /{interaction.command.name}: {error = }, user = {interaction.user.name}")
        if type(error) == app_commands.MissingRole:
            missing_role = (interaction.guild.get_role(error.missing_role))
            embed = EmbedBuilder.error_embed(desc=f'The following error has occured:\n/{interaction.command.name} requires you to have Role: {missing_role.mention}', username=interaction.user.name)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            pxlcoarl = interaction.guild.get_member(261118995464192000)
            embed = EmbedBuilder.error_embed(desc=f'The following error has occured:\n{error}', username=interaction.user.name)
            await interaction.response.send_message(f'Please dm {pxlcoarl.mention} with a screenshot of this message!', embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ExceptionHandler(bot))