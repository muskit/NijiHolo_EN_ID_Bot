# NijiHolo EN/ID Bot
*Twitter bot that tracks interactions between Nijisanji EN/ID and hololive EN/ID members.*

![The project banner](images/banner.png)

**This bot is intended to run [this account](https://twitter.com/NijiHolo_EN_ID).**

## Running modes
The bot will be runnable in three modes:
* Catch-up (`c`): intended to run only once, scan all accounts for cross-company tweets and post them. Terminate when done posting all.
* Listen (`l`): post any new tweets that come up if it's cross-company
    * may implement short-term catch-up function
* Command-line (`cmd`): an interactive mode for manual control (TBA; currently drops into Python interpretor)

## Extra TODOs
* Include screenshot of tweet being replied to

## Notes
* Tweets should only occur if involved parties are cross-company
* Tweets should only occur if interaction involves [EN and EN] or [EN and (former) ID] parties
    * cross-company ID interactions are regular enough IMO
* Our tweets should include:
    * involved names (w/o @) and the tweet (as a quote tweet)
    * screenshot of the tweet (+ maybe image of tweet being replied to when applicable)

**This project was created for the spirit of entertainment and in the name of unity.**
