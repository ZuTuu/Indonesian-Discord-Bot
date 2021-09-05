import discord
import asyncio
import random
import youtube_dl
import string
import os
from discord.ext import commands
from googleapiclient.discovery import build
from discord.ext.commands import command

# import pymongo
# NOTE: Import pymongo if you are using the database function commands
# NOTE: Also add `pymongo` and `dnspython` inside the requirements.txt file if you are using pymongo

# TODO: CREATE PLAYLIST SUPPORT FOR MUSIC


# NOTE: Without database, the music bot will not save your volume


# flat-playlist:True?
# extract_flat:True
# audioquality 0 best 9 worst
# format bestaudio/best or worstaudio
# 'noplaylist': None
ytdl_format_options = {
    'audioquality': 5,
    'format': 'bestaudio',
    'outtmpl': '{}',
    'restrictfilenames': True,
    'flatplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    "extractaudio": True,
    "audioformat": "opus",
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

# Download youtube-dl options
ytdl_download_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.mp3',
    'reactrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addreacses cause issues sometimes
    'source_addreacs': '0.0.0.0',
    'output': r'youtube-dl',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
        }]
}

stim = {
    'default_search': 'auto',
    "ignoreerrors": True,
    'quiet': True,
    "no_warnings": True,
    "simulate": True,  # do not keep the video files
    "nooverwrites": True,
    "keepvideo": False,
    "noplaylist": True,
    "skip_download": False,
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}


