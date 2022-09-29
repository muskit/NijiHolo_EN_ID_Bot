import asyncio
import datetime
import traceback

import tweepy

import api_secrets
import talenttweet as tt
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
        try:
            self.me = self.client.get_me().data
        except Exception as e:
            print('Did you setup secrets.ini?')
            raise e
        print(f'Assuming the account of @{self.me.data["username"]} ({self.me["id"]})')
    
    ## ---[COMMENT OUT WHEN NOT IN USE]---
    async def nuke_tweets(self):
        async def delete_tweet(id):
            try:
                self.client.delete_tweet(id)
            except tweepy.TooManyRequests as e:
                wait_for = float(e.response.headers["x-rate-limit-reset"]) - datetime.datetime.now().timestamp() + 1
                print(f'\thit rate limit deleting {id}, retrying in {wait_for} seconds...')
                await asyncio.sleep(wait_for)
                print('continuing...')
                await delete_tweet(id)

        print(f'Retrieving all of {self.me["username"]}\'s tweets...')
        tweets = self.get_all_tweet_ids_from_user(self.me['id'])

        print(f'Retrieved {len(tweets)} tweets.')
        if not len(tweets) > 0:
            print('No tweets obtained. Make sure the profile is public.')
            return

        print(f'Deleting {len(tweets)} tweets...')
        deleted_count = 0
        try:
            for tweet in tweets:
                print(f'deleted {deleted_count}/{len(tweets)}')
                await delete_tweet(tweet.id)
                await asyncio.sleep(0.5)
                deleted_count += 1
        except:
            print('Unhandled error occurred while trying to delete tweets.')
            traceback.print_exc()
            print('Try running again.')
        else:
            print('Saul Gone')

    def get_all_tweet_ids_from_user(self, user_id):
        next_page_token = None
        tokens_retrieved = 0
        tweets_retrieved = 0
        tweets = list()
        while True:
            print(f'Retrieved {tokens_retrieved} tokens so far...')
            resp = self.client.get_users_tweets(
                user_id, max_results=100, pagination_token=next_page_token,
                media_fields=TwAPI.TWEET_MEDIA_FIELDS,
                tweet_fields=TwAPI.TWEET_FIELDS,
                expansions=TwAPI.TWEET_EXPANSIONS
            )

            for tweet in resp.data:
                tweets.append(tweet)

            # update counters and pagination token
            tweets_retrieved += resp.meta['result_count']
            try:
                next_page_token = resp.meta['next_token']
                tokens_retrieved += 1
            except KeyError:
                print("next_token wasn't provided; we've reached the end!")
                break  # reached end of user's tweets

        print(f'Retrieved {tweets_retrieved} tweets using {tokens_retrieved} tokens.')
        return tweets

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

    async def post_tweet(self, text='', media_ids: list=None, reply_to_tweet: int=None):
        try:
            tweet = self.client.create_tweet(text=text, media_ids=None if media_ids == None else media_ids, in_reply_to_tweet_id=reply_to_tweet)
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
    async def post_ttweet(self, ttweet: tt.TalentTweet, is_catchup=False):
        print(f'------{ttweet.tweet_id} ({util.get_username_local(ttweet.author_id)})------')

        REPLY = '{0} replied to {1}!\n'
        QUOTE_TWEET = '{0} quote tweeted {1}!\n'
        TWEET = '{0} tweeted!\n'
        RETWEET = '{0} retweeted {1}!\n'

        def create_text():
            author_username = f'@/{util.get_username_local(ttweet.author_id)}'
            mention_ids = set()
            ret = str()
            if is_catchup:
                # ret += '[catch-up tweet]\n'
                ret += f'{ttweet.get_datetime_str()}\n'
                pass

            # Tweet types
            if ttweet.rt_target is not None: # standalone tweet
                ret += RETWEET.format(author_username, f'@/{util.get_username(ttweet.rt_author_id)}')
                mention_ids.clear()
            elif ttweet.reply_to is not None: # reply (w/ qrt; push it into mentions)
                reply_username = f'@/{util.get_username_local(ttweet.reply_to)}'
                ret += REPLY.format(author_username, reply_username)
                
                mention_ids = set(ttweet.mentions)
                mention_ids.add(ttweet.quote_retweeted)
                try: mention_ids.remove(None)
                except: pass
            elif ttweet.quote_retweeted is not None: # standalone qrt
                quoted_username = f'@/{util.get_username_local(ttweet.quote_retweeted)}'
                ret += QUOTE_TWEET.format(author_username, quoted_username)
            elif len(ttweet.mentions) > 0: # standalone tweet w/ mentions
                ret += TWEET.format(author_username)
            else:
                raise ValueError(f'TalentTweet {ttweet.tweet_id} has insufficient other parties')

            # mention line
            if len(mention_ids) > 0:
                mention_usernames = [f'@/{util.get_username_local(x)}' for x in mention_ids]
                ret += (
                    'mentioning '
                    f'{" ".join(mention_usernames)}\n'
                )
            ret += f'\n{util.ttweet_to_url(ttweet)}'
            return ret
        
        text = create_text()
        try:
            # print('creating reply img')
            # media_ids = [await self.get_ttweet_image_media_id(ttweet)]
            print('posting main tweet')
            twt_resp = await self.post_tweet(text)
            twt_id = twt_resp.data['id']
            print('creating reply img')
            media_ids = [await self.get_ttweet_image_media_id(ttweet)]
            # if ttweet.reply_to is not None:
                # re_ttweet = tt.TalentTweet(tweet_id=ttweet.reply_to, author_id=)
                # media_ids.insert(0, await self.get_ttweet_image_media_id())
            print('posting reply tweet')
            await self.post_tweet(reply_to_tweet=twt_id, media_ids=media_ids,)
            print('successfully posted ttweet!')
            return True
        except tweepy.Forbidden as e:
            if 'duplicate content' in e.api_messages[0]:
                print('Twitter says the TalentTweet is a duplicate; skipping error-free...')
                return False
            else:
                raise e



        
        
