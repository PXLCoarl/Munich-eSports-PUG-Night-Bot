from discord.ui import View, Select
from discord import SelectOption, Interaction, Embed
from .helpers import fetch_mappool, insert_mappool, remove_map, fetch_captains, fetch_voting_team, insert_voting_team
from .match import match_json
from utilities import get_servers, query_servers, fetch_server_data, push_match
from DiscordBot import EmbedBuilder
from typing import Any

#i know it is ugly
def toggle_voting_team(current_voting_team: int) -> int:
    return 1 if current_voting_team == 2 else 2

class VoteView(View):
    def __init__(self, uuid, placeholder):
        super().__init__(timeout=None)
        self.add_item(VoteSelect(uuid, placeholder))
        
class VoteSelect(Select):
    def __init__(self, uuid, placeholder):
        maps = fetch_mappool(uuid=uuid)
        options = [SelectOption(label=cs_map, description=f'Map {cs_map}') for cs_map in maps]
        super().__init__(placeholder=placeholder, max_values=1, min_values=1, options=options, custom_id='vote')
        
    async def callback(self, interaction:Interaction):
        await interaction.response.defer()
        uuid = interaction.message.embeds[0].footer.text
        map_pool = fetch_mappool(uuid=uuid)
        voted_map = interaction.data['values'][0]
        embed = interaction.message.embeds[0]
        voting_team = await fetch_voting_team(uuid=uuid)
        captain1, captain2 = await fetch_captains(uuid=uuid)
        
        async def update_embed(embed: Embed, value):
            if len(embed.fields) < 3:
                embed.add_field(name='', value=f'```{value}```', inline=False)
            else:
                updated_value = f'{embed.fields[2].value[:-3]}\n{value}```'
                embed.set_field_at(2, name='', value=f'{updated_value}', inline=False)
        
        if voting_team == 1 and interaction.user.id != int(captain1):
            embed = EmbedBuilder.error_embed(title="PUG | Warning", desc='It\'s not your turn to vote!\nOnly Team 1 captain may vote', username=interaction.user.name)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        elif voting_team == 2 and interaction.user.id != int(captain2):
            embed = EmbedBuilder.error_embed(title="PUG | Warning", desc='It\'s not your turn to vote!\nOnly Team 2 captain may vote', username=interaction.user.name)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if len(map_pool) != 1:
            await remove_map(uuid=uuid, map=voted_map)
            value = f'{interaction.user.name} banned: {voted_map}'
            await update_embed(embed, value)
            placeholder = 'Pick a map' if len(map_pool) == 2 else 'Ban a map'
            await interaction.message.edit(embed=embed, view=VoteView(uuid=uuid, placeholder=placeholder))
        else: #This happens if the match actually starts
            serverlist = await get_servers()
            server_id = await query_servers(serverlist)
            server_details: dict[str, Any] = await fetch_server_data(server_id=server_id)           
            match_id = await match_json(uuid=uuid)
            await push_match(server_id=server_id, match_id=match_id)
            value = f'```{interaction.user.name} picked: {voted_map}```'
            embed.add_field(name="", value=value, inline=False)
            embed.add_field(
                name='Server details:',
                value=(f'||```connect {server_details["IP"]}:{server_details["PORT"]}; password {server_details["PASSWD"]}```||Copy this into your cs2 console to connect to the pug.'
                    if server_details["PASSWD"] != ''
                    else f'||```connect {server_details["IP"]}:{server_details["PORT"]}```||Copy this into your cs2 console to connect to the pug.'),
                inline=False
            )
            await interaction.message.edit(embed=embed, view=None)
            
        voting_team = toggle_voting_team(voting_team)
        await insert_voting_team(uuid=uuid, voting_team=voting_team)
