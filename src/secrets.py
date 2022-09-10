## Twitter developer credentials management.

import os
import configparser

# returns dictionary of the Credentials section.
# [NOT TO BE USED OUTSIDE OF THIS FILE.]
def get_ini_credentials():
    c = configparser.RawConfigParser()
    if len(c.read(os.path.join(os.path.dirname(__file__), os.pardir, 'secrets.ini'))) > 0 and c.has_section('Credentials'):
        return c['Credentials']
    return None

# returns the api_key stored in secrets.ini
def api_key():
    c = get_ini_credentials()
    return c.get(option='api_key', fallback='xxx') if c is not None else 'xxx'

# returns the api_secret stored in secrets.ini
def api_secret():
    c = get_ini_credentials()
    return c.get(option='api_secret', fallback='yyy') if c is not None else 'yyy'

# returns the bearer_token stored in secrets.ini
def bearer_token():
    c = get_ini_credentials()
    return c.get(option='bearer_token', fallback='zzz') if c is not None else 'zzz'

def get_all_secrets():
    return f'api_key:{api_key()}\napi_secret:{api_secret()}\nbearer_token:{bearer_token()}'

# print(api_key())
# print(api_secret())
# print(bearer_token())