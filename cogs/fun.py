import discord
from discord.ext import commands
# import json

class fun(commands.Cog):

    def __init__(self, client):
        self.client = client
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Indihome sekarang sedang {round(self.client.latency * 100)}ms!')

def setup(client):
    client.add_cog(fun(client))
