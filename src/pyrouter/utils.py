from urllib.parse import unquote, quote


def unquote_dict(d: dict) -> dict:
    if not isinstance(d, dict):
        return d
    for k, v in d.items():
        if isinstance(v, dict):
            v = unquote_dict(v)
        elif isinstance(v, str):
            v = unquote(v)
        elif isinstance(v, list):
            for i, _v in enumerate(v):
                v[i] = unquote_dict(_v)
        d[k] = v
    return d


def quote_dict(d: dict) -> dict:
    if not isinstance(d, dict):
        return d
    for k, v in d.items():
        if isinstance(v, dict):
            v = quote_dict(v)
        elif isinstance(v, bool):
            v = "1" if v else "0"
        elif isinstance(v, str):
            v = quote(v)
        elif isinstance(v, list):
            for i, _v in enumerate(v):
                v[i] = quote_dict(_v)
        else:
            # for example, when the value is an int
            v = quote(str(v))
        d[k] = v
    return d
