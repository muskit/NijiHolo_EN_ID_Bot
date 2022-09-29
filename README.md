# NijiHolo_EN_ID_Bot
*Twitter bot that follows interactions between Nijisanji EN/ID and hololive EN/ID members.*  
...because some folks are that desperate. Like me!

**This project is intended to run [this account](https://twitter.com/NijiHolo_EN_ID).**

## Running modes
The bot will be runnable in three modes:
* Catch-up (`c`): intended to run only once, scan all accounts for cross-company tweets and post them. Terminate when done posting all.
* Listen (`l`): post any new tweets that come up if it's cross-company
    * may implement short-term catch-up function
* Command-line (`cmd`): an interactive mode for manual control (TBA; currently drops into Python interpretor)

## Roadmap
* ~~Read past tweets of members from both companies~~
* ~~Create screenshot of tweet~~
* ~~Track tweets in queue files~~
* ~~Post tweets along with screenshot of tweet~~
    * Include screenshot of tweet being replied to?
* ~~Combine image with quote tweet~~
* ~~Don't tweet already-existing tweets (check our past quote tweets; might be saved in a file for quicker access)~~
* Track posted tweets in a history file

## Notes
* Tweets should only occur if involved parties are cross-company
* Tweets should only occur if interaction involves [EN and EN] or [EN and (former) ID] parties
    * cross-company ID interactions are regular enough IMO
* Our tweets should include:
    * involved names (w/o @) and the tweet (as a quote tweet)
    * screenshot of the tweet (+ maybe image of tweet being replied to when applicable)
