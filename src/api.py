import tweepy

import secrets
import util

class API:
    instance = None

    def __init__(self):
        API.instance = self
        self.client = tweepy.Client(
            bearer_token=secrets.bearer_token(),
            # consumer_key=secrets.api_key(),
            # consumer_secret=secrets.api_secret(),
            # access_token=secrets.access_token(),
            # access_token_secret=secrets.access_secret()
        )
    
    def get_tweets(self, id: int, count=5):
        posts = list()

        step = util.clamp(count, 5, 100)
        retrieved_tweets = 0
        pagination_token = None

        # while retrieved_tweets < count:

        resp = self.client.get_users_tweets(id, max_results=count)
        print(resp)