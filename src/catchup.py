## The bot's catch-up mode
# Scan all accounts for cross-company interactions.
# Terminates when finished scanning and posting.
#
# We should post, at the fastest, one tweet per minute.

import traceback
import datetime

import twint

from util import *
from talent_lists import *
from twapi import TwAPI
import talenttweet as tt

PROGRAM_ARGS = None
safe_to_post_tweets = True

def write_user_timestamp(user_id, file, timestamp = None, error = False):
    if timestamp is None:
        timestamp = datetime.datetime.now().timestamp()

    file.write(f'# {user_id} {timestamp if not error else "-1"}\n')
    pass

def get_queue_path():
    return f'{util.get_project_dir()}/queue.txt'

def get_local_queue():
    # f = open(os.path.join(get_project_dir(), 'queue.txt'))
    pass

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
        traceback.print_exc()

    for twt in tweets:
        if type(twt.quote_url) is str and twt.quote_url != '':
            qrt_count += 1
    
    print(f'Scraped {len(tweets)} tweets, {qrt_count} of which are quote tweets.')
    return tweets

# Returns dict of accounts that successfully caught up.
# LINE FORMAT: "# {user_id} {status_num} {UNIX_timestamp}
def get_finished_user_timestamps(queue_file):
    results = dict()
    for line in queue_file:
        tokens = line.split()
        if len(tokens) == 0: continue

        if tokens[0][0] != '#':
            print(f'{line} is our stopper!')
            # reached end of accounts list
            break
        if tokens[2] != '-1':
            results[int(tokens[1])] = float(tokens[2])
    return results

def get_user_timestamps_str(queue_file):
    results = str()
    for line in queue_file:
        tokens = line.split()
        if len(tokens) != 3 or tokens[0][0] != '#':
            # reached end of accounts list
            break
        results += f'{line}\n'
    return results[:-1]

# If queue.txt doesn't exist, creates and populates it.
# Returns a list of sorted and filtered TalentTweets (should
# be equivalent to queue.txt)
async def get_cross_talent_tweets(queue_path):
    finished_user_timestamps = dict()
    ttweets_dict = dict()
    posted_ttweets = set() # TODO: don't add TTweet to ttweets_dict if its id exists in posted_ttweets
    global safe_to_post_tweets

    # Populate structures with existing data from queue.txt
    try:
        with open(queue_path, 'r') as f:
            finished_user_timestamps =  get_finished_user_timestamps(f)
        
        with open(queue_path, 'r') as f: # reset seek head
            # Get existing queued TalentTweets
            for line in f:
                tokens = line.split()
                if len(tokens) == 0 or tokens[0][0] == '#':
                    continue
                ttweet = tt.TalentTweet.deserialize(line)
                ttweets_dict[ttweet.tweet_id] = ttweet
            print(f'Found {len(finished_user_timestamps)} scraped accounts and {len(ttweets_dict)} tweets.')
    except FileNotFoundError:
        print('queue.txt not found.')

    # Begin getting tweets from online
    with open(queue_path, 'w') as f:
        print('Pulling tweets from online!')
        try:
            for i, (talent_id, talent_username) in enumerate(talent_lists.talents.items()):
                print(f'[{i+1}/{len(talent_lists.talents)}] {talent_username}-----------------------------------')
                try:
                    # tweets = get_user_tweets(talent_id, since_timestamp=1663698621) # shorten test runs
                    tweets = get_user_tweets(talent_id, since_timestamp=finished_user_timestamps.get(talent_id, None))
                    for tweet in tweets:
                        if tweet.id not in ttweets_dict:
                            ttweet = await tt.TalentTweet.create_from_twint_tweet(tweet)
                            if ttweet.is_cross_company():
                                ttweets_dict[ttweet.tweet_id] = ttweet
                except:
                    print('Error occurred processing tweet data.')
                    safe_to_post_tweets = False
                    print(traceback.format_exc())
                    write_user_timestamp(user_id=talent_id, file=f, error=True)
                else:
                    write_user_timestamp(user_id=talent_id, file=f)
            f.write('\n')
            ttweets_dict = dict(sorted(ttweets_dict.items()))
            for ttweet in ttweets_dict.values():
                f.write(f'{ttweet.serialize()}\n')
        except:
            print('Unhandled error occurred while pulling tweets.')
            traceback.print_exc()
            print('Saving queue.txt and exiting.')
            safe_to_post_tweets = False
    
    return ttweets_dict

# Return number of TalentTweets successfully posted
async def process_queue(ttweets_dict: dict) -> int:
    global PROGRAM_ARGS
    ttweets_posted = 0

    if len(ttweets_dict) == 0: return ttweets_posted
    
    if PROGRAM_ARGS.announce_catchup:
        TwAPI.instance.post_tweet(text=f'Starting to catch up through {len(ttweets_dict)} logged tweets.')
    
    try:
        while len(ttweets_dict) > 0:
            key = list(ttweets_dict.keys())[0]
            ttweet = ttweets_dict[key]
            if await TwAPI.instance.post_ttweet(ttweet, is_catchup=True):
                ttweets_posted += 1
            ttweets_dict.pop(key)
            # TODO: add ttweet.tweet_id to some success list
    except:
        print('Unhandled error occurred while posting tweets from queue.')
        traceback.print_exc()
    else:
        if PROGRAM_ARGS.announce_catchup:
            await TwAPI.instance.post_tweet('Finished with catch-up tweets!')

    print('Updating what\'s left in ttweet_dict to queue.txt.')
    with open(get_queue_path(), 'r') as f:
        user_timestamps_str = get_user_timestamps_str(f)
    with open(get_queue_path(), 'w') as f:
        f.write(user_timestamps_str + '\n\n')
        for ttweet in ttweets_dict.values():
            f.write(f'{ttweet.serialize()}\n')
    
    return ttweets_posted

# return True = no problems
# return False = issue occurred where we couldn't post all past tweets properly
async def run(program_args):
    global PROGRAM_ARGS
    global safe_to_post_tweets
    PROGRAM_ARGS = program_args
    queue_path = get_queue_path()
    while True:
        ttweets_dict = await get_cross_talent_tweets(queue_path)
        print(f'found {len(ttweets_dict)} cross-company tweets')
        if safe_to_post_tweets:
            if await process_queue(ttweets_dict) == 0:
                print('Posted no new tweets; we\'re caught up!')
                return True
        else:
            print('Tweets were not retrieved cleanly.')
            return False