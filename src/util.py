## Shared utility functions.

import os
import traceback
import datetime

import pytz
import twint
import twapi
from tweetcapture import TweetCapture

import talent_lists

# returns system path to this project, which is
# up one level from this file's directory (effective path: ..../src/../).
def get_project_dir():
    return os.path.join(os.path.dirname(__file__), os.pardir)

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def datetime_to_tdate(date_time: datetime.datetime):
    return date_time.strftime("%Y-%m-%d")

def tdate_to_datetime(tdate: str):
    return datetime.datetime.strptime("%Y-%m-%d")

def timestamp_to_tdate(timestamp=None):
    if timestamp==None:
        timestamp = datetime.datetime.now().timestamp()
    return datetime_to_tdate(datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc))

def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None

async def create_ttweet_image(ttweet):
    tc = TweetCapture()
    filename = f'{get_project_dir()}/img.png'
    url = ttweet_to_url(ttweet)
    img = None

    try: os.remove(filename)
    except: pass
    try:
        img = await tc.screenshot(
            url=url,
            path=filename,
            mode=4,
            night_mode=1
        )
    except:
        print('unable to create tweet image')
        traceback.print_exc()
        return None
    else:
        print(f'successfully saved {img}')
        return img

def get_tweet_url(id, username):
    return f'https://twitter.com/{username}/status/{id}'

def ttweet_to_url(ttweet):
    username = get_username(ttweet.author_id)
    return get_tweet_url(ttweet.tweet_id, username)

def get_username_local(id):
    return talent_lists.talents.get(id, f'{id}')

# twint
# May not work with short user IDs (ie. 1354241437)
# def get_username_online(id, default=None):
#     c = twint.Config()
#     c.User_id = id
#     c.Store_object = True
#     c.Hide_output = True
#     try:
#         twint.output.users_list.clear()
#         twint.run.Lookup(c)
#         user = twint.output.users_list[0]
#         return user.username
#     except:
#         return str(default) if default is not None else f'{id}'

# API v2 (tweepy)
# Short user IDs (ie. 1354241437) apparently don't work with twint
def get_username_online(id, default=None):
    try:
        resp = twapi.TwAPI.instance.client.get_user(id=id)
        return resp.data.username
    except:
        print(f'Unhandled error retrieving username for {id}!')
        traceback.print_exc()
        return str(default) if default is not None else f'id:{id}'

## Attempt to pull username from local; pull from online if doesn't exist.
def get_username(id):
    ret = talent_lists.talents.get(id, None)
    if ret == None:
        return get_username_online(id)
    return ret

def get_user_id_local(username) -> int:
    talent_usernames = list(talent_lists.talents.values())
    for i in range(0, len(talent_usernames)):
        if username.lower() == talent_usernames[i].lower():
            return list(talent_lists.talents)[i]
    
def get_user_id_online(username) -> int:
    c = twint.Config()
    c.Username = username
    c.Store_object = True
    c.Hide_output = True
    try:
        twint.output.users_list.clear()
        twint.run.Lookup(c)
        user = twint.output.users_list[0]
        return user.id
    except:
        return -1
