from discord.ext import commands
from DiscordBot import EmbedBuilder
from utilities import logger, generic_rcon, fetch_server_data, get_server_ids
from discord import app_commands, Interaction, Object
from typing import Literal
from utilities import get_appsettings
import json



class RCON(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    appsettings = get_appsettings()
        
    @app_commands.command(name='rcon', description='Send an RCON command to a server')
    @app_commands.choices(server_id=[app_commands.Choice(name=f'Server #{id}', value=id) for id in get_server_ids()])
    @app_commands.checks.has_any_role(*appsettings['roles'])
    @app_commands.describe(mode='The RCON command you want to send', server_id='The server you want to target')
    async def server_rcon(self, interaction: Interaction, mode: Literal['gamestate', 'end_match', 'debug'], server_id: int) -> None:
        match mode:
            case 'gamestate':
                server_data = await fetch_server_data(server_id)
                response = json.loads(await generic_rcon(server_data['IP'], server_data['RCON_PORT'], server_data['RCON_PASSWD'], command='get5_status', name=f'/server gamestate #{server_id}'))
                gamestate = response['gamestate']
                if gamestate == 'none':
                    gamestate = 'available'
                embed = EmbedBuilder.info_embed(desc=f'Server #{server_id}\'s current state is:\n{gamestate}', username=interaction.user.name)
                logger.info(f"{interaction.user.name} queried the {mode} for Server #{server_id}")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
            case 'end_match':
                server_data = await fetch_server_data(server_id)
                response = await generic_rcon(server_data['IP'], server_data['RCON_PORT'], server_data['RCON_PASSWD'], command='get5_endmatch', name=f'/server force end match #{server_id}')
                embed = EmbedBuilder.info_embed(desc=f'Server response:\n{response}', username=interaction.user.name)
                logger.info(f"{interaction.user.name} force ended a match on Server #{server_id}")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
            case 'debug':
                if interaction.user.id != 261118995464192000:
                    embed = EmbedBuilder.error_embed(desc="You need to be <@261118995464192000> to use this mode!", username=interaction.user.name)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                server_data = await fetch_server_data(server_id)
                response = await generic_rcon(server_data['IP'], server_data['RCON_PORT'], server_data['RCON_PASSWD'], command='matchzy_loadmatch_url "https://pugs.pxlcoarl.de/api/matches/match_1.json', name=f'/debug #{server_id}')
                embed = EmbedBuilder.info_embed(f'Server response:\n{response}', username=interaction.user.name)
                logger.info(f"{interaction.user.name} startet a match on Server #{server_id}")
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        
        
        
        
        
async def setup(bot):
    await bot.add_cog(RCON(bot),guilds=[Object(id=1019608824023371866), Object(id=841127630564622366), Object(id=615552039027736595)])