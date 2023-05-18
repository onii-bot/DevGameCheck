import discord
from discord.ext import commands
from discord import ui
from discord.interactions import Interaction
import requests
import json
from pymongo import MongoClient
import os

# Discord Intents
intents = discord.Intents.all()
intents.members = True

# MongoDB
client = MongoClient(os.environ["MONGO_TOKEN"])
db = client['discord']
collection = db['dev_steam']


client = commands.Bot(intents=intents, command_prefix='!')

def has_wishlisted(steam_id):
    steamLoginSecure = os.environ["STEAM_TOKEN"]
    devid = "2391300"
    testApi = f'https://store.steampowered.com/wishlist/profiles/{steam_id}/wishlistdata'

    # Set the cookie header
    header = 'steamLoginSecure=' + steamLoginSecure + ';'
    headers = {'Cookie': header}

    # Send the request
    responseObject = requests.get(testApi, headers=headers)
    jsonObject = json.loads(responseObject.content)
    if devid in list(jsonObject.keys()):
        return True
    return False

class PersistentViewBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix=commands.when_mentioned_or('!'), intents=intents)

    async def setup_hook(self) -> None:
        self.add_view(Menu())


class SteamModal(discord.ui.Modal, title="Steam ID"):
    steam_id = ui.TextInput(label="Enter your Steam ID: ", placeholder="Id", style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        steam_id = self.steam_id
        # Make a request to the Steam Web API to get the user's profile information
        response = requests.get(f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=CFBC5403952CC322EFCF72A2471C7AF1&steamids={steam_id}")
        data = response.json()

        # checking if steam account is already connected to discord
        user = collection.find_one({"steamid": str(steam_id)})
        if user:
            await interaction.response.send_message(content=f"This account is already connected to discord account with id {user['discordid']}", ephemeral=True)
            return

        # Check if the response contains the user's profile information
        if "response" in data and "players" in data["response"]:
            players = data["response"]["players"]
            if len(players) > 0:
                player = players[0]
                username = player.get("personaname")
                if username:
                    # if it is not connected
                    if has_wishlisted(steam_id):
                        userObj = interaction.user
                        role_id = 1108709170183671808
                        role = interaction.guild.get_role(role_id)
                        if role:
                            await userObj.add_roles(role)
                            await interaction.response.send_message(content=f"Role is added", ephemeral=True)
                        post = {
                            "discordid": str(interaction.user.id),
                            "steamid": str(steam_id)
                        }
                        collection.insert_one(post)
                    else:
                        await interaction.response.send_message(content=f"You havent wishlisted the game yet, please go to https://store.steampowered.com/app/2391300/The_Dev_Enter_The_Blockchain/?beta=0", ephemeral=True)
        else:
            await interaction.response.send_message(content=f"No account found for {steam_id}",ephemeral=True)

# client = PersistentViewBot()

class Menu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None
    
    @discord.ui.button(label="Connect", style=discord.ButtonStyle.grey, custom_id="1")
    async def menu1(self, interaction: discord.Interaction, button:discord.ui.Button):
        user = collection.find_one({"discordid": str(interaction.user.id)})
        if user:
            if has_wishlisted(user['steamid']):
                userObj = interaction.user
                role_id = 1108709170183671808
                role = interaction.guild.get_role(role_id)
                if role:
                    await userObj.add_roles(role)
                    await interaction.response.send_message(content=f"Role is added", ephemeral=True)
            else:
                userObj = interaction.user
                role_id = 1108709170183671808
                role = interaction.guild.get_role(role_id)
                if role:
                    await userObj.remove_roles(role)
                    await interaction.response.send_message(content=f"You havent wishlisted the game yet, please go to https://store.steampowered.com/app/2391300/The_Dev_Enter_The_Blockchain/?beta=0", ephemeral=True)
            return
        await interaction.response.send_modal(SteamModal())
    
    @discord.ui.button(label="Tutorial", style=discord.ButtonStyle.red, custom_id="2")
    async def menu2(self, interaction: discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_message("https://cdn.discordapp.com/attachments/1089783112004812832/1108703575623876608/Studio_Project_V1.gif", ephemeral=True)



@client.command()
async def menu(ctx):
    embed = discord.Embed(title="Connect with Steam", description="Click to connect to steam")
    await ctx.send(embed=embed, view=Menu())

client.run(os.environ["DISCORD_TOKEN"])