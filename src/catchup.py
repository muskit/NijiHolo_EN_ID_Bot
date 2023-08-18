## The bot's catch-up mode
# Scan all accounts for cross-company interactions.
# Terminates when finished scanning and posting.
#
# We should post, at the fastest, one tweet per minute.

import traceback
import datetime
import asyncio
import shutil
from datetime import datetime

from scraper import Scraper
from util import *
from talent_lists import *
from twapi import TwAPI
import talenttweet as tt
import ttweetqueue as ttq

safe_to_post_tweets = True
errored = False

# Returns a list of sorted and filtered TalentTweets (should
# be equivalent to queue.txt)
async def get_cross_tweets_online():
    global safe_to_post_tweets

    scraper = Scraper()
    queue = ttq.TalentTweetQueue.instance

    # Begin getting tweets from online
    print('Pulling tweets from online!')
    try:
        for i, (talent_id, talent_username) in enumerate(talent_lists.talents.items()):
            print(f'[{i+1}/{len(talent_lists.talents)}] {talent_username}-----------------------------------')
            try:
                # tweets = get_user_tweets(talent_id, since_date=queue.finished_user_dates.get(talent_id, None))
                since_date = queue.finished_user_dates.get(talent_id, None)
                ttweets = scraper.get_cross_ttweets_from_user(talent_username, since_date=since_date)
                print(f'got {len(ttweets)} TalentTweets')
                for ttweet in ttweets:
                    if ttweet.tweet_id not in queue.finished_ttweets \
                        and ttweet.is_cross_company():
                        queue.add_ttweet(ttweet)
            except KeyboardInterrupt as e:
                raise e
            except:
                print('Error occurred processing tweet data.')
                safe_to_post_tweets = False
                traceback.print_exc()
                if talent_id not in queue.finished_user_dates:
                    queue.finished_user_dates[talent_id] = '2023-04-26' # date is when bot token first got revoked 
            else:
                queue.finished_user_dates[talent_id] = util.get_current_date()
                queue.save_file()
    except KeyboardInterrupt:
        print('Interrupting tweet pulling... NOTE: remaining dates in queue file will not be updated!')
        queue.save_file()
    except:
        print('Unhandled error occurred while pulling tweets.')
        traceback.print_exc()
        safe_to_post_tweets = False
    else:
        print('Successfully saved all tweets from online!')
        queue.save_file()

# return False = errored or we posted at least one ttweet
# return True = we didn't post a single ttweet
async def process_queue() -> bool:
    global errored
    
    WAIT_TIME = 60*15
    ttweets_posted = 0
    errored = False

    queue = ttq.TalentTweetQueue.instance
    queued_ttweets_count = queue.get_count()

    if queued_ttweets_count == 0:
        print('Posting queue is empty!')
        return True
    
    try:
        while not queue.is_empty():
            ttweet = queue.get_next_ttweet()
            tweet_was_successful = await TwAPI.instance.post_ttweet(ttweet)
            
            print('running queue.good()...')
            queue.good()
            if tweet_was_successful:
                ttweets_posted += 1
                print(f'({ttweets_posted}/{queued_ttweets_count}) done')
                if not queue.is_empty():
                    print(f'resting for {WAIT_TIME}s...')
                    await asyncio.sleep(WAIT_TIME-5)
                    print('5 second warning!')
                    await asyncio.sleep(5)
    except:
        print('Unhandled error occurred while posting tweets from queue.')
        errored = True
        traceback.print_exc()

    if errored or ttweets_posted > 0:
        return False
    return True

# return True = no problems
# return False = issue occurred where we couldn't post all past tweets properly
async def run(PROGRAM_ARGS):
    global errored
    global safe_to_post_tweets

    queue = ttq.TalentTweetQueue.instance

    async def queue_loop():
        while True:
            print(f'{queue.get_count()} cross-company tweets to attempt sharing.')
            try:
                if safe_to_post_tweets:
                    if await process_queue():
                        print('Posted no new tweets; we\'re caught up!')
                        return True
                else:
                    print('Tweets were not retrieved cleanly.')
                    return False
            except KeyboardInterrupt:
                print('Interrupting queue processing...')
                return False
            except:
                print('Unhandled error occurred while running catch up in posting phase.')
                traceback.print_exc()
                return False
            
            if errored:
                return False
            
            await get_cross_tweets_online()

    if PROGRAM_ARGS.straight_to_queue:
        print('Processing queue first before pulling tweets...')
        return await queue_loop()
    else:
        await get_cross_tweets_online()
        return await queue_loop()
