import discord
from discord.ext import commands

# Discord Intents
intents = discord.Intents.all()
intents.members = True

client = commands.Bot(intents=intents, command_prefix='!')

@client.command()
async def hello(ctx):
    await ctx.send("ashim gay")
 
 client.run("TOKEN") 
