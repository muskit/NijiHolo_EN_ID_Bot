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

def work_on_queue():
    # while Queue.txt has lines present
    #   attempt to deserialize first line of Queue.txt
    #     exit program if failed, stating error
    #   while post isn't successful
    #     attempt to post tweet
    #   delete serialized line from Queue.txt, save it
    # 
    # we're done! post tweet announcing done with archives
    pass

async def run():
    pass
    # if Queue.txt exists
    #   work through the tweets in Queue.txt
    # else
    #   look through every talent's tweets, saving only cross-company tweets into a list
    #   sort the list by tweet_id
    #   create Queue.txt and save all tweets through there
    #   post a tweet announcing archival intent
    #   work through the tweets in Queue.txt