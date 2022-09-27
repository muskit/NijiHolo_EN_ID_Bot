import sys
import asyncio
import argparse
from argparse import RawTextHelpFormatter

import nest_asyncio

import talent_lists
import api_secrets
import catchup
import listen
from twapi import TwAPI

PROGRAM_ARGS = None

MODES_HELP_STR = '''mode to run the bot at:
l,listen:       listen for new tweets from all accounts; will not terminate unless error occurs
c,catchup:      scan all tweets from all accounts; will terminate when done'''

def init_argparse():
    p = argparse.ArgumentParser(description='Twitter bot that follows interactions between Nijisanji EN/ID and hololive EN/ID members.', formatter_class=RawTextHelpFormatter)
    p.add_argument('mode', nargs='?', \
        help=MODES_HELP_STR)
    p.add_argument('--show-tokens', action='store_true', help='[DO NOT USE IN PUBLIC SETTING] print stored tokens from secrets.ini')
    p.add_argument('--announce-catchup', action='store_true', help='In catch-up mode, post a tweet announcing catch-up mode.')
    return p

def command_line():
    # TODO: implement command line mode for manually controlling the bot
    pass

async def async_main():
    global PROGRAM_ARGS

    ## Determine running mode
    match PROGRAM_ARGS.mode.lower():
        case 'l' | 'listen':
            print('RUNNING IN LISTEN MODE\n')
            listen.run()
        case 'c' | 'catchup':
            print('RUNNING IN CATCH-UP MODE\n')
            await catchup.run(PROGRAM_ARGS)
        case _: 
            command_line()
            #TODO: remove message
            print('\ninvalid mode. run with no arguments or "-h" for help page, including mode list.')
            return

def main():
    global PROGRAM_ARGS

    parser = init_argparse()
    if len(sys.argv) < 2:
        parser.print_help()
        return

    PROGRAM_ARGS = parser.parse_args()

    if PROGRAM_ARGS.show_tokens:
        print(api_secrets.get_all_secrets())

    if PROGRAM_ARGS.mode is None: return

    ## We expect to run in some mode now.

    # Initialize shared API instance
    twApi = TwAPI.instance = TwAPI()

    # Initialize talent account lists
    talent_lists.init()

    ## Asynchronous execution
    nest_asyncio.apply()
    asyncio.run(async_main())
    

if __name__ == "__main__":
    main()