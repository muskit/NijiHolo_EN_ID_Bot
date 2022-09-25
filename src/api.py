from lib2to3.pgen2 import token
from math import inf
from urllib import response
import tweepy

import api_secrets
import talenttweet as tt
import util

class TwAPI:
    instance = None
    TWEET_MEDIA_FIELDS = ['url']
    TWEET_FIELDS = ['created_at', 'in_reply_to_user_id']
    TWEET_EXPANSIONS = ['entities.mentions.username', 'referenced_tweets.id.author_id']

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

    def __init__(self):
        TwAPI.instance = self
        self.client = tweepy.Client(
            bearer_token=api_secrets.bearer_token(),
            consumer_key=api_secrets.api_key(), consumer_secret=api_secrets.api_secret(),
            access_token=api_secrets.access_token(), access_token_secret=api_secrets.access_secret()
        )
    
    # Returns a list of TalentTweets from a user.
    def get_users_all_tweets_mentions(self, id: int, count=inf):
        ttweets = list()

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
                ttweets.append(tt.TalentTweet(tweet=tweet, other_parties=mentions))

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
        return ttweets
    
    # Returns a list of cross-company TalentTweets from a user.
    def get_users_cross_tweets_mentions(self, id):
        ret = list()
        ttweets = self.get_users_all_tweets_mentions(id)
        for ttweet in ttweets:
            if ttweet.is_cross_company():
                ret.append(ttweet)
        
        return ret

    # Create a post that showcases given tweet and its mentions set.
    def create_post(self, tweet, mentions):
        pass