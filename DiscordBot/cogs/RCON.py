from discord.ext import commands
from discord import app_commands, Interaction
from utilities import logger, RconUtils, AppSettings, Embeds
from main import PugBot
from typing import Literal
from icecream import ic
import json

async def setup(bot: PugBot):
    await bot.add_cog(RCON(bot), guilds=AppSettings().guilds)


class RCON(commands.Cog):
    def __init__(self, bot: PugBot):
        self.bot = bot
        
    @app_commands.command(name='rcon', description='Send an RCON command to a server')
    @app_commands.choices(server_id = [app_commands.Choice(name=f'Server #{id}', value=id) for id, _ in RconUtils().servers.items()])
    @app_commands.checks.has_any_role(*AppSettings().roles)
    @app_commands.describe(mode='The RCON command you want to send', server_id='The server you want to target')
    async def server_rcon(self, interaction: Interaction, mode: Literal['gamestate', 'end_match', 'debug'], server_id: int) -> None:
        match mode:
            case 'gamestate':
                response = json.loads(await RconUtils().generic_rcon(server_id=server_id, command='get5_status', name=f'/rcon gamestate #{server_id}'))
                #ToDo: handle different kinds of gamestates (low prio, this also works well!)
                
                await interaction.response.send_message(embed=Embeds(match_id=-1, match_uuid='info', info=response).info, ephemeral=True)
            
            case 'end_match':
                _: dict = json.loads(await RconUtils().generic_rcon(server_id=server_id, command='get5_status', name=f'/rcon gamestate #{server_id}'))
                match_id: int = _.get('matchid')
                response: str | bool = await RconUtils().generic_rcon(server_id=server_id, command='get5_endmatch', name=f'/rcon endmatch #{server_id}')
                if response:
                    logger.warn(f'{interaction.user.display_name} force ended match #{match_id} on server #{server_id}')
                    await interaction.response.send_message(embed=Embeds(match_id=match_id, match_uuid='info', info=f'Ended match #{match_id} on server #{server_id}.\n{response = }').info, ephemeral=True)
                else:
                    embed = Embeds(match_id=-1, match_uuid='error').error
                    embed.description = f"Something went wrong trying to end the match on Server #{server_id}"
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            
            case 'debug':
                if interaction.user.id != 261118995464192000:
                    embed = Embeds(match_id=-1, match_uuid='error').error
                    embed.description = "You need to be <@261118995464192000> to use this mode!"
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                response = await RconUtils().generic_rcon(server_id=server_id, command="matchzy_loadmatch_url \"https://pugs.pxlcoarl.de/api/matches/match_debug.json\" ", name=f'/rcon debug #{server_id}')
                if response:
                    embed = Embeds(match_id=-1, match_uuid='info', info=response).info
                    logger.warn(f'{interaction.user.display_name} startet a match on server #{server_id}')
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed = Embeds(match_id=-1, match_uuid='error').error
                    embed.description = f"Something went wrong trying to push debug match onto server #{server_id}"
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                