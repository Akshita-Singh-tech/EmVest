import re
import xml.etree.ElementTree as ET
import datetime
import hashlib
from typing import List, Dict, Any, Optional

INDIAN_STOCK_MAPPINGS = {
    "RELIANCE": ["reliance", "ril", "jio", "ambani"],
    "TCS": ["tcs", "tata consultancy"],
    "HDFCBANK": ["hdfc bank", "hdfc"],
    "INFY": ["infosys", "infy"],
    "ICICIBANK": ["icici bank", "icici"],
    "TATAMOTORS": ["tata motors", "jlr"],
    "SBIN": ["state bank of india", "sbi"],
    "SUNPHARMA": ["sun pharma", "sun pharmaceutical"],
    "MARUTI": ["maruti suzuki", "maruti"],
    "ITC": ["itc"],
    "WIPRO": ["wipro"],
    "ONGC": ["ongc", "oil and natural gas"],
    "BPCL": ["bpcl", "bharat petroleum"],
    "BHARTIARTL": ["airtel", "bharti airtel"],
}

SECTOR_KEYWORDS = {
    "Banking & Financial Services": ["bank", "nbfc", "rbi", "repo rate", "lending", "credit", "nim", "monetary policy"],
    "Information Technology": ["it services", "tech", "software", "cloud", "saas", "digital", "ai", "deal pipeline"],
    "Automobile & Auto Ancillary": ["auto", "vehicle", "ev", "electric vehicle", "passenger car", "suv", "oem"],
    "Energy, Oil & Gas": ["crude", "oil", "brent", "gas", "petroleum", "opec", "refining", "omc"],
    "Pharmaceuticals & Healthcare": ["pharma", "fda", "drug", "healthcare", "formulation", "clinical", "eir"],
    "Fast Moving Consumer Goods (FMCG)": ["fmcg", "consumer goods", "retail", "grocery", "consumption", "festive sales"],
}


def clean_html(raw_html: str) -> str:
    """Removes HTML tags and normalizes spaces."""
    if not raw_html:
        return ""
    clean_text = re.sub(r"<[^>]+>", " ", raw_html)
    clean_text = re.sub(r"&[a-zA-Z0-9#]+;", " ", clean_text)
    return " ".join(clean_text.split())


def extract_symbols(text: str) -> List[str]:
    """Finds Indian stock tickers mentioned in the text."""
    lower_text = text.lower()
    matched = []
    for symbol, keywords in INDIAN_STOCK_MAPPINGS.items():
        if any(re.search(r"\b" + re.escape(kw) + r"\b", lower_text) for kw in keywords):
            matched.append(symbol)
    return matched if matched else ["NIFTY"]


def classify_sector(text: str) -> str:
    """Classifies financial news into relevant industry sector."""
    lower_text = text.lower()
    for sector, keywords in SECTOR_KEYWORDS.items():
        if any(re.search(r"\b" + re.escape(kw) + r"\b", lower_text) for kw in keywords):
            return sector
    return "Macro & Multi-Sector"


def parse_rss_xml(xml_content: str, source_name: str) -> List[Dict[str, Any]]:
    """Parses standard RSS 2.0 XML string and extracts normalized news items."""
    articles = []
    try:
        root = ET.fromstring(xml_content)
        # Handle standard RSS channel items
        channel = root.find("channel")
        items = channel.findall("item") if channel is not None else root.findall(".//item")

        for item in items:
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            guid_el = item.find("guid")

            title = clean_html(title_el.text if title_el is not None else "")
            url = link_el.text if link_el is not None else ""
            summary = clean_html(desc_el.text if desc_el is not None else "")

            if not title or not url:
                continue

            external_id = guid_el.text if guid_el is not None and guid_el.text else hashlib.md5(url.encode()).hexdigest()
            symbols = extract_symbols(f"{title} {summary}")
            sector = classify_sector(f"{title} {summary}")

            articles.append({
                "external_id": external_id,
                "title": title,
                "summary": summary,
                "content": summary,
                "source": source_name,
                "url": url,
                "published_at": datetime.datetime.utcnow(),
                "sector": sector,
                "symbols": symbols,
            })
    except Exception:
        # Gracefully handle malformed XML
        pass

    return articles
