import discord
from discord.ext import commands
import random

class DBotClient(commands.Bot):

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

        # Allows the bot to process commands.
        await self.process_commands(message)

@commands.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)

@commands.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))

def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = DBotClient(command_prefix="$", intents=intents)

    bot.add_command(add)
    bot.add_command(choose)

    return bot