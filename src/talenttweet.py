from datetime import datetime
from zoneinfo import ZoneInfo
import platform

import pytz
from tweety.types import *

# from talent_lists import is_cross_company, talents
import talent_lists as tl
import util

class TalentTweet:
    # Serialized one-liner format:
    # {tweet} {author} {time in seconds since epoch UTC} m {mention set} r {reply to author} q {quote tweet author} rt {retweeted user's id} rtm {mentions in retweet}
    def serialize(self):
        s = f'{self.tweet_id} {self.author_id} {int(self.date_time.timestamp())} '
        if self.date_time.tzinfo is None:
            print(f'warning: serialized tweet {self.tweet_id} has a NAIVE timestamp!')

        if len(self.rt_mentions) > 0:
            s += 'rtm '
            for n in self.rt_mentions:
                s += f'{n} '

        if self.rt_author_id != None:
            s += f'rt {self.rt_author_id} '
            return s[:-1] # stop here since retweets can't have other info
        
        if len(self.mentions) > 0:
            s += 'm '
            for id in self.mentions:
                s += f'{id} '
        if self.reply_to:
            s += f'r {self.reply_to} '
        if self.quote_tweeted:
            s += f'q {self.quote_tweeted} '
            
        return s[:-1]

    @staticmethod
    def deserialize(serialized_str: str):
        token_check = serialized_str.split('#')[0]
        if len(token_check) < 3:
            raise ValueError('not enough tokens to reconstruct a TalentTweet')
        
        tokens = serialized_str.split()
        
        tweet_id, author_id = int(tokens[0]), int(tokens[1])
        date_time = datetime.fromtimestamp(float(tokens[2]), tz=pytz.utc)
        
        mentions = list()
        reply_to = None
        quote_retweeted = None
        rt = None
        rtm = list()

        mode = ''
        for i in range(3, len(tokens)):
            if len(tokens[i]) == 1 and not tokens[i].isnumeric(): # mode switch
                mode = tokens[i]
                continue
        
            if tokens[i].isnumeric():
                if mode == 'm': # mentions
                    mentions.append(int(tokens[i]))
                    continue
                if mode == 'r': # reply_to
                    reply_to = int(tokens[i])
                    continue
                if mode == 'q': # quote_retweeted
                    quote_retweeted = int(tokens[i])
                if mode == 'rt': # retweeted user
                    rt = int(tokens[i])
                if mode == 'rtm': # retweet/qrt mentions
                    rtm.append(int(tokens[i]))
        
        return TalentTweet(
            tweet_id=tweet_id, author_id=author_id,
            date_time=date_time, mrq=(mentions, reply_to, quote_retweeted),
            rt_author_id=rt, rt_mentions=rtm
        )
    
    ## Creates a TalentTweet from a Tweety-library Tweet.
    @staticmethod
    def create_from_tweety(tweety: Tweet):
        if tweety.is_retweet:
            rtm = [int(x.id) for x in tweety.retweeted_tweet.user_mentions]
        elif tweety.is_quoted:
            rtm = [int(x.id) for x in tweety.quoted_tweet.user_mentions]
        else:
            rtm = list()

        return TalentTweet(
            tweet_id=int(tweety.id), author_id=int(tweety.author.id),
            date_time=tweety.date, text=tweety.text,
            mrq=(
                [int(x.id) for x in tweety.user_mentions],
                int(tweety.original_tweet['in_reply_to_user_id_str']) if tweety.is_reply else None,
                int(tweety.quoted_tweet.author.id) if tweety.quoted_tweet is not None else None
            ),
            rt_author_id=tweety.retweeted_tweet.author.id if tweety.is_retweet else None,
            rt_mentions=rtm
        )

    def __init__(self, tweet_id: int, author_id: int, date_time: datetime, text: str = None, mrq: tuple[list[int], int|None, int|None]=None, rt_author_id: int=None, rt_mentions: list[int]=None):
        # basic information
        self.tweet_id, self.author_id = tweet_id, author_id
        self.username = util.get_username_local(self.author_id)
        self.date_time = date_time
        self.text = text

        # filter users to only be talents
        self.mentions = {x for x in mrq[0] if x in tl.talents}
        self.rt_mentions = {x for x in rt_mentions if x in tl.talents}

        self.reply_to = mrq[1]
        self.quote_tweeted = mrq[2]
        self.rt_author_id = rt_author_id

        try: self.mentions.remove(self.reply_to)
        except: pass

        # -1 if user is not in company
        self.reply_to = self.reply_to if self.reply_to is None or self.reply_to in tl.talents else -1
        self.quote_tweeted = self.quote_tweeted if self.quote_tweeted is None or self.quote_tweeted in tl.talents else -1
        self.rt_author_id = self.rt_author_id if self.rt_author_id is None or self.rt_author_id in tl.talents else -1

        # all users involved except for the author
        self.all_parties = {self.reply_to, self.quote_tweeted, rt_author_id}
        self.all_parties.update(self.mentions, self.rt_mentions)
        try: self.all_parties.remove(None)
        except: pass
        try: self.all_parties.remove(self.author_id)
        except: pass
    

    def __repr__(self) -> str:
        return (
            f'======================================================\n'
            f'{self.tweet_id} from {self.username}:\n'
            f'{self.get_datetime_str()}\n'
            f'parties: {self.get_all_parties_usernames()}\n'
            f'mentions: {self.mentions}\n'
            f'reply_to: {self.reply_to}\n'
            f'quote_retweeted: {self.quote_tweeted}\n'
            f'cross-company? {self.is_cross_company()}\n'
            f'{self.serialize()}\n'
            f'----\n{self.announce_text()}\n----\n'
            f'{self.url()}'
        )

    def url(self):
        return util.get_tweet_url(self.tweet_id, self.username)

    def is_cross_company(self):
        for other_id in self.all_parties:
            if tl.is_cross_company(self.author_id, other_id):
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

    def announce_text(self):
        # templates
        TWEET = '{0} tweeted mentioning {1}!'
        REPLY = '{0} replied to {1}!'
        REPLY_TO_MENTION_B = '{0} replied to a tweet{1}mentioning {1}!' #########################
        RETWEET = '{0} retweeted {1}!'
        RETWEET_MENTIONS_B = '{0} shared a tweet{1}mentioning {2}!' #########################
        QUOTE_TWEET = '{0} quote tweeted {1}!'
        QUOTED_TWEET_MENTIONS_B = '{0} quoted a tweet{1}mentioning {2}!' #########################

        author_username = f'@/{util.get_username_with_company(self.author_id)}'
        ret = str()

        print_mention_ids = set(self.mentions)
        try: print_mention_ids.remove(None)
        except: pass
        mention_usernames = [f'@/{util.get_username_with_company(x)}' for x in print_mention_ids]

        def rtm_msg(TEMPLATE: str, rtm_author_username: str):
            if self.rt_author_id != -1: # rtm tweet is not from talent; rtm should be everyone
                rtm_names = [f'@/{util.get_username_with_company(x)}' for x in self.rt_mentions]
                between = f' from {rtm_author_username} '
                ret += TEMPLATE.format(author_username, between, ", ".join(rtm_names))
            else: # rtm tweet is from a talent; rtm should just be cross company
                rtm_names = [f'@/{util.get_username_with_company(x)}' for x in self.rt_mentions if tl.is_cross_company(self.author_id, x)]
                ret += TEMPLATE.format(author_username, ' ', ", ".join(rtm_names))

        # Tweet types
        if self.rt_author_id is not None: # retweet
            rt_username = f'@/{util.get_username_with_company(self.rt_author_id)}' if self.rt_author_id != -1 else None
            if len(self.rt_mentions) > 0:
                rtm_msg(RETWEET_MENTIONS_B, rt_username)
            else:
                ret += RETWEET.format(author_username, rt_username)
        elif self.reply_to is not None: # reply
            reply_username = f'@/{util.get_username_with_company(self.reply_to)}' if self.reply_to != -1 else None
            if len(self.rt_mentions) > 0:
                rtm_msg(REPLY_TO_MENTION_B, reply_username)
            else:
                ret += REPLY.format(author_username, reply_username)
        elif self.quote_tweeted is not None: # qrt
            quoted_username = f'@/{util.get_username_with_company(self.quote_tweeted)}' if self.quote_tweeted != -1 else None
            if len(self.rt_mentions) > 0:
                rtm_msg(QUOTED_TWEET_MENTIONS_B, quoted_username)
            else:
                ret += QUOTE_TWEET.format(author_username, quoted_username)
        elif len(self.mentions) > 0: # standalone tweet
            ret += TWEET.format(author_username, ", ".join(mention_usernames))
            f'[{self.get_datetime_str()}]\n'
            return ret
        else:
            raise ValueError(f'TalentTweet {self.tweet_id} has insufficient other parties')

        # mention line
        if len(print_mention_ids) > 0:
            ret += (
                '\nMentioning '
                f'{", ".join(mention_usernames)}'
            )
        
        ret += f'\n\n{self.get_datetime_str()}'
        return ret
