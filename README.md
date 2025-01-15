# NijiHolo EN/ID Bot
Twitter bot that tracks cross-company interactions between the non-JP branches of *hololive*/*HOLOSTARS* and *Nijisanji*!

![The project banner](images/banner.png)

**This project was created to run [this account](https://twitter.com/NijiHolo_EN_ID).**

![Screenshot_20230912_235245](https://github.com/muskit/muskit/assets/15199219/0359fb26-8a48-4698-9b78-66d7d852099e)

## Running
With the way packages are setup, **you must have Docker installed and running!!**

Setup the `.env` in the project root. Refer to the [`.env`](#env) section for variables.

Build and run the Docker container:
```bash
# to delete container and built image
sh scripts/delete.sh

# to build image
sh scripts/build.sh

# to create container and run attached (can CTRL+P,CTRL+Q to detach)
sh scripts/run.sh

# ... or to run headless/detached
sh scripts/run_detached.sh
```

If attached to a container prepared by Dockerfile, you can run the program from project root (not in `src`). Refer to the following section for options.
```
python src/main.py
```

## Modes & Options
The bot may run in these modes:
* Pass no argument to run in listen mode, which scrapes all accounts in the *list* folder at an interval.
   * Pass `--straight-to-queue` to process the locally-stored queue first before attempting to scrape.
* Command-line (`cmd`): an interactive mode for manual control and debugging (drops into Python interpretor)

## `.env`
These need to be defined in a `.env` file in the `run` ephemeral directory.

### Scraper Credentials
To get around rate limitations imposed on users, we scrape with multiple accounts. Each account is defined in the file using the following format:
```
scraperX_username=twitter_username
scraperX_password=twitter_auth_token
```
where `X` is a number starting from 0, increasing by 1 for each account added. For instance:
```
scraper0_username=
scraper0_password=
scraper1_username=
scraper1_password=
```
The first account (`scraper0_username` and `scraper0_password`) **MUST be defined (`scraper_username` and `scraper_password` without number will not work!)**  and will be used to attempt scraping private accounts. Make sure this account follows any private accounts that you want to scrape!
### Twitter API Stuff
The following keys/tokens are used for the official API via `tweepy`. We mainly use these to just post tweets.
```
app_key=
app_secret=
user_token=
user_secret=
```
### Screenshot Cookie *(optional)*
This is the authentication token obtained from a browser when signed in on the Twitter website. It's only needed if you want to screenshot tweets from privated accounts. Make sure the token belongs to an account that follows desired private accounts! Maybe have it belong to `scraper0`?
```
web_auth_token=
```
### Example `.env` without values
```
scraper0_username=
scraper0_password=
scraper1_username=
scraper1_password=
web_auth_token=
app_key=
app_secret=
user_token=
user_secret=
```

*Created for the spirit of entertainment and in the name of unity.* ❤