ffmpeg_options = {
    'options': '-vn',
    # 'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}


class Downloader(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get("url")
        self.thumbnail = data.get('thumbnail')
        self.duration = data.get('duration')
        self.views = data.get('view_count')
        self.playlist = {}

    @classmethod
    async def video_url(cls, url, ytdl, *, loop=None, stream=False):
        """
        Download the song file and data
        """
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        song_list = {'queue': []}
        if 'entries' in data:
            if len(data['entries']) > 1:
                playlist_titles = [title['title'] for title in data['entries']]
                song_list = {'queue': playlist_titles}
                song_list['queue'].pop(0)

            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data), song_list

    async def get_info(self, url):
        """
        Get the info of the next song by not downloading the actual file but just the data of song/query
        """
        yt = youtube_dl.YoutubeDL(stim)
        down = yt.extract_info(url, download=False)
        data1 = {'queue': []}
        if 'entries' in down:
            if len(down['entries']) > 1:
                playlist_titles = [title['title'] for title in down['entries']]
                data1 = {'title': down['title'], 'queue': playlist_titles}

            down = down['entries'][0]['title']

        return down, data1


class music(commands.Cog, name='music'):
    """
    Commands untuk music bot
    """
    def __init__(self, client):
        self.client = client
        # self.music=self.database.find_one('music')
        self.player = {
            "audio_files": []
        }
        # self.database_setup()

    def database_setup(self):
        URL = os.getenv("MONGO")
        if URL is None:
            return False

    @property
    def random_color(self):
        return discord.Color.from_rgb(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))

    async def yt_info(self, song):
        """
        Get info from youtube
        """
        API_KEY = 'API_KEY'
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        song_data = youtube.search().list(part='snippet').execute()
        return song_data[0]

    @commands.Cog.listener('on_voice_state_update')
    async def music_voice(self, user, before, after):
        """
        Clear the server's playlist after bot leave the voice channel
        """
        if after.channel is None and user.id == self.client.user.id:
            try:
                self.player[user.guild.id]['queue'].clear()
            except KeyError:
                # NOTE: server ID not in bot's local self.player dict
                # Server ID lost or was not in data before disconnecting
                print(f"Failed to get guild id {user.guild.id}")

    async def filename_generator(self):
        """
        Generate a unique file name for the song file to be named as
        """
        chars = list(string.ascii_letters+string.digits)
        name = ''
        for i in range(random.randint(9, 25)):
            name += random.choice(chars)

        if name not in self.player['audio_files']:
            return name

        return await self.filename_generator()

    async def playlist(self, data, msg):
        """
        THIS FUNCTION IS FOR WHEN YOUTUBE LINK IS A PLAYLIST
        Add song into the server's playlist inside the self.player dict
        """
        for i in data['queue']:
            print(i)
            self.player[msg.guild.id]['queue'].append(
                {'title': i, 'author': msg})

    async def queue(self, msg, song):
        """
        Add the query/song to the queue of the server
        """
        title1 = await Downloader.get_info(self, url=song)
        title = title1[0]
        data = title1[1]
        # NOTE:needs fix here
        if data['queue']:
            await self.playlist(data, msg)
            # NOTE: needs to be embeded to make it better output
            return await msg.send(f"Ditambahkan playlist {data['title']} ke list lagu")
        self.player[msg.guild.id]['queue'].append(
            {'title': title, 'author': msg})
        return await msg.send(f"**{title} Ditambahkan ke list lagu**".title())

    async def voice_check(self, msg):
        """
        function used to make bot leave voice channel if music not being played for longer than 2 minutes
        """
        if msg.voice_client is not None:
            await asyncio.sleep(120)
            if msg.voice_client is not None and msg.voice_client.is_playing() is False and msg.voice_client.is_paused() is False:
                await msg.voice_client.disconnect()

    async def clear_data(self, msg):
        """
        Clear the local dict data
            name - remove file name from dict
            remove file and filename from directory
            remove filename from global audio file names
        """
        name = self.player[msg.guild.id]['name']
        os.remove(name)
        self.player['audio_files'].remove(name)

    async def loop_song(self, msg):
        """
        Loop the currently playing song by replaying the same audio file via `discord.PCMVolumeTransformer()`
        """
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(self.player[msg.guild.id]['name']))
        loop = asyncio.get_event_loop()
        try:
            msg.voice_client.play(
                source, after=lambda a: loop.create_task(self.done(msg)))
            msg.voice_client.source.volume = self.player[msg.guild.id]['volume']
            # if str(msg.guild.id) in self.music:
            #     msg.voice_client.source.volume=self.music['vol']/100
        except Exception as Error:
            # Has no attribute play
            print(Error)  # NOTE: output back the error for later debugging

    async def done(self, msg, msgId: int = None):
        """
        Function to run once song completes
        Delete the "Now playing" message via ID
        """
        if msgId:
            try:
                message = await msg.channel.fetch_message(msgId)
                await message.delete()
            except Exception as Error:
                print("Gagal mendapatkan message")

        if self.player[msg.guild.id]['reset'] is True:
            self.player[msg.guild.id]['reset'] = False
            return await self.loop_song(msg)

        if msg.guild.id in self.player and self.player[msg.guild.id]['repeat'] is True:
            return await self.loop_song(msg)

        await self.clear_data(msg)

        if self.player[msg.guild.id]['queue']:
            queue_data = self.player[msg.guild.id]['queue'].pop(0)
            return await self.start_song(msg=queue_data['author'], song=queue_data['title'])

        else:
            await self.voice_check(msg)

    async def start_song(self, msg, song):
        new_opts = ytdl_format_options.copy()
        audio_name = await self.filename_generator()

        self.player['audio_files'].append(audio_name)
        new_opts['outtmpl'] = new_opts['outtmpl'].format(audio_name)

        ytdl = youtube_dl.YoutubeDL(new_opts)
        download1 = await Downloader.video_url(song, ytdl=ytdl, loop=self.client.loop)
        download = download1[0]
        data = download1[1]
        self.player[msg.guild.id]['name'] = audio_name
        emb = discord.Embed(colour=self.random_color, title='Sekarang memutar',
                            description=download.title, url=download.url)
        emb.set_thumbnail(url=download.thumbnail)
        emb.set_footer(
            text=f'Diputar oleh {msg.author.display_name}', icon_url=msg.author.avatar_url)
        loop = asyncio.get_event_loop()

        if data['queue']:
            await self.playlist(data, msg)

        msgId = await msg.send(embed=emb)
        self.player[msg.guild.id]['player'] = download
        self.player[msg.guild.id]['author'] = msg
        msg.voice_client.play(
            download, after=lambda a: loop.create_task(self.done(msg, msgId.id)))

        # if str(msg.guild.id) in self.music: #NOTE adds user's default volume if in database
        #     msg.voice_client.source.volume=self.music[str(msg.guild.id)]['vol']/100
        msg.voice_client.source.volume = self.player[msg.guild.id]['volume']
        return msg.voice_client

    @command()
    async def play(self, msg, *, lagu):
        """
        Memutar lagu dari url atau judul youtube
        Contoh: >play Freedom dive
        """
        # `Command:` play <lagu>
        # """
        if msg.guild.id in self.player:
            if msg.voice_client.is_playing() is True:  # NOTE: SONG CURRENTLY PLAYING
                return await self.queue(msg, lagu)

            if self.player[msg.guild.id]['queue']:
                return await self.queue(msg, lagu)

            if msg.voice_client.is_playing() is False and not self.player[msg.guild.id]['queue']:
                return await self.start_song(msg, lagu)

        else:
            # IMPORTANT: THE ONLY PLACE WHERE NEW `self.player[msg.guild.id]={}` IS CREATED
            self.player[msg.guild.id] = {
                'player': None,
                'queue': [],
                'author': msg,
                'name': None,
                "reset": False,
                'repeat': False,
                'volume': 0.5
            }
            return await self.start_song(msg, lagu)

    @play.before_invoke
    async def before_play(self, msg):
        """
        Check voice_client
            - User voice = None:
                please join a voice channel
            - bot voice == None:
                joins the user's voice channel
            - user and bot voice NOT SAME:
                - music NOT Playing AND queue EMPTY
                    join user's voice channel
                - items in queue:
                    please join the same voice channel as the bot to add song to queue
        """

        if msg.author.voice is None:
            return await msg.send('**Mohon join voice channel terlebih dahulu untuk memutar musik**'.title())

        if msg.voice_client is None:
            return await msg.author.voice.channel.connect()

        if msg.voice_client.channel != msg.author.voice.channel:

            # NOTE: Check player and queue
            if msg.voice_client.is_playing() is False and not self.player[msg.guild.id]['queue']:
                return await msg.voice_client.move_to(msg.author.voice.channel)
                # NOTE: move bot to user's voice channel if queue does not exist

            if self.player[msg.guild.id]['queue']:
                # NOTE: user must join same voice channel if queue exist
                return await msg.send("Mohon join voice channel yang sama dengan bot")

    @commands.has_permissions(manage_channels=True)
    @command()
    async def repeat(self, msg):
        """
        Mengulang lagu yang sedang di putar (Ketik lagi jika ingin dimatikan)
        Contoh: >repeat
        """
        # `Command:` repeat()
        # """
        if msg.guild.id in self.player:
            if msg.voice_client.is_playing() is True:
                if self.player[msg.guild.id]['repeat'] is True:
                    self.player[msg.guild.id]['repeat'] = False
                    return await msg.message.add_reaction(emoji='✅')

                self.player[msg.guild.id]['repeat'] = True
                return await msg.message.add_reaction(emoji='✅')

            return await msg.send("Sedang tidak ada lagu yang diputar")
        return await msg.send("Bot sedang tidak di voice channel atau sedang memutar lagu")

    @commands.has_permissions(manage_channels=True)
    @command(aliases=['restart-loop'])
    async def reset(self, msg):
        """
        Menghapus list lagu yang sedang diputar
        Contoh: >reset
        """
        # `Command:` reset()
        # """
        if msg.voice_client is None:
            return await msg.send(f"**{msg.author.display_name}, sedang tidak ada lagu yang diputar oleh bot.**")

        if msg.author.voice is None or msg.author.voice.channel != msg.voice_client.channel:
            return await msg.send(f"**{msg.author.display_name}, anda harus di voice channel yang sama dengan bot.**")

        if self.player[msg.guild.id]['queue'] and msg.voice_client.is_playing() is False:
            return await msg.send("**Sedang tidak ada lagu yang di putar**".title(), delete_after=25)

        self.player[msg.guild.id]['reset'] = True
        msg.voice_client.stop()

    @commands.has_permissions(manage_channels=True)
    @command()
    async def skip(self, msg):
        """
        Melewatkan lagu yang diputar
        Contoh: >skip
        """
        # `Command:` skip()
        # """
        if msg.voice_client is None:
            return await msg.send("**Sedang tidak ada lagu yang sedang diputar**".title(), delete_after=60)

        if msg.author.voice is None or msg.author.voice.channel != msg.voice_client.channel:
            return await msg.send("Mohon masuk ke voice channel yang sama dengan bot")

        if not self.player[msg.guild.id]['queue'] and msg.voice_client.is_playing() is False:
            return await msg.send("**Tidak ada lagu yang bisa di skip**".title(), delete_after=60)

        self.player[msg.guild.id]['repeat'] = False
        msg.voice_client.stop()
        return await msg.message.add_reaction(emoji='✅')

    @commands.has_permissions(manage_channels=True)
    @command()
    async def stop(self, msg):
        """
        Menghentikan lagu yang sedang diputar dan menghapus list lagu yang diputar
        Contoh: >stop
        """
        # `Command:` stop()
        # """
        if msg.voice_client is None:
            return await msg.send("Bot sedang tidak ada di voice channel")

        if msg.author.voice is None:
            return await msg.send("Anda harus di voice channel yang sama dengan bot")

        if msg.author.voice is not None and msg.voice_client is not None:
            if msg.voice_client.is_playing() is True or self.player[msg.guild.id]['queue']:
                self.player[msg.guild.id]['queue'].clear()
                self.player[msg.guild.id]['repeat'] = False
                msg.voice_client.stop()
                return await msg.message.add_reaction(emoji='✅')

            return await msg.send(f"**{msg.author.display_name}, tidak ada lagu yang sedang diputar**")

    @commands.has_permissions(manage_channels=True)
    @command(aliases=['keluar', 'disconnect'])
    async def leave(self, msg):
        """
        Mengeluarkan bot dari voice channel
        Contoh: >leave
        """
        # `Command:` leave()
        # """
        if msg.author.voice is not None and msg.voice_client is not None:
            if msg.voice_client.is_playing() is True or self.player[msg.guild.id]['queue']:
                self.player[msg.guild.id]['queue'].clear()
                msg.voice_client.stop()
                return await msg.voice_client.disconnect(), await msg.message.add_reaction(emoji='✅')

            return await msg.voice_client.disconnect(), await msg.message.add_reaction(emoji='✅')

        if msg.author.voice is None:
            return await msg.send("Anda harus di voice channel yang sama dengan bot untuk mengeluarkannya melalui command!")

    @commands.has_permissions(manage_channels=True)
    @command()
    async def pause(self, msg):
        """
        Memberhentikan lagu yang sedang diputar
        Contoh: >pause
        """
        # `Command:` pause()
        # """
        if msg.author.voice is not None and msg.voice_client is not None:
            if msg.voice_client.is_paused() is True:
                return await msg.send("Lagu sudah dipause!")

            if msg.voice_client.is_paused() is False:
                msg.voice_client.pause()
                await msg.message.add_reaction(emoji='✅')

    @commands.has_permissions(manage_channels=True)
    @command()
    async def resume(self, msg):
        """
        Melanjutkan lagu yang diberhentikan
        Contoh: >resume
        """
        # `Command:` resume()
        # """
        if msg.author.voice is not None and msg.voice_client is not None:
            if msg.voice_client.is_paused() is False:
                return await msg.send("Lagu sudah diresume!")

            if msg.voice_client.is_paused() is True:
                msg.voice_client.resume()
                return await msg.message.add_reaction(emoji='✅')

    @command(name='queue', aliases=['list-lagu', 'q', 'song-list'])
    async def _queue(self, msg):
        """
        Melihat lagu apa yang akan diputar setelah lagu ini
        Contoh: >queue
        """
        # `Command:` queue()
        # """
        if msg.voice_client is not None:
            if msg.guild.id in self.player:
                if self.player[msg.guild.id]['queue']:
                    emb = discord.Embed(
                        colour=self.random_color, title='queue')
                    emb.set_footer(
                        text=f'Command oleh {msg.author.name}', icon_url=msg.author.avatar_url)
                    for i in self.player[msg.guild.id]['queue']:
                        emb.add_field(
                            name=f"**{i['author'].author.name}**", value=i['title'], inline=False)
                    return await msg.send(embed=emb, delete_after=120)

        return await msg.send("Tidak ada lagu selanjutnya")

    @command(name='song-info', aliases=['song?', 'nowplaying', 'current-song'])
    async def song_info(self, msg):
        """
        Melihat informasi tentang lagu yang sedang diputar
        >contoh: >song_info
        """
        # `Command:` song-into()
        # """
        if msg.voice_client is not None and msg.voice_client.is_playing() is True:
            emb = discord.Embed(colour=self.random_color, title='Currently Playing',
                                description=self.player[msg.guild.id]['player'].title)
            emb.set_footer(
                text=f"{self.player[msg.guild.id]['author'].author.name}", icon_url=msg.author.avatar_url)
            emb.set_thumbnail(
                url=self.player[msg.guild.id]['player'].thumbnail)
            return await msg.send(embed=emb, delete_after=120)

        return await msg.send(f"**Sedang tidak ada lagu yang diputar**".title(), delete_after=30)

    @command(aliases=['move-bot', 'move-b', 'mb', 'mbot'])
    async def join(self, msg, *, channel: discord.VoiceChannel = None):
        """
        Membuat bot masuk voice channel
        Contoh: >join
        """
        # `Command:` join(channel:optional)
        # """
        if msg.voice_client is not None:
            return await msg.send(f"Bot sudah masuk voice channel\nApakah maksudnya {msg.prefix}moveTo?")

        if msg.voice_client is None:
            if channel is None:
                return await msg.author.voice.channel.connect(), await msg.message.add_reaction(emoji='✅')

            return await channel.connect(), await msg.message.add_reaction(emoji='✅')

        else:
            if msg.voice_client.is_playing() is False and not self.player[msg.guild.id]['queue']:
                return await msg.author.voice.channel.connect(), await msg.message.add_reaction(emoji='✅')

    @join.before_invoke
    async def before_join(self, msg):
        if msg.author.voice is None:
            return await msg.send("Anda tidak sedang di voice channel")

    @join.error
    async def join_error(self, msg, error):
        if isinstance(error, commands.BadArgument):
            return msg.send(error)

        if error.args[0] == 'Command raised an exception: Exception: playing':
            return await msg.send("**Mohon join voice channel yang sama dengan bot untuk menambahkan lagu**".title())

    @commands.has_permissions(manage_channels=True)
    @command(aliases=['vol'])
    async def volume(self, msg, vol: int):
        """
        Mengubah volume bot
        Contoh: >vol 100 (200 max)
        """
        # `Permission:` manage_channels
        # `Command:` volume(amount:integer)
        # """

        if vol > 200:
            vol = 200
        vol = vol/100
        if msg.author.voice is not None:
            if msg.voice_client is not None:
                if msg.voice_client.channel == msg.author.voice.channel and msg.voice_client.is_playing() is True:
                    msg.voice_client.source.volume = vol
                    self.player[msg.guild.id]['volume'] = vol
                    # if (msg.guild.id) in self.music:
                    #     self.music[str(msg.guild.id)]['vol']=vol
                    return await msg.message.add_reaction(emoji='✅')

        return await msg.send("**Mohon join voice channel yang sama dengan bot untuk menggunakan command**".title(), delete_after=30)

    @commands.command(brief='Mendownload lagu')
    async def download(self, ctx, *, song):
        """
        Mendownload lagu dan mengirimnya di text channel
        Contoh: >download AliA - Utopia
        """
        # `Command`: download(url:required)
        # `NOTE`: file size can't exceed 8MB, otherwise it will fail to upload and cause error
        # """
        try:
            with youtube_dl.YoutubeDL(ytdl_download_format_options) as ydl:
                if "https://www.youtube.com/" in song:
                    download = ydl.extract_info(song, True)
                else:
                    infosearched = ydl.extract_info(
                        "ytsearch:"+song, False)
                    download = ydl.extract_info(
                        infosearched['entries'][0]['webpage_url'], True)
                filename = ydl.prepare_filename(download)
                embed = discord.Embed(
                    title="Lagu anda sudah siap", description="Mohon tunggu sebentar, file sedang di upload.")
                await ctx.send(embed=embed, delete_after=30)
                await ctx.send(file=discord.File(filename))
                os.remove(filename)
        except (youtube_dl.utils.ExtractorError, youtube_dl.utils.DownloadError):
            embed = discord.Embed(title="Lagu tidak bisa di download", description=("Song:"+song))
            await ctx.send(embed=embed)

    # @volume.error
    # async def volume_error(self, msg,error):
    #     if isinstance(error, commands.MissingPermissions):
    #         return await msg.send("Manage channels or admin perms required to change volume", delete_after=30)


def setup(client):
    client.add_cog(music(client))
