from os.path import exists
from time import sleep
from datetime import datetime, timedelta

from dotenv import dotenv_values
import pytz

from tweety import Twitter
from tweety.types import *

from tweety_utils import *
from talenttweet import *
from talent_lists import is_niji, is_holo

class Scraper:
	def __init__(self):
		creds = dotenv_values()
		self.app = Twitter("session")
		if exists("session.json"):
			self.app.connect()
		else:
			self.app.sign_in(creds["scraper_username"], creds["scraper_password"])

	# since MUST BE TIMEZONE AWARE
	# usage example: since=datetime(2023, 8, 1).replace(tzinfo=pytz.utc)
	def get_tweets_from_user(self, uid: int | str, since: datetime = None) -> list:
		reached_backdate = False
		tweets: list[Tweet] = []

		if since == None:
			since = datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(days=7)
			print(f'Grabbing tweets since 7 days ago ({since.date()})')

		if isinstance(uid, str):
			name = uid
			uid = self.app._get_user_id(uid)
			print(f"{name} = {uid}")

		def add_tweet(tweet: Tweet):
			nonlocal reached_backdate
			try:
				tweet.author
				tweets.append(tweet)
				if not reached_backdate and tweet.date <= since:
					print("reached backdate")
					reached_backdate = True
			except AttributeError:
				print("skipping malformed tweet: {tweet}")
				return

		uts = self.app.get_tweets(uid, replies=True)
		while not reached_backdate:
			cur_page = uts.tweets
			print(f'obtained {len(cur_page)} tweets')

			if len(cur_page) == 0: break

			for e in cur_page:
				if isinstance(e, Tweet):
					add_tweet(e)
				elif isinstance(e, TweetThread):
					# FIXME: rework when replied_to is fixed (currently only user_mentions works)
					t = e[-1] # latest tweet in thread = og author's reply
					t.replied_to = e[-2]
					add_tweet(t)
					print(f"adding thread latest: {t.id}")

			uts = self.app.get_tweets(uid, replies=True, cursor=uts.cursor)
		
		tweets.sort(key=lambda t: t.id)
		return tweets
	
	def get_cross_ttweets_from_user(self, uid: int | str, since: datetime = None):
		tweets = self.get_tweets_from_user(uid, since)
		ret: [TalentTweet] = []
		for t in tweets:
			is_niji = is_niji(int(t.author.id))
			is_cross = False

			# cross-rt?
			
			# rt mentions cross-company?

			# cross-qrt?

			# cross-reply?
			if t.replied_to is not None:
				if is_niji == is_holo(int(t.replied_to.author.id)):
					is_cross = True

			# cross-mention? in-thread?
			for u in t.user_mentions:
				if is_niji == is_holo(int(u.id)):
					is_cross = True

if __name__ == '__main__':
	app = Scraper()
	tweets = app.get_tweets_from_user("pomurainpuff")
	print_tweets(tweets)