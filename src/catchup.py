## The bot's catch-up mode
# Scan all accounts for cross-company interactions.
# Terminates when finished scanning and posting.
#
# We should post, at the fastest, one tweet per minute.

import traceback
import datetime
import asyncio
import shutil

import twint

from util import *
from talent_lists import *
from twapi import TwAPI
import talenttweet as tt
import ttweetqueue as ttq

PROGRAM_ARGS = None
safe_to_post_tweets = True
errored = False

## Returns the ID of all tweets (up to limit) from a user ID.
def get_user_tweets(id, since_timestamp=None, limit=None):
    qrt_count = 0
    tweets = list()
    c = twint.Config()
    c.User_id = id
    c.Limit = limit
    c.Store_object = True
    c.Store_object_tweets_list = tweets
    c.Hide_output = True
    c.Since = '' if since_timestamp == None else util.timestamp_to_tdate(since_timestamp)
    
    user_str = f'@{util.get_username_local(id)}'
    print(f'Scraping tweets from {user_str} since {"forever ago" if c.Since == "" else c.Since}...')
    try:
        twint.run.Search(c)
    except:
        print(f'Had trouble getting tweets from {user_str}')
        safe_to_post_tweets = False
        traceback.print_exc()

    for twt in tweets:
        if type(twt.quote_url) is str and twt.quote_url != '':
            qrt_count += 1
    
    print(f'Scraped {len(tweets)} tweets, {qrt_count} of which are quote tweets.')
    return tweets

# Returns a list of sorted and filtered TalentTweets (should
# be equivalent to queue.txt)
async def get_cross_talent_tweets():
    posted_ttweets = set() # TODO: don't add TTweet to ttweets_dict if its id exists in posted_ttweets
    global safe_to_post_tweets

    queue = ttq.TalentTweetQueue.instance

    # Begin getting tweets from online
    print('Pulling tweets from online!')
    try:
        for i, (talent_id, talent_username) in enumerate(talent_lists.talents.items()):
            print(f'[{i+1}/{len(talent_lists.talents)}] {talent_username}-----------------------------------')
            try:
                tweets = get_user_tweets(talent_id, since_timestamp=queue.finished_user_timestamps.get(talent_id, None))
                for tweet in tweets:
                    if tweet.id not in queue.ttweets_dict:
                        ttweet = await tt.TalentTweet.create_from_twint_tweet(tweet)
                        if ttweet.is_cross_company():
                            queue.add_ttweet(ttweet)
            except:
                print('Error occurred processing tweet data.')
                safe_to_post_tweets = False
                print(traceback.format_exc())
                queue.finished_user_timestamps[talent_id] = -1
            else:
                queue.finished_user_timestamps[talent_id] = util.get_current_timestamp()
    except:
        print('Unhandled error occurred while pulling tweets.')
        traceback.print_exc()
        safe_to_post_tweets = False
    else:
        print('Successfully saved all tweets from online!')
        queue.save_file()
    
    return queue.get_ttweets_dict()

# return False = errored or we posted at least one ttweet
# return True = we didn't post a single ttweet
async def process_queue() -> bool:
    global PROGRAM_ARGS
    global errored
    WAIT_TIME = 30
    ttweets_posted = 0
    errored = False

    queue = ttq.TalentTweetQueue.instance
    queued_ttweets_count = len(queue.ttweets_dict)

    if queued_ttweets_count == 0: return ttweets_posted
    
    if PROGRAM_ARGS.announce_catchup:
        TwAPI.instance.post_tweet(text=f'Starting to catch up through {queued_ttweets_count} logged tweets.')
    
    try:
        while len(queue.ttweets_dict) > 0:
            key = list(queue.ttweets_dict.keys())[0]
            ttweet = queue.ttweets_dict[key]
            queue.good = False
            tweet_was_successful = await TwAPI.instance.post_ttweet(ttweet, is_catchup=True)
            queue.ttweets_dict.pop(key)
            
            print('saving new queue...')
            queue.good = True
            queue.save_file()
            if tweet_was_successful:
                ttweets_posted += 1
                print(f'({ttweets_posted}/{queued_ttweets_count}) done')
                if len(queue.ttweets_dict) > 0:
                    print(f'resting for {WAIT_TIME}s...')
                    await asyncio.sleep(WAIT_TIME-5)
                    print('5 second warning!')
                    await asyncio.sleep(5)
    except:
        print('Unhandled error occurred while posting tweets from queue.')
        errored = True
        traceback.print_exc()
    else:
        if PROGRAM_ARGS.announce_catchup:
            await TwAPI.instance.post_tweet('Finished with catch-up tweets!')
    
    if errored or ttweets_posted > 0:
        return False
    return True

# return True = no problems
# return False = issue occurred where we couldn't post all past tweets properly
async def run(program_args):
    global PROGRAM_ARGS
    global errored
    global safe_to_post_tweets
    PROGRAM_ARGS = program_args

    # in case we we experience failure and we're left with blank queue.txt
    # TODO: create TweetQueue class to organize file IO better; move all backup operations to there
    ttq.TalentTweetQueue()

    ret = None
    while True:
        queue = ttq.TalentTweetQueue.instance
        ttweets_dict = queue.ttweets_dict = await get_cross_talent_tweets()
        print(f'found {len(ttweets_dict)} cross-company tweets')
        try:
            if safe_to_post_tweets:
                if await process_queue():
                    print('Posted no new tweets; we\'re caught up!')
                    return True
            else:
                print('Tweets were not retrieved cleanly.')
                # os.remove(queue_path)  # keep backup queue
                return False
        except:
            print('Unhandled error occurred while running catch up in posting phase.')
            traceback.print_exc()
            return False
        
        if errored:
            return False
