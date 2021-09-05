import discord
from discord.ext import commands
# import json

class fun(commands.Cog):
    """
    Commands for fun
    """
    def __init__(self, client):
        self.client = client
    @commands.command(name="ping", brief='Ping')
    async def _ping(self, ctx):
        """
        Melihat ping bot
        Contoh: >ping
        """
        # `Command`: download(url:required)
        # `NOTE`: file size can't exceed 8MB, otherwise it will fail to upload and cause error
        # """
        await ctx.send(f'Indihome sekarang sedang {round(self.client.latency * 100)}ms!')

def setup(client):
    client.add_cog(fun(client))
