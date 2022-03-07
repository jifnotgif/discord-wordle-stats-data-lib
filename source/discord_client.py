from dotenv import load_dotenv
from os import getenv

import csv
import discord
import re
import threading
import time

API_TOKEN_ENV_VAR = "DISCORD_API_TOKEN"
WORDLE_SCORE_MESSAGE_REGEX = 'Wordle \d+? (\d|X)/\d'

class DiscordClient(discord.Client):
    def __init__(self, program_args, message_limit, *args, **kwargs):
        self.program_args = program_args
        self.message_limit = message_limit
        super().__init__(*args, **kwargs)
    
    async def on_ready(self):
        print('We have logged in as {0.user}'.format(client))
        await self.fetch_server_messages()

    async def export_channel_messages(self, txt_channel):
        with open(txt_channel.name + '.csv', 'w', encoding="utf-8", newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(['user_id','message','created_timestamp','last_edited_timestamp'])
            async for message in txt_channel.history(limit=self.message_limit):
                if (
                        message.clean_content and
                        re.match(WORDLE_SCORE_MESSAGE_REGEX, message.clean_content) and
                        is_valid_wordle_result(message.clean_content)
                    ):
                    csv_writer.writerow([format_author(message.author.name), message.clean_content, message.created_at, message.edited_at])

    async def fetch_server_messages(self):
        start = time.time()
        if self.program_args.server not in [guild.id for guild in client.guilds]:
            raise RuntimeError('Guild not found!')

        target_guild = client.get_guild(self.program_args.server)
        if self.program_args.aggregate_mode:
            for txt_channel in target_guild.text_channels:
                await self.export_channel_messages(txt_channel)
        else:
            if self.program_args.channel not in [channel.id for channel in target_guild.text_channels]:
                raise RuntimeError('Channel not found!')
            else:
                target_channel = target_guild.get_channel(self.program_args.channel)
                await self.export_channel_messages(target_channel)

        end = time.time()
        print('Execution time: {}'.format(end - start))
        await self.close()


def run(args):
    load_dotenv()
    token = getenv(API_TOKEN_ENV_VAR)

    MESSAGE_LIMIT = None
    if args.debug_mode:
        MESSAGE_LIMIT = 5

    global client
    client = DiscordClient(args, MESSAGE_LIMIT)
    client.run(token)


def format_author(author_name):
    """
    Removes 4 digit user identifier
    """
    return author_name.split('#')[0]

def is_valid_wordle_result(message):
    """
    Determines if given message is a valid wordle result.
    Possible scores are out of 6, or X for a loss (did not finish in 6 tries)
    """
    ratio = message.split(" ")[2] # e.g "1/6"
    score = ratio.split("/")[0] # e.g "1"
    return score == 'X' or int(score) <= 6
