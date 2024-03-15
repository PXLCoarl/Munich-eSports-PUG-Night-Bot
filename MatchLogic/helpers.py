import sqlite3, os, requests, random
from utilities import logger
from discord import Interaction
db_path = 'static/app.db'

async def get_faceit_elo(steam_id):
    FACEIT_TOKEN = os.getenv("FACEIT_TOKEN")
    header = {
        "Authorization": f"Bearer {FACEIT_TOKEN}",
        "Accept": "application/json"
        }
    response = requests.get(f"https://open.faceit.com/data/v4/players?game=cs2&game_player_id={steam_id}", headers=header)
    if response.status_code == 200:
        data = response.json()
        faceit_elo = data.get("games", {}).get("cs2", {}).get("faceit_elo", 800)
    else:
        faceit_elo = 800
    return faceit_elo


async def insert_teams(uuid, teams, interaction: Interaction):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            for discord_id,_ in teams[0]['team_members']:
                team_flag = '1'
                member = await interaction.guild.fetch_member(discord_id)
                cursor.execute("INSERT INTO teams (uuid, name, discord_id, team_flag) VALUES (?, ?, ?, ?)", (uuid, member.name, discord_id, team_flag))
            for discord_id,_ in teams[1]['team_members']:
                team_flag = '2'
                member = await interaction.guild.fetch_member(discord_id)
                cursor.execute("INSERT INTO teams (uuid, name, discord_id, team_flag) VALUES (?, ?, ?, ?)", (uuid, member.name, discord_id, team_flag))
            conn.commit()
        return True
    except Exception as e:
        logger.error(e)
        return False
    
async def create_json():
    pass



async def fetch_random_captain(uuid, team_flag):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, discord_id FROM teams WHERE uuid = ? AND team_flag = ?", (uuid, team_flag))
        result = cursor.fetchall()
    if result:
        name, discord_id = random.choice(result)
    return (name, discord_id)


async def fetch_team(uuid, team_flag):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, discord_id FROM teams WHERE uuid = ? AND team_flag = ?", (uuid, team_flag))
        result = cursor.fetchall()
    team = []
    if result:
        for row in result:
            team.append(row[0])
    return team


def insert_mappool(uuid, map_pool):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        for map in map_pool:
            cursor.execute("INSERT INTO map_pool (uuid, map) VALUES (?, ?)", (uuid, map))
        conn.commit()
        
def fetch_mappool(uuid):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT map FROM map_pool WHERE uuid = ?", (uuid,))
        result = cursor.fetchall()
        map_pool = [obj[0] for obj in result]
    return map_pool

async def remove_map(uuid, map):
     with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM map_pool WHERE uuid = ? AND map = ?", (uuid, map))
        conn.commit()
        
async def fetch_captains(uuid):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT discord_id FROM teams WHERE uuid = ? AND team_flag = 1 AND captain_flag = 1", (uuid,))
        team1_captain = cursor.fetchone()
        cursor.execute("SELECT discord_id FROM teams WHERE uuid = ? AND team_flag = 2 AND captain_flag = 1", (uuid,))
        team2_captain = cursor.fetchone()
        
    return team1_captain[0], team2_captain[0]

async def fetch_voting_team(uuid):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT voting_team FROM match WHERE uuid = ?", (uuid,))
        result = cursor.fetchone()
        if result[0] != None:
            return result[0]
        else:
            return 1

async def insert_voting_team(uuid, voting_team):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE match SET voting_team = ? WHERE uuid = ?", (voting_team, uuid))
        conn.commit()
        
