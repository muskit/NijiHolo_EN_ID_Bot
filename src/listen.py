## The bot's listen mode
# Continuously listen for cross-company interactions.
from time import sleep

import asyncio
import traceback

import catchup

errors_encountered = 0

def run(PROGRAM_ARGS):
    global errors_encountered
    while True:
        try:
            asyncio.run(catchup.run(PROGRAM_ARGS))
            print('Sleeping for 10 minutes...')
            sleep(60*10) # run every 10 minutes
        except KeyboardInterrupt:
            print('Interrupt signal received. Exiting listen mode.')
            print(f'{errors_encountered} errors encountered throughout session.')
            break
        except:
            errors_encountered += 1
            print('Ran into an error while in listen mode.')
            traceback.print_exc()
        else:
            print('API stream exited gracefully.')
        print('Re-running listen mode...')
        print(f'(Had {errors_encountered} errors so far.)')
