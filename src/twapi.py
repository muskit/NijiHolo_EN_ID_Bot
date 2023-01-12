import datetime
import traceback
import asyncio

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

    async def post_tweet(self, text='', media_ids: list=None, reply_to_tweet: int=None, quote_tweet_id: int=None):
        try:
            tweet = self.client.create_tweet(text=text, media_ids=media_ids, in_reply_to_tweet_id=reply_to_tweet, quote_tweet_id=str(quote_tweet_id))
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

        REPLY = '{0} replied to {1}\n'
        QUOTE_TWEET = '{0} quote tweeted {1}\n'
        TWEET = '{0} tweeted\n'
        RETWEET = '{0} retweeted {1}\n'

        def create_text():
            author_username = f'@/{util.get_username_local(ttweet.author_id)}'
            print_mention_ids = set(ttweet.mentions)
            ret = str()
            if is_catchup:
                ret += f'{ttweet.get_datetime_str()}\n'
                pass
            
            # Tweet types
            if ttweet.rt_target is not None: # retweet
                ret += RETWEET.format(author_username, f'@/{util.get_username(ttweet.rt_author_id)}')
            elif ttweet.reply_to is not None: # reply
                reply_username = f'@/{util.get_username(ttweet.reply_to)}'
                ret += REPLY.format(author_username, reply_username)
                # if qrt, push id into mentions
                print_mention_ids.add(ttweet.quote_retweeted)
            elif ttweet.quote_retweeted is not None: # qrt
                quoted_username = f'@/{util.get_username(ttweet.quote_retweeted)}'
                ret += QUOTE_TWEET.format(author_username, quoted_username)
            elif len(ttweet.mentions) > 0: # standalone tweet
                ret += TWEET.format(author_username)
            else:
                raise ValueError(f'TalentTweet {ttweet.tweet_id} has insufficient other parties')

            try: print_mention_ids.remove(None)
            except: pass

            # mention line
            if len(print_mention_ids) > 0:
                mention_usernames = [f'@/{util.get_username(x)}' for x in print_mention_ids]
                ret += (
                    'mentioning '
                    f'{" ".join(mention_usernames)}\n'
                )
            ret += '\n'
            ret += '(this is a missed tweet)\n' if is_catchup else ''
            return ret
        
        text = create_text()
        ttweet_url = util.ttweet_to_url(ttweet)
        
        if dry_run: # DRY-RUN: only print tweet
            print(text)
            print(f'QRT: {ttweet_url}')
        else: # NO DRY-RUN: post actual tweet
            # main tweet: text + screenshot
            try:
                print('creating main QRT w/ screenshot...', end='')
                media_ids = [await self.get_ttweet_image_media_id(ttweet)]
                twt_resp = await self.post_tweet(text, media_ids=media_ids, quote_tweet_id=ttweet.tweet_id)
                print('done')
                # twt_id = twt_resp.data['id']
                # try:
                #     print('posting reply tweet...', end='')
                #     await self.post_tweet(text=ttweet_url, reply_to_tweet=twt_id)
                #     print('done')
                # except:
                #     print('Had trouble posting reply tweet.')
            except:
                print('error occurred trying to create main tweet, falling back to URL-main + reply format')
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
                        await self.post_tweet(reply_to_tweet=twt_id, media_ids=media_ids,)
                        print('done')
                    except:
                        print('Had trouble posting reply image tweet.')
                    print('successfully posted ttweet!')
                    return True
                except tweepy.Forbidden as e:
                    if 'duplicate content' in e.api_messages[0]:
                        print('Twitter says the TalentTweet is a duplicate; skipping error-free...')
                        return False
                    else:
                        raise e



        
        
