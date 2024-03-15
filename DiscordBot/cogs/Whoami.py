import discord, sqlite3, requests
from discord.ext import commands
from discord import app_commands
from DiscordBot import EmbedBuilder
from xml.etree import ElementTree as ET


class WhoAmI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="whoami", description="Shows information about the currently linked steam account")
    async def steam(self, interaction: discord.Interaction):
        username = interaction.user.name
        userid = interaction.user.id
        with sqlite3.connect('static/app.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT steam_id64 FROM user_links WHERE discord_id = ?", (userid,))
            result = cursor.fetchone()
            if result:
                steamid = result[0] 
            else:
                steamid = None   
        api_url = f'https://steamcommunity.com/profiles/{steamid}/?xml=1'
        if steamid is not None:
            try:
                response = requests.get(api_url)
                response.raise_for_status()
                xml_data = ET.fromstring(response.text)
                steamName = xml_data.find('.//steamID').text
                icon = xml_data.find('.//avatarMedium').text
                
            except requests.RequestException as e:
                pass
            embed = EmbedBuilder.build_embed(
                title='Linked Steam Account',
                desc=f'{steamName}',
                username=username
                )
            embed.set_thumbnail(url=icon)
            embed.url = f"https://steamcommunity.com/profiles/{steamid}/"
        else:
            embed = EmbedBuilder.build_embed(
            title='No Steam Account Linked',
            desc=f'use /steam to link your account',
            username=username
        )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        
        
        
        
async def setup(bot):
    await bot.add_cog(WhoAmI(bot),guilds=[discord.Object(id=1019608824023371866), discord.Object(id=841127630564622366), discord.Object(id=615552039027736595)])