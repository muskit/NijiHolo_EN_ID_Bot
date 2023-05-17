# NijiHolo EN/ID Bot
Twitter bot that tracks cross-company interactions between the non-JP branches of *hololive*/*HOLOSTARS* and *Nijisanji*!

![The project banner](images/banner.png)

**This project was created to run [this account](https://twitter.com/NijiHolo_EN_ID).**

## `.env`
These need to be defined in a `.env` file at the project root (outside of `src`):
```
# Scweet (scraping)
SCWEET_EMAIL=
SCWEET_USERNAME=
SCWEET_PASSWORD=

# Twitter API bot keys (posting)
api_key=
api_secret=
oauth1_access_token=
oauth1_access_secret=
bearer_token=
```

## Running modes
The bot may run in these modes:
* Catch-up (`c`): intended to run only once, scan all accounts for cross-company tweets and post them. Terminate when done posting all.
   - use `--auto-listen` to switch to listen mode when finished
* Listen (`l`): listens for tweets from list, sharing it if it's cross-company
* Command-line (`cmd`): an interactive mode for manual control and debugging (drops into Python interpretor)

*Created for the spirit of entertainment and in the name of unity.* ❤
