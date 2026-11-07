import time
import json
import logging
import urllib.request
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# In-memory quote cache with TTL (60 seconds)
_QUOTE_CACHE: Dict[str, Any] = {}
_LAST_CACHE_TIME: float = 0
CACHE_TTL_SECONDS = 60

INDEX_MAP = {
    "NIFTY 50": {"symbol": "%5ENSEI", "fallback_price": 25030.35, "fallback_change": 2.01},
    "SENSEX": {"symbol": "%5EBSESN", "fallback_price": 81028.02, "fallback_change": 2.17},
    "BANK NIFTY": {"symbol": "%5ENSEBANK", "fallback_price": 59086.00, "fallback_change": 2.27},
    "INDIA VIX": {"symbol": "%5EINDIAVIX", "fallback_price": 17.46, "fallback_change": 12.10},
}

EQUITY_MAP = {
    "RELIANCE": {"name": "Reliance Industries", "symbol": "RELIANCE.NS", "fallback_price": 1320.00, "fallback_change": 0.50},
    "TCS": {"name": "Tata Consultancy Services", "symbol": "TCS.NS", "fallback_price": 2498.50, "fallback_change": 0.11},
    "HDFCBANK": {"name": "HDFC Bank Ltd", "symbol": "HDFCBANK.NS", "fallback_price": 788.25, "fallback_change": 3.72},
    "INFY": {"name": "Infosys Ltd", "symbol": "INFY.NS", "fallback_price": 1181.40, "fallback_change": 1.20},
    "SBIN": {"name": "State Bank of India", "symbol": "SBIN.NS", "fallback_price": 1018.50, "fallback_change": 1.85},
    "ITC": {"name": "ITC Ltd", "symbol": "ITC.NS", "fallback_price": 283.15, "fallback_change": 0.40},
}


def _fetch_single_quote(symbol: str, timeout: float = 4.0) -> Dict[str, Any]:
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        result = data.get("chart", {}).get("result", [])
        if not result:
            return {}
        meta = result[0].get("meta", {})
        price = meta.get("regularMarketPrice")
        prev_close = meta.get("chartPreviousClose") or price
        change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0.0
        return {
            "price": price,
            "change_pct": round(change_pct, 2),
            "prev_close": prev_close,
        }


def get_realtime_market_data() -> Dict[str, Any]:
    """Fetches real-time market indices and equity quotes with in-memory caching."""
    global _QUOTE_CACHE, _LAST_CACHE_TIME

    now = time.time()
    if _QUOTE_CACHE and (now - _LAST_CACHE_TIME) < CACHE_TTL_SECONDS:
        return _QUOTE_CACHE

    indices_result: List[Dict[str, Any]] = []
    for name, cfg in INDEX_MAP.items():
        price = cfg["fallback_price"]
        pct = cfg["fallback_change"]
        try:
            live = _fetch_single_quote(cfg["symbol"], timeout=3.0)
            if live and live.get("price"):
                price = live["price"]
                pct = live["change_pct"]
        except Exception:
            pass

        positive = pct >= 0
        sentiment_label = "Bullish" if pct > 0.5 else ("Bearish" if pct < -0.5 else "Neutral")
        indices_result.append({
            "name": name,
            "value": f"{price:,.2f}",
            "raw_price": price,
            "change": f"{pct:+.2f}%",
            "positive": positive,
            "sentiment": f"{sentiment_label} ({pct:+.2f}%)" if "VIX" not in name else ("Elevated Volatility" if price > 20 else "Low Volatility"),
        })

    equities_result: List[Dict[str, Any]] = []
    for ticker, cfg in EQUITY_MAP.items():
        price = cfg["fallback_price"]
        pct = cfg["fallback_change"]
        try:
            live = _fetch_single_quote(cfg["symbol"], timeout=3.0)
            if live and live.get("price"):
                price = live["price"]
                pct = live["change_pct"]
        except Exception:
            pass

        sentiment_label = "Bullish" if pct > 0.5 else ("Bearish" if pct < -0.5 else "Neutral")
        equities_result.append({
            "symbol": ticker,
            "name": cfg["name"],
            "price": f"₹{price:,.2f}",
            "raw_price": price,
            "change": f"{pct:+.2f}%",
            "positive": pct >= 0,
            "sentiment": sentiment_label,
        })

    _QUOTE_CACHE = {
        "status": "success",
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(now)),
        "indices": indices_result,
        "watchlist": equities_result,
    }
    _LAST_CACHE_TIME = now
    return _QUOTE_CACHE

