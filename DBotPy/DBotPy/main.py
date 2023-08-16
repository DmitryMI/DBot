import discord
import argparse
import os
import os.path
import logging
import logging.handlers
import asyncio
from DBotClient import DBotClient, create_bot

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
    parser.add_argument("--downloads_max_size", help = "Downloads folder max size in Mb", default = 1024)
    #parser.add_argument('-v', '--verbose', action='store_true')  # on/off flag

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
    
    bot = await create_bot(args.prefix)

    async with bot:
        await bot.start(api_token)

if __name__ == "__main__":
    asyncio.run(main())