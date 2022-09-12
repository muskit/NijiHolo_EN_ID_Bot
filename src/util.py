## Shared utility functions.

import os

global twAPI
twAPI = None

# returns system path to this project, which is
# up one level from this file's directory.
def get_project_dir():
    return os.path.join(os.path.dirname(__file__), os.pardir)

# determine if tweet involves cross-company interaction
def is_cross_company(tweet):
    pass

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))