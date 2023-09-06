import discord
from discord.ext import commands


class CommonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()


    @commands.command()
    async def leave(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()


    @commands.command()
    async def voice_volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

