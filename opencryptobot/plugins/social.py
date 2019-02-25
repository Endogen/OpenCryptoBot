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

    def get_cmds(self):
        return ["soc", "social"]

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

        try:
            response = APICache.get_cg_coins_list()
        except Exception as e:
            return self.handle_error(e, update)

        for entry in response:
            if entry["symbol"].lower() == coin.lower():
                try:
                    data = CoinGecko().get_coin_by_id(entry["id"])
                except Exception as e:
                    return self.handle_error(e, update)

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

                msg = f"`Social data for {data['name']} ({coin})`\n\n"

                if home_lst:
                    url = utl.esc_md(utl.url(home_lst))
                    msg += f"`Homepage:`\n{url}\n"
                if block_lst:
                    url = utl.esc_md(utl.url(block_lst))
                    msg += f"`Block Explorer:`\n{url}\n"
                if annou_lst:
                    url = utl.esc_md(utl.url(annou_lst))
                    msg += f"`Announcements:`\n{url}\n"
                if chat_lst:
                    url = utl.esc_md(utl.url(chat_lst))
                    msg += f"`Chat:`\n{url}\n"
                if forum_lst:
                    url = utl.esc_md(utl.url(forum_lst))
                    msg += f"`Forum:`\n{url}\n"
                if twitter:
                    tw_follow = utl.format(tw_follow)
                    url = utl.esc_md(f"{self.TW_URL}{twitter}")
                    msg += f"`Twitter ({tw_follow} Followers):`\n{url}\n"
                if facebook:
                    fb_likes = utl.format(fb_likes)
                    url = utl.esc_md(f"{self.FB_URL}{facebook}")
                    msg += f"`Facebook ({fb_likes} Likes):`\n{url}\n"
                if btctalk:
                    url = utl.esc_md(f"{self.BT_URL}{btctalk}")
                    msg += f"`BitcoinTalk:`\n{url}\n"
                if telegram:
                    tg_usr_cnt = utl.format(tg_usr_cnt)
                    url = utl.esc_md(f"{self.TG_URL}{telegram}")
                    msg += f"`Telegram ({tg_usr_cnt} Users):`\n{url}\n"
                if reddit:
                    rd_subsc = utl.format(rd_subsc)
                    url = utl.esc_md(f"{utl.url(reddit)}")
                    msg += f"`Reddit ({rd_subsc} Subscribers):`\n{url}\n"

                break

        if not msg:
            update.message.reply_text(
                text=f"{emo.ERROR} No data found for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        update.message.reply_text(
            text=msg,
            disable_web_page_preview=True,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>`"

    def get_description(self):
        return "Social media details"

    def get_category(self):
        return Category.NEWS
