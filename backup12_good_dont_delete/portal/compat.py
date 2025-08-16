# portal/compat.py
# Werkzeug 3.x removed url_decode/url_encode; some Flask-Login versions still import them.
# This shim provides minimal polyfills before flask_login is imported.
from urllib.parse import parse_qsl, urlencode
try:
    import werkzeug.urls as _wz_urls  # type: ignore
except Exception:
    _wz_urls = None

def _url_decode(s, charset='utf-8', errors='replace', include_empty=True, separator='&', cls=None):
    try:
        from werkzeug.datastructures import MultiDict as WZMultiDict
        md = WZMultiDict()
        for k, v in parse_qsl(
            s or '',
            keep_blank_values=include_empty,
            strict_parsing=False,
            encoding=charset,
            errors=errors,
            separator=separator
        ):
            md.add(k, v)
        return md
    except Exception:
        pairs = parse_qsl(s or '', keep_blank_values=include_empty)
        md = {}
        for k, v in pairs:
            md.setdefault(k, []).append(v)
        return md

def _url_encode(obj, charset='utf-8', sort=False, key=None, separator='&'):
    try:
        return urlencode(obj, doseq=True)
    except Exception:
        try:
            return urlencode(list(obj.items()), doseq=True)
        except Exception:
            return ''

if _wz_urls is not None:
    if not hasattr(_wz_urls, 'url_decode'):
        _wz_urls.url_decode = _url_decode  # type: ignore
    if not hasattr(_wz_urls, 'url_encode'):
        _wz_urls.url_encode = _url_encode  # type: ignore
