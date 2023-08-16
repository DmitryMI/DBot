import discord
from discord.ext import commands
import random
import logging
import YtDlpCog

class DBotClient(commands.Bot):

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

async def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = DBotClient(command_prefix=commands.when_mentioned_or("!"), intents=intents)

    bot.add_command(add)
    await bot.add_cog(YtDlpCog.YtDlpCog(bot))

    return bot