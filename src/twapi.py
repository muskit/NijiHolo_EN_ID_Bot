import asyncio
import datetime

import tweepy
from tweetcapture import TweetCapture

import api_secrets
import talenttweet as tt
import util

class TwAPI:
    tweets_fetched = 0
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
        self.api = tweepy.API(
            auth=tweepy.OAuthHandler(
                consumer_key=api_secrets.api_key(), consumer_secret=api_secrets.api_secret(),
                access_token=api_secrets.access_token(), access_token_secret=api_secrets.access_secret()
            )
        )
    
    async def get_tweet_response(self, id, attempt = 0):
        try:
            twt = TwAPI.instance.client.get_tweet(
                id,
                media_fields=TwAPI.TWEET_MEDIA_FIELDS,
                tweet_fields=TwAPI.TWEET_FIELDS,
                expansions=TwAPI.TWEET_EXPANSIONS
            )
            TwAPI.tweets_fetched += 1
            return twt
        except tweepy.TooManyRequests as e:
            wait_for = float(e.response.headers["x-rate-limit-reset"]) - datetime.datetime.now().timestamp() + 1
            print(f'[{attempt}]\tget_tweet_response({id}):\n\thit rate limit after {TwAPI.tweets_fetched} fetches -- trying again in {wait_for} seconds...')
            await asyncio.sleep(wait_for)
            return await self.get_tweet_response(id, attempt=attempt+1)

    async def post_tweet(self, text, media_id=None, reply_to_tweet: int=None):
        try:
            tweet = self.client.create_tweet(text=text, media_ids=None if media_id == None else [media_id], in_reply_to_tweet_id=reply_to_tweet)
            return tweet
        except tweepy.TooManyRequests as e:
            wait_for = float(e.response.headers["x-rate-limit-reset"]) - datetime.datetime.now().timestamp() + 1
            print(f'\thit rate limit -- attempting to create Tweet again in {wait_for} seconds...')
            await asyncio.sleep(wait_for)
            return await self.post_tweet(text=text, media_ids=[media_id])

    async def get_ttweet_image_media_id(self, ttweet):
        img = await util.create_ttweet_image(ttweet)
        media = self.api.media_upload(img)
        return media.media_id

    async def post_ttweet(self, ttweet: tt.TalentTweet):
        REPLY = '{0} replied to {1}!\n'
        MENTION = '{0} mentioned {1}!\n'
        QUOTE_TWEET = '{0} quote tweeted {1}!\n'

        def create_text():
            if ttweet.reply_to is not None:
                author_username = f'@/{util.get_username_online(ttweet.author_id)}'
                reply_username = f'@/{util.get_username_online(ttweet.reply_to)}'
                mention_ids = set(ttweet.mentions)
                mention_ids.add(ttweet.quote_retweeted)
                try: mention_ids.remove(None)
                except: pass
                mention_usernames = [f'@/{util.get_username_online(x)}' for x in mention_ids]
                
                ret = REPLY.format(author_username, reply_username)
                ret += (
                    'mentions '
                    f'{" ".join(mention_usernames)}'
                    f'\n{util.ttweet_to_url(ttweet)}'
                )
                return ret
        
        img_media_id_task = asyncio.create_task(self.get_ttweet_image_media_id(ttweet))
        text = create_text()
        media_id = await img_media_id_task
        twt_resp = await self.post_tweet(text)
        twt_id = twt_resp.data['id']
        await self.post_tweet(text='Image backup', reply_to_tweet=twt_id, media_id=media_id,)



        
        