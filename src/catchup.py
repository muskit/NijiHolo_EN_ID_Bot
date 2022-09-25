## The bot's catch-up mode
# Scan all accounts for cross-company interactions.
# Terminates when finished scanning and posting.
#
# We should post, at the fastest, one tweet per minute.

import os

import twint

from util import *
from talent_lists import *
from api import TwAPI
import talenttweet as tt

## Returns list of tweets present in queue.txt
def get_local_queue():
    # f = open(os.path.join(get_project_dir(), 'queue.txt'))
    pass

## Returns the ID of all tweets (up to limit) from a user ID.
def get_user_tweet_ids(id, limit=None):
    tweets = list()
    c = twint.Config()
    c.User_id = id
    c.Limit = limit
    c.Store_object = True
    c.Store_object_tweets_list = tweets
    
    twint.run.Search(c)
    return [x.id for x in tweets]

def run():
    queue = get_local_queue()

    tweets_ids = get_user_tweet_ids(1390620618001838086, limit=20)
    for id in tweets_ids:
        ttweet = tt.TalentTweet(id)
        print(ttweet)