import sys
import argparse
from argparse import RawTextHelpFormatter
import TwitterAPI as api
import catchup as catchup

HELP_TEXT = \
'''OPTIONS:
    -h                  Displays this help text.
    -c, --catchup       Scan all tweets from all accounts and makes posts all cross-company
                        interactions found.
    -l, --listern       Listen for all new tweets from all accounts.
'''

def init_argparse():
    p = argparse.ArgumentParser(description='Twitter bot that follows interactions between Nijisanji EN/ID and hololive EN/ID members.', formatter_class=RawTextHelpFormatter)
    p.add_argument('mode', nargs='?', \
        help='mode to run the bot at:\n\
  l,listen:       (default) listen for new tweets from all accounts; will not terminate unless error occurs\n\
  c,catchup:      scan all tweets from all accounts; will terminate when done')
    return p

def main():
    parser = init_argparse()
    if len(sys.argv) < 2:
        parser.print_help()
        return

    args = parser.parse_args()
    print(args.mode)

    match args.mode:
        case 'l' | 'listen':
            print('LISTEN MODE')
        case 'c' | 'catchup':
            print('CATCH-UP MODE')
    

if __name__ == "__main__":
    main()
