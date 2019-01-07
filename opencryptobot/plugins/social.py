import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Social(OpenCryptoPlugin):

    TG_URL = "https://t.me/"
    TW_URL = "https://twitter.com/"
    FB_URL = "https://www.facebook.com/"
    BT_URL = "https://bitcointalk.org/index.php?topic="

    def get_cmd(self):
        return "soc"

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if RateLimit.limit_reached(update):
            return

        coin = args[0].upper()
        msg = str()

        for entry in APICache.get_cg_coins_list():
            if entry["symbol"].lower() == coin.lower():
                data = CoinGecko().get_coin_by_id(entry["id"])

                home_lst = list(filter(None, data["links"]["homepage"]))
                block_lst = list(filter(None, data["links"]["blockchain_site"]))
                annou_lst = list(filter(None, data["links"]["announcement_url"]))
                chat_lst = list(filter(None, data["links"]["chat_url"]))
                forum_lst = list(filter(None, data["links"]["official_forum_url"]))
                twitter = data["links"]["twitter_screen_name"]
                facebook = data["links"]["facebook_username"]
                btctalk = data["links"]["bitcointalk_thread_identifier"]
                telegram = data["links"]["telegram_channel_identifier"]
                reddit = data["links"]["subreddit_url"]

                fb_likes = data["community_data"]["facebook_likes"]
                tw_follow = data["community_data"]["twitter_followers"]
                rd_subsc = data["community_data"]["reddit_subscribers"]
                tg_usr_cnt = data["community_data"]["telegram_channel_user_count"]

                msg = f"Social data for {data['name']} ({coin})\n\n"

                if home_lst:
                    msg += f"Homepage:\n{utl.url(home_lst)}\n"
                if block_lst:
                    msg += f"Block Explorer:\n{utl.url(block_lst)}\n"
                if annou_lst:
                    msg += f"Announcements:\n{utl.url(annou_lst)}\n"
                if chat_lst:
                    msg += f"Chat:\n{utl.url(chat_lst)}\n"
                if forum_lst:
                    msg += f"Forum:\n{utl.url(forum_lst)}\n"
                if twitter:
                    tw_follow = utl.format(tw_follow)
                    msg += f"Twitter ({tw_follow} Followers):\n{self.TW_URL}{twitter}\n"
                if facebook:
                    fb_likes = utl.format(fb_likes)
                    msg += f"Facebook ({fb_likes} Likes):\n{self.FB_URL}{facebook}\n"
                if btctalk:
                    msg += f"BitcoinTalk:\n{self.BT_URL}{btctalk}\n"
                if telegram:
                    tg_usr_cnt = utl.format(tg_usr_cnt)
                    msg += f"Telegram ({tg_usr_cnt} Users):\n{self.TG_URL}{telegram}\n"
                if reddit:
                    rd_subsc = utl.format(rd_subsc)
                    msg += f"Reddit ({rd_subsc} Subscribers):\n{utl.url(reddit)}\n"

                break

        if not msg:
            update.message.reply_text(
                text=f"{emo.ERROR} No data found for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        update.message.reply_text(
            text=msg,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin>`"

    def get_description(self):
        return "Social media details"

    def get_category(self):
        return Category.NEWS
