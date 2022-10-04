## The bot's listen mode
# Continuously listen for cross-company interactions.

import asyncio
import traceback
import tweepy
from talenttweet import TalentTweet

from twapi import TwAPI
import ttweetqueue as ttq
import api_secrets
import talent_lists as tl

errors_encountered = 0

def on_response(resp):
    ttweet = TalentTweet.create_from_v2api_response(resp)
        
    if ttweet.is_cross_company():
        print(f'Tweet {ttweet.tweet_id} is cross-company! Creating post...')
        asyncio.run(TwAPI.instance.post_ttweet(ttweet))
        ttq.TalentTweetQueue.instance.add_finished_tweet(ttweet.tweet_id)
    else:
        print(f'Tweet {ttweet.tweet_id} is not cross-company.')

def run():
    global errors_encountered
    while True:
        try:
            sc = tweepy.StreamingClient(api_secrets.bearer_token())

            # clear rules
            rules_resp = sc.get_rules()
            if rules_resp.data:
                sc.delete_rules(rules_resp.data)

            # create new rules
            for rule in tl.get_twitter_rules():
                sc.add_rules(tweepy.StreamRule(rule))

            sc.on_response=on_response
            sc.filter(
                expansions=TwAPI.TWEET_EXPANSIONS,
                media_fields=TwAPI.TWEET_MEDIA_FIELDS,
                tweet_fields=TwAPI.TWEET_FIELDS
            )
        except KeyboardInterrupt:
            print('Interrupt signal received. Exiting listen mode.')
            print(f'{errors_encountered} errors encountered throughout session.')
            break
        except:
            errors_encountered += 1
            print('Ran into an error while in listen mode.')
            traceback.print_exc()
        else:
            print('API stream exited gracefully.')
        print('Re-running listen mode...')
        print(f'(Had {errors_encountered} errors so far.)')