from utilities import logger, DBOps, generic_rcon, fetch_server_data, query_servers, get_servers, get_appsettings
from discord import Interaction, app_commands, ButtonStyle, Object
from discord.ext import commands
from discord.ui import Button, View
from DiscordBot import EmbedBuilder
import uuid, sqlite3, json


async def setup(bot):
    await bot.add_cog(PUG(bot), guilds=[Object(id=1019608824023371866), Object(id=841127630564622366), Object(id=615552039027736595)])

async def send_error_response(interaction: Interaction, error:str) -> None:
        embed = EmbedBuilder.error_embed(desc=error, username=interaction.user.name)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
class PUG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pug_embed = None

    appsettings = get_appsettings()

    @app_commands.command(name="pug", description="starts a pug queue")
    @app_commands.checks.has_any_role(*appsettings['roles'])
    async def pug(self, interaction: Interaction):
        from icecream import ic
        servers = await get_servers()
        if servers == []:
            await send_error_response(interaction=interaction, error='No server data found. Check servers.json for mistakes.')
            return
        
        serverid = await query_servers(servers)
        if serverid == -1:
            await send_error_response(interaction=interaction, error='No free server available. Please wait for another match to finish or check servers.json for mistakes.')
            return
        
        server_info = await fetch_server_data(serverid)
        if server_info is None:
            await send_error_response(interaction=interaction, error='No server data found. Check servers.json for mistakes.')
            return
        
        response = json.loads(await generic_rcon(server_info['IP'], server_info['RCON_PORT'], server_info['RCON_PASSWD'], command='get5_status', name='PreQueue Server Query')) 
        
        if response is None or response.get('gamestate') != 'none':
            await send_error_response(interaction=interaction, error="No free server available. Please wait for another match to finish or check servers.json for mistakes.")
            return
        
        logger.info(f'A new queue was started by {interaction.user.name}')
        
        match_uuid = str(uuid.uuid4())
        
        if not await DBOps.insert_match_data(data=(match_uuid,)):
            await send_error_response(interaction=interaction, error="An error occurred. Please contact <@261118995464192000>")
            return
        
        match_data = await DBOps.get_match_id(query_value=match_uuid)
        if not match_data:
            await send_error_response(interaction=interaction, error="An error occurred. Please contact <@261118995464192000>")
            return
        
        match_id = match_data[0]
        embed = EmbedBuilder.default_embed(match_id=match_id, desc="Ready to join the queue? Simply press the button below, and don't forget to ensure your Steam account is linked!", match_uuid=match_uuid)
        embed.add_field(name='People in Queue:', value='', inline=False)
        
        await interaction.response.send_message(embed=embed, view=QueueView())
        message = await interaction.original_response()
        message_id = message.id
        await DBOps.insert_message_id(match_id=match_id, values=message_id)
        
        
        
        '''
        # Deprecated
        if server_info is not None:
            response = json.loads(await generic_rcon(server_info['IP'], server_info['RCON_PORT'], server_info['RCON_PASSWD'], command='get5_status', name='PreQueue Server Query'))
        else:
            response = None
        if response is not None and response['gamestate'] == 'none':
            logger.info(f"A new queue was started by {interaction.user.name}")
            match_uuid = str(uuid.uuid4())
            if await DBOps.insert_match_data(data=(match_uuid,)) is False:
                embed = EmbedBuilder.error_embed(title='PUG | Error', desc='An error has occured.\nPlease contact <@261118995464192000>', username=interaction.user.name)
                await interaction.response.send_message(embed=embed)        
            else:
                data = await DBOps.get_match_id(query_value=match_uuid)
                if data is not []:
                    id = data[0]
                    #deprecated embed = EmbedBuilder.build_embed(title=f"PUG | Queue #{id}", desc="Ready to join the queue? Simply press the button below, and don't forget to ensure your Steam account is linked!", username=match_uuid)
                    embed = EmbedBuilder.default_embed(match_id=id, desc="Ready to join the queue? Simply press the button below, and don't forget to ensure your Steam account is linked!", match_uuid=match_uuid)
                    embed.add_field(name='People in Queue:', value='', inline=False)
                    await interaction.response.send_message(embed=embed, view=QueueView())
                    message = await interaction.original_response()
                    message_id = message.id
                    await DBOps.insert_message_id(match_id=id, values=message_id)  
                else:
                    embed = EmbedBuilder.error_embed(title='PUG | Error', desc='An error has occured.\nPlease contact <@261118995464192000>', username=interaction.user.name)
                    await interaction.response.send_message(embed=embed)
        else:
            embed = EmbedBuilder.error_embed(title='PUG | Error', desc='No free server available.\nPlease wait for another match to finish or check servers.json for mistakes.', username=interaction.user.name)
            await interaction.response.send_message(embed=embed, ephemeral=True)'''
            
            
            
        
