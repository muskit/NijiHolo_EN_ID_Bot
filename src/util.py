## Shared utility functions.

import datetime
import os

import pytz
import twint
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
        return None
    else:
        print(f'successfully saved {img}')
        return img

def ttweet_to_url(ttweet):
    username = get_username_online(ttweet.author_id)
    return f'https://twitter.com/{username}/status/{ttweet.tweet_id}'

def get_username_local(user_id):
    return talent_lists.talents.get(user_id, f'#{id}')

def get_username_online(user_id):
    c = twint.Config()
    c.User_id = user_id
    c.Store_object = True
    c.Hide_output = True
    try:
        twint.output.users_list.clear()
        twint.run.Lookup(c)
        user = twint.output.users_list[0]
        return user.username
    except:
        return f'#{user_id}'

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
