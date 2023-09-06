import discord
from discord.ext import commands
import YtDlpSource
import logging
from ContextMap import ContextMap
import asyncio
from Whistle.WhistlingDetectingSink import WhistlingDetectingSink
import discord.member

WHISTLE_PUNISHMENT_SCORE = 3

class WhistleSilencerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sinks_map = ContextMap()
        self.background_tasks = []
        self.users_punished = []
    
    @commands.command()
    async def whistle_listen(self, ctx: commands.Context):
        # ctx.voice_client.pla
        if ctx.voice_client:
            # sink = discord.sinks.WaveSink()
            sink = WhistlingDetectingSink(ctx, self.whistler_updated_callback)
            self.sinks_map[ctx] = sink
            ctx.voice_client.start_recording(sink, self.listen_stopped_callback, ctx)

            await ctx.send("Listening for whistlers...")
        else:
            await ctx.send("Not in a voice channel!")

    
    @commands.command()
    async def whistle_stop(self, ctx: commands.Context):
        ctx.voice_client.stop_recording()

    async def whistler_punishment_handler(self, ctx: commands.Context, user, score):

        members = await ctx.guild.query_members(user_ids=[user])
        # print(members)
        if not members:
            logging.error("Failed to load member with id {user}")

        member: discord.Member = members[0]

        await ctx.send(f"Whistler detected: {member.display_name}")

        await member.edit(mute=True)
        await asyncio.sleep(10)
        self.users_punished.remove(user)

        await member.edit(mute=False)

        await ctx.send(f"Whistler {member.display_name}: punishment ended")


    async def whistler_updated_callback_async(self, sink: WhistlingDetectingSink, user, score):
        ctx = sink.ctx

        if score > 0:
            logging.info(f"{user}' score is {score}'")

        if score > WHISTLE_PUNISHMENT_SCORE:
            if user in self.users_punished:
                return

            self.users_punished.append(user)
            sink.user_whistle_map[user] = 0

            task =  self.bot.loop.create_task(self.whistler_punishment_handler(ctx, user, score))
            task.add_done_callback(lambda task: self.background_tasks.remove(task))
            self.background_tasks.append(task)

    def whistler_updated_callback(self, sink: WhistlingDetectingSink, user, score):
        task =  self.bot.loop.create_task(self.whistler_updated_callback_async(sink, user, score))
        task.add_done_callback(lambda task: self.background_tasks.remove(task))
        self.background_tasks.append(task)

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





