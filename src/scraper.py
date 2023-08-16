from os.path import exists
from time import sleep
from datetime import datetime, timedelta

from dotenv import dotenv_values
import pytz

from tweety import Twitter
from tweety.types import *
from tweety.exceptions_ import *
from tweety.filters import SearchFilters

from tweety_utils import *
from talenttweet import *
import talent_lists

class Scraper:
	def __init__(self):
		creds = dotenv_values()
		self.app = Twitter("session")
		# if exists("session.json"):
		# 	self.app.connect()
		# else:
		self.app.sign_in(creds["scraper_username"], creds["scraper_password"])

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
				tweet.author
			except AttributeError:
				print("skipping malformed tweet: {tweet}")
				return

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
						add_tweet(e[0])
						for t in e:
							add_tweet(t)
				
				cur = search.cursor
			except UnknownError:
				print("UnknownError occurred, probably rate-limited")
				print("sleeping for 1 minute...")
				sleep(60)
		
		tweets.sort(key=lambda t: t.id)
		return tweets
	
	def get_cross_ttweets_from_user(self, username: str, since: datetime = None) -> list[TalentTweet]:
		tweets = self.get_tweets_from_user(username, since)
		print_tweets(tweets)
		ret: list[TalentTweet] = []
		for t in tweets:
			tt = TalentTweet.create_from_tweety(t)
			if tt.is_cross_company():
				ret.append(tt)
		return ret

talent_lists.init()
s = Scraper()
ttweets = s.get_cross_ttweets_from_user("pomurainpuff", since=datetime(2023, 7, 30).replace(tzinfo=pytz.utc))
print("\n".join([x.__repr__() for x in ttweets]))