# NijiHolo EN/ID Bot
Twitter bot that tracks cross-company interactions between the non-JP branches of *hololive*/*HOLOSTARS* and *Nijisanji*!

![The project banner](images/banner.png)

**This project was created to run [this account](https://twitter.com/NijiHolo_EN_ID).**

## Running
With the way packages are setup, **you must have Docker installed and running!!**

Setup the `.env` in the project root. Refer to the [`.env`](#env) section for variables.

Build and run the Docker container:
```bash
# to run attached (can CTRL+P,CTRL+Q to detach)
sh run.sh

# ... or to run headless
sh run_detached.sh
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
scraper_usernameX=twitter_username
scraper_passwordX=twitter_password
```
where `X` is a number starting from 0, increasing by 1 for each account added. For instance:
```
scraper_username0=
scraper_password0=
scraper_username1=
scraper_password1=
```
The first account (`scraper_username0` and `scraper_password0`) **MUST be defined (`scraper_username` and `scraper_password` without number will not work!)**  and will be used to attempt scraping private accounts. Make sure this account follows any private accounts that you want to scrape!
### Twitter API Stuff
The following keys/tokens are used for the official API via `tweepy`. We mainly use these to just post tweets.
```
app_key=
app_secret=
user_token=
user_secret=
```
### Screenshot Cookie *(optional)*
This is the authentication token obtained from a browser when signed in on the Twitter website. It's only needed if you want to screenshot tweets from privated accounts. Make sure the token belongs to an account that follows desired private accounts! Maybe have it belong to `scraper_username0`?
```
web_auth_token=
```
### Example `.env` without values
```
scraper_username0=
scraper_password0=
scraper_username1=
scraper_password1=
scraper_username2=
scraper_password2=
scraper_username3=
scraper_password3=
web_auth_token=
app_key=
app_secret=
user_token=
user_secret=
```

*Created for the spirit of entertainment and in the name of unity.* ❤
