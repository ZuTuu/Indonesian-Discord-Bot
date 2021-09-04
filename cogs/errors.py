import discord
from discord.ext import commands
import asyncio
from discord.ext.commands import MissingPermissions, has_permissions, bot_has_permissions, BotMissingPermissions

class errors(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(f"<@{ctx.message.author.id}> Anda tidak memiliki permission!!")
            return
        if isinstance(error, BotMissingPermissions):
            await ctx.send("Saya tidak memiliki permission untuk melakukan itu!")
            return


def setup(client):
    client.add_cog(errors(client))
