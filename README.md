# OpenCryptoBot
Welcome to the Swiss Army knife for crypto! *OpenCryptoBot* is an open source Telegram bot written in Python and you can [add this bot directly](https://telegram.me/OpenCryptoBot) or add him by searching for user *@OpenCryptoBot* on Telegram.

If you are interested in news regarding this bot or want more indept explanations for all available commands, please visit the [homepage](https://endogen.github.io/OpenCryptoBot).

<p align="center">
  <img src="https://endogen.github.io/OpenCryptoBot/assets/screenshots/1.png">
  <img src="https://endogen.github.io/OpenCryptoBot/assets/screenshots/2.png">
</p>

<p align="center">
  <img src="https://endogen.github.io/OpenCryptoBot/assets/screenshots/3.png">
  <img src="https://endogen.github.io/OpenCryptoBot/assets/screenshots/4.png">
</p>

## Overview
This Python script is a polling based Telegram bot. [Webhook mode](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks) is implemented but untested.

### General bot features
* Written in Python and fully open source
* Update notifications for new releases on GitHub
* Update your running bot to any release or branch
* Admin specific commands like `restart` and `shutdown`
* Every command is a plugin that can be enabled / disabled
* Custom rate limit per user or per user and command
* Use database to track usage or disable it all together
* Cache functionality (can be disabled)
* Run the bot locally or hosted on a server
* Powerful logging functionality
* Set up the bot by using command line arguments
* Bot can be administered by more then one user
* Data provided by seven different API providers
* BPMN diagrams for commands to understand the data flow
* Users can provide feedback about the bot
* Experimental inline-mode (only `price` command for now)
* Repeatedly send commands at specified time interval

### Command features
* Current price
* Price change over time
* Current and historical volume
* Market capitalization
* Candlestick charts
* Price and volume charts
* All Time High details
* Calculated value of coin quantity
* Find out where to buy a coin
* Sort trading pairs by volume
* Details about the team behind a coin
* Details about the people in a team
* Coin-specific news or filtered by keywords
* Return on Investment for a coin
* Details about ICO if there was one
* Whitepaper download
* Best and worst movers
* Compare different coins
* Google Trends chart for keywords
* Description for a coin
* Details about exchanges and toplist
* Details about coin development
* Social media links and stats
* Get a coin summary
* Global dominance, volume and market cap
* Coin logo and technical coin details
* Search for a coin by name
* Get latest Tweets from Twitter for a coin

## Configuration
This part is only relevant if you want to host this bot yourself. If you just want to use the bot, add user *@OpenCryptoBot* to your Telegram contacts.

Before starting up the bot you have to take care of some settings and add some API tokens. All configuration files or token files are located in the `conf` folder.

### config.json
This file holds the configuration for the bot. You have to at least edit the value for __admin_id__. Every else setting is optional.

- __admin_id__: This is a list of Telegram user IDs that will control the bot. You can just add your own user or multiple users if you want. If you don't know your Telegram user ID, get in a conversation with Telegram bot [@userinfobot](https://telegram.me/userinfobot) and if you write him he will return you your user ID.
- __telegram - read_timeout__: Read timeout in seconds as integer. Default Telegram value is about 5 seconds. Usually this value doesn't have to be changed.
- __telegram - connect_timeout__: Connect timeout in seconds as integer. Default Telegram value is about 5 seconds. Usually this value doesn't have to be changed.
- __webhook - listen__: Required for webhook mode. IP to listen to.
- __webhook - port__: Required for webhook mode. Port to listen on.
- __webhook - privkey_path__: Required for webhook mode. Path to private key  (.pem file).
- __webhook - cert_path__: Required for webhook mode. Path to certificate (.pem file).
- __webhook - url__: Required for webhook mode. URL where the bot is hosted.
- __use_db__: If `true` then a new database file (SQLite) will be generated on first start and every usage of the bot will be recorded in this database. If `false`, no database will be used.
- __rate_limit - enabled__: If `true` then a rate limit for users will be activated so that only a specific number of requests in a specific timeframe are possible. If `false` then rate limit functionality will be disabled.
- __rate_limit - requests__: Number (integer) of API requests that are allowed for a specific timeframe (see _rate_limit - timespan_).
- __rate_limit - timespan__: Number (integer) of seconds for which the issued API requests will be counted. If the count exceeds the value in _rate_limit - requests_, the user will be informed and can not issue new requests until the timeframe is reached.
- __rate\_limit - incl_cmd__: If `true` then the rate limit will be per command. If `false` then it doesn't matter which command you used. If you exceed the limit you can't issue any API calls anymore until the timeframe is over.
- __refresh_cache__: If `null` then caching is disabled and every API call will reach the API provider. It's highly recommanded to enabled caching. The timeframe to refresh the cache can be specified in seconds `s` or minutes `m` or hours `h` or days `d`. Example: `6h`.
- __update - github_user__: Only relevant if you want to provide your own updates. The GitHub username.
- __update - github_repo__: Only relevant if you want to provide your own updates. The GitHub repository that you want to do the updates from.
- __update - update_hash__: *This should not be changed*. The bot saves here the hash of the currently running bot (only if an update happened).
- __update - update_hash__: How ofter should the bot automatically check for updates? The timeframe can be specified in seconds `s` or minutes `m` or hours `h` or days `d`. Example: `1d`. To disable update checks, enter `null`.

### bot.token
This file holds the Telegram bot token. You have to provide one and you will get it in a conversation with Telegram user [@BotFather](https://telegram.me/BotFather) while registering your bot.

### cryptopanic.token
This file is optional and only needed if you use the `news` plugin. News are requested from [http://cryptopanic.com](http://cryptopanic.com) and thus you have to register an account there and get you API token and enter it in here.

## Starting
In order to run the bot you need to execute some Python code. If you don't have any idea where to host the bot, take a look at [Where to host Telegram Bots](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Where-to-host-Telegram-Bots). But services like [Heroku](https://www.heroku.com) (free) will work fine too. You can also run the script locally on your own computer for testing purposes.

### Prerequisites
##### Python version
You have to use at least __Python 3.7__ to execute the scripts. Everything else is not supported.

##### Installing needed modules from `Pipfile`
Install all needed Python modules automatically with [Pipenv](https://pipenv.readthedocs.io). You have to be in the root folder of the bot - on the same level as the `Pipfile`:

```shell
pipenv install
```

##### Installing needed modules from `requirements.txt`
This is an alternative way to install all needed Python modules. If done this way, every installed module will be available for every other Python script you run. Installing modules globally is only recommanded if you know what you are doing:

1. Generate `requirements.txt` from `Pipfile`

```shell
pipenv lock -r
```

2. Install all needed Python modules

```shell
pip3 install -r requirements.txt
```

##### Installing `orca`
After you installed the modules, you also have to install [orca](https://github.com/plotly/orca) if you want to use the `candlestick` plugin or the `chart` plugin (because [Plotly](https://plot.ly/python) is used to generate the static charts and `orca` is a dependency for static image generation under Plotly). For more info check out [Plotly Static Image Export](https://plot.ly/python/static-image-export)

If you get error `xvfb-run: error:Xvfb failed to start` please execute:

```script
xvfb-run -a /path/to/orca "$@"
```

### Starting
1. First you have to make the script `run.sh` executable with

```shell
chmod +x run.sh
```

2. If you installed the needed Python modules via `Pipfile` you have to execute the following in the root folder of the bot:

```shell
pipenv run ./run.sh &
```

If you installed the modules globally:

```shell
./run.sh &
```

### Stopping
The recommanded way to stop the bot is the bot command `/shutdown`. If you don't want or can't use this, you can shut the bot down with:

```shell
pkill python3.7
```

which will kill __every__ Python 3.7 process that is currently running.

## Usage
If you configured the bot correctly and execute it, the bot will check for updates (if enabled in `config.json`) and notify you if a new release is available. **Please ignore the update if you purposely downloaded the newest version from the `master` branch because the bot will only notify you about releases**. And in this case the release will be older then the current version from the `master` branch.

### Available commands
##### Charts
```
/c - Chart with price and volume
/cs - Candlestick chart for coin
```

##### Price
```
/51 - PoW 51% attack cost
/ath - All time high price for coin
/best - Best movers for hour or day
/ch - Price change over time
/ico - ICO info for coin
/p - Coin price
/roi - Return on Investment for a coin
/s - Price, market cap and volume
/v - Value of coin quantity
/worst - Worst movers for hour or day
```

##### General
```
/comp - Compare coins
/de - Show decentralization info
/des - Coin description
/dev - Development information
/ex - Exchange details and toplist
/g - Global crypto data
/i - General coin information
/m - Find exchanges to trade a coin
/pe - Info about person from a team
/re - Repeat any command periodically
/se - Search for symbol by coin name
/t - Info about team behind a coin
/top - List top 30 coins
/tr - Google Trends - Interest Over Time
/wp - Find whitepaper for a coin
```

##### News & Events
```
/ev - Show crypto events
/n - News about a coin
/soc - Social media details
/tw - Latest Tweets from Twitter
```

##### Utilities
```
/po - Info about mining pools
/wa - Details about wallets
```

##### Bot
```
/about - Information about bot
/bpmn - BPMN diagram for a command
/feedback - Send us your feedback
/man - Show how to use a command
/re - Repeat any command periodically
```

If you want to show a list of available commands as you type, open a chat with Telegram user [@BotFather](https://telegram.me/BotFather) and send the command `/setcommands`. Then choose the bot you want to activate the list for and after that send the list of commands with description. Something like this:

```
51 - PoW 51% attack cost
about - Information about bot
ath - All time high price for coin
best - Best movers for hour or day
bpmn - BPMN diagram for a command
c - Chart with price and volume
ch - Price change over time
comp - Compare coins
cs - Candlestick chart for coin
de - Show decentralization info
des - Coin description
dev - Development information
ev - Show crypto events
ex - Exchange details and toplist
feedback - Send us your feedback
g - Global crypto data
h - Show overview of all commands
i - General coin information
ico - ICO info for coin
m - Find exchanges to trade a coin
man - Show how to use a command
mc - Market capitalization
n - News about a coin
p - Coin price
pe - Info about person from a team
po - Info about mining pools
re - Repeat any command periodically
roi - Return on Investment for a coin
s - Price, market cap and volume
se - Search for symbol by coin name
soc - Social media details
t - Info about team behind a coin
top - List top 30 coins
tr - Google Trends - Interest Over Time
tw - Get newest tweets for coin
v - Value of coin quantity
vol - Volume for a coin
wa - Details about wallets
worst - Worst movers for hour or day
wp - Find whitepaper for a coin
```

## Development
I am actively developing this bot and will do so also in the near future. If you would like to help out with development, send a message via Telegram to [@endogen](https://telegram.me/endogen) or open an issue here at GitHub. 

### Todo
##### Priority 1
- [ ] Add alerts for prices

##### Priority 2
- [ ] Add maintenance mode
- [ ] Ban user if rate limit exceeded to often

##### Priority 3
- [ ] Provide BPMN diagrams for all commands

## Disclaimer
I use this bot personally to check the current state of some coins but since all the data is relying on external APIs, i can't guarantee that all informations are correct. Please use with caution. **I can't be held responsible for anything!**

## Donating
If you find **OpenCryptoBot** suitable for your needs, please consider donating whatever amount you like to:

#### Bitcoin
```
1EoBYmfdJznJ21v8Uiiv44iJ2sDb6Bsqc1
```

#### Bitcoin Cash
```
qzken7mgslv0w9t4ycj4uganv66ljccsq5ngcepp6h
```

#### Ethereum (ETH)
```
0x15c3dB6f0f3cC3A187Cfa4b20605293a08b9Be46
```

#### Monero (XMR)
```
42eSjjHF63P3LtxcdeC71TT3ZCcGbTtk1aESTvfrz4VqYeKMFP9tbWhjmcUJZE3yVrgDjH8uZhnob9czCtm764cFDWYPe7c
```

#### How else can you support me?
If you can't or don't want to donate, please consider signing up on listed exchanges below. They are really good and by using these links to register an account i get a share of the trading-fee that you pay to the exchange if you execute a trade.

- [Binance](https://www.binance.com/?ref=16770868)
- [KuCoin](https://www.kucoin.com/#/?r=H3QdJJ)