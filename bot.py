import discord
from discord.ext import commands
import os
from os import path
import asyncio
import shutil
# import json

client = commands.Bot(command_prefix='>')
token = "your mother"
seting = ""

@client.event
async def on_ready():
    print('Bot {0.user}  ready'.format(client))

@client.event
async def on_guild_join(guild):
    guildid = guild.id
    print(guildid)
    if os.path.exists(f"./data/{guildid}.json"):
        seting = f"{filename}.json"
        return
    else:
        shutil.copyfile("./data/default.json", f"./data/{guildid}.json")

#for loading and unloading cogs
@client.command()
async def unload(ctx, ext):
    client.unload_extension(f"cogs.{ext}")
    await ctx.send(f"unloaded {ext}")

@client.command()
async def load(ctx, ext):
    client.load_extension(f"cogs.{ext}")
    await ctx.send(f"loaded {ext}")

@client.command()
async def reload(ctx, ext):
    client.unload_extension(f"cogs.{ext}")
    client.load_extension(f"cogs.{ext}")
    await ctx.send(f"reloaded {ext}")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")
#
# for filename in os.litdir("./data"):
#     if filename.endswith(".json")

client.run(token)
