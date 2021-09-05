import discord
from discord.ext import commands, tasks
import os
from os import path
import asyncio
import shutil
import json
from pretty_help import PrettyHelp, DefaultMenu

client = commands.Bot(command_prefix='>')
token = "token"

@client.event
async def on_ready():
    menu = DefaultMenu(page_left="👍", page_right="👎", remove="❌", active_time=50)
    ending = "{ctx.bot.user.name}\n{help.clean_prefix}{help.invoked_with}"
    client.help_command = PrettyHelp(menu=menu, ending_note=ending, color=discord.Color.from_rgb(77, 142, 255))
    print('Bot {0.user}  ready'.format(client))
    data_check.start()


@client.event
async def on_guild_join(guild):
    guildid = guild.id
    print(guildid)
    if os.path.exists(f"./data/{guildid}.json"):
        return
    else:
        shutil.copyfile("./data/default.json", f"./data/{guildid}.json")






for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

@tasks.loop(seconds=10)
async def data_check():
    print("loop")
    for filename in os.listdir("./data"):
        if filename.endswith(".json") and not filename.startswith("d"):
            with open(f"./data/{filename}", "r") as f, open("./data/default.json", "r") as d:
                data = json.load(f)
                default = json.load(d)
                test = default.keys() - data.keys()
                for key in test:
                    data[key] = 1
                    with open(f"./data/{filename}", "w") as f:
                        json.dump(data, f, indent=4)



client.run(token)
