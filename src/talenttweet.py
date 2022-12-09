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
    
    @staticmethod
    async def create_from_twint_tweet(tweet):
        # MRQ
        mentions = set()
        reply_to = None
        quoted_id = None
            
        # reply_to/mentions
        is_reply = tweet.id != int(tweet.conversation_id)
        mentions = set([x['id'] for x in tweet.mentions])
        if is_reply and len(tweet.reply_to) > 0:
            reply_to = tweet.reply_to[0]['id'] # FIXME: QRT = is_reply and len(tweet.reply_to) == 0?
            reply_others = [x['id'] for x in tweet.reply_to[1:]]
            mentions.update(reply_others)
            try: mentions.remove(reply_to)
            except: pass

        # qrt
        if type(tweet.quote_url) == str:
            # print(f'url: {tweet.quote_url} ({type(tweet.quote_url)})')
            quote_tokens = tweet.quote_url.split('/')
            if len(quote_tokens) >= 2:
                quoted_username = quote_tokens[-2]
                quoted_id = util.get_user_id_local(quoted_username)
                if quoted_id == -1:
                    quoted_id = util.get_user_id_online(quoted_username)

        # NOTE: strptime doesn't attach timezone info.
        # tweet's datetime will be in local time
        date_time = datetime.datetime.strptime(tweet.datetime, '%Y-%m-%d %H:%M:%S %Z')
        LOCAL_TIMEZONE = datetime.datetime.now().astimezone().tzinfo
        date_time = date_time.replace(tzinfo=LOCAL_TIMEZONE) # attach system local timezone
        return TalentTweet(tweet_id=tweet.id, author_id=tweet.user_id, date_time=date_time, mrq=(mentions, reply_to, quoted_id))

    @staticmethod
    def create_from_v2api_response(resp):
        tweet = resp.data
        mrq = twapi.TwAPI.get_mrq(tweet, resp)
        rt_target = None
        rt_author_id = None

        # check if is RT
        if tweet.referenced_tweets is not None and len(tweet.referenced_tweets) > 0:
            for ref in tweet.referenced_tweets:
                if ref.type == 'retweeted':
                    rt_target = ref.id
                    for incl_tweet in resp.includes['tweets']:
                        if incl_tweet.id == ref.id:
                            rt_author_id = incl_tweet.author_id

        return TalentTweet(
            tweet_id=tweet.id,
            author_id=tweet.author_id,
            date_time=tweet.created_at,
            mrq=mrq,
            rt_target=rt_target,
            rt_author_id=rt_author_id
        )

    @staticmethod
    async def create_from_id(id):
        resp = await twapi.TwAPI.instance.get_tweet_response(id)
        return TalentTweet.create_from_v2api_response(resp)

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
    
    # Serialized one-liner format:
    # {tweet} {author} {time in seconds since epoch} m {mention_set} r {reply_to_author} q {quote_retweet_author}
    def serialize(self):
        s = f'{self.tweet_id} {self.author_id} {self.date_time.timestamp()} '
        if len(self.mentions) > 0:
            s += 'm '
            for id in self.mentions:
                s += f'{id} '
        if self.reply_to:
            s += f'r {self.reply_to} '
        if self.quote_retweeted:
            s += f'q {self.quote_retweeted} '
        return s[:-1]

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