import platform

import tweepy

from api import *
import talent_lists

class TalentTweet:
    def __init__(self, tweet: tweepy.Tweet, other_parties: set):
        self.tweet = tweet
        self.other_parties = other_parties
    
    def __init__(self, tweet_id):
        resp = TwAPI.instance.client.get_tweet(tweet_id,
            media_fields=TwAPI.TWEET_MEDIA_FIELDS,
            tweet_fields=TwAPI.TWEET_FIELDS,
            expansions=TwAPI.TWEET_EXPANSIONS)
        
        self.tweet = resp.data
        self.other_parties = TwAPI.get_involved_parties(self.tweet, resp)

    def __repr__(self) -> str:
        return (
            f'{self.tweet.id} from {talent_lists.talents.get(self.tweet.author_id, "???")}:\n'
            f'{self.tweet.text}\n'
            f'------------------------------------------------------\n'
            f'{self.get_datetime_str()}\n'
            f'{self.get_mentions_usernames()}\n'
            f'Cross-company: {self.is_cross_company()}\n'
            f'======================================================'
        )
    
    def is_cross_company(self):
        author_id = self.tweet.author_id
        mentions = self.other_parties

        # TODO: update for EN/ID
        for mention_id in mentions:
            if author_id in talent_lists.niji_en:
                if mention_id in talent_lists.holo_en:
                    return True
            elif author_id in talent_lists.holo_en:
                if mention_id in talent_lists.niji_en:
                    return True
        return False
    
    def get_mentions_usernames(self):
        if len(self.other_parties) > 0:
            s = str()
            for id in self.other_parties:
                s += f'{talent_lists.talents.get(id, "???")}, '
            return s[0:-2]

        return 'none'

    def get_datetime_str(self):
        unpad = '#' if platform.system() == 'Windows' else '-'
        return self.tweet.created_at.strftime(f'%b %{unpad}d %Y, %{unpad}I:%M%p (%Z)')


class TalentTweets:
    def __init__(self):
        self.ttweets = list()

    def get_ttweets(self):
        pass

    def get_ttweet_ids(self):
        pass