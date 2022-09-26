## The bot's catch-up mode
# Scan all accounts for cross-company interactions.
# Terminates when finished scanning and posting.
#
# We should post, at the fastest, one tweet per minute.

import traceback
import datetime
import sys
import os
import asyncio

import twint

from util import *
from talent_lists import *
from twapi import TwAPI
import talenttweet as tt

def write_user_date(user_id, file, date_str = None, error = False):
    if date_str is None:
        date_str = util.datetime_to_tdate(datetime.datetime.now())

    file.write(f'# {user_id} {date_str if not error else "-1"}\n')
    pass

def get_queue_file():
    return f'{util.get_project_dir()}/queue.txt'

def get_local_queue():
    # f = open(os.path.join(get_project_dir(), 'queue.txt'))
    pass

## Returns the ID of all tweets (up to limit) from a user ID.
def get_user_tweets(id, since_date='', limit=None):
    tweets = list()
    c = twint.Config()
    c.User_id = id
    c.Limit = limit
    c.Store_object = True
    c.Store_object_tweets_list = tweets
    c.Hide_output = True
    c.Since = since_date
    
    user_str = f'{util.get_username(id)}'
    print(f'Scraping tweets from {user_str}...')
    try:
        twint.run.Search(c)
    except:
        print(f'Had trouble getting tweets from {user_str}')
    
    print(f'Scraped {len(tweets)} tweets')
    return tweets

# If queue.txt doesn't exist, creates and populates it.
# Returns a list of sorted and filtered TalentTweets (should
# be equivalent to queue.txt)
async def get_cross_talent_tweets(queue_path):
    finished_user_tdates = dict()
    ttweets_dict = dict()

    # Populate structures with existing data from queue.txt
    try:
        print('Processing existing data in queue.txt...')
        with open(queue_path, 'r') as f:
            # Check for finished and incomplete accounts
            # LINE FORMAT: "# {user_id} {status_num} (TODO: use date of retrival YYYY-MM-DD)
            for line in f:
                tokens = line.split()
                if len(tokens) != 3 or tokens[0][0] != '#':
                    # reached end of accounts list
                    break

                if tokens[2] != '-1':
                    finished_user_tdates[int(tokens[1])] = tokens[2]
            
            # Add existing serialized TalentTweets into ttweets
            for line in f:
                tokens = line.split()
                if len(tokens) == 0 or tokens[0][0] == '#':
                    continue
                ttweet = tt.TalentTweet.deserialize(line)
                ttweets_dict[ttweet.tweet_id] = ttweet
    except FileNotFoundError:
        print('Couldn\'t find queue.txt.')

    # Pull tweets from twint
    with open(queue_path, 'w') as f:
        # for talent_id in talent_lists.talents:
        for talent_id in talent_lists.test_talents:
            print('using test_talents')
            if talent_id not in finished_user_tdates or \
                finished_user_tdates[talent_id] != util.datetime_to_tdate(datetime.datetime.today()):
                try:
                    tweets = get_user_tweets(talent_id, since_date=finished_user_tdates.get(talent_id, None))
                    for tweet in tweets:
                        ttweet = await tt.TalentTweet.create_from_twint_tweet(tweet)
                        if ttweet.is_cross_company():
                            ttweets_dict[ttweet.tweet_id] = ttweet
                except:
                    print('Error occurred processing tweet data. Traceback:')
                    print(traceback.format_exc())
                    write_user_date(user_id=talent_id, file=f, error=True)
                else:
                    write_user_date(user_id=talent_id, file=f)
            else:
                print(f'Skipping already completed {util.get_username(talent_id)}')
                write_user_date(user_id=talent_id, file=f, date_str=finished_user_tdates[talent_id])
        f.write('\n')
        ttweets_dict = dict(sorted(ttweets_dict.items()))
        for ttweet in ttweets_dict.values():
            f.write(f'{ttweet.serialize()}\n')
    
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
    print(f'got {len(ttweet_dict)} tweets')