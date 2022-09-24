from lib2to3.pgen2 import token
from math import inf
from urllib import response
import tweepy

import secrets
import util

class TwAPI:
    instance = None
    TWEET_MEDIA_FIELDS = ['url']
    TWEET_FIELDS = ['created_at', 'in_reply_to_user_id']
    TWEET_EXPANSIONS = ['entities.mentions.username', 'referenced_tweets.id.author_id']

    def __init__(self):
        TwAPI.instance = self
        self.client = tweepy.Client(
            bearer_token=secrets.bearer_token(),
            consumer_key=secrets.api_key(), consumer_secret=secrets.api_secret(),
            access_token=secrets.access_token(), access_token_secret=secrets.access_secret()
        )
    
    # Returns a set of involved parties for a single tweet.
    #
    # Tweet must have been queried with these parameters:
    # media_fields=['url'],
    # tweet_fields=['created_at', 'in_reply_to_user_id'],
    # expansions=['entities.mentions.username', 'referenced_tweets.id.author_id']
    @staticmethod
    def get_involved_parties(tweet, response):
        involved_parties = set()
        # mentions
        try:
            mention_list = tweet.entities['mentions']
            for mention in mention_list:
                involved_parties.add(int(mention['id']))
        except: pass
        # reply-to
        if tweet.in_reply_to_user_id != None:
            involved_parties.add(tweet.in_reply_to_user_id)
        # qrt
        if tweet.attachments:
            for ref_tweet in tweet.attachments:
                if ref_tweet.type == 'quoted':
                    for incl_tweet in response.includes['tweets']:
                        if incl_tweet.id == ref_tweet.id:
                            involved_parties.add(incl_tweet.author_id)

        return involved_parties
    
    # Returns a tweet and mention-set pair, given a tweet ID.
    def get_tweet_mentions(self, id):
        resp = self.client.get_tweet(id,
            media_fields=TwAPI.TWEET_MEDIA_FIELDS,
            tweet_fields=TwAPI.TWEET_FIELDS,
            expansions=TwAPI.TWEET_EXPANSIONS)
        
        tweet = resp.data
        mentions = TwAPI.get_involved_parties(tweet, resp)
        return (tweet, mentions)
    
    # Returns a list (tweet, {mentions}) from a user.
    # mentions- a set comprised of any other parties involved
    # in this tweet (reply, mention, qrt)
    def get_users_all_tweets_mentions(self, id: int, count=inf):
        pairs = list()

        retrieve_size = util.clamp(count, 5, 100)
        next_page_token = None
        tokens_retrieved = 0
        tweets_retrieved = 0

        while tweets_retrieved < count:
            print(f'Retrieved {tokens_retrieved} tokens so far...')
            resp = self.client.get_users_tweets(id, max_results=retrieve_size, pagination_token=next_page_token,
                media_fields=TwAPI.TWEET_MEDIA_FIELDS,
                tweet_fields=TwAPI.TWEET_FIELDS,
                expansions=TwAPI.TWEET_EXPANSIONS)

            for tweet in resp.data:
                mentions = TwAPI.get_involved_parties(tweet, resp)
                pairs.append((tweet, mentions))

            # update counters and pagination token
            tweets_retrieved += resp.meta['result_count']
            if tweets_retrieved < count:
                try:
                    next_page_token = resp.meta['next_token']
                    tokens_retrieved += 1
                except KeyError:
                    print("next_token wasn't provided; we've reached the end!")
                    break  # reached end of user's tweets

        print(f'Retrieved {tweets_retrieved} tweets using {tokens_retrieved} tokens.')
        return pairs
    
    # returns a filtered list (tweet, [mentions]) from a user
    def get_users_cross_tweets_mentions(self, id):
        ret = list()
        pairs = self.get_users_all_tweets_mentions(id)
        for pair in pairs:
            if util.is_cross_company(pair):
                ret.append(pair)
        
        return ret

    # Create a post that showcases given tweet and its mentions set.
    def create_post(self, tweet, mentions):
        pass