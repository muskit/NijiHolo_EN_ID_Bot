from math import inf
import tweepy

import secrets
import util

class API:
    instance = None

    def __init__(self):
        API.instance = self
        self.client = tweepy.Client(
            bearer_token=secrets.bearer_token(),
            consumer_key=secrets.api_key(), consumer_secret=secrets.api_secret(),
            access_token=secrets.access_token(), access_token_secret=secrets.access_secret()
        )
    
    def get_user_tweets(self, id: int, count=inf):
        posts = list()

        retrieve_size = util.clamp(count, 5, 100)
        retrieved_tweets = 0
        pagination_token = None

        # while retrieved_tweets < count: # or we haven't reached the end of user's tweets
        resp = self.client.get_users_tweets(id, max_results=retrieve_size, media_fields=['url'], expansions=['entities.mentions.username', 'referenced_tweets.id.author_id'])
        return resp