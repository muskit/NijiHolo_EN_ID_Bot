# NijiHolo EN/ID Bot
Twitter bot that tracks cross-company interactions between the non-JP branches of *hololive*/*HOLOSTARS* and *Nijisanji*!

![The project banner](images/banner.png)

**This project was created to run [this account](https://twitter.com/NijiHolo_EN_ID).**

## `.env`
These need to be defined in a `.env` file at the project root (outside of `src`):

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
The first account (`scraper_username0` and `scraper_password0`) will be used to attempt scraping private accounts. Make sure this account follows any private accounts that you want to scrape!
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

## Running modes
The bot may run in these modes:
* Pass no argument to run in listen mode, which scrapes all accounts in the *list* folder at an interval.
   * Pass `--straight-to-queue` to process the queue first before attempting to scrape.
* Command-line (`cmd`): an interactive mode for manual control and debugging (drops into Python interpretor)

*Created for the spirit of entertainment and in the name of unity.* ❤
