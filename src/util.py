## Shared utility functions.

import os
import talent_lists

# returns system path to this project, which is
# up one level from this file's directory (src).
def get_project_dir():
    return os.path.join(os.path.dirname(__file__), os.pardir)

# determine if tweet involves cross-company interaction
def is_cross_company(pair: tuple):
    author_id, mentions = pair[0].author_id, pair[1]

    for mention_id in mentions:
        if author_id in talent_lists.niji_en:
            if mention_id in talent_lists.holo_en:
                return True
        elif author_id in talent_lists.holo_en:
            if mention_id in talent_lists.niji_en:
                return True
    return False

def tweet_id_to_url(id):
    return f'https://twitter.com/twitter/status/{id}'

def print_tweet(pair: tuple):
    tweet, mentions = pair
    s = (
        f'{tweet.id}: {tweet.created_at}: involves {mentions}\n'
        f'{tweet.text}\n'
        f'-----\n'
        f'{tweet.entities}\n'
        f'{tweet.referenced_tweets}\n'
        f'================================================='
    )
    print(s)

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))