import json, sqlite3
from .helpers import fetch_mappool, fetch_team, fetch_captains


async def match_json(uuid):
    mappool = fetch_mappool(uuid)
    with sqlite3.connect('static/app.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM match WHERE uuid = ?", (uuid,))
        match_id = cursor.fetchone()[0]
        cursor.execute("SELECT name, discord_id FROM teams WHERE uuid = ? AND team_flag = ?", (uuid, 1))
        result = cursor.fetchall()
        team1 = []
        if result:
            for row in result:
                team1.append(row)
        cursor.execute("SELECT name, discord_id FROM teams WHERE uuid = ? AND team_flag = ?", (uuid, 2))
        result = cursor.fetchall()
        team2 = []
        if result:
            for row in result:
                team2.append(row)
        team1_players = {}
        for name, id in team1:
                cursor.execute("SELECT steam_id64 FROM user_links WHERE discord_id = ?", (id,))
                result = cursor.fetchone()
                steam_id = result[0]
                team1_players[steam_id] = name
        team2_players = {}
        for name, id in team2:
                cursor.execute("SELECT steam_id64 FROM user_links WHERE discord_id = ?", (id,))
                result = cursor.fetchone()
                steam_id = result[0]
                team2_players[steam_id] = name
                
        cursor.execute("SELECT name FROM teams WHERE uuid = ? AND team_flag = 1 AND captain_flag = 1", (uuid,))
        captain1 = cursor.fetchone()[0]
        cursor.execute("SELECT name FROM teams WHERE uuid = ? AND team_flag = 2 AND captain_flag = 1", (uuid,))
        captain2 = cursor.fetchone()[0]
            
    data = {
        "matchid": f"{match_id}",
        "team1": {
            "name": f"Team_{captain1}",
            "players": team1_players
        },
        "team2": {
            "name": f"Team_{captain2}",
            "players": team2_players
        },
        "num_maps": int(len(mappool)),
        "maplist": mappool,
        "map_sides": [
            "team1_ct",
            "team2_ct",
            "knife"
        ],
        "spectators": {
            "players": {}
        },
        "clinch_series": True,
        "players_per_team": 5,
        "cvars": {
            "hostname": f"FPN: Team_{captain1} vs Team_{captain2} #{match_id}",
            "mp_friendlyfire": "0"
        }
    }
    
    with open(f"api/matches/match_{match_id}.json", 'w') as match_file:
        json.dump(data, match_file, indent=4)
        
    return match_id