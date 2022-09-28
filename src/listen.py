## The bot's listen mode
# Continuously listen for cross-company interactions.

import asyncio
import tweepy
from talenttweet import TalentTweet

from twapi import TwAPI
import api_secrets
import talent_lists as tl

def on_response(resp):
    print(resp)
    print(resp.data)
    ttweet = TalentTweet.create_from_v2api_response(resp)
    asyncio.run(TwAPI.instance.post_ttweet(ttweet))

def run():
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