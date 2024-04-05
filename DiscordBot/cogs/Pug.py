from discord import app_commands, Interaction, ButtonStyle, Embed
from discord.app_commands import Choice
from discord.ext import commands
from discord.ui import Button, View, button, select
from utilities import Embeds, AppSettings, RconUtils, DataBaseUtils, MapPools, logger, Player, Match_Handler
from main import PugBot
from typing import Literal
from icecream import ic
import uuid

async def setup(bot: PugBot):
    await bot.add_cog(Pug(bot), guilds=AppSettings().guilds)



class Pug(commands.Cog):
    def __init__(self, bot: PugBot) -> None:
        self.bot = bot

    async def send_error_response(self, interaction: Interaction, error: str) -> None:
        embed = Embeds(match_id=-1, match_uuid='error').error
        embed.description = error
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='pug', description='start a pug')
    @app_commands.checks.has_any_role(*AppSettings().roles)
    async def pug(self, interaction: Interaction, map_pool: Literal['Active duty', 'All maps'], mode: Literal['BO1', 'BO3', 'BO5']):
        # Literal['Active duty', 'All maps', 'Mapcore'] MatchHandler cant Handle Map Core (yet). Ironic lol
        match map_pool:
            case 'Mapcore':
                maps = MapPools.MAPCORE_LIST
            case 'Active duty':
                maps = MapPools.ACTIVE_DUTY
            case 'All maps':
                maps = MapPools.ALL_MAPS
              
        SERVER_ID: int = await RconUtils().get_free_server()
        if SERVER_ID == -1:
            await self.send_error_response(interaction=interaction, error='No free server available. Please wait for another match to finish or check servers.json for mistakes.')
            logger.error(f'{interaction.user.name} tried to start a queue, but no server was available.')
            return
        
        logger.info(f'A new queue was started by {interaction.user.display_name}')
        match_uuid: str = str(uuid.uuid4())
        match_id = DataBaseUtils().create_match(match_uuid=match_uuid, map_pool=[str(map) for map in maps])
        
        embed = Embeds(match_id=match_id, match_uuid=match_uuid).queue
        embed.add_field(name='Queue Members:', value='', inline=False)
        
        await interaction.response.send_message(embed=embed, view=QueueView(timeout=None, match_uuid=match_uuid, mode=mode, map_pool=map_pool))


class QueueView(View):
    def __init__(self, *, timeout: float | None = 180, match_uuid: str, mode: str, map_pool: str):
        self.map_pool = map_pool
        self.mode = mode
        self.match_uuid = match_uuid
        super().__init__(timeout=timeout)


    async def send_error_response(self, interaction: Interaction, error: str) -> None:
        embed = Embeds(match_id=-1, match_uuid='error').error
        embed.description = error
        await interaction.followup.send(embed=embed, ephemeral=True)


    @button(label='Join', style=ButtonStyle.green)
    async def join(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        db = DataBaseUtils()
        
        username = interaction.user.display_name
        userid = interaction.user.id
        match_uuid = self.match_uuid #match_uuid = interaction.message.embeds[0].footer.text
        
        if not db.query_user(userid=userid):
            await self.send_error_response(interaction=interaction, error='You dont have a profile yet.\nUse </profile:1224853196988616825> to create one.')
            return
        
        if db.query_queue_for_player(match_uuid=match_uuid, userid=userid):
            # Player is already in Queue
            return
        
        if not db.insert_player(match_uuid=match_uuid, userid=userid, username=username):
            # Handle this error (Something went wrong during inserting a name into the database)
            return
        logger.info(f"{username} joined queue #'{match_uuid}'.")
        names = db.get_queue_names(match_uuid=match_uuid)
        if not names:
            # Handle this error (Something went wrong during fetching the names from the database)
            return
        
        embed = interaction.message.embeds[0]
        embed.set_field_at(
            0,
            name='Queue members:',
            value='\n'.join(names)
        )
        await interaction.edit_original_response(embed=embed)

        with db.Session() as session:
            player = len(session.query(Player).filter(Player.match_uuid == match_uuid).all())
        if player >= 10:
            await interaction.edit_original_response(view=None)
            # Handle the match
            # Use self.match_uuid and self.mode


    @button(label='Leave', style=ButtonStyle.danger)
    async def leave(self, interaction: Interaction, button: Button):
        db = DataBaseUtils()
        await interaction.response.defer()

        username = interaction.user.display_name
        userid = interaction.user.id
        match_uuid = self.match_uuid
        
        if not db.query_queue_for_player(match_uuid=match_uuid, userid=userid):
            # Player is not in Queue
            return
        names = db.remove_player(match_uuid=match_uuid, userid=userid)
        if names is None and not []:
            # Handle this error (Something went wrong removing a player from the queue)
            return
        logger.info(f"{username} left queue #'{match_uuid}'.")
        embed: Embed = interaction.message.embeds[0]
        embed.set_field_at(
            0,
            name='Queue members:',
            value='\n'.join(names)
        )
        await interaction.edit_original_response(embed=embed)


    @button(label='Force Start', style=ButtonStyle.grey, disabled=True)
    async def fs(self, interaction: Interaction, button: Button):
        interaction.response.defer()
        # Handle Debug Start (do i even bother i wonder)
        raise NotImplementedError('I cant bother.')