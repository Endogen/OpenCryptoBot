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


def format(value, decimals=None, force_length=False, template=None):
    """Format a crypto coin value so that it isn't unnecessarily long"""
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
