from utilities import logger
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpVariable, LpInteger
import pulp
from .helpers import get_faceit_elo
import sqlite3


async def get_players(uuid):
    db_path = 'static/app.db'
    players = []
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT discord_id FROM queue WHERE uuid = ?", (uuid,))
        result = cursor.fetchall()
        for id in result:
            cursor.execute("SELECT steam_id64 FROM user_links WHERE discord_id = ?", id)
            result = cursor.fetchone()
            steam_id = result[0]
            faceit_elo = await get_faceit_elo(steam_id)
            players.append((id[0], faceit_elo))
            
    return players


async def appoint_teams(players):
    num_players = len(players)
    num_teams = 2
    players_per_team = num_players // num_teams
    # Create LP problem
    prob = LpProblem("TeamBalancing", LpMinimize)
    # Decision variables
    x = {(i, j): LpVariable(f"x_{i}_{j}", 0, 1, LpInteger) for i in range(num_players) for j in range(num_teams)}
    z = LpVariable("z", 0)
    # Objective function
    prob += z, "Objective"
    # Constraints
    for i in range(num_players):
        prob += lpSum(x[i, j] for j in range(num_teams)) <= 1  # Each player assigned to only one team
    for j in range(num_teams):
        prob += lpSum(x[i, j] for i in range(num_players)) == players_per_team  # Each team should ideally have 5 players
    for j in range(num_teams):
        prob += (lpSum(players[i][1] * x[i, j] for i in range(num_players)) / players_per_team) - z <= z  # Minimize the difference in average Elo
    # Solve the problem
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    # Extract results
    indexes = {j: [i for i in range(num_players) if x[i, j].value() == 1] for j in range(num_teams)}
    teams_temp = {j: [players[i] for i in team_indices] for j, team_indices in indexes.items()}
    avg_elo = {j: sum(players[i][1] for i in indexes[j]) / players_per_team for j in range(num_teams)}
    teams = {j: {'team_members': teams_temp[j], 'avg_elo': avg_elo[j]} for j in teams_temp}
    
    return teams
    
        
    