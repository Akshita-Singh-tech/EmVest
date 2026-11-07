import re
import html
import ssl
import urllib.request
import xml.etree.ElementTree as ET
import datetime
import hashlib
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional

INDIAN_STOCK_MAPPINGS = {
    # Banking & Financial Services
    "HDFCBANK": ["hdfc bank", "hdfc", "hdfcbank"],
    "ICICIBANK": ["icici bank", "icici", "icicibank"],
    "SBIN": ["state bank of india", "sbi", "sbin"],
    "KOTAKBANK": ["kotak mahindra bank", "kotak bank", "kotak"],
    "AXISBANK": ["axis bank", "axisbank"],
    "INDUSINDBK": ["indusind bank", "indusind"],
    "BANKBARODA": ["bank of baroda", "bob"],
    "PNB": ["punjab national bank", "pnb"],
    "BAJFINANCE": ["bajaj finance", "bajaj finserv", "bajfinance"],
    "JIOFIN": ["jio financial", "jio financial services", "jfs"],
    "LIC": ["lic", "life insurance corporation"],

    # Information Technology
    "TCS": ["tata consultancy services", "tcs"],
    "INFY": ["infosys", "infy"],
    "WIPRO": ["wipro"],
    "HCLTECH": ["hcl tech", "hcl technologies", "hcltech"],
    "TECHM": ["tech mahindra", "techm"],
    "LTIM": ["ltimindtree", "ltim"],
    "PERSISTENT": ["persistent systems", "persistent"],
    "COFORGE": ["coforge"],

    # Automobile & Auto Ancillary
    "TATAMOTORS": ["tata motors", "tatamotors", "jlr", "jaguar land rover"],
    "MARUTI": ["maruti suzuki", "maruti"],
    "M&M": ["mahindra & mahindra", "mahindra and mahindra", "m&m", "mahindra"],
    "BAJAJ-AUTO": ["bajaj auto"],
    "HEROMOTOCO": ["hero motocorp", "hero moto"],
    "EICHERMOT": ["eicher motors", "royal enfield"],
    "TVSMOTOR": ["tvs motor", "tvs"],

    # Energy, Oil & Gas & Utilities
    "RELIANCE": ["reliance industries", "reliance", "ril", "mukesh ambani", "jio"],
    "ONGC": ["oil and natural gas", "ongc"],
    "BPCL": ["bharat petroleum", "bpcl"],
    "IOC": ["indian oil", "iocl"],
    "NTPC": ["ntpc"],
    "POWERGRID": ["power grid", "powergrid", "pgcil"],
    "ADANIGREEN": ["adani green"],
    "ADANIPOWER": ["adani power"],
    "COALINDIA": ["coal india", "coalindia"],

    # Pharmaceuticals & Healthcare
    "SUNPHARMA": ["sun pharma", "sun pharmaceutical"],
    "DRREDDY": ["dr reddy", "dr. reddy's", "drreddys"],
    "CIPLA": ["cipla"],
    "DIVISLAB": ["divi's laboratories", "divis lab", "divislab"],
    "APOLLOHOSP": ["apollo hospitals", "apollo hospital"],
    "LUPIN": ["lupin"],
    "BIOCON": ["biocon"],

    # Fast Moving Consumer Goods (FMCG)
    "ITC": ["itc", "itc limited"],
    "HINDUNILVR": ["hindustan unilever", "hul", "hindunilvr"],
    "NESTLEIND": ["nestle india", "nestle"],
    "BRITANNIA": ["britannia industries", "britannia"],
    "TATACONSUM": ["tata consumer", "tata consumer products"],
    "DABUR": ["dabur"],
    "MARICO": ["marico"],

    # Metals, Mining & Materials
    "TATASTEEL": ["tata steel"],
    "JSWSTEEL": ["jsw steel", "jsw"],
    "HINDALCO": ["hindalco", "novelis"],
    "VEDL": ["vedanta", "vedl"],

    # Infrastructure, Telecom & Capital Goods
    "LT": ["larsen & toubro", "l&t", "larsen and toubro"],
    "BHARTIARTL": ["bharti airtel", "airtel"],
    "ULTRACEMCO": ["ultratech cement", "ultratech"],
    "GRASIM": ["grasim"],
    "ADANIPORTS": ["adani ports", "adani port", "special economic zone"],
    "TITAN": ["titan company", "titan"],
}

