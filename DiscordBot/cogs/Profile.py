from discord import Interaction, app_commands, Embed, Color, TextStyle
from discord.ext import commands
from discord.ui import View, Button, Select, Modal, TextInput, button, select
from main import PugBot
from typing import List, Dict, Type, Literal
from datetime import datetime
from utilities import AppSettings, logger, DataBaseUtils
from xml.etree import ElementTree as ET
import requests, re, json


from icecream import ic


async def setup(bot: PugBot):
    await bot.add_cog(Profile(bot), guilds=AppSettings().guilds)
    
    
class Profile(commands.Cog):
    def __init__(self, bot: PugBot) -> None:
        self.bot = bot
 
    @app_commands.command(name='profile', description='Open the user profile interface')
    async def profile(self, interaction: Interaction) -> None:
        with DataBaseUtils().Session() as session:
            user = session.query(DataBaseUtils().User).filter(DataBaseUtils().User.discord_id == str(interaction.user.id)).first()
            if user:
                embed = Embed(title=f'{interaction.user.display_name}', description=f'', color=Color.dark_magenta(), timestamp=datetime.now())
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                embed.add_field(name='Linked Steam Account:', value=f'Steam Name: {user.steam_name}\nProfile Link: {user.steam_url}\nSteamID64: {user.steam_id64}')
                await interaction.response.send_message(embed=embed, ephemeral=True, view=ProfileView(timeout=None))
                return
            else:
                embed = Embed(title=f'Create Profile', description=f'', color=Color.dark_magenta(), timestamp=datetime.now())
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                await interaction.response.send_message(embed=embed, ephemeral=True, view=CreateProfile(timeout=None))
                return
        return
    
class ProfileView(View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
    
    @button(label='Update steam url')
    async def update_steam(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(InputProfileData(title='Enter your steam profile url', timeout=None, custom_id='steam_url'))


class CreateProfile(View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        
    @button(label='➕ Create Profile')
    async def create_profile(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(InputProfileData(title='Enter your steam profile url', timeout=None, custom_id='steam_url'))
        
        
class InputProfileData(Modal):
    def __init__(self, *, title: str = ..., timeout: float | None = None, custom_id: str = ...) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        
    steam_url = TextInput(label='Steam url', style=TextStyle.short, placeholder='https://steamcommunity.com/id/example/', required=True)
    
    @classmethod
    def get_steamid(self, *, url: str) -> List[str]:
        patterns = [
            r'https://steamcommunity.com/profiles/(\d+)',
            r'https://steamcommunity.com/id/([^/]+)'
        ]
        for pattern in patterns:
            match = re.match(pattern, url)
            if match:
                if pattern == patterns[0]:
                    steam_id64 = match.group(1)
                    api_url = f'https://steamcommunity.com/profiles/{steam_id64}/?xml=1'
                    try:
                        response = requests.get(api_url)
                        response.raise_for_status()
                        xml_data = ET.fromstring(response.text)
                        steam_name = xml_data.find('.//steamID').text
                        return [steam_id64, steam_name]
                    except Exception as error:
                        logger.error(f'{error = }')
                        return False
                else:
                    custom_id = match.group(1)
                    api_url = f'https://steamcommunity.com/id/{custom_id}/?xml=1'
                    try:
                        response = requests.get(api_url)
                        response.raise_for_status()
                        xml_data = ET.fromstring(response.text)
                        steam_id64 = xml_data.find('.//steamID64').text
                        steam_name = xml_data.find('.//steamID').text
                        return [steam_id64, steam_name]
                    except AttributeError as error:
                        return False
                    except Exception as error:
                        logger.error(f'{error = }')
                        return False
        return False
    
    async def on_submit(self, interaction: Interaction) -> None:
        db = DataBaseUtils()
        await interaction.response.defer()
        steam_data = self.get_steamid(url=self.steam_url.value)
        if not steam_data:
            await interaction.followup.send(f'`{self.steam_url.value}` does not appear to be a valid steam url. Please try again.', ephemeral=True)
            return
        with db.Session() as session:
            existing_user = session.query(db.User).filter_by(steam_id64=steam_data[0]).first()
        if existing_user:
            await interaction.followup.send(f'The Steam profile with steamID64 `{steam_data[0]}` is already claimed by <@{existing_user.discord_id}>.', ephemeral=True)
            return
        db.manage_user(discord_id=interaction.user.id, discord_name=interaction.user.display_name, steam_id64=steam_data[0], steam_url=self.steam_url.value, steam_name=steam_data[1])
        with db.Session() as session:
            user = session.query(db.User).filter(db.User.discord_id == str(interaction.user.id)).first()
            if user:
                embed = Embed(title=f'{interaction.user.display_name}', description=f'', color=Color.dark_magenta(), timestamp=datetime.now())
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                embed.add_field(name='Linked Steam Account:', value=f'Steam Name: {user.steam_name}\nProfile Link: {user.steam_url}\nSteamID64: {user.steam_id64}')
                await interaction.edit_original_response(embed=embed, view=ProfileView(timeout=None))