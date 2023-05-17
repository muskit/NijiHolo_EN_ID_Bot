## Twitter developer credentials management.

from os.path import join, isfile
from dotenv import dotenv_values

import util

# returns dictionary of the Credentials section.
# [NOT TO BE USED OUTSIDE OF THIS FILE.]
def __get_env():
    f = join(util.get_project_dir(), '.env')
    if isfile(f):
        return dotenv_values(f)
    return None

# returns the consumer api_key stored in secrets.ini
def api_key():
    c = __get_env()
    return c.get(option='api_key', fallback='xxx') if c is not None else 'xxx'

# returns the consumer api_secret stored in secrets.ini
def api_secret():
    c = __get_env()
    return c.get(option='api_secret', fallback='yyy') if c is not None else 'yyy'

# returns the bearer_token stored in secrets.ini
def bearer_token():
    c = __get_env()
    return c.get(option='bearer_token', fallback='zzz') if c is not None else 'zzz'

# returns the access_token stroed in secrets.ini
def access_token():
    c = __get_env()
    return c.get(option='oauth1_access_token', fallback='zzz') if c is not None else 'aaa'

# returns the access_secret stroed in secrets.ini
def access_secret():
    c = __get_env()
    return c.get(option='oauth1_access_secret', fallback='zzz') if c is not None else 'bbb'

def get_all_secrets():
    return f'api_key:{api_key()}\napi_secret:{api_secret()}\nbearer_token:{bearer_token()}\naccess_token:{access_token()}\naccess_secret:{access_secret()}'