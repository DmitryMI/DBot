import discord
from discord.ext import commands
import random
import logging
import Whistle.WhistleSilencerCog
import YtDlpCog

class DBotConfig:
    def __init__(self):
        self.downloads_max_size = 32 * 1024 * 1024
        self.downloads_dir = "Downloads"
        self.command_prefix = "$"
        self.intents = discord.Intents.default()
        self.streaming_only = False

class DBotClient(commands.Bot):

    def __init__(self, config: DBotConfig):
        super().__init__(command_prefix=commands.when_mentioned_or(config.command_prefix), intents=config.intents)
        self.config = config

    async def on_ready(self):
        logging.info(f'Logged on as {self.user}')

    async def on_message(self, message):
        logging.info(f'Message from {message.author}: {message.content}')

        # Allows the bot to process commands.
        await self.process_commands(message)

@commands.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)

async def create_bot(config : DBotConfig):
    config.intents.message_content = True

    bot = DBotClient(config)

    bot.add_command(add)
    bot.add_cog(YtDlpCog.YtDlpCog(bot))
    bot.add_cog(Whistle.WhistleSilencerCog.WhistleSilencerCog(bot))

    return bot