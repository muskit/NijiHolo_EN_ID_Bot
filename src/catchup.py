## The bot's catch-up mode
# Scan all accounts for cross-company interactions.
# Terminates when finished scanning and posting.
#
# We should post, at the fastest, one tweet per minute.

import traceback
import sys
import os
import asyncio

import twint
import tweepy

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
    
    user_str = f'{util.get_username(id)}'
    print(f'Scraping tweets from {user_str}...')
    try:
        twint.run.Search(c)
    except:
        print(f'Had trouble getting tweets from {user_str}')
    
    ret = [x.id for x in tweets]
    print(f'Scraped {len(ret)} tweets')
    return ret

# Produce tweet IDs from talent_list.talents for the producer/consumer model.
# Put lists of tweet IDs as we create them.
# Put None to queue to indicate end.
async def produce_ids_from_talents(queue: asyncio.Queue, finished_users):
    def debug(str):
        print(f'[prd] {str}')

    for talent_id in talents.keys():
        if talent_id in finished_users:
            debug(f'@{util.get_username(talent_id)} already done, skipping...')
        else:
            tweet_ids = get_user_tweet_ids(talent_id)
            debug(f'adding {util.get_username(talent_id)}\'s tweets to queue')
            await queue.put(tweet_ids)
        
    await queue.put(None)

async def consume_ids_into_ttweets(queue: asyncio.Queue, queue_file: str):
    def debug(str):
        print(f'[con] {str}')

    ttweets_dict = dict()
    with open(queue_file, 'w') as f:
        while True:
            tweet_ids = await queue.get()
            if tweet_ids is None: break
            try:
                for tweet_id in tweet_ids:
                    ttweet = await tt.TalentTweet.create_from_id(id=tweet_id)
                    if ttweet.is_cross_company():
                        ttweets_dict['tweet_id'] = ttweet
            except:
                debug(traceback.format_exc())
                debug(f'Error retrieving Tweet #{tweet_id} from api!')
                f.write('1\n') # 1 = error/incomplete
                break
            else:
                f.write('0\n') # 0 = success
        f.write('\n')
        ttweets_dict = dict(sorted(ttweets_dict.items()))
        for ttweet in ttweets_dict.values():
            f.write(f'{ttweet.serialize()}\n')
    return ttweets_dict

# If queue.txt doesn't exist, creates and populates it.
# Returns a list of sorted and filtered TalentTweets (should
# be equivalent to queue.txt)
async def get_cross_talent_tweets(queue_file):
    finished_users = set()
    ttweets_dict = dict()

    # Populate structures with existing data from queue.txt
    try:
        print('Processing existing data in queue.txt...')
        with open(queue_file, 'r') as f:
            # Check for finished and incomplete accounts
            # LINE FORMAT: "# {user_id} {status_num}"
            for line in f:
                tokens = line.split()
                if len(tokens) != 3 or tokens[0][0] != '#':
                    # reached end of accounts list
                    break
                if tokens[2] == 0:
                    finished_users.add(tokens[1])
            
            # Add existing serialized TalentTweets into ttweets
            for line in f:
                tokens = line.split()
                if len(tokens) == 0 or tokens[0][0] == '#':
                    continue
                ttweet = tt.TalentTweet.deserialize(line)
                ttweets_dict[ttweet.tweet_id] = ttweet
    except FileNotFoundError:
        print('Couldn\'t find queue.txt.')

    async_queue = asyncio.Queue()
    consumer = asyncio.create_task(consume_ids_into_ttweets(queue=async_queue, queue_file=queue_file))
    await produce_ids_from_talents(queue=async_queue, finished_users=finished_users)
    ttweets_dict = await consumer
    return ttweets_dict

def process_queue(file):
    print('TODO: implement process_queue')
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
    # if Queue.txt exists
    #   work through the tweets in Queue.txt
    # else
    #   look through every talent's tweets, saving only cross-company tweets into a list
    #   sort the list by tweet_id
    #   create Queue.txt and save all tweets (serialized) there
    #   post a tweet announcing archival intent
    #   work through the tweets in Queue.txt

    queue_path = get_queue_file()
    ttweet_dict = await get_cross_talent_tweets(queue_path)
    for ttweet in ttweet_dict.values():
        print(ttweet)