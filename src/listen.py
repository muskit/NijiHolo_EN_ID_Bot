## The bot's listen mode
# Continuously listen for cross-company interactions.
from time import sleep

import asyncio

import catchup


def run(PROGRAM_ARGS):
    while True:
        try:
            asyncio.run(catchup.run(PROGRAM_ARGS))
            print('Sleeping for 60 minutes...')
            sleep(60*60) # run every hour
        except KeyboardInterrupt:
            print('Interrupt signal received. Exiting listen mode.')
            print(f'errors encountered throughout session.')
            break
