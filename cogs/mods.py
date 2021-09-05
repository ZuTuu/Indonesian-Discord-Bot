import discord
from discord.ext import commands
import asyncio
from discord.ext.commands import MissingPermissions, has_permissions, bot_has_permissions, BotMissingPermissions
import json

class mods(commands.Cog):
    """
    Commands untuk admin/mod
    """
    def __init__(self, client):
        self.client = client

    # @commands.command(name="cek")
    # async def _ceke(self, ctx):
    #     print(ctx.guild.id)
    @commands.is_owner()
    @commands.command()
    async def unload(ctx, ext):
        client.unload_extension(f"cogs.{ext}")
        await ctx.send(f"unloaded {ext}")

    @commands.is_owner()
    @commands.command()
    async def load(ctx, ext):
        client.load_extension(f"cogs.{ext}")
        await ctx.send(f"loaded {ext}")

    @commands.is_owner()
    @commands.command()
    async def reload(ctx, ext):
        client.unload_extension(f"cogs.{ext}")
        client.load_extension(f"cogs.{ext}")
        await ctx.send(f"reloaded {ext}")

    @commands.command(name="purge", brief='Menghapus messages')
    async def _purge(self, ctx, *, jumlah):
        """
        Menghapus beberapa messages sebelumnya
        Contoh: >purge 3
        """
        # `Command`: download(url:required)
        # `NOTE`: file size can't exceed 8MB, otherwise it will fail to upload and cause error
        # """
        jumlah = 0
        if(jumlah < 1):
            await ctx.send(f"Tolong ketik jumlah message(s) yang ingin di hapus! <@{ctx.message.author.id}>")
        else:
            await ctx.channel.purge(limit=jumlah + 1 )
            embedVar = discord.Embed(title=f'Telah dihapus {jumlah} message', colour=discord.Colour.from_rgb(64, 239, 255))
            await ctx.send(embed=embedVar, delete_after=5.0)
            return
            # else:
            #     embedVar2 = discord.Embed(title=f'Deleted {amount} messages', colour=discord.Colour.from_rgb(64, 239, 255))
            #     await ctx.send(embed=embedVar2, delete_after=5.0)

    @commands.bot_has_permissions(kick_members=True)
    @commands.command(name="kick", brief='Mengeluarkan member')
    @commands.has_permissions(kick_members=True)
    async def _kick(self, ctx, member : discord.Member, *, alasan):
        """
        Mengeluarkan member melalui command
        Contoh: >kick @zutu#4866
        """
        # `Command`: download(url:required)
        # `NOTE`: file size can't exceed 8MB, otherwise it will fail to upload and cause error
        # """
        alasan = "Gaada"
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
                        await ctx.send(f"<@{member.id}> telah dikeluarkan dari server ini\nAlasan: {alasan}")
                        await member.kick(reason=alasan)
                else:
                    await ctx.send(f"<@{member.id}> telah dikeluarkan dari server ini\nAlasan: {alasan}")
                    await member.kick(reason=alasan)

    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="ban", brief='Mengusir member')
    @commands.has_permissions(ban_members=True)
    async def _ban(self, ctx, member : discord.Member, *, alasan):
        """
        Mengeluarkan member secara permanen melalui command
        Contoh: >ban @zutu#4866
        """
        # `Command`: download(url:required)
        # `NOTE`: file size can't exceed 8MB, otherwise it will fail to upload and cause error
        # """
        alasan = "Gaada"
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
                        await ctx.send(f"<@{member.id}> telah dikeluarkan dari server ini\nAlasan: {alasan}\nhttps://tenor.com/view/rip-pack-bozo-dead-gif-20309754")
                        await member.ban(reason=alasan)
                else:
                    await ctx.send(f"<@{member.id}> telah dikeluarkan dari server ini\nAlasan: {alasan}\nhttps://tenor.com/view/rip-pack-bozo-dead-gif-20309754")
                    await member.ban(reason=alasan)

    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="unban", brief='Menghilangkan ban member')
    @commands.has_permissions(ban_members=True)
    async def _unban(self, ctx, *, member):
        """
        Menghilangkan ban member sehingga member bisa join kembali
        Contoh: >unban zutu#4866

        # `Command`: download(url:required)
         Catatan: username tidak memakai tanda "@"
         """
        # """
        # if(member.id == ctx.message.author.id):
        #     await ctx.send(f"Sumpah lu nape dah <@{ctx.author.id}>")
        #     return
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
