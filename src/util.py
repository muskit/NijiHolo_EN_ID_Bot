## Shared utility functions.

import os
import talent_lists
import talenttweet as tt

# returns system path to this project, which is
# up one level from this file's directory (src).
def get_project_dir():
    return os.path.join(os.path.dirname(__file__), os.pardir)

def tweet_id_to_url(id):
    return f'https://twitter.com/twitter/status/{id}'

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))