## The bot's catch-up mode
# Scan all accounts for cross-company interactions.
# Terminates when finished scanning.

import os
import TwitterAPI as api

from util import *

## Returns list of tweets present in queue.txt
def get_local_queue():
    f = open(os.path.join(get_project_dir(), 'queue.txt'))
    pass

def run():
    queue = get_local_queue()
    pass