import discord, re, requests
from discord.ext import commands
from discord import app_commands
from utilities import DBOps
from DiscordBot import EmbedBuilder
from xml.etree import ElementTree as ET



class AddUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('AddUser cog loaded.')
        
    @staticmethod
    def get_steam_id64_from_custom_url(custom_url):
        api_url = f'https://steamcommunity.com/id/{custom_url}/?xml=1'
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            xml_data = ET.fromstring(response.text)
            steam_id64 = xml_data.find('.//steamID64').text
            return steam_id64
        except requests.RequestException as e:
            print(f"Error retrieving SteamID64 for custom URL: {e}")
            return None

    @staticmethod
    def get_steam_id64_from_url(profile_url):
        # Define regular expressions for different profile URL formats
        patterns = [
            r'https://steamcommunity.com/profiles/(\d+)'
            ]

        # Check each pattern to find a match
        for pattern in patterns:
            match = re.search(pattern, profile_url)
            if match:
                return match.group(1)

        # If no numeric SteamID64 is found, consider the URL as a custom URL
        custom_url_match = re.search(r'https://steamcommunity.com/id/(\S+)', profile_url)
        if custom_url_match:
            custom_url = custom_url_match.group(1)
            steam_id64 = AddUser.get_steam_id64_from_custom_url(custom_url)
            return steam_id64

        # Return None if no match is found
        return None

    @app_commands.command(name="steam", description="link your steam profile to the bot")
    @app_commands.describe(url='Hyperlink to your steam profile. Example: \"https://steamcommunity.com/profiles/76561198315490909\"')
    async def steam(self, interaction: discord.Interaction, url: str):
        steam_id64 = AddUser.get_steam_id64_from_url(url)
        username = interaction.user.name
        discord_user_id = interaction.user.id

        if steam_id64:
            # If SteamID64 is found, push it into the database:
            await DBOps.save_user(discord_user_id, steam_id64)

            embed = EmbedBuilder.build_embed(
                title='Success',
                desc=f'Steam Profile \"{url}\"\nhas been linked to Discord Account with the name \"{username}\"',
                username=username
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            # If SteamID64 is not found, display an error message
            embed = discord.Embed(
                title='Error',
                description=f'Unable to retrieve SteamID64 for the provided Steam profile URL \"{url}\"',
                color=0xFF0000  # Red color for error
            )
            embed.set_footer(
            text=username
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(AddUser(bot),guilds=[discord.Object(id=1019608824023371866), discord.Object(id=841127630564622366), discord.Object(id=615552039027736595)])
