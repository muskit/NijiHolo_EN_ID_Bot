## The bot's listen mode
# Continuously listen for cross-company interactions.
from time import sleep

import asyncio
import traceback

import catchup

errors_encountered = 0

def run():
    global errors_encountered
    while True:
        try:
            asyncio.run(catchup.run())
            print('Sleeping for 30 minutes...')
            sleep(1800) # run every half-hour
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
