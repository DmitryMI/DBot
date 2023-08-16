import discord
import argparse
import os
import os.path
import logging
import logging.handlers

def configure_logging(logs_dir="logs", log_level = logging.INFO):
    log_file = os.path.join(logs_dir, "dbot.log")

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    handler_console = logging.StreamHandler()
    handler_rotating = logging.handlers.RotatingFileHandler(
        filename=log_file,
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )

    # Setup default logger
    logger_default = logging.getLogger()
    logger_default.setLevel(log_level)
    logger_default.addHandler(handler_rotating)
    logger_default.addHandler(handler_console)



def main():
    parser = argparse.ArgumentParser(
                    prog='DBot',
                    description='Discord Bot for playing meme sounds',
                    epilog='By The Gang of Three')

    #parser.add_argument('filename')           # positional argument
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--token', help="API Token for the bot. Must be kept in secret!")
    group.add_argument('--token_file', help="API Token for the bot stored in a text file. The token must be kept in secret!")
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
    
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    client.run(api_token)

if __name__ == "__main__":
    main()