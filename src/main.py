import sys
import asyncio
import argparse
from argparse import RawTextHelpFormatter
import code

import nest_asyncio

import talent_lists
import ttweetqueue as ttq
import api_secrets
import catchup
import listen
from twapi import TwAPI

PROGRAM_ARGS = None

MODES_HELP_STR = '''mode to run the bot at:
l,listen:      listen for new tweets from all accounts; will not terminate unless error occurs
c,catchup:     scan all tweets from all accounts; will terminate when done
d,delete-all:  delete all tweets on account provided by secrets.ini; make sure the function is uncommented in twapi.py'''

def init_argparse():
    p = argparse.ArgumentParser(description='Twitter bot that follows interactions between Nijisanji EN/ID and hololive EN/ID members.', formatter_class=RawTextHelpFormatter)
    p.add_argument('mode', nargs='?', \
        help=MODES_HELP_STR)
    p.add_argument('--no-delay', action='store_true', help='In self-destruct mode, clear tweets without safety waiting.')
    return p

def command_line():
    # TODO (extra): implement command line mode for manually controlling the bot
    print('Shell coming soon. For now, here\'s a Python interpretor.')
    code.interact(local=globals())
    pass

async def self_destruct():
    if not PROGRAM_ARGS.no_delay:
        print('\033[31;6m-----DELETING ALL TWEETS IN 10 SECONDS!! PRESS CTRL+C TO CANCEL.-----\033[0m')
        await asyncio.sleep(10)
    await TwAPI.instance.nuke_tweets()

async def async_main():
    global PROGRAM_ARGS

    if PROGRAM_ARGS.mode == None:
        await catchup.run()
        return
    
    mode = PROGRAM_ARGS.mode.lower()
    if mode in ['d', 'delete-all']:
        print('WARNING: SELF-DESTRUCT MODE')
        await self_destruct()
    elif mode == 'cmd':
        command_line()
    else:
        print('\nunknown mode. run with no arguments or -h for help and modes')

def main():
    global PROGRAM_ARGS

    parser = init_argparse()
    # if len(sys.argv) < 2:
    #     parser.print_help()
    #     return

    PROGRAM_ARGS = parser.parse_args()

    ## We expect to run in some mode now.

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
