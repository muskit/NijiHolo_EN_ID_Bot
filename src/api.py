import asyncio
from math import inf

import tweepy
from tweetcapture import TweetCapture

import api_secrets
import talenttweet as tt
import util

class TwAPI:
    instance = None
    TWEET_MEDIA_FIELDS = ['url']
    TWEET_FIELDS = ['created_at', 'in_reply_to_user_id']
    TWEET_EXPANSIONS = ['entities.mentions.username', 'referenced_tweets.id.author_id']
    
    # Returns a tuple of user IDs:(reply_to, qrt, {mentions})
    # for a single tweet.
    #
    # Tweet must have been queried with these parameters:
    # media_fields=['url'],
    # tweet_fields=['created_at', 'in_reply_to_user_id'],
    # expansions=['entities.mentions.username', 'referenced_tweets.id.author_id']
    @staticmethod
    def get_mrq(tweet: tweepy.Tweet, response):
        mentions = set()
        reply_to = None
        qrt = None

        # mentions
        try:
            mention_list = tweet.entities['mentions']
            for mention in mention_list:
                mentions.add(int(mention['id']))
        except:
            pass
        # reply-to
        if tweet.in_reply_to_user_id != None:
            reply_to = tweet.in_reply_to_user_id
        # qrt
        if tweet.referenced_tweets:
            for ref_tweet in tweet.referenced_tweets:
                if ref_tweet.type == 'quoted':
                    for incl_tweet in response.includes['tweets']:
                        if incl_tweet.id == ref_tweet.id:
                            qrt = incl_tweet.author_id

        try:
            mentions.remove(reply_to)
            mentions.remove(qrt)
        except: pass
        
        return (mentions, reply_to, qrt)


    def __init__(self):
        TwAPI.instance = self
        self.client = tweepy.Client(
            bearer_token=api_secrets.bearer_token(),
            consumer_key=api_secrets.api_key(), consumer_secret=api_secrets.api_secret(),
            access_token=api_secrets.access_token(), access_token_secret=api_secrets.access_secret()
        )
    
    def get_tweet_response(self, id):
        return TwAPI.instance.client.get_tweet(
            id,
            media_fields=TwAPI.TWEET_MEDIA_FIELDS,
            tweet_fields=TwAPI.TWEET_FIELDS,
            expansions=TwAPI.TWEET_EXPANSIONS
        )

    # Create a post that showcases given tweet and its mentions set.
    # Try do do this without retireving Tweet data.
    async def create_post(self, ttweet):
        img = await util.create_ttweet_image(ttweet)


        
        