import datetime
import traceback
import asyncio

import tweepy

import api_secrets
import talenttweet as tt
import talent_lists as tl
import ttweetqueue as ttq
import util

class TwAPI:
    tweets_fetched = 0
    instance = None
    TWEET_MEDIA_FIELDS = ['url']
    TWEET_FIELDS = ['created_at', 'in_reply_to_user_id', 'referenced_tweets']
    TWEET_EXPANSIONS = ['entities.mentions.username', 'referenced_tweets.id.author_id']
    
    # Returns a tuple of user IDs:(reply_to, qrt, {mentions})
    # for a single tweet.
    #
    # Tweet must have been queried with these parameters:
    # media_fields=['url'],
    # tweet_fields=['created_at', 'in_reply_to_user_id'],
    # expansions=['entities.mentions.username', 'referenced_tweets.id.author_id']
    #
    # VALUES IN TUPLE ARE NONE OR INT.
    @staticmethod
    def get_mrq(response):
        tweet = response.data

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
        except: pass
        try:
            mentions.remove(qrt)
        except: pass

        mention_list = list(mentions)
        for uid in mention_list:
            if uid not in tl.talents.keys():
                mentions.remove(uid)
        if reply_to not in tl.talents.keys():
            reply_to = None
        
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
        try:
            self.me = self.client.get_me().data
        except Exception as e:
            print('Did you setup secrets.ini?')
            raise e
        print(f'Assuming the account of @{self.me.data["username"]} ({self.me["id"]})')
    
    ## ---[COMMENT OUT WHEN NOT IN USE]---
    # async def nuke_tweets(self):
    #     async def delete_tweet(id):
    #         try:
    #             self.client.delete_tweet(id)
    #         except tweepy.TooManyRequests as e:
    #             wait_for = float(e.response.headers["x-rate-limit-reset"]) - datetime.datetime.now().timestamp() + 1
    #             print(f'\thit rate limit deleting {id}, retrying in {wait_for} seconds...')
    #             await asyncio.sleep(wait_for)
    #             print('continuing...')
    #             await delete_tweet(id)

    #     print(f'Retrieving all of {self.me["username"]}\'s tweets...')
    #     tweets = self.get_all_tweet_ids_from_user(self.me['id'])

    #     print(f'Retrieved {len(tweets)} tweets.')
    #     if not len(tweets) > 0:
    #         print('No tweets obtained. Make sure the profile is public.')
    #         return

    #     print(f'Deleting {len(tweets)} tweets...')
    #     deleted_count = 0
    #     try:
    #         for tweet in tweets:
    #             print(f'deleted {deleted_count}/{len(tweets)}')
    #             await delete_tweet(tweet.id)
    #             await asyncio.sleep(0.5)
    #             deleted_count += 1
    #     except:
    #         print('Unhandled error occurred while trying to delete tweets.')
    #         traceback.print_exc()
    #         print('Try running again.')
    #     else:
    #         print('Saul Gone')

    async def post_tweet(self, text='', media_ids: list=None, reply_to_tweet: int=None, quote_tweet_id: int=None):
        try:
            tweet = self.client.create_tweet(text=text, media_ids=media_ids, in_reply_to_tweet_id=reply_to_tweet, quote_tweet_id=quote_tweet_id)
            return tweet
        except tweepy.TooManyRequests as e:
            wait_for = float(e.response.headers["x-rate-limit-reset"]) - datetime.datetime.now().timestamp() + 1
            print(f'\thit rate limit -- attempting to create Tweet again in {wait_for} seconds...')
            await asyncio.sleep(wait_for)
            return await self.post_tweet(text=text, media_ids=media_ids, reply_to_tweet=reply_to_tweet)

    async def get_ttweet_image_media_id(self, ttweet):
        img = await util.create_ttweet_image(ttweet)
        media = self.api.media_upload(img)
        return media.media_id

    # return True = successfully posted a single ttweet
    # return False = did not post ttweet (duplicate)
    async def post_ttweet(self, ttweet: tt.TalentTweet, is_catchup=False, dry_run=False):
        print(f'------{ttweet.tweet_id} ({util.get_username_local(ttweet.author_id)})------')
        
        text = ttweet.announce_text()
        ttweet_url = ttweet.url()
        
        if dry_run: print('-------------------- DRY RUN --------------------')
        print(ttweet)
        if dry_run: return False

        # NO DRY-RUN: actually post tweet
        # main tweet: text + screenshot
        try:
            print('creating main QRT w/ screenshot...', end='')
            media_ids = [await self.get_ttweet_image_media_id(ttweet)]
            twt_resp = await self.post_tweet(text, media_ids=media_ids, quote_tweet_id=ttweet.tweet_id)
            print('done')
        except:
            print('error occurred trying to create main tweet, falling back to URL-main + reply screencap format')
            traceback.print_exc()
            text += f"\n{ttweet_url}"
            try:
                print('posting main tweet...', end='')
                twt_resp = await self.post_tweet(text)
                print('done')
                twt_id = twt_resp.data['id']
                # if ttweet.reply_to is not None:
                    # re_ttweet = tt.TalentTweet(tweet_id=ttweet.reply_to, author_id=)
                    # media_ids.insert(0, await self.get_ttweet_image_media_id())

                try:
                    print('creating reply img...', end='')
                    media_ids = [await self.get_ttweet_image_media_id(ttweet)]
                    print('posting reply tweet...', end='')
                    await self.post_tweet(reply_to_tweet=twt_id, media_ids=media_ids)
                    print('done')
                except:
                    print('Had trouble posting reply image tweet.')
                print('successfully posted ttweet!')
            except tweepy.Forbidden as e:
                if 'duplicate content' in e.api_messages[0]:
                    print('Twitter says the TalentTweet is a duplicate; skipping error-free...')
                    return False
                else:
                    raise e
        return True
