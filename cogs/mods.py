import discord
from discord.ext import commands
import asyncio
from discord.ext.commands import MissingPermissions, has_permissions, bot_has_permissions, BotMissingPermissions
import json

class mods(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command(name="purge")
    async def _purge(self, ctx, *, amount=0):
        if(amount < 1):
            await ctx.send(f"Tolong ketik jumlah message(s) yang ingin di hapus! <@{ctx.message.author.id}>")
        else:
            await ctx.channel.purge(limit=amount + 1 )
            embedVar = discord.Embed(title=f'Telah dihapus {amount} message', colour=discord.Colour.from_rgb(64, 239, 255))
            await ctx.send(embed=embedVar, delete_after=5.0)
            return
            # else:
            #     embedVar2 = discord.Embed(title=f'Deleted {amount} messages', colour=discord.Colour.from_rgb(64, 239, 255))
            #     await ctx.send(embed=embedVar2, delete_after=5.0)

    @commands.bot_has_permissions(kick_members=True)
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def _kick(self, ctx, member : discord.Member, *, reason="Gaada"):
        bot_member = ctx.guild.get_member(self.client.user.id)
        if(bot_member.top_role <= member.top_role):
            await ctx.send("Saya tidak bisa mengeluarkan orang dengan role yang lebih tinggi")
            return
        if(member.id == ctx.message.author.id):
            await ctx.send(f"Lu tolol atau napa dah <@{ctx.author.id}>")
            return
        if(member.top_role >= ctx.message.author.top_role):
            await ctx.send(f"Anda cuman bisa mengeluarkan orang dibawahmu <@{ctx.author.id}>")
        else:
            with open(f"./data/{ctx.guild.id}.json", "r") as f:
                data = json.load(f)
                if(data["confirmation"] == 1):
                    confirm = await ctx.send(f"Apakah anda yakin? <@{ctx.message.author.id}>")
                    await confirm.add_reaction("\N{WHITE HEAVY CHECK MARK}")
                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) == '\N{WHITE HEAVY CHECK MARK}'
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=10.0, check=check)
                    except asyncio.TimeoutError:
                        await ctx.send(f"Waktu terlalu lama untuk mereact! <@{ctx.author.id}>")
                    else:
                        await ctx.send(f"<@{member.id}> telah dikeluarkan dari server ini\nAlasan: {reason}")
                        await member.kick(reason=reason)
                else:
                    await ctx.send(f"<@{member.id}> telah dikeluarkan dari server ini\nAlasan: {reason}")
                    await member.kick(reason=reason)

    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def _ban(self, ctx, member : discord.Member, *, reason="Gaada"):
        bot_member = ctx.guild.get_member(self.client.user.id)
        if(bot_member.top_role <= member.top_role):
            await ctx.send("Saya tidak bisa mengeluarkan orang dengan role yang lebih tinggi")
            return
        if(member.id == ctx.message.author.id):
            await ctx.send(f"Lu tolol atau napa dah <@{ctx.author.id}>")
            return
        if(member.top_role >= ctx.message.author.top_role):
            await ctx.send(f"Anda cuman bisa mengeluarkan orang dibawahmu <@{ctx.author.id}>")
        else:
            with open(f"./data/{ctx.guild.id}.json", "r") as f:
                data = json.load(f)
                if(data["confirmation"] == 1):
                    confirm = await ctx.send(f"Apakah anda yakin? <@{ctx.message.author.id}>")
                    await confirm.add_reaction("\N{WHITE HEAVY CHECK MARK}")
                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) == '\N{WHITE HEAVY CHECK MARK}'
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=10.0, check=check)
                    except asyncio.TimeoutError:
                        await ctx.send(f"Waktu terlalu lama untuk mereact! <@{ctx.author.id}>")
                    else:
                        await ctx.send(f"<@{member.id}> telah dikeluarkan dari server ini\nAlasan: {reason}\nhttps://tenor.com/view/rip-pack-bozo-dead-gif-20309754")
                        await member.ban(reason=reason)
                else:
                    await ctx.send(f"<@{member.id}> telah dikeluarkan dari server ini\nAlasan: {reason}\nhttps://tenor.com/view/rip-pack-bozo-dead-gif-20309754")
                    await member.ban(reason=reason)

    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def _unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_tag = member.split('#')

        for ban_entry in banned_users:
            user  = ban_entry.user

            if(user.name, user.discriminator) == (member_name, member_tag):
                with open(f"./data/{ctx.guild.id}.json", "r") as f:
                    data = json.load(f)
                    if(data["confirmation"] == 1):
                        confirm = await ctx.send(f"Apakah anda yakin? <@{ctx.message.author.id}>")
                        await confirm.add_reaction("\N{WHITE HEAVY CHECK MARK}")
                        def check(reaction, userb):
                            return userb == ctx.author and str(reaction.emoji) == '\N{WHITE HEAVY CHECK MARK}'
                        try:
                            reaction, userb = await self.client.wait_for('reaction_add', timeout=10.0, check=check)
                        except asyncio.TimeoutError:
                            await ctx.send(f"Waktu terlalu lama untuk mereact! <@{ctx.author.id}>")
                        else:
                            await ctx.guild.unban(user)
                            await ctx.send(f"{user.name}#{user.discriminator} telah di unban di server ini!")
                            return
                    else:
                        await ctx.guild.unban(user)
                        await ctx.send(f"{user.name}#{user.discriminator} telah di unban di server ini!")
                        return
            elif(user.name, user.discriminator) != (member_name, member_tag):
                await ctx.send("Dia ga di banned cok")
                return

def setup(client):
    client.add_cog(mods(client))
