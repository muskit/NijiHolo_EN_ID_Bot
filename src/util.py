## Shared utility functions.

import os

import twint
from tweetcapture import TweetCapture

import talent_lists
import talenttweet as tt

# returns system path to this project, which is
# up one level from this file's directory (effective path: ..../src/../).
def get_project_dir():
    return os.path.join(os.path.dirname(__file__), os.pardir)

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

async def create_ttweet_image(ttweet):
    tc = TweetCapture()
    filename = 'img.png'
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
    username = get_username(ttweet.author_id)
    return f'https://twitter.com/{username}/status/{ttweet.tweet_id}'

def get_username(user_id):
    return talent_lists.talents.get(user_id, f'#{id}')

def get_username_online(user_id):
    c = twint.Config()
    c.User_id = user_id
    c.Store_object = True
    c.Hide_output = True
    try:
        twint.run.Lookup(c)
        user = twint.output.users_list[0]
        twint.output.users_list.clear()
        return user.username
    except:
        return f'#{user_id}'