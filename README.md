# NijiHolo_EN_ID_Bot
*Twitter bot that follows interactions between Nijisanji EN/ID and hololive EN/ID members.*  
...because some folks are that desperate. Like me!

## Roadmap
* Read past tweets of members from both companies
* Store tweets in a queue file
* Create image of tweet, including up to three image attachments from that tweet
* Combine image(s) with quote retweet
* Don't tweet already-existing tweets (check quoted RTs?)
* Check out new tweets as soon as they post

## Notes
* Tweets should only occur if involved parties are cross-company
* Tweets should only occur if interaction involves [EN and EN] or [EN and (former) ID members]
    * cross-company ID interactions are regular enough
* Text of tweet should include involved names (w/o @) and the message, up to tweet limit

## API Calls
**retrieving tweets from a user**

https://oauth-playground.glitch.me/?id=usersIdTweets
* `id`: user
* `max_results=100`: 100 is the highest number of tweets we can retrieve
* `pagination_token`: token that takes us to the next/prev page of tweets
    * use `meta[next_token]`
* `expansions=entities.mentions.username,in_reply_to_user_id`
    * exposes mentions and replied users