from discord import Interaction, SelectOption
from discord.ui import View, Select
from .teams import get_players, appoint_teams
from .helpers import insert_teams, create_json, fetch_random_captain, fetch_team, fetch_mappool, insert_mappool
from .views import VoteView
from utilities import logger, MapPools
import re, sqlite3



async def handle_match(uuid, interaction: Interaction):
    map_pools = MapPools()
    insert_mappool(uuid=uuid, map_pool=map_pools.active_duty)
    players = await get_players(uuid=uuid)
    teams = await appoint_teams(players=players)
    if not await insert_teams(uuid=uuid, teams=teams, interaction=interaction):
        return
    
    captain1 = await fetch_random_captain(uuid=uuid, team_flag='1')
    captain2 = await fetch_random_captain(uuid=uuid, team_flag='2')
    team1 = await fetch_team(uuid=uuid, team_flag='1')
    team2 = await fetch_team(uuid=uuid, team_flag='2')
    
    with sqlite3.connect('static/app.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE teams SET captain_flag = 1 WHERE uuid = ? AND discord_id = ?", (uuid, captain1[1]))
        cursor.execute("UPDATE teams SET captain_flag = 1 WHERE uuid = ? AND discord_id = ?", (uuid, captain2[1]))
        conn.commit()
        
    embed = interaction.message.embeds[0]
    title = embed.title
    new_title = re.sub(r'Queue', r'Match', title)
    embed.title = new_title
    embed.description = ''
    embed.set_field_at(0,
                       name=f"**Team {captain1[0]}**",
                       value=f"```Average elo: {int(teams[0]['avg_elo'])}```" +
                       '```' +
                        '\n'.join([f'- {name}' for name in team1]) +
                        '```',
                        inline=True
                       )
    embed.add_field(
        name=f'**Team {captain2[0]}**', 
        value=f'```average elo: {int(teams[1]["avg_elo"])}```' +
        '```' +
        '\n'.join([f'- {name}' for name in team2]) +
        '```', 
        inline=True
        )
    await interaction.edit_original_response(embed=embed, view=VoteView(uuid=uuid, placeholder='Ban a map'))