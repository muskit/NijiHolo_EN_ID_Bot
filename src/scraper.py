from os.path import exists
from time import sleep
from datetime import datetime, timedelta

import pytz

from tweety import Twitter
from tweety.types import *
from tweety.exceptions_ import *
from tweety.filters import SearchFilters

from account_pool import AccountPool
from tweety_utils import *
from talenttweet import *
import talent_lists

class Scraper:
	def __init__(self):
		Scraper.instance = self
		self.__account = AccountPool()
		self.try_login()
	
	def try_login(self) -> bool:
		acc = self.__account.next()
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
		print('exhausted all accounts!')
		return False

	# since MUST BE TIMEZONE AWARE
	# usage example: since=datetime(2023, 8, 1).replace(tzinfo=pytz.utc)
	def get_tweets_from_user(self, username: str, since: datetime = None) -> list[Tweet]:
		reached_backdate = False
		tweets: list[Tweet] = []
		cur = None

		if since == None:
			since = datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(days=7)
			print(f'falling back to grabbing tweets since 7 days ago ({since.date()})')
		else:
			print(f'grabbing tweets since {since.date()}')

		uid = self.app._get_user_id(username)
		print(f"{username} = {uid}")

		def add_tweet(tweet: Tweet):
			# malformed tweet check
			nonlocal reached_backdate
			try:
				tweet.author.id
			except:
				print(f"skipping malformed tweet: {tweet}")
				return

			# recover lost info
			if tweet.is_retweet:
				if tweet.retweeted_tweet is None:
					print(f'{tweet.author.username}/{tweet.id} is missing the RT! Recovering...')
					tweet.retweeted_tweet = self.app.tweet_detail(str(tweet.id)).retweeted_tweet
				if tweet.retweeted_tweet.author is None:
					print(f'WARNING: {tweet.author.username}/{tweet.id} is missing the RT author! Recovering details...')
					tweet.retweeted_tweet = self.app.tweet_detail(tweet.retweeted_tweet.id)

			if tweet.is_quoted:
				if tweet.quoted_tweet is None: # quoted tweet is deleted
					# print(f'{tweet.author.username}/{tweet.id} is missing the QRT! Recovering...')
					# tweet.quoted_tweet = self.app.tweet_detail(str(tweet.id)).quoted_tweet
					tweet.is_quoted = False
				elif tweet.quoted_tweet.author is None:
					print(f'WARNING: {tweet.author.username}/{tweet.id} is missing the QRT author! Recovering details...')
					tweet.quoted_tweet= self.app.tweet_detail(tweet.quoted_tweet.id)

			# fix reply if it exists
			# if tweet.is_reply and tweet.replied_to is None:
			# 	tweet.replied_to = self.app.tweet_detail(tweet._original_tweet['in_reply_to_status_id_str'])
			tweets.append(tweet)

			if not reached_backdate and int(tweet.author.id) == uid and tweet.date <= since:
				print("reached backdate")
				reached_backdate = True

		while not reached_backdate:
			try:
				# uts = self.app.get_tweets(uid, replies=True, cursor=cur)
				search = self.app.search(f'from:{username}', filter_=SearchFilters.Latest(), cursor=cur)
				cur_page = search.tweets
				print(f'obtained {len(cur_page)} tweets')

				if len(cur_page) == 0: break

				for e in cur_page:
					if isinstance(e, Tweet):
						add_tweet(e)
					elif isinstance(e, TweetThread):
						# FIXME: rework when replied_to is fixed (currently populates user_mentions)
						# latest tweet in thread = og author's reply
						for t in e:
							add_tweet(t)
				
				cur = search.cursor
			except UnknownError:
				print("UnknownError occurred, probably rate-limited")
				# traceback.print_exc()
				if not self.try_login():
					print("sleeping for 1 minute...")
					sleep(60)
					print()
					self.try_login()
		
		tweets.sort(key=lambda t: t.id)
		return tweets
	
	def get_cross_ttweets_from_user(self, username: str, since_date: str = None) -> list[TalentTweet]:
		if since_date is not None:
			d = since_date.split('-')
			since = datetime(*[int(x) for x in d]).replace(tzinfo=pytz.utc)
		else:
			since = None
		tweets = self.get_tweets_from_user(username, since)
		# print_tweets(tweets)
		ret: list[TalentTweet] = []
		for t in tweets:
			tt = TalentTweet.create_from_tweety(t)
			if tt.is_cross_company():
				ret.append(tt)
		return ret

if __name__== '__main__':
	talent_lists.init()
	s = Scraper()
	ttweets = s.get_cross_ttweets_from_user("pomurainpuff", since=datetime(2023, 7, 30).replace(tzinfo=pytz.utc))
	print("\n".join([x.__repr__() for x in ttweets]))