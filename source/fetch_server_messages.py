from threading import Thread

import argparse
import asyncio
import discord_client
import logging

LOG_OUTPUT_FILENAME = 'discord.out.log'

def initialize_logger():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename=LOG_OUTPUT_FILENAME, encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", dest='debug_mode', help="Enter program debug mode",
                        action="store_true")
    parser.add_argument("-s", dest='server', help="Discord numerical server id", type=int)
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", dest='aggregate_mode', help="Analyzes all text channels for given server",
                        action="store_true")
    group.add_argument("-c", dest='channel', help="Text channel to target, numeric id", type=int)                    
    return parser.parse_args()

def main():
    initialize_logger()
    args = parse_args()
    discord_client.run(args)

if __name__ == '__main__':
    main()

