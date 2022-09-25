## The bot's catch-up mode
# Scan all accounts for cross-company interactions.
# Terminates when finished scanning and posting.
#
# We should post, at the fastest, one tweet per minute.

import os
import asyncio

import twint

from util import *
from talent_lists import *
from api import TwAPI
import talenttweet as tt

cross_tweets_queue = dict()

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
    c.Hide_output = True
    
    twint.run.Search(c)
    return [x.id for x in tweets]

async def run():
    queue = get_local_queue()

    # for user_id in talents.keys():
    #     tweets_ids = get_user_tweet_ids(user_id, limit=20)
    #     for id in tweets_ids:
    #         ttweet = tt.TalentAPITweet(id)
    #         print(ttweet)

    # ids = get_user_tweet_ids(1413339084076978179, limit=20)
    # for id in ids:
    #     ttweet = tt.TalentAPITweet(tweet_id=id)
    #     print(ttweet)

    # serialized_ttweet = '1573778069441200129 1390620618001838086 1664052905.0 m 70876713 1413326894435602434 r 1413326894435602434'
    # ttweet = tt.TalentTweet.deserialize(serialized_ttweet)
    # print(ttweet)

    ttweet = tt.TalentAPITweet(1573563417415233536)
    print(ttweet)
    # await TwAPI.instance.create_post(ttweet)