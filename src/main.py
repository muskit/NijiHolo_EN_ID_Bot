import sys
import argparse
from argparse import RawTextHelpFormatter

import secrets
import catchup
import listen

from api import API

def init_argparse():
    p = argparse.ArgumentParser(description='Twitter bot that follows interactions between Nijisanji EN/ID and hololive EN/ID members.', formatter_class=RawTextHelpFormatter)
    p.add_argument('mode', nargs='?', \
        help='mode to run the bot at:\n\
  l,listen:       listen for new tweets from all accounts; will not terminate unless error occurs\n\
  c,catchup:      scan all tweets from all accounts; will terminate when done')
    p.add_argument('--show-tokens', action='store_true', help='[DO NOT USE IN PUBLIC SETTING] print stored tokens from secrets.ini')
    return p

def main():
    parser = init_argparse()
    if len(sys.argv) < 2:
        parser.print_help()
        return

    args = parser.parse_args()

    if args.show_tokens:
        print(secrets.get_all_secrets())

    if args.mode is None: return

    api = API()
    api.get_tweets(1390620618001838086)

    # determine running mode
    match args.mode.lower():
        case 'l' | 'listen':
            print('RUNNING IN LISTEN MODE\n')
            listen.run()
        case 'c' | 'catchup':
            print('RUNNING IN CATCH-UP MODE\n')
            catchup.run()
        case _:
            print('\ninvalid mode. run with no arguments for help page, including mode list.')
            return
    

if __name__ == "__main__":
    main()