class QueueView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(QueueButton(label='Join', style=ButtonStyle.green, id='Join'))
        self.add_item(QueueButton(label='Leave', style=ButtonStyle.red, id='Leave'))
        #self.add_item(QueueButton(label='FS', style=ButtonStyle.grey, id='FS')) #just for debugging!
        
        
class QueueButton(Button):
    def __init__(self, label, style, id):
        super().__init__(label=label, style=style)
        self.id = id
        
    async def callback(self, interaction: Interaction):
        if self.id == 'Join':
            await interaction.response.defer()
            await join(interaction)
        
        if self.id == 'Leave':
            await interaction.response.defer()
            await leave(interaction)

        # Should not be used, thats why i didnt bother to clean up the code and make it functional
        if self.id == 'FS':
            appsettings = get_appsettings()
            for priv_role in appsettings['roles']:
                from icecream import ic
                ic(priv_role)
                role = interaction.guild.get_role(priv_role)
                ic(role)
                if role in interaction.user.roles:
                    await interaction.response.defer()
                    await force_start(interaction)
                    embed = EmbedBuilder.error_embed(title="PUG | Error", desc='Need at least 2 people in queue', username=interaction.user.name)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    return
                    '''embed = EmbedBuilder.error_embed(title="PUG | Error", desc='You need to be \'Pug Leader\' to use this button!', username=interaction.user.name)
                    await interaction.response.send_message(embed=embed, ephemeral=True)'''
                
                
                
async def join(interaction: Interaction):
    username = interaction.user.name
    userid = interaction.user.id
    match_uuid = interaction.message.embeds[0].footer.text
    
    db_path = 'static/app.db'
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Check if user has linked their steam account
        cursor.execute("SELECT steam_id64 FROM user_links WHERE discord_id = ?", (userid,))
        result = cursor.fetchone()
        
        if not result:
            error_embed = EmbedBuilder.error_embed(title="PUG | Error", desc='You need to link your steam account first in order to join the queue!\nUse /steam to link your steam account', username=username)
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return
            
        # Check if user is already in the queue
        cursor.execute("SELECT discord_id FROM queue WHERE uuid = ?", (match_uuid,))
        result = cursor.fetchall()
        discord_ids = [int(tpl[0]) for tpl in result]      
        if not userid in discord_ids:
            # Insert user into the queue
            cursor.execute("INSERT INTO queue (uuid, name, discord_id) VALUES (?, ?, ?)", (match_uuid, username, userid))
            conn.commit()
            logger.info(f"{username} joined the queue")
            
            cursor.execute("SELECT name FROM queue WHERE uuid = ?", (match_uuid,))
            result = cursor.fetchall()
            embed_names = [name[0] for name in result]
            formatted_names = '\n'.join(embed_names)
            embed = interaction.message.embeds[0]
            embed.set_field_at(0,
                               name='People in Queue:',
                               value=formatted_names
                               )
            await interaction.edit_original_response(embed=embed)
            
            #check for number of user in queue
            cursor.execute("SELECT COUNT(*) FROM queue WHERE uuid = ?", (match_uuid, ))
            result = cursor.fetchone()[0]
            logger.info(f"{result} user are currently in queue with the id {match_uuid}")
            if result >= 10:
                await interaction.edit_original_response(view=None)
                from MatchLogic import handle_match
                await handle_match(uuid=match_uuid, interaction=interaction)
             
        else:
            embed = EmbedBuilder.error_embed(title="PUG | Error", desc='You are already in the queue', username=username)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
           

async def leave(interaction: Interaction):    
    username = interaction.user.name
    userid = interaction.user.id
    match_uuid = interaction.message.embeds[0].footer.text
    db_path = 'static/app.db'
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT discord_id FROM queue WHERE uuid = ?", (match_uuid,))
        result = cursor.fetchall()
        
        discord_ids = [int(tpl[0]) for tpl in result]      
        if not userid in discord_ids:
            embed = EmbedBuilder.error_embed(title="PUG | Error", desc='You are not in the queue', username=username)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        cursor.execute("DELETE FROM queue WHERE discord_id = ? AND uuid = ?", (userid, match_uuid))
        conn.commit()
        
        cursor.execute("SELECT name FROM queue WHERE uuid = ?", (match_uuid,))
        result = cursor.fetchall()
        embed_names = [name[0] for name in result]
        formatted_names = '\n'.join(embed_names)
        embed = interaction.message.embeds[0]
        embed.set_field_at(0,
                            name='People in Queue:',
                            value=formatted_names
                            )
        logger.info(f"{username} left the queue")
        await interaction.edit_original_response(embed=embed)
        
        
async def force_start(interaction: Interaction):
    match_uuid = interaction.message.embeds[0].footer.text
    
    db_path = 'static/app.db'
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM queue WHERE uuid = ?", (match_uuid, ))
        result = cursor.fetchone()[0]
        if not result >= 2:
            return
        
    from MatchLogic import handle_match
    await interaction.edit_original_response(view=None)
    await handle_match(uuid=match_uuid, interaction=interaction)