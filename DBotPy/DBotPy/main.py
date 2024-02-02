from threading import Thread
import discord
import argparse
import os
import os.path
import logging
import logging.handlers
import asyncio
from DBotClient import DBotClient, create_bot, DBotConfig

background_tasks = []

def configure_logging(logs_dir="logs", log_level = logging.INFO):
    log_file = os.path.join(logs_dir, "dbot.log")

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

    handler_console = logging.StreamHandler()
    handler_console.setFormatter(formatter)
    handler_rotating = logging.handlers.RotatingFileHandler(
        filename=log_file,
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    handler_rotating.setFormatter(formatter)

    # Setup default logger
    logger_default = logging.getLogger()
    logger_default.setLevel(log_level)
    logger_default.addHandler(handler_rotating)
    logger_default.addHandler(handler_console)


async def main():
    parser = argparse.ArgumentParser(
                    prog='DBot',
                    description='Discord Bot for playing meme sounds',
                    epilog='By The Gang of Three')

    #parser.add_argument('filename')           # positional argument
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--token', help="API Token for the bot. Must be kept in secret!")
    group.add_argument('--token_file', help="API Token for the bot stored in a text file. The token must be kept in secret!")

    parser.add_argument("--prefix", help="Commands prefix", default="$")
    parser.add_argument("--log_dir", help= "Directory for log files")
    parser.add_argument("--downloads_dir", help = "Directory for downloads", default = "downloads")
    parser.add_argument("--downloads_max_size", help = "Downloads folder max size in Mb", default = 32)
    parser.add_argument('--streaming_only', help="Do not save audio to the disk, stream directly into Discord instead", action='store_true')  # on/off flag
    parser.add_argument("--prison_channel", help="Prison channel name", default="Prison")
    parser.add_argument("--prisoner_role", help="Prisoner role name", default="Prisoner")
    parser.add_argument("--admin_roles", help="Admin role name", nargs="*")
    parser.add_argument("--admin_usernames", help="Admin nickname", nargs="*")
    parser.add_argument("--announcement_pattern", help="Announcement pattern for imprisonment", type=str, default="{}, say {}")
    parser.add_argument("--announcement_language", help="Announcement language for imprisonment", type=str, default="en")

    args = parser.parse_args()

    configure_logging()

    api_token = None

    if args.token is not None:
        api_token = args.token
    else:
        token_file_path = args.token_file
        if not os.path.exists(token_file_path):
            logging.error(f"File {token_file_path} does not exist!")
            return
        with open(token_file_path, 'r') as fin:
            api_token = fin.read()
    
    bot_config = DBotConfig()
    bot_config.command_prefix = args.prefix
    bot_config.downloads_dir = args.downloads_dir
    bot_config.downloads_max_size = args.downloads_max_size
    bot_config.streaming_only = args.streaming_only
    bot_config.prisoner_role_name = args.prisoner_role
    bot_config.prison_channel_name = args.prison_channel
    bot_config.admin_roles = args.admin_roles
    bot_config.admin_usernames = args.admin_usernames
    bot_config.announcement_pattern = args.announcement_pattern
    bot_config.announcement_language = args.announcement_language

    bot = await create_bot(bot_config)

    bot_task = asyncio.create_task(bot.start(api_token))
    # await bot.start(api_token)
    background_tasks.append(bot_task)

    # plot_task = asyncio.create_task(plot_loop())
    # background_tasks.append(plot_task)

    await bot_task

if __name__ == "__main__":

    asyncio.run(main())