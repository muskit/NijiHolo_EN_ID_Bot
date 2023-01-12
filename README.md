# NijiHolo EN/ID Bot
Twitter bot that tracks interactions between Nijisanji EN/ID, hololive EN/ID, and holostars EN members.

![The project banner](images/banner.png)

**This project was created to run [this account](https://twitter.com/NijiHolo_EN_ID).**

## Running modes
The bot may run in these modes:
* Catch-up (`c`): intended to run only once, scan all accounts for cross-company tweets and post them. Terminate when done posting all.
   - use `--auto-listen` to switch to listen mode when finished
* Listen (`l`): listens for tweets from list, sharing it if it's cross-company
* Command-line (`cmd`): an interactive mode for manual control and debugging (drops into Python interpretor)

## TODOs
* Fix catch-up mode (`TWINT` is broken yet again *\*sigh\**)

*Created for the spirit of entertainment and in the name of unity.*
