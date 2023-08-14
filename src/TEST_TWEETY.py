from time import sleep
from datetime import datetime, timedelta

from dotenv import dotenv_values
import pytz

from tweety import Twitter
from tweety.types import *

creds = dotenv_values()

app = Twitter("session")
app.sign_in(creds["username"], creds["password"])

def url(t: Tweet):
	return f'https://twitter.com/{t.author.username}/status/{t.id}'

def print_tweets(tweets: list):
	print(f'{len(tweets)} tweets:')
	for t in tweets:
		if isinstance(t, Tweet):
			print(f'{t.date} : {url(t)} : RT? {t.is_retweet}')
		elif isinstance(t, TweetThread):
			print('-----------TTd----------')
			print_tweets(t.tweets)
			print('-----------end----------')

def get_tweets_from_user(uid: int | str, since: datetime = None) -> list:
	reached_backdate = False
	tweets: [Tweet] = []
	if since == None:
		since = datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(days=7)
		print(f'Grabbing tweets since 7 days ago ({since.date()})')

	if isinstance(uid, str):
		name = uid
		uid = app._get_user_id(uid)
		print(f"{name} = {uid}")

	def add_tweet(tweet: Tweet):
		nonlocal reached_backdate
		try:
			if tweet.is_retweet or tweet.author.id == uid:
				tweets.append(tweet)
				if not reached_backdate and tweet.date <= since:
					print("reached backdate")
					reached_backdate = True
		except AttributeError:
			print("skipping malformed tweet: {tweet}")
			return

	uts = app.get_tweets(uid, replies=True)
	while not reached_backdate:
		cur_page = uts.tweets
		print(f'obtained {len(cur_page)} tweets')

		if len(cur_page) == 0: break

		for e in cur_page:
			if isinstance(e, Tweet):
				add_tweet(e)
			elif isinstance(e, TweetThread):
				for t in e.tweets:
					add_tweet(t)
		
		uts.get_next_page()
	
	tweets.sort(key=lambda t: t.id)
	return tweets

tweets = get_tweets_from_user("ninakosaka", since=datetime(2023, 7, 1))
print_tweets(tweets)