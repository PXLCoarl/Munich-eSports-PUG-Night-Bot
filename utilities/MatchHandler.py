from .database import DataBaseUtils
from .Models import User
from .Runtime import AppSettings, MapPools
from .Embeds import Embeds
from discord import Interaction, SelectOption
from discord.ui import View, select, Select
from typing import List, Tuple, Dict
from statistics import mean
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpVariable, LpInteger, PULP_CBC_CMD

import requests, re


class VoteView(View):
    def __init__(self, *, timeout: float | None = None, options = List[SelectOption]):
        super().__init__(timeout=timeout)
        self.map_veto.options = options
        
    @select(cls=Select, placeholder='Select a map', options=[])
    async def map_veto(self, interaction: Interaction, select: Select):
        raise NotImplementedError()





'''
Shower Thoughts:
  - Make MatchHandler an extension of View, so i can implement the components directly into the class, might be worthwile - is at least worth a test
    Update: I tried it and it is so much better, faster and cleaner to implement. (FUCK)
'''

# To Do:
# - Delete this file and rewrite Pug.py (as in DebugBot)


class Match_Handler():
    def __init__(self, *, interaction: Interaction, match_uuid: str, mode: str, map_pool: str) -> None:
        self.map_pool = map_pool
        self.match_uuid = match_uuid
        self.interaction = Interaction
        self.mode = mode
        self.FACEIT_TOKEN = AppSettings().faceit_token
        self.db = DataBaseUtils()
        
        
    async def main(self):
        db = self.db
        match_id = db.get_match_id(match_uuid=self.match_uuid)
        interaction = self.interaction
        map_pool = self.map_pool
        match map_pool:
            case 'Mapcore':
                maps = MapPools.MAPCORE_LIST
            case 'Active duty':
                maps = MapPools.ACTIVE_DUTY
            case 'All maps':
                maps = MapPools.ALL_MAPS
        
        players = db.fetch_players(match_uuid=self.match_uuid)
        if not players:
            raise Exception('Cant process match: Players List is None')
        teams = await self.appoint_teams(players=players)
        team1 = teams.get('Team1'); team1_elo = int(mean(member[1] for member in team1))
        team2 = teams.get('Team2'); team2_elo = int(mean(member[1] for member in team2))
        embed = Embeds(match_id=match_id, match_uuid=self.match_uuid).lobby
        embed.add_field(
            name=f'**Team {team1[0][0].discord_name}**',
            value=f'```Average elo: {team1_elo}```' +
            '```' +
            "\n".join(f"-{member[0].discord_name}" for member in team1) +
            '```',
            inline=True            
        )
        embed.add_field(
            name=f'**Team {team2[0][0].discord_name}**',
            value=f'```Average elo: {team2_elo}```' +
            '```' +
            "\n".join(f"-{member[0].discord_name}" for member in team2) +
            '```',
            inline=True            
        )
        options = [SelectOption(label=re.sub(r'^[^_]+_', '', map).capitalize(), description=f'ban {map}') for map in maps]
        view = VoteView(options=options)
        await interaction.edit_original_response(embed=embed, view=view)
        
        
    
    
    async def get_faceit_elo(self, *, steam_id: str) -> int:
        header = {
            "Authorization": f"Bearer {self.FACEIT_TOKEN}",
            "Accept": "application/json"
        }
        response = requests.get(f"https://open.faceit.com/data/v4/players?game=cs2&game_player_id={steam_id}", headers=header)
        if response.status_code != 200:
            return 800
        else:
            try:
                data = response.json()
                elo = data.get("games", {}).get("cs2", {}).get("faceit_elo", 800)
                if elo is not None:
                    return elo
                else:
                    return 800
            except Exception as error:
                return 800        
        
        
    async def appoint_teams(self, *, players: List[User]) -> Dict[str, List[Tuple[User, int]]]:
        """Balance Teams by average Faceit elo

        Args:
            players (List[User]): A list of user instances loaded from the database

        Returns:
            Dict[str, List[Tuple[User, int]]]: A dictionary with the following format: {'Team{i}': List[Tuple[User, elo: int]] where i is either 1 or 2}
        """
        players_with_elo = [{'elo': self.get_faceit_elo(player.steam_id64), 'player': player} for player in players]
        
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
            prob += (lpSum(players_with_elo[i].get('elo') * x[i, j] for i in range(num_players)) / players_per_team) - z <= z  # Minimize the difference in average Elo
        # Solve the problem
        prob.solve(PULP_CBC_CMD(msg=False))
            
        teams: dict[str, List[Tuple[User, int]]] = {f'Team{i+1}': [] for i in range(num_teams)}
        for i in range(num_players):
            index = next(j for j in range(num_teams) if x[i, j].varValue == 1)
            teams[f'Team{index+1}'].append((players[i], players_with_elo[i].get('elo')))
                    
        return teams   
        
        
        
    