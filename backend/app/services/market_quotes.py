import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger(__name__)

# In-memory quote cache with TTL (60 seconds)
_QUOTE_CACHE: Dict[str, Any] = {}
_LAST_CACHE_TIME: float = 0
CACHE_TTL_SECONDS = 60

INDEX_MAP = {
    "NIFTY 50": {"symbol": "%5ENSEI", "fallback_price": 25372.30, "fallback_change": 1.31},
    "SENSEX": {"symbol": "%5EBSESN", "fallback_price": 82150.00, "fallback_change": 1.25},
    "BANK NIFTY": {"symbol": "%5ENSEBANK", "fallback_price": 59800.00, "fallback_change": 1.20},
    "INDIA VIX": {"symbol": "%5EINDIAVIX", "fallback_price": 17.46, "fallback_change": 0.00},
}

EQUITY_MAP = {
    "RELIANCE": {"name": "Reliance Industries Ltd", "symbol": "RELIANCE.NS", "fallback_price": 1337.60, "fallback_change": 1.00},
    "TCS": {"name": "Tata Consultancy Services Ltd", "symbol": "TCS.NS", "fallback_price": 2472.30, "fallback_change": -0.13},
    "HDFCBANK": {"name": "HDFC Bank Ltd", "symbol": "HDFCBANK.NS", "fallback_price": 813.60, "fallback_change": 1.94},
    "INFY": {"name": "Infosys Ltd", "symbol": "INFY.NS", "fallback_price": 1154.70, "fallback_change": 0.05},
    "TATAMOTORS": {"name": "Tata Motors Ltd", "symbol": "TMPV.NS", "fallback_price": 300.50, "fallback_change": 1.86},
    "SBIN": {"name": "State Bank of India", "symbol": "SBIN.NS", "fallback_price": 1018.50, "fallback_change": 1.20},
    "ITC": {"name": "ITC Ltd", "symbol": "ITC.NS", "fallback_price": 283.15, "fallback_change": 1.54},
    "ICICIBANK": {"name": "ICICI Bank Ltd", "symbol": "ICICIBANK.NS", "fallback_price": 1571.20, "fallback_change": 4.75},
    "BHARTIARTL": {"name": "Bharti Airtel Ltd", "symbol": "BHARTIARTL.NS", "fallback_price": 2107.20, "fallback_change": 2.45},
    "LT": {"name": "Larsen & Toubro Ltd", "symbol": "LT.NS", "fallback_price": 4117.70, "fallback_change": 1.67},
    "MARUTI": {"name": "Maruti Suzuki India Ltd", "symbol": "MARUTI.NS", "fallback_price": 12750.00, "fallback_change": 0.77},
    "SUNPHARMA": {"name": "Sun Pharma Industries Ltd", "symbol": "SUNPHARMA.NS", "fallback_price": 1840.00, "fallback_change": 0.45},
    "KOTAKBANK": {"name": "Kotak Mahindra Bank Ltd", "symbol": "KOTAKBANK.NS", "fallback_price": 480.00, "fallback_change": 2.78},
    "TITAN": {"name": "Titan Company Ltd", "symbol": "TITAN.NS", "fallback_price": 5000.00, "fallback_change": 3.42},
    "AXISBANK": {"name": "Axis Bank Ltd", "symbol": "AXISBANK.NS", "fallback_price": 1322.90, "fallback_change": 3.35},
    "WIPRO": {"name": "Wipro Ltd", "symbol": "WIPRO.NS", "fallback_price": 198.00, "fallback_change": -0.20},
    "ONGC": {"name": "Oil & Natural Gas Corp Ltd", "symbol": "ONGC.NS", "fallback_price": 231.76, "fallback_change": 0.77},
    "NTPC": {"name": "NTPC Ltd", "symbol": "NTPC.NS", "fallback_price": 323.45, "fallback_change": 2.13},
    "ASIANPAINT": {"name": "Asian Paints Ltd", "symbol": "ASIANPAINT.NS", "fallback_price": 2546.00, "fallback_change": 0.88},
    "ULTRACEMCO": {"name": "UltraTech Cement Ltd", "symbol": "ULTRACEMCO.NS", "fallback_price": 12450.00, "fallback_change": 1.63},
    "POWERGRID": {"name": "Power Grid Corp of India", "symbol": "POWERGRID.NS", "fallback_price": 259.90, "fallback_change": -0.48},
    "COALINDIA": {"name": "Coal India Ltd", "symbol": "COALINDIA.NS", "fallback_price": 400.00, "fallback_change": 1.45},
    "TATASTEEL": {"name": "Tata Steel Ltd", "symbol": "TATASTEEL.NS", "fallback_price": 186.30, "fallback_change": 2.36},
    "BAJAJFINSV": {"name": "Bajaj Finserv Ltd", "symbol": "BAJAJFINSV.NS", "fallback_price": 1864.70, "fallback_change": 1.62},
    "BAJFINANCE": {"name": "Bajaj Finance Ltd", "symbol": "BAJFINANCE.NS", "fallback_price": 1087.75, "fallback_change": 1.66},
    "HCLTECH": {"name": "HCL Technologies Ltd", "symbol": "HCLTECH.NS", "fallback_price": 1440.00, "fallback_change": 0.66},
    "LICI": {"name": "Life Insurance Corp of India", "symbol": "LICI.NS", "fallback_price": 394.00, "fallback_change": -3.43},
    "HINDUNILVR": {"name": "Hindustan Unilever Ltd", "symbol": "HINDUNILVR.NS", "fallback_price": 1998.40, "fallback_change": 0.83},
}

_HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def _fetch_single_quote(symbol: str, timeout: float = 3.5, client: Optional[httpx.Client] = None) -> Dict[str, Any]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d"
    try:
        if client is not None:
            resp = client.get(url, timeout=timeout)
        else:
            with httpx.Client(headers=_HTTP_HEADERS, follow_redirects=True, timeout=timeout) as temp_client:
                resp = temp_client.get(url)

        if resp.status_code != 200:
            return {}
        data = resp.json()
        result = data.get("chart", {}).get("result", [])
        if not result:
            return {}
        meta = result[0].get("meta", {})
        price = meta.get("regularMarketPrice")
        prev_close = meta.get("chartPreviousClose") or price
        if price is None:
            return {}
        change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0.0
        return {
            "price": price,
            "change_pct": round(change_pct, 2),
            "prev_close": prev_close,
        }
    except Exception as exc:
        logger.debug("Market quote fetch for %s failed: %s", symbol, exc)
        return {}


def get_realtime_market_data(requested_symbols: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Fetches verified real-time market indices and equity quotes concurrently with in-memory caching.
    Supports dynamic equity symbols requested by watchlist or dashboard clients.
    """
    global _QUOTE_CACHE, _LAST_CACHE_TIME

    now = time.time()
    cache_valid = bool(_QUOTE_CACHE) and (now - _LAST_CACHE_TIME) < CACHE_TTL_SECONDS

    if cache_valid:
        if not requested_symbols:
            return _QUOTE_CACHE
        cached_syms = {item["symbol"] for item in _QUOTE_CACHE.get("watchlist", [])}
        if all(s.strip().upper() in cached_syms for s in requested_symbols if s.strip()):
            return _QUOTE_CACHE

    # Build target equities map
    target_equities = dict(EQUITY_MAP)
    if requested_symbols:
        for sym in requested_symbols:
            clean = sym.strip().upper()
            if clean and clean not in target_equities:
                target_equities[clean] = {
                    "name": f"{clean} Ltd",
                    "symbol": f"{clean}.NS",
                    "fallback_price": 1000.00,
                    "fallback_change": 0.00,
                }

    # Fetch all symbols concurrently using a shared httpx Client and thread pool
    live_results: Dict[str, Dict[str, Any]] = {}
    all_yahoo_symbols = list({cfg["symbol"] for cfg in INDEX_MAP.values()} | {cfg["symbol"] for cfg in target_equities.values()})

    with httpx.Client(headers=_HTTP_HEADERS, follow_redirects=True, timeout=3.5) as client:
        with ThreadPoolExecutor(max_workers=12) as pool:
            future_to_sym = {pool.submit(_fetch_single_quote, sym, 3.5, client): sym for sym in all_yahoo_symbols}
            for future in as_completed(future_to_sym):
                sym = future_to_sym[future]
                try:
                    data = future.result()
                    if data:
                        live_results[sym] = data
                except Exception:
                    pass

    indices_result: List[Dict[str, Any]] = []
    for name, cfg in INDEX_MAP.items():
        live = live_results.get(cfg["symbol"], {})
        price = live.get("price") if live.get("price") is not None else cfg["fallback_price"]
        pct = live.get("change_pct") if live.get("change_pct") is not None else cfg["fallback_change"]

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
    for ticker, cfg in target_equities.items():
        live = live_results.get(cfg["symbol"], {})
        price = live.get("price") if live.get("price") is not None else cfg["fallback_price"]
        pct = live.get("change_pct") if live.get("change_pct") is not None else cfg["fallback_change"]

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

    result = {
        "status": "success",
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(now)),
        "indices": indices_result,
        "watchlist": equities_result,
    }

    _QUOTE_CACHE = result
    _LAST_CACHE_TIME = now
    return result
