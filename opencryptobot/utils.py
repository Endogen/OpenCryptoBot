def is_number(string):
    """Also accepts '.' in the string. Function 'isnumeric()' doesn't"""
    try:
        float(string)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(string)
        return True
    except (TypeError, ValueError):
        pass

    return False


def get_fiat_list():
    return ['usd', 'aed', 'ars', 'aud', 'bdt', 'bhd', 'bmd', 'brl', 'cad',
            'chf', 'clp', 'cny', 'czk', 'dkk', 'eur', 'gbp', 'hkd', 'huf',
            'idr', 'ils', 'inr', 'jpy', 'krw', 'kwd', 'lkr', 'mmk', 'mxn',
            'myr', 'nok', 'nzd', 'php', 'pkr', 'pln', 'rub', 'sar', 'sek',
            'sgd', 'thb', 'try', 'twd', 'vef', 'zar', 'xdr']


def format(value,
           decimals=None,
           force_length=False,
           template=None,
           on_zero=0,
           on_none=None,
           symbol=None):
    """Format a crypto coin value so that it isn't unnecessarily long"""

    fiat = False
    if symbol and isinstance(symbol, str):
        if symbol.lower() in get_fiat_list():
            fiat = True

    if value is None:
        return on_none

    try:
        if isinstance(value, str):
            value = value.replace(",", "")
        v = float(value)
    except Exception:
        return str(value)

    try:
        if isinstance(template, str):
            template = template.replace(",", "")
        t = float(template)
    except Exception:
        t = v

    try:
        decimals = int(decimals)
    except Exception:
        decimals = None

    try:
        if float(value) == 0:
            return on_zero
    except Exception:
        return str(value)

    if t < 1:
        if decimals:
            v = "{1:.{0}f}".format(decimals, v)
        else:
            v = "{0:.8f}".format(v)
    elif t < 100:
        if decimals:
            v = "{1:.{0}f}".format(decimals, v)
        else:
            v = "{0:.4f}".format(v)
    elif t < 10000:
        if decimals:
            v = "{1:,.{0}f}".format(decimals, v)
        else:
            v = "{0:,.2f}".format(v)
    else:
        v = "{0:,.0f}".format(v)

    if not force_length:
        cut_zeros = False

        if t >= 1:
            cut_zeros = True
        else:
            if fiat:
                cut_zeros = True

        if cut_zeros:
            while "." in v and v.endswith(("0", ".")):
                v = v[:-1]
    return v


def get_seconds(time_span, valid="s,m,h,d"):
    if isinstance(time_span, str):
        if time_span.isnumeric():
            return int(time_span)

        resolution = time_span.strip()[-1:].lower()
        time_frame = time_span.strip()[:-1]

        if resolution not in valid.split(","):
            return None

        if time_frame.isnumeric():
            if resolution == "s":
                return int(time_frame)
            elif resolution == "m":
                return int(time_frame) * 60
            elif resolution == "h":
                return int(time_frame) * 60 * 60
            elif resolution == "d":
                return int(time_frame) * 60 * 60 * 24
            else:
                return int(time_frame)
        else:
            return None
    elif isinstance(time_span, float):
        return int(time_span)
    elif isinstance(time_span, int):
        return time_span
    else:
        return None


def get_date(from_date, time_span):
    resolution = time_span.strip()[-1:].lower()
    time_frame = time_span.strip()[:-1]

    valid = "d,m,y"
    if resolution not in valid.split(","):
        return None

    if not time_frame.isnumeric():
        return None

    time_frame = int(time_frame)

    from datetime import timedelta

    if resolution == "d":
        t = from_date - timedelta(days=time_frame)
    elif resolution == "m":
        t = from_date - timedelta(days=time_frame * 30)
    elif resolution == "y":
        t = from_date - timedelta(days=time_frame * 365)
    else:
        return None

    return str(t)[:10]


# Get list of keywords or value of keyword
def get_kw(args, keyword=None, fallback=None):
    keywords = dict()

    if args:
        for arg in args:
            if "=" in arg:
                kv = arg.split("=")
                v = str2bool(kv[1]) if is_bool(kv[1]) else kv[1]
                keywords[kv[0]] = v

    if keyword:
        return keywords.get(keyword, fallback)

    return keywords


# Remove all keywords from list with arguments
def del_kw(args):
    ar = list()
    for arg in args:
        if "=" not in arg:
            ar.append(arg)
    return ar


def remove_html_links(text):
    import html2text

    h = html2text.HTML2Text()
    h.ignore_links = True

    start = "<a href="
    end = "</a>"

    while start in text and end in text:
        s_index = text.find(start)
        e_index = text.find(end) + len(end)

        html_link = text[s_index:e_index]
        title = h.handle(html_link).strip()
        text = text.replace(html_link, title)

    return text.strip()


def url(url, join=True):
    if isinstance(url, list):
        url = [x[:len(x) - 1] if x.endswith("/") else x for x in url]
        return "\n".join(url) if join else url
    else:
        return url[:len(url) - 1] if url.endswith("/") else url


def esc_md(text):
    import re

    rep = {"_": "\\_", "*": "\\*", "[": "\\[", "`": "\\`"}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))

    return pattern.sub(lambda m: rep[re.escape(m.group(0))], text)


# Returns a pre compiled Regex pattern to ignore case
def comp(pattern):
    import re
    return re.compile(pattern, re.IGNORECASE)


def is_bool(v):
    return v.lower() in ("yes", "true", "t", "1", "no", "false", "f", "0")


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


# Return 'Yes' for True and 'No' for False
def bool2str(b):
    return "Yes" if b else "No"


# Restrict message length to max characters as defined by Telegram
def split_msg(msg, max_len=None, split_char="\n", only_one=False):
    if not max_len:
        import opencryptobot.constants as con
        max_len = con.MAX_TG_MSG_LEN

    if only_one:
        return [msg[:max_len][:msg[:max_len].rfind(split_char)]]

    remaining = msg
    messages = list()
    while len(remaining) > max_len:
        split_at = remaining[:max_len].rfind(split_char)
        message = remaining[:max_len][:split_at]
        messages.append(message)
        remaining = remaining[len(message):]
    else:
        messages.append(remaining)

    return messages


# Check if every value in each list is the same
def all_same(*items):
    return True if all(v == items[0] for v in items) else False
