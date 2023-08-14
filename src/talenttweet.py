import datetime
from zoneinfo import ZoneInfo
import platform

import pytz

import twapi
import talent_lists
import util

class TalentTweet:
    @staticmethod
    def deserialize(serialized_str: str):
        tokens = serialized_str.split()
        if len(tokens) < 3:
            raise ValueError('not enough tokens to reconstruct a TalentTweet')
        
        tweet_id, author_id = int(tokens[0]), int(tokens[1])
        date_time = datetime.datetime.fromtimestamp(float(tokens[2]), tz=pytz.utc)
        
        mentions = set()
        reply_to = None
        quote_retweeted = None

        mode = ''
        for i in range(3, len(tokens)):
            if len(tokens[i]) == 1 and not tokens[i].isnumeric(): # mode switch
                mode = tokens[i]
                continue
        
            if tokens[i].isnumeric():
                if mode == 'm': # mentions
                    mentions.add(int(tokens[i]))
                    continue
                if mode == 'r': # reply_to
                    reply_to = int(tokens[i])
                    continue
                if mode == 'q': # quote_retweeted
                    quote_retweeted = int(tokens[i])
        
        return TalentTweet(
            tweet_id=tweet_id, author_id=author_id,
            date_time=date_time, mrq=(mentions, reply_to, quote_retweeted)
        )

    # Serialized one-liner format:
    # {tweet} {author} {time in seconds since epoch} m {mention_set} r {reply_to_author} q {quote_retweet_author}
    def serialize(self):
        s = f'{self.tweet_id} {self.author_id} {self.date_time.timestamp()} '

        if None not in [self.rt_target, self.rt_author_id]:
            s += f'rt {self.rt_target} {self.rt_author_id}'
            return s[:-1] # stop here since retweets can't have other info
        
        if len(self.mentions) > 0:
            s += 'm '
            for id in self.mentions:
                s += f'{id} '
        if self.reply_to:
            s += f'r {self.reply_to} '
        if self.quote_retweeted:
            s += f'q {self.quote_retweeted} '
            
        return s[:-1]

    def __init__(self, tweet_id: int, author_id: int, date_time: datetime.datetime, mrq: tuple, rt_target: int=None, rt_author_id: int=None):
        self.tweet_id, self.author_id = tweet_id, author_id
        self.date_time = date_time
        self.mentions = tuple(int(x) for x in mrq[0])
        self.reply_to = int(mrq[1]) if mrq[1] is not None else None
        self.quote_retweeted = int(mrq[2]) if mrq[2] is not None else None
        self.rt_target, self.rt_author_id = rt_target, rt_author_id

        # all users involved, except for the author
        self.all_parties = {self.reply_to, self.quote_retweeted}
        self.all_parties.update(self.mentions)
        try:
            self.all_parties.remove(None)
        except: pass
        try:
            self.all_parties.remove(self.author_id)
        except: pass
    

    def __repr__(self) -> str:
        return (
            f'{self.tweet_id} from {util.get_username_local(self.author_id)}):\n'
            f'{self.get_datetime_str()}\n'
            f'{self.get_all_parties_usernames()}\n'
            f'mentions: {self.mentions}\n'
            f'reply_to: {self.reply_to}\n'
            f'quote_retweeted: {self.quote_retweeted}\n'
            f'Cross-company: {self.is_cross_company()}\n'
            f'{self.serialize()}\n'
            f'======================================================'
        )

    def is_cross_company(self):
        for other_id in self.all_parties:
            if self.author_id in talent_lists.holo_en:
                if other_id in talent_lists.niji_en or other_id in talent_lists.niji_exid:
                    return True
            if self.author_id in talent_lists.niji_en:
                if other_id in talent_lists.holo_en or other_id in talent_lists.holo_id:
                    return True
            if self.author_id in talent_lists.holo_id:
                if other_id in talent_lists.niji_en or other_id in talent_lists.niji_exid:
                    return True
            if self.author_id in talent_lists.niji_exid:
                if other_id in talent_lists.holo_en or other_id in talent_lists.holo_id:
                    return True
        return False
    
    def get_all_parties_usernames(self):
        if len(self.all_parties) > 0:
            s = str()
            for id in self.all_parties:
                s += f'{util.get_username_local(id)}, '
            return s[0:-2]

        return 'none'

    def get_datetime_str(self):
        unpad = '#' if platform.system() == 'Windows' else '-'
        return self.date_time.strftime(f'%b %{unpad}d %Y, %{unpad}I:%M%p (%Z)')
