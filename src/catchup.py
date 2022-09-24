## The bot's catch-up mode
# Scan all accounts for cross-company interactions.
# Terminates when finished scanning and posting.
#
# We should post, at the fastest, one tweet per minute.

import os

from util import *
from api import TwAPI

## Returns list of tweets present in queue.txt
def get_local_queue():
    # f = open(os.path.join(get_project_dir(), 'queue.txt'))
    pass

def run():
    queue = get_local_queue()
    pairs = TwAPI.instance.get_users_all_tweets_mentions(1390620618001838086, count=5)
    for (tweet, mentions) in pairs:
        print_tweet(tweet, mentions)