SECTOR_KEYWORDS = {
    "Banking & Financial Services": [
        "bank", "banking", "nbfc", "rbi", "repo rate", "lending", "credit", "nim",
        "monetary policy", "deposit", "advances", "fintech", "insurance", "vnb", "mutual fund", "etf", "sebi"
    ],
    "Information Technology": [
        "it services", "tech", "software", "cloud", "saas", "digital", "ai", "artificial intelligence",
        "deal pipeline", "tcv", "h-1b", "nasdaq", "it sector", "infosys", "tcs", "wipro"
    ],
    "Automobile & Auto Ancillary": [
        "auto", "automobile", "vehicle", "ev", "electric vehicle", "passenger car", "suv",
        "oem", "two-wheeler", "commercial vehicle", "maruti", "tata motors", "mahindra"
    ],
    "Energy, Oil & Gas": [
        "crude", "oil", "brent", "gas", "petroleum", "opec", "refining", "omc", "power",
        "renewable", "solar", "fuel", "diesel", "petrol", "reliance"
    ],
    "Pharmaceuticals & Healthcare": [
        "pharma", "pharmaceutical", "fda", "drug", "healthcare", "formulation", "clinical",
        "eir", "usfda", "hospital", "medicine", "biotech"
    ],
    "Fast Moving Consumer Goods (FMCG)": [
        "fmcg", "consumer goods", "retail", "grocery", "consumption", "festive sales",
        "rural demand", "staples", "itc", "unilever", "nestle"
    ],
    "Metals & Mining": [
        "steel", "iron ore", "copper", "aluminum", "metal", "mining", "coal", "coking coal", "smelter"
    ],
    "Infrastructure & Capital Goods": [
        "infrastructure", "capex", "railway", "defense", "order book", "construction", "cement", "ports", "l&t"
    ],
    "Telecommunications": [
        "telecom", "5g", "spectrum", "arpu", "airtel", "jio", "vodafone", "telecom tariff"
    ],
}

RSS_FEED_REGISTRY = [
    {
        "source": "Economic Times",
        "url": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
        "default_sector": "Automobile & Auto Ancillary",
    },
    {
        "source": "Economic Times",
        "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "default_sector": "Macro & Multi-Sector",
    },
    {
        "source": "LiveMint",
        "url": "https://www.livemint.com/rss/markets",
        "default_sector": "Banking & Financial Services",
    },
    {
        "source": "LiveMint",
        "url": "https://www.livemint.com/rss/companies",
        "default_sector": "Information Technology",
    },
    {
        "source": "Moneycontrol",
        "url": "https://www.moneycontrol.com/rss/business.xml",
        "default_sector": "Energy, Oil & Gas",
    },
    {
        "source": "Moneycontrol",
        "url": "https://www.moneycontrol.com/rss/marketreports.xml",
        "default_sector": "Banking & Financial Services",
    },
]


def clean_html(raw_html: str) -> str:
    """Removes HTML tags and normalizes entities/whitespace."""
    if not raw_html:
        return ""
    # Unescape HTML entities (&amp;, &#39;, &quot;, etc.)
    text = html.unescape(raw_html)
    # Remove HTML tags including <img>, <script>, <a>, etc.
    text = re.sub(r"<[^>]+>", " ", text)
    # Normalize multiple whitespace chars into a single space
    return " ".join(text.split())


