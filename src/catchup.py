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
from twapi import TwAPI
import talenttweet as tt

def get_queue_file():
    return f'{util.get_project_dir()}/queue.txt'

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
    
    user_str = f'{id} ({util.get_username(id)})'
    print(f'Finding tweets from {user_str})')
    try:
        twint.run.Search(c)
        return [x.id for x in tweets]
    except:
        print(f'Had trouble getting tweets from {user_str}')
        return list()

def work_on_queue(file):
    print('TODO: implement work_on_queue')
    # while Queue.txt has lines present
    #   attempt to deserialize first line of Queue.txt
    #     exit program if failed, stating error
    #   while post isn't successful
    #     attempt to post tweet
    #   delete serialized line from Queue.txt, save it
    # 
    # we're done! post tweet announcing done with archives
    pass

# If queue.txt doesn't exist, creates and populates it.
# Returns a list of sorted and filtered TalentTweets (should
# be equivalent to queue.txt)
def create_ttweets_queue(path) -> list:
    print('Creating ttweets queue')
    if not os.path.exists(path):
        ttweets = list()
        with open(path, 'x') as f:
            for talent_id in talents.keys():
                tweet_ids = get_user_tweet_ids(talent_id)
                print(f'retrieved {len(tweet_ids)} tweets')
                for tweet_id in tweet_ids:
                    ttweet = tt.TalentAPITweet(tweet_id)
                    if ttweet.is_cross_company():
                        ttweets.append(ttweet)

            ttweets.sort(key=lambda ttweet: ttweet.tweet_id)
            for ttweet in ttweets:
                f.write(f'{ttweet.serialize()}\n')
        return ttweets
    else:
        return list()
                    

async def run():
    # if Queue.txt exists
    #   work through the tweets in Queue.txt
    # else
    #   look through every talent's tweets, saving only cross-company tweets into a list
    #   sort the list by tweet_id
    #   create Queue.txt and save all tweets through there
    #   post a tweet announcing archival intent
    #   work through the tweets in Queue.txt
    queue_path = get_queue_file()
    if os.path.exists(queue_path):
        work_on_queue(queue_path)
    else:
        ttweets = create_ttweets_queue(queue_path)