import discord
from discord.ext import commands
import YtDlpSource
import logging
from ContextMap import ContextMap
import asyncio
from Whistle.WhistlingDetectingSink import WhistlingDetectingSink
import discord.member



class WhistleSilencerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sinks_map = ContextMap()
        self.background_tasks = []
    
    @commands.command()
    async def whistle_listen(self, ctx: commands.Context):
        if ctx.voice_client:
            sink = WhistlingDetectingSink(ctx)
            self.sinks_map[ctx] = sink
            ctx.voice_client.start_recording(sink, self.listen_stopped_callback, ctx)

            await ctx.send("Listening for whistlers...")
        else:
            await ctx.send("Not in a voice channel!")

    
    @commands.command()
    async def whistle_stop(self, ctx: commands.Context):
        ctx.voice_client.stop_recording()
        del self.sinks_map[ctx]

    async def listen_stopped_callback(self, sink: discord.sinks, ctx):
        '''
        for user_id, audio in sink.audio_data.items():
            audio: discord.sinks.core.AudioData = audio
            filename = f"Recordings/{user_id}.pcm"
            with open(filename, "wb") as f:
                f.write(audio.file.getvalue())
        '''
        pass

    @whistle_listen.before_invoke
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





