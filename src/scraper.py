from os.path import exists
from time import sleep
from datetime import datetime, timedelta
import traceback

import pytz

from tweety import Twitter
from tweety.types import *
from tweety.exceptions_ import *
from tweety.filters import SearchFilters

from account_pool import AccountPool
from tweety_utils import *
from talenttweet import *
import talent_lists

# TODO: on RateLimit encounter, determine when it will probably
# unlock and wait just until then
class Scraper:
    COOLDOWN = 16 # minutes
    def __init__(self):
        Scraper.instance = self
        self.__account = AccountPool()
        self.try_login(0)

    def try_login(self, account_idx: int = None) -> bool:
        # decide on which account to use
        if account_idx is not None:
            acc = self.__account.use_index(account_idx)
        else:
            acc = self.__account.next()

        # attempt to login with the account
        if acc is not None:
            name = acc[0]
            print(f"using {name}")
            self.app = Twitter(name)
            if exists(f"{name}.json"):
                try:
                    self.app.connect()
                except:
                    self.app.sign_in(*acc)
            else:
                self.app.sign_in(*acc)
            return True
        print("exhausted all accounts!")
        return False

    def login_wait(self, private=False):
        if private:
            print(
                f"keeping pvt-accessible account ({self.__account.use_index(0)[0]}). sleeping for {Scraper.COOLDOWN} minutes..."
            )
            sleep(60*Scraper.COOLDOWN)
            print()
            l = self.try_login(0)
        else:
            l = self.try_login()
        if not l:
            print(f"sleeping for {Scraper.COOLDOWN} minutes...")
            sleep(60*Scraper.COOLDOWN)
            print()
            self.try_login()

    # recover lost info
    def fix_tweet(self, tweet: Tweet):
        if tweet.is_retweet:
            if tweet.retweeted_tweet is None:
                # tweet.retweeted_tweet = self.app.tweet_detail(str(tweet.id)).retweeted_tweet
                # print(f'{tweet.author.username}/{tweet.id} is missing the RT! It\'s probably nothing...')
                tweet.is_retweet = False
            elif tweet.retweeted_tweet.author is None:
                # print(f'{tweet.author.username}/{tweet.id} is missing the RT author! Fetching RT\'d...')
                tweet.retweeted_tweet = self.get_tweet(tweet.retweeted_tweet.id)

        if tweet.is_quoted:
            if tweet.quoted_tweet is None:  # quoted tweet is deleted
                tweet.is_quoted = False
            elif tweet.quoted_tweet.author is None:
                # print(f'{tweet.author.username}/{tweet.id} is missing the QRT author! Fetching QRT\'d...')
                tweet.quoted_tweet = self.get_tweet(tweet.quoted_tweet.id)

        if tweet.is_reply and tweet.replied_to is None:
            # print(f'{tweet.author.username}/{tweet.id} is missing reply-to tweet! Recovering...')
            tweet.replied_to = self.get_tweet(
                tweet._original_tweet["in_reply_to_status_id_str"]
            )
        return tweet

    def get_tweet(self, id: int, private_user=False):
        # print(f'getting {id}{" on private" if private_user else ""}')
        if private_user:
            self.try_login(0)
        while True:
            try:
                t = self.app.tweet_detail(str(id))
                return self.fix_tweet(t) if t is not None else None
            except RateLimitReached:
                print("RateLimitReached occurred")
                self.login_wait(private_user)
            except UnknownError as e:
                print(f"UnknownError occurred: {e.message.rstrip()}")
                print(f"skipping attempt to get tweet {id}...")
                return None
                # if any(x in e.message.lower() for x in ["missing", "post is unavailable", "delete"]) :  # tweet is probably unavailable
                #     print(f"tweet {id} seems unavailable; skipping...")
                #     return None
                # if "account owner limits" in e.message.lower(): # private tweet
                #     print("trying again as pvt-accessible...\n")
                #     return self.get_tweet(id, True)
                # print("treating like RateLimitReached and using the next scraper...")
                # traceback.print_exc()
                # self.login_wait(private_user)
            except Exception as e:
                # if not private_user:
                #     print("Unhandled exception occurred getting tweet!")
                #     traceback.print_exc()
                #     print("trying again as pvt-accessible...\n")
                #     return self.get_tweet(id, True)
                # else:
                    print("Unhandled exception occurred")
                    traceback.print_exc()
                    print(f"skipping tweet {id}")
                    return None

    # since MUST BE TIMEZONE AWARE
    # usage example: since=datetime(2023, 8, 1).replace(tzinfo=pytz.utc)
    def get_tweets_from_user(
        self, username: str, since: datetime = None
    ) -> list[Tweet]:
        reached_backdate = False
        tweets: list[Tweet] = []
        cur = None

        if since == None:
            since = datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(days=7)
            print(f"falling back to grabbing tweets since 7 days ago ({since.date()})")
        else:
            print(f"grabbing tweets since {since.date()}")

        uid = int(self.app._get_user_id(username))
        print(f"{username} = {uid}")

        def add_tweet(tweet: Tweet):
            # malformed tweet check
            nonlocal reached_backdate
            try:
                tweet.author.id
            except:
                print(f"skipping malformed tweet: {tweet}")
                return

            tweet = self.fix_tweet(tweet)

            tweets.append(tweet)

            if (
                not reached_backdate
                and int(tweet.author.id) == uid
                and tweet.date <= since
            ):
                print("reached backdate")
                reached_backdate = True

        if uid in talent_lists.privated_accounts:
            self.try_login(0)

        while not reached_backdate:
            try:
                # uts = self.app.get_tweets(uid, replies=True, cursor=cur)
                search = self.app.search(
                    f"from:{username}", filter_=SearchFilters.Latest(), cursor=cur
                )
                cur_page = search.results
                print(f"obtained {len(cur_page)} tweets")

                if len(cur_page) == 0:
                    break

                for e in cur_page:
                    if isinstance(e, Tweet):
                        add_tweet(e)
                        if e == cur_page[-1]:
                            print(f"{e.date} (last tweet) < {since.date()} (since) ?")
                    elif isinstance(e, SelfThread):
                        # FIXME: rework when replied_to is fixed (currently populates user_mentions)
                        # latest tweet in thread = og author's reply
                        for t in e:
                            add_tweet(t)

                cur = search.cursor
            except RateLimitReached:
                print("RateLimitReached occurred getting tweets from user")
                self.login_wait(uid in talent_lists.privated_accounts)
            except UnknownError as e:
                print(f"UnknownError occurred getting tweets from user: {e.message.rstrip()}")
                print("treating like RateLimitReached...")
                self.login_wait(uid in talent_lists.privated_accounts)
            sleep(5) # FIXME: temporary attempt to avoid scraper lock-up

        tweets.sort(key=lambda t: t.id)
        return tweets

    def get_cross_ttweets_from_user(
        self, username: str, since_date: str = None
    ) -> list[TalentTweet]:
        if since_date is not None:
            d = since_date.split("-")
            since = datetime(*[int(x) for x in d]).replace(tzinfo=pytz.utc)
        else:
            since = None
        tweets = self.get_tweets_from_user(username, since)
        # print_tweets(tweets)
        ret: list[TalentTweet] = []
        for t in tweets:
            tt = TalentTweet.create_from_tweety(t)
            if tt.is_cross_company():
                print(f"cross t_id: {tt.tweet_id}")
                ret.append(tt)
        print(f"Found {len(ret)}/{len(tweets)} cross tweets")
        return ret


if __name__ == "__main__":
    talent_lists.init()
    s = Scraper()
    ttweets = s.get_cross_ttweets_from_user(
        "pomurainpuff", since=datetime(2023, 7, 30).replace(tzinfo=pytz.utc)
    )
    print("\n".join([x.__repr__() for x in ttweets]))
