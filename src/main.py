import sys
import asyncio
import argparse
from argparse import RawTextHelpFormatter
import code

import nest_asyncio

import talent_lists
import ttweetqueue as ttq
import catchup
import listen
from twapi import TwAPI

PROGRAM_ARGS = None

MODES_HELP_STR = '''mode to run the bot at:
<blank>      scrape accounts in lists and post cross-company tweets if relevant
cmd          drop into Python interpretor with access to initialized variables'''

def init_argparse():
    p = argparse.ArgumentParser(description='Twitter bot that follows interactions between Nijisanji EN/ID and hololive EN/ID members.', formatter_class=RawTextHelpFormatter)
    p.add_argument('mode', nargs='?', help=MODES_HELP_STR)
    p.add_argument('--no-listen', action='store_true', help='Run one scraping-posting cycle without waiting to run again.')
    p.add_argument('--straight-to-queue', action='store_true', help='Go through queue first before attempting to pull tweets.')
    return p

def command_line():
    # TODO (extra): implement command line mode for manually controlling the bot
    print('Here\'s a Python interpretor.')
    code.interact(local=globals())

async def async_main():
    global PROGRAM_ARGS

    if PROGRAM_ARGS.mode == None:
        if PROGRAM_ARGS.no_listen:
            await catchup.run(PROGRAM_ARGS)
        else:
            listen.run(PROGRAM_ARGS)
        return
    
    mode = PROGRAM_ARGS.mode.lower()
    if mode == 'cmd':
        command_line()
    else:
        print('\nunknown mode. run with no arguments or -h for help and modes')

def main():
    global PROGRAM_ARGS

    parser = init_argparse()
    if len(sys.argv) < 2:
        parser.print_help()
        return

    PROGRAM_ARGS = parser.parse_args()

    # Initialize shared API instance
    TwAPI()

    # Initialize talent account lists
    talent_lists.init()

    # Initialize queue files system
    ttq.TalentTweetQueue()

    ## Asynchronous execution
    nest_asyncio.apply()
    asyncio.run(async_main())
    

if __name__ == "__main__":
    main()
