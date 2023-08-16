import discord
from discord.ext import commands
import YtDlpSource
import logging
from ContextMap import ContextMap
import asyncio

class YtDlpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playlist_map = ContextMap()
        self.playing_source_map = ContextMap()
        self.background_tasks = set()

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx : commands.Context, *, url):
        """Plays from a url"""

        async with ctx.typing():
            if ctx in self.playlist_map:
                playlist = self.playlist_map[ctx]
                playlist.clear()
                ctx.send(f'Playlist cleared. Use enqueue command to add to the playlist.')

            await self.play_internal(ctx, url)

    async def play_internal(self, ctx: commands.Context, url):
        await self.ensure_voice(ctx)

        ctx.voice_client.stop()

        self.playing_source_map[ctx] = url

        player = await YtDlpSource.YtDlpSource.from_url(url, loop=self.bot.loop, stream=self.bot.config.streaming_only)
        ctx.voice_client.play(player, after=lambda e: self.on_play_end(ctx, e))
        await ctx.send(f'Now playing: {player.title}')

        playlist = None 
        if ctx in self.playlist_map:
            playlist = self.playlist_map[ctx]
            await ctx.send("Playlist:")
            for i, url in enumerate(playlist):
                await ctx.send(f"{i}: {url}")

    @commands.command()
    async def next(self, ctx : commands.Context):

        # async with ctx.typing():
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        playing_now = None
        if ctx in self.playing_source_map:
            playing_now = self.playing_source_map[ctx]

        if playing_now:
            self.playing_source_map[ctx] = None

        if playing_now:
            await ctx.send(f"Skipping {playing_now}")
        else:
            await ctx.send("Nothing to skip!")
            return

        playlist = None
        if ctx in self.playlist_map:
            playlist = self.playlist_map[ctx]
            if playlist:
                source_next = playlist[0]
                del playlist[0]

                await ctx.send(f"Next source in playlist is {source_next}")
                await self.play_internal(ctx, source_next)
            else:
                await ctx.send("Playlist finished!")
        else:
            await ctx.send("Playlist finished!")

    @commands.command()
    async def enqueue(self, ctx : commands.Context, *, url):
        """Adds url to a playlist"""

        playing_now = None
        if ctx in self.playing_source_map:
            playing_now = self.playing_source_map[ctx]

        if not playing_now:
            await self.play_internal(ctx, url)
        else:
            async with ctx.typing():
                playlist = None
                if ctx in self.playlist_map:
                    playlist = self.playlist_map[ctx]

                if playlist:
                    playlist.append(url)
                else:
                    playlist = [url]
                    self.playlist_map[ctx] = playlist

                await ctx.send(f'Added to playlist!')

                await ctx.send("Playlist:")
                for i, url in enumerate(playlist):
                    await ctx.send(f"{i}: {url}")


    def on_play_end(self, ctx, error):
        if error:
            ctx.send(f"Error occured during playback: {error}")
            self.playing_source_map[ctx] = None
            return
        
        playlist = None
        if ctx in self.playlist_map:
            playlist = self.playlist_map[ctx]

        if playlist:
            source_next = playlist[0]
            del playlist[0]

            # self.bot.loop.run_in_executor(None, lambda: self.play_internal(ctx, source_next))\
            task = self.bot.loop.create_task(self.play_internal(ctx, source_next))

            # Add task to the set. This creates a strong reference.
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)

            logging.info(f"Playback finished for context {ctx}, playing next source in playlist: {source_next}")
        # self.play_internal(source_next)
        else:
            logging.info(f"Playback finished for context {ctx}, playlist is empty")


    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @enqueue.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            # ctx.voice_client.stop()
            pass





