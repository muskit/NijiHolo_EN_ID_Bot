## Shared utility functions.

import os
import sys
import traceback
from datetime import datetime
from dotenv import dotenv_values

import pytz
from tweetcapture import TweetCapture
import tweepy

from recrop import fix_aspect_ratio
import talent_lists

# returns system path to this project, which is
# up one level from this file's directory (effective path: ..../src/../).
def get_project_dir():
    return os.path.join(os.path.dirname(__file__), os.pardir)

def get_queue_path():
    return f'{get_project_dir()}/queue.txt'

def get_queue_backup_path():
    return f'{get_project_dir()}/_queue_backup.txt'

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def datetime_to_tdate(date_time: datetime):
    return date_time.strftime("%Y-%m-%d")

def tdate_to_datetime(tdate: str):
    return datetime.strptime("%Y-%m-%d")

def timestamp_to_tdate(timestamp=None):
    if timestamp==None:
        timestamp = datetime.now().timestamp()
    return datetime_to_tdate(datetime.fromtimestamp(timestamp, tz=pytz.utc))

def get_current_timestamp():
    return datetime.now().timestamp()

def get_current_date():
    return datetime.today().strftime('%Y-%m-%d')

def get_key_from_value(d: dict, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None

# FIXME: web_auth_token under rate-limitation will fail to screenshot
async def create_ttweet_image(ttweet):
    tc = TweetCapture()
    auth_token = dotenv_values().get('web_auth_token')
    if auth_token:
        tc.cookies = [{'name': 'auth_token', 'value': auth_token}]
    if 'linux' in sys.platform:
        # Linux chromedriver path
        tc.driver_path = '/usr/bin/chromedriver'
    filename = f'{get_project_dir()}/img.png'
    img = None
    try: os.remove(filename)
    except: pass
    try:
        img = await tc.screenshot(
            url=ttweet.url(),
            path=filename,
            mode=4,
            night_mode=1,
            show_parent_tweets=True
        )
        img = fix_aspect_ratio(img)
    except:
        print('unable to create tweet image')
        traceback.print_exc()
        return None
    
    print(f'successfully saved {img}')
    return img

def get_tweet_url(id, username):
    return f'https://www.twitter.com/{username}/status/{id}'

## Attempt to pull username from local; pull from online if doesn't exist.
def get_username(id):
    ret = talent_lists.talents.get(id, None)
    if ret == None:
        return get_username_online(id)
    return ret

def get_username_with_company(id):
    company = talent_lists.talents_company.get(id, None)
    return f'{get_username(id)} {f"({company})" if company is not None else ""}'

def get_username_local(id: int):
    return talent_lists.talents.get(id, f'{id}')

# Retrieve username via API v2 (tweepy)
def get_username_online(id, default=None):
    import twapi
    try:
        resp = twapi.TwAPI.instance.client.get_user(id=id)
        return resp.data.username
    except tweepy.TooManyRequests:
        return str(default) if default is not None else f'id:{id}'
    except:
        print(f'Unhandled error retrieving username for {id}!')
        traceback.print_exc()
        return str(default) if default is not None else f'id:{id}'