def extract_symbols(text: str) -> List[str]:
    """Finds Indian stock tickers mentioned in the headline or text body."""
    lower_text = text.lower()
    matched = []
    for symbol, keywords in INDIAN_STOCK_MAPPINGS.items():
        if any(re.search(r"\b" + re.escape(kw) + r"\b", lower_text) for kw in keywords):
            matched.append(symbol)
    return matched if matched else ["NIFTY"]


def classify_sector(text: str, fallback_sector: str = "Macro & Multi-Sector") -> str:
    """Classifies financial news into relevant industry sector based on content keywords."""
    lower_text = text.lower()
    scores = {}
    for sector, keywords in SECTOR_KEYWORDS.items():
        score = sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", lower_text))
        if score > 0:
            scores[sector] = score

    if scores:
        # Return sector with highest keyword match
        return max(scores.items(), key=lambda x: x[1])[0]
    return fallback_sector


def parse_pub_date(pub_date_str: Optional[str]) -> datetime.datetime:
    """Safely parses RFC 2822 or ISO date strings into a timezone-naive UTC datetime."""
    if not pub_date_str:
        return datetime.datetime.utcnow()
    try:
        dt = parsedate_to_datetime(pub_date_str.strip())
        if dt.tzinfo:
            return dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return dt
    except Exception:
        pass

    try:
        # Try ISO 8601 parsing fallback
        dt = datetime.datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
        if dt.tzinfo:
            return dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return dt
    except Exception:
        return datetime.datetime.utcnow()


def parse_rss_xml(xml_content: str, source_name: str, default_sector: str = "Macro & Multi-Sector") -> List[Dict[str, Any]]:
    """Parses standard RSS 2.0 XML string and extracts normalized news items."""
    articles = []
    try:
        # Clean invalid XML control characters
        clean_xml = re.sub(
            r"[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]",
            "",
            xml_content
        )
        root = ET.fromstring(clean_xml)
        items = root.findall(".//item")

        for item in items:
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            guid_el = item.find("guid")
            pub_date_el = item.find("pubDate")

            title = clean_html(title_el.text if title_el is not None and title_el.text else "")
            url = link_el.text.strip() if link_el is not None and link_el.text else ""
            summary = clean_html(desc_el.text if desc_el is not None and desc_el.text else "")
            pub_date_str = pub_date_el.text if pub_date_el is not None and pub_date_el.text else None

            if not title or not url:
                continue

            # Generate unique external ID
            guid_text = guid_el.text.strip() if guid_el is not None and guid_el.text else None
            external_id = guid_text if guid_text else hashlib.md5(url.encode()).hexdigest()

            full_text = f"{title} {summary}"
            symbols = extract_symbols(full_text)
            sector = classify_sector(full_text, fallback_sector=default_sector)
            published_at = parse_pub_date(pub_date_str)

            articles.append({
                "external_id": external_id,
                "title": title,
                "summary": summary if summary else title,
                "content": summary if summary else title,
                "source": source_name,
                "url": url,
                "published_at": published_at,
                "sector": sector,
                "symbols": symbols,
            })
    except Exception:
        # Gracefully tolerate XML format anomalies
        pass

    return articles


def fetch_all_rss_feeds(timeout_seconds: int = 8) -> List[Dict[str, Any]]:
    """
    Actively fetches live RSS feeds from major Indian financial portals:
    Economic Times, LiveMint, and Moneycontrol.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }

    all_articles = []
    seen_urls = set()

    for feed_info in RSS_FEED_REGISTRY:
        source = feed_info["source"]
        url = feed_info["url"]
        default_sec = feed_info.get("default_sector", "Macro & Multi-Sector")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout_seconds, context=ctx) as resp:
                xml_raw = resp.read().decode("utf-8", errors="replace")
                parsed = parse_rss_xml(xml_raw, source_name=source, default_sector=default_sec)
                for item in parsed:
                    if item["url"] not in seen_urls:
                        seen_urls.add(item["url"])
                        all_articles.append(item)
        except Exception:
            # Continue to next feed if one times out or errors
            continue

    return all_articles
