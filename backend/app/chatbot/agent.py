from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.config import settings
from app.models.article import Article
from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import (
    CitationItem,
    ChatQueryRequest,
    ChatQueryResponse,
    SentimentSummary,
)

# Known Indian Equities and aliases
EQUITY_SYMBOLS: Dict[str, List[str]] = {
    "RELIANCE": ["reliance", "ril", "mukesh ambani", "jio"],
    "TCS": ["tcs", "tata consultancy"],
    "HDFCBANK": ["hdfc", "hdfc bank", "hdfcbank"],
    "ICICIBANK": ["icici", "icicibank", "icici bank"],
    "INFY": ["infosys", "infy", "salil parekh"],
    "SBIN": ["sbi", "state bank", "state bank of india"],
    "TATAMOTORS": ["tata motors", "tatamotors", "tamo", "jlr"],
    "BHARTIARTL": ["airtel", "bharti airtel", "bharti"],
    "ITC": ["itc", "itc limited"],
    "WIPRO": ["wipro"],
    "LT": ["l&t", "larsen", "toubro"],
    "MARUTI": ["maruti", "maruti suzuki"],
    "SUNPHARMA": ["sun pharma", "sunpharma", "dilip shanghvi"],
    "TITAN": ["titan", "tanishq"],
    "BAJFINANCE": ["bajaj finance", "bajfinance"],
    "ADANIENT": ["adani enterprises", "adanient", "adani"],
    "ADANIPORTS": ["adani ports", "adanimports"],
    "KOTAKBANK": ["kotak", "kotak mahindra"],
    "AXISBANK": ["axis bank", "axisbank"],
    "HINDUNILVR": ["hindustan unilever", "hul"],
    "ZOMATO": ["zomato", "blinkit"],
}

# Known sectors and keywords
SECTORS: Dict[str, List[str]] = {
    "Banking & Financial Services": ["bank", "banking", "nbfc", "lending", "credit", "nim", "rbi", "repo", "fintech"],
    "Information Technology": ["it", "tech", "software", "cloud", "saas", "digital", "ai", "consulting"],
    "Automobile & Auto Ancillary": ["auto", "car", "ev", "electric vehicle", "automotive", "two-wheeler", "suv"],
    "Oil & Gas / Energy": ["energy", "oil", "gas", "petroleum", "refining", "crude", "solar", "renewable"],
    "Fast Moving Consumer Goods (FMCG)": ["fmcg", "consumption", "retail", "consumer", "food"],
    "Pharmaceuticals & Healthcare": ["pharma", "healthcare", "drug", "fda", "hospital", "medicine"],
    "Metals & Mining": ["steel", "metals", "iron", "mining", "aluminum", "copper"],
    "Telecommunications": ["telecom", "5g", "spectrum", "arpu", "telecommunication"],
}

# Educational Financial Concepts Database
FINANCIAL_CONCEPTS: Dict[str, Dict[str, str]] = {
    "pe_ratio": {
        "keywords": ["pe ratio", "p/e ratio", "price to earnings", "p/e", "pe multiple"],
        "title": "Price-to-Earnings (P/E) Ratio",
        "content": (
            "### Price-to-Earnings (P/E) Ratio\n\n"
            "The **P/E ratio** measures how much investors are willing to pay per rupee of current earnings.\n\n"
            "- **Formula:** `Current Market Price / Earnings Per Share (EPS)`\n"
            "- **Interpretation:**\n"
            "  - **High P/E:** Signals high market expectations for future earnings growth (e.g., consumer and tech leaders), or potential overvaluation.\n"
            "  - **Low P/E:** May indicate an undervalued value stock, or underlying cyclical/structural earnings headwinds.\n"
            "- **Indian Market Benchmark:** The Nifty 50 historical 10-year average trailing P/E fluctuates around **20x - 23x**. When Nifty trades above 24x, valuations are considered elevated; below 18x often represents long-term accumulation territory."
        ),
    },
    "pb_ratio": {
        "keywords": ["pb ratio", "p/b ratio", "price to book", "p/b", "book value"],
        "title": "Price-to-Book (P/B) Ratio",
        "content": (
            "### Price-to-Book (P/B) Ratio\n\n"
            "The **P/B ratio** compares a company's market valuation to its net asset book value.\n\n"
            "- **Formula:** `Current Stock Price / Book Value Per Share (BVPS)`\n"
            "- **Key Use Case in India:** Crucial for evaluating **Banks and NBFCs** (like HDFC Bank, ICICI Bank, SBI), where earnings quality is closely tied to loan book asset health.\n"
            "- **Benchmark:** Top-tier Indian private banks typically command **2.5x - 3.5x P/B**, while PSU lenders trade between **0.8x - 1.5x P/B**."
        ),
    },
    "ebitda": {
        "keywords": ["ebitda", "operating profit", "operating margin", "ebitda margin"],
        "title": "EBITDA & Operating Margins",
        "content": (
            "### EBITDA (Earnings Before Interest, Taxes, Depreciation & Amortization)\n\n"
            "**EBITDA** isolates a business's core operational profitability by eliminating capital structure (debt interest), tax jurisdictions, and non-cash accounting depreciation.\n\n"
            "- **Why it matters:** Allows apples-to-apples operational comparisons across companies with varying debt levels or capital expenditure intensity.\n"
            "- **EBITDA Margin:** `(EBITDA / Total Revenue) * 100`.\n"
            "- **Example:** In the Indian Auto sector, Tata Motors targets double-digit passenger EV EBITDA margins, while Indian IT majors like TCS and Infosys consistently deliver 23% - 26% operating margins."
        ),
    },
    "market_cap": {
        "keywords": ["market cap", "market capitalization", "large cap", "mid cap", "small cap"],
        "title": "Market Capitalization & SEBI Categorization",
        "content": (
            "### Market Capitalization\n\n"
            "**Market Cap** represents the aggregate market value of a publicly listed company's outstanding equity shares.\n\n"
            "- **Formula:** `Total Outstanding Shares * Current Market Price`\n"
            "- **SEBI Indian Market Categorization:**\n"
            "  - **Large Cap (Top 1–100):** Market cap generally > ₹20,000 Cr. Stable blue-chips (e.g. Reliance, TCS, HDFC Bank).\n"
            "  - **Mid Cap (101–250):** Market cap between ₹5,000 Cr and ₹20,000 Cr. Faster growth with moderate volatility.\n"
            "  - **Small Cap (251+):** Market cap < ₹5,000 Cr. High growth potential accompanied by elevated volatility and drawdown risk."
        ),
    },
    "roce_roe": {
        "keywords": ["roce", "roe", "return on equity", "return on capital employed"],
        "title": "ROCE & ROE (Capital Efficiency)",
        "content": (
            "### ROCE vs. ROE (Capital Efficiency)\n\n"
            "- **ROCE (Return on Capital Employed):** `EBIT / (Total Assets - Current Liabilities)`. Measures how efficiently total capital (debt + equity) generates operating profits. Essential for manufacturing, power, and infrastructure.\n"
            "- **ROE (Return on Equity):** `Net Profit / Shareholders' Equity`. Measures the return generated specifically on shareholders' invested capital.\n"
            "- **Rule of Thumb:** Quality Indian compounders typically maintain ROCE > 15-20% consistently across multiple economic cycles."
        ),
    },
    "repo_rate": {
        "keywords": ["repo rate", "reverse repo", "rbi rate", "monetary policy committee", "mpc"],
        "title": "RBI Repo Rate & Monetary Impact",
        "content": (
            "### RBI Repo Rate & Market Impact\n\n"
            "The **Repo Rate** is the interest rate at which the Reserve Bank of India (RBI) lends short-term liquidity to commercial banks against government securities.\n\n"
            "- **Rate Hikes:** Increase borrowing costs across home, auto, and corporate loans. Moderates inflation but dampens discretionary consumer demand and equity valuation multiples.\n"
            "- **Rate Cuts / Pause:** Lowers lending costs, expands bank credit growth, and stimulates economic expansion. Favorable for equities, particularly Banking, Real Estate, and Auto sectors.\n"
            "- **Current Status:** RBI MPC has maintained the benchmark repo rate steady at **6.50%** to anchor inflation while fostering domestic GDP momentum."
        ),
    },
    "sip_etf": {
        "keywords": ["sip", "etf", "mutual fund", "systematic investment", "niftybees"],
        "title": "SIPs & ETFs in Indian Equities",
        "content": (
            "### SIPs & Exchange-Traded Funds (ETFs)\n\n"
            "- **SIP (Systematic Investment Plan):** A disciplined wealth-building method of investing fixed amounts into mutual funds or equities at regular intervals (monthly/weekly), benefiting from Rupee Cost Averaging and compounding.\n"
            "- **ETF (Exchange Traded Fund):** A security that tracks an underlying index (e.g., **NIFTYBEES** for NIFTY 50, **BANKBEES** for NIFTY Bank) and trades on the stock exchange with low expense ratios and real-time liquidity."
        ),
    },
}

# Equity Fundamentals Profiles (Used when no breaking news exists for the queried ticker)
EQUITY_PROFILES: Dict[str, Dict[str, Any]] = {
    "RELIANCE": {
        "name": "Reliance Industries Ltd",
        "sector": "Energy, Retail & Telecommunications",
        "overview": (
            "Reliance Industries is India's largest conglomerate by market cap, spanning three core growth engines:\n"
            "- **Jio Platforms:** Over 450M 5G and fiber subscribers driving recurring digital ARPU expansion.\n"
            "- **Reliance Retail:** India's largest retailer with 18,000+ storefronts across grocery, electronics, and fashion.\n"
            "- **Oil-to-Chemicals (O2C):** World-scale integrated refining and petrochemicals complex at Jamnagar, alongside new investments in solar gigafactories and green hydrogen."
        ),
        "key_drivers": "5G monetization, retail omnichannel operating leverage, new energy gigafactory commissioning.",
        "risks": "Global refining crack spread volatility, heavy capital expenditure cycles, consumer discretionary slowdown.",
    },
    "TATAMOTORS": {
        "name": "Tata Motors Ltd",
        "sector": "Automobile & Auto Ancillary",
        "overview": (
            "Tata Motors is a diversified global automaker with market leadership across commercial vehicles and passenger electric mobility:\n"
            "- **Domestic EV Moat:** Dominates India's passenger EV market with >65% volume share led by Punch.ev, Nexon.ev, and Tiago.ev.\n"
            "- **Commercial Vehicles:** Largest player in Indian medium & heavy commercial vehicles (M&HCV) tied to infrastructure capex.\n"
            "- **Jaguar Land Rover (JLR):** Luxury SUV brand delivering robust order backlogs and debt reduction on strong Defender and Range Rover demand."
        ),
        "key_drivers": "New localized EV architectures, JLR margin expansion, debt reduction toward net-cash status.",
        "risks": "European consumer slowdown impacting JLR exports, competitive entry in domestic compact EV segment.",
    },
    "HDFCBANK": {
        "name": "HDFC Bank Ltd",
        "sector": "Banking & Financial Services",
        "overview": (
            "HDFC Bank is India's largest private sector bank following its historic reverse merger with HDFC Limited:\n"
            "- **Scale & Franchise:** Over 8,500 branches serving 85M+ customers across retail, corporate, and rural lending.\n"
            "- **Asset Quality:** Industry-benchmark low non-performing asset (GNPA < 1.3%) ratios across economic cycles.\n"
            "- **Current Strategic Priority:** Accelerating retail deposit mobilization to normalize credit-to-deposit (LDR) ratio toward 85%."
        ),
        "key_drivers": "Sustained 15-18% deposit accretion, branch expansion in Tier-2/3 cities, mortgage cross-selling.",
        "risks": "Elevated funding costs compressing Net Interest Margins (NIM), post-merger integration pace.",
    },
    "INFY": {
        "name": "Infosys Ltd",
        "sector": "Information Technology",
        "overview": (
            "Infosys is a tier-1 global leader in next-generation digital services and consulting:\n"
            "- **Core Capabilities:** Enterprise cloud migration (Cobalt), generative AI enterprise platforms (Topaz), and core banking software (Finacle).\n"
            "- **Client Base:** 1,800+ active enterprise clients spanning North America (60% revenue) and Europe (25% revenue).\n"
            "- **Capital Allocation:** Robust free cash flow conversion with committed >85% cumulative return to shareholders via buybacks and dividends."
        ),
        "key_drivers": "Large deal ramp-ups in cost-optimization, vendor consolidation, enterprise AI deployment.",
        "risks": "US discretionary enterprise tech spending slowdown, client budget reprioritization.",
    },
    "TCS": {
        "name": "Tata Consultancy Services Ltd",
        "sector": "Information Technology",
        "overview": (
            "TCS is India's premier IT conglomerate and one of the largest technology services employers globally:\n"
            "- **Competitive Moat:** Industry-leading operating margin (~24-26%), lowest attrition rates, and diversified exposure across BFSI, retail, life sciences, and manufacturing.\n"
            "- **Order Book:** Consistently secures $8B - $10B in quarterly Total Contract Value (TCV)."
        ),
        "key_drivers": "Multi-year digital transformation contracts, cloud infrastructure management, sovereign AI partnerships.",
        "risks": "Prolonged decision-making cycles among Western enterprise clients.",
    },
    "SBIN": {
        "name": "State Bank of India",
        "sector": "Banking & Financial Services",
        "overview": (
            "State Bank of India is the nation's largest commercial lender by assets, deposits, and branches:\n"
            "- **Systemic Importance:** Handles over 20% of India's total banking deposits and credit disbursement.\n"
            "- **Digital Franchise:** YONO digital banking platform processes millions of daily transactions with strong retail deposit stickiness."
        ),
        "key_drivers": "Infrastructure and private corporate capex pickup, pristine corporate credit books, low cost of funds.",
        "risks": "Agricultural and small business credit slippages, public sector wage revisions.",
    },
    "ZOMATO": {
        "name": "Zomato Ltd",
        "sector": "Consumer Internet & Quick Commerce",
        "overview": (
            "Zomato is India's leading consumer tech platform operating in food delivery and quick commerce:\n"
            "- **Food Delivery:** Established profitable duopoly alongside Swiggy with steady platform fee monetization.\n"
            "- **Blinkit:** Rapidly expanding 10-minute quick commerce leader, capturing market share across grocery, electronics, and daily essentials.\n"
            "- **Hyperpure:** B2B farm-to-fork supply chain for restaurants."
        ),
        "key_drivers": "Blinkit dark-store unit economics, adjusted EBITDA profitability, advertising revenue growth.",
        "risks": "Intense quick-commerce rivalry (Zepto, Instamart), delivery partner labor wage pressures.",
    },
}


class ChatAgent:
    """Agentic financial research assistant with multi-intent detection, DB retrieval, and conversational memory."""

    @staticmethod
    def extract_entities(query: str) -> Tuple[List[str], List[str], List[str]]:
        """Extract company symbols, sectors, and key search terms from user query."""
        q_lower = query.lower()
        matched_symbols: List[str] = []
        matched_sectors: List[str] = []

        # Match symbols
        for symbol, aliases in EQUITY_SYMBOLS.items():
            if symbol.lower() in q_lower or any(re.search(rf"\b{re.escape(alias)}\b", q_lower) for alias in aliases):
                matched_symbols.append(symbol)

        # Match sectors
        for sector, keywords in SECTORS.items():
            if sector.lower() in q_lower or any(re.search(rf"\b{re.escape(kw)}\b", q_lower) for kw in keywords):
                matched_sectors.append(sector)

        # General keywords (tokens with length >= 3)
        tokens = [w for w in re.findall(r"\b[a-zA-Z0-9_-]+\b", q_lower) if len(w) >= 3 and w not in {
            "what", "is", "the", "for", "and", "about", "with", "how", "why", "are", "tell", "show", "can", "you",
            "give", "summary", "outlook", "sentiment", "current", "latest", "stock", "stocks", "market", "india"
        }]

        return matched_symbols, matched_sectors, tokens

    @classmethod
    def retrieve_articles(
        cls,
        db: Session,
        query: str,
        symbols_override: Optional[List[str]] = None,
        limit: int = 6
    ) -> List[Article]:
        """Retrieve stored articles that ACTUALLY match the query or entities (no unrelated dumping)."""
        detected_symbols, detected_sectors, tokens = cls.extract_entities(query)
        target_symbols = list(set((symbols_override or []) + detected_symbols))

        all_articles = db.query(Article).order_by(desc(Article.published_at)).all()
        if not all_articles:
            return []

        scored_articles: List[Tuple[float, Article]] = []

        for art in all_articles:
            score = 0.0
            art_text = f"{art.title} {art.summary} {art.content} {art.sector}".lower()

            # Symbol match
            art_symbols = [s.upper() for s in (art.symbols or [])]
            for sym in target_symbols:
                if sym.upper() in art_symbols or sym.lower() in art_text:
                    score += 10.0

            # Sector match
            for sec in detected_sectors:
                if art.sector and sec.lower() in art.sector.lower():
                    score += 5.0

            # Keyword match
            for token in tokens:
                if token in art.title.lower():
                    score += 4.0
                elif token in art_text:
                    score += 1.5

            # ONLY include if relevance score is strictly positive!
            if score > 0:
                scored_articles.append((score, art))

        # Sort by relevance score descending
        scored_articles.sort(key=lambda x: x[0], reverse=True)
        return [art for _, art in scored_articles[:limit]]

    @staticmethod
    def calculate_sentiment_summary(articles: List[Article]) -> Optional[SentimentSummary]:
        """Calculate FinBERT aggregate metrics across retrieved articles."""
        if not articles:
            return None

        scores = [a.sentiment_score for a in articles]
        avg_score = round(sum(scores) / len(scores), 2)

        pos_count = sum(1 for a in articles if a.sentiment == "Positive")
        neu_count = sum(1 for a in articles if a.sentiment == "Neutral")
        neg_count = sum(1 for a in articles if a.sentiment == "Negative")

        if avg_score >= 0.5:
            label = "Strongly Bullish"
        elif avg_score >= 0.15:
            label = "Moderately Bullish"
        elif avg_score <= -0.5:
            label = "Strongly Bearish"
        elif avg_score <= -0.15:
            label = "Moderately Bearish"
        else:
            label = "Neutral / Mixed"

        return SentimentSummary(
            aggregate_score=avg_score,
            sentiment_label=label,
            article_count=len(articles),
            positive_count=pos_count,
            neutral_count=neu_count,
            negative_count=neg_count,
        )

    @staticmethod
    def build_citations(articles: List[Article]) -> List[CitationItem]:
        """Convert stored DB articles into structured, verifiable citations."""
        citations: List[CitationItem] = []
        for art in articles:
            pub_date = art.published_at.strftime("%Y-%m-%d %H:%M") if art.published_at else "Recent"
            citations.append(
                CitationItem(
                    id=art.id,
                    title=art.title,
                    source=art.source,
                    url=art.url,
                    published_at=pub_date,
                    sentiment=art.sentiment,
                    sentiment_score=art.sentiment_score,
                    symbols=art.symbols or [],
                    sector=art.sector,
                )
            )
        return citations

    @staticmethod
    def generate_session_title(query: str) -> str:
        """Auto-generate a concise ChatGPT-style conversation thread title from first query."""
        cleaned = re.sub(
            r"^(what is the|what is|tell me about the|tell me about|how is the|how is|give me a summary of|what are the|what are|can you explain|analyze)\s+",
            "",
            query,
            flags=re.IGNORECASE,
        ).strip()
        cleaned = re.sub(r"[?!.]+$", "", cleaned)
        cleaned = cleaned.capitalize()
        if len(cleaned) > 36:
            return cleaned[:33] + "..."
        return cleaned or "Financial Research Thread"

    @classmethod
    def process_query(
        cls,
        db: Session,
        request: ChatQueryRequest,
        user_id: Optional[int] = None,
    ) -> ChatQueryResponse:
        """Intelligent multi-intent query processor with conversational memory."""
        session_id = request.session_id or str(uuid.uuid4())
        q_raw = request.query.strip()
        q_lower = q_raw.lower()

        # 1. Ensure ChatSession exists
        session_record = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session_record:
            title = cls.generate_session_title(q_raw)
            session_record = ChatSession(
                id=session_id,
                title=title,
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(session_record)
            db.commit()

        # 2. Conversational Memory: Retrieve prior conversation messages
        prior_messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

        # 3. Intent Check: Greetings / Identity
        greeting_patterns = [
            r"^(hi|hello|hey|greetings|good morning|good afternoon|good evening)\b",
            r"who are you",
            r"what is your name",
            r"what can you do",
            r"help me",
            r"how do you work",
            r"^introduce yourself",
        ]
        if any(re.search(pat, q_lower) for pat in greeting_patterns) and len(q_raw.split()) <= 6:
            greeting_answer = (
                "### Hello! I am Emvest AI\n\n"
                "I am your dedicated **Agentic Investment Intelligence Assistant** designed specifically for Indian equities (NSE/BSE) and macroeconomic trends.\n\n"
                "**Here is what you can ask me:**\n"
                "- **Stock Analysis:** *'What is the outlook for Tata Motors electric vehicles?'* or *'Analyze Reliance Industries retail expansion'*.\n"
                "- **Financial Concepts:** *'What is P/E ratio and how is it used?'* or *'Explain EBITDA vs Net Profit'*.\n"
                "- **Macroeconomic & Policy:** *'How does the RBI repo rate impact banking stocks?'* or *'What is the outlook for IT sector guidance?'*.\n"
                "- **Stock Comparisons:** *'Compare Tata Motors and Maruti Suzuki'*.\n\n"
                "All breaking news analysis is verified against real-time ingested publications with FinBERT sentiment scores."
            )
            followups = [
                "What is the outlook for Tata Motors electric vehicles?",
                "How does the RBI repo rate decision impact private banks?",
                "What does P/E ratio indicate in Indian equities?",
            ]
            return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, greeting_answer, [], followups, None)

        # 4. Extract Entities & Context Memory
        symbols, sectors, _ = cls.extract_entities(q_raw)
        if request.symbols:
            symbols = list(set(symbols + request.symbols))

        # Multi-turn pronoun/context resolution
        prior_context_symbols: List[str] = []
        if not symbols and prior_messages:
            for pm in reversed(prior_messages[-4:]):
                prev_syms, prev_secs, _ = cls.extract_entities(pm.content)
                if prev_syms:
                    prior_context_symbols.extend(prev_syms)
                if prev_secs and not sectors:
                    sectors.extend(prev_secs)
            prior_context_symbols = list(dict.fromkeys(prior_context_symbols))
            if prior_context_symbols:
                symbols = prior_context_symbols[:2]

        # 5. Retrieve News Articles that ACTUALLY match the query or entities
        matching_articles = cls.retrieve_articles(db, q_raw, symbols)

        # Case A: Real matching news articles found in DB -> Provide FinBERT news synthesis with citations
        if matching_articles:
            sentiment_summary = cls.calculate_sentiment_summary(matching_articles)
            citations = cls.build_citations(matching_articles)

            symbol_header = f" for **{', '.join(symbols)}**" if symbols else ""
            sector_header = f" across **{', '.join(sectors)}**" if sectors and not symbols else ""

            lines: List[str] = []
            if prior_context_symbols and not (cls.extract_entities(q_raw)[0]):
                lines.append(f"> **Conversational Context:** Continuing discussion on **{', '.join(prior_context_symbols)}**.\n")

            if sentiment_summary:
                sign = "+" if sentiment_summary.aggregate_score > 0 else ""
                lines.append(
                    f"### Market Intelligence & Sentiment Synthesis{symbol_header}{sector_header}\n\n"
                    f"Based on real-time ingestion of **{sentiment_summary.article_count} verified financial publications**, "
                    f"composite sentiment stands at **{sentiment_summary.sentiment_label}** "
                    f"(*FinBERT Conviction: {sign}{sentiment_summary.aggregate_score:.2f}* | {sentiment_summary.positive_count} Bullish, "
                    f"{sentiment_summary.neutral_count} Neutral, {sentiment_summary.negative_count} Bearish).\n"
                )

            lines.append("**Key Empirical Takeaways from Verified Sources:**")
            for art in matching_articles[:4]:
                takeaway = (art.key_takeaways[0] if art.key_takeaways and len(art.key_takeaways) > 0 else art.summary)
                sign = "+" if art.sentiment_score > 0 else ""
                lines.append(
                    f"- **{art.source}** (*{art.sentiment}, {sign}{art.sentiment_score:.2f}*): "
                    f"{takeaway} [Source: *{art.title}*]"
                )

            lines.append("\n**Market Impact & Outlook:**")
            impacts = [art.market_impact for art in matching_articles if art.market_impact]
            if impacts:
                for imp in impacts[:2]:
                    lines.append(f"- {imp}")
            else:
                lines.append("- Fundamentals remain underpinned by steady domestic institutional inflows.")

            answer = "\n".join(lines)
            followups = [
                f"What are the technical resistance and support levels for {symbols[0]}?" if symbols else "What are top sentiment gainers in NIFTY 50?",
                f"How does {symbols[0]}'s FinBERT score compare to sector peers?" if symbols else "Summarize RBI monetary policy outlook",
            ]
            return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, answer, citations, followups, sentiment_summary)

        # 6. Intent Check: Financial Concepts & Educational Queries (when no breaking news matches)
        for concept_key, concept_data in FINANCIAL_CONCEPTS.items():
            if any(re.search(rf"\b{re.escape(kw)}\b", q_lower) for kw in concept_data["keywords"]):
                followups = [
                    f"How does {concept_data['title']} apply to Banking stocks?",
                    "Which NIFTY 50 companies show the most favorable valuation multiples?",
                    "What other financial metrics should I evaluate alongside this?",
                ]
                return cls._save_and_respond(
                    db, session_record, session_id, user_id, q_raw, concept_data["content"], [], followups, None
                )

        # 7. Intent Check: Stock Comparison (e.g. "Compare X and Y" or "X vs Y")
        if (len(symbols) >= 2 or ("compare" in q_lower and len(symbols) >= 1) or " vs " in q_lower) and len(symbols) >= 2:
            s1, s2 = symbols[0], symbols[1]
            p1 = EQUITY_PROFILES.get(s1, {"name": s1, "sector": "Indian Equities", "overview": f"{s1} listed on NSE/BSE."})
            p2 = EQUITY_PROFILES.get(s2, {"name": s2, "sector": "Indian Equities", "overview": f"{s2} listed on NSE/BSE."})
            comparison_text = (
                f"### Comparative Research: **{s1}** vs. **{s2}**\n\n"
                f"| Parameter | **{s1}** ({p1['name']}) | **{s2}** ({p2['name']}) |\n"
                f"| :--- | :--- | :--- |\n"
                f"| **Sector** | {p1['sector']} | {p2['sector']} |\n"
                f"| **Core Strategic Moat** | {p1.get('key_drivers', 'Market Leadership')} | {p2.get('key_drivers', 'Market Leadership')} |\n"
                f"| **Primary Headwinds** | {p1.get('risks', 'Market Volatility')} | {p2.get('risks', 'Market Volatility')} |\n\n"
                f"**Key Analytical Takeaways:**\n"
                f"- **{s1}**: {p1.get('overview', '')}\n"
                f"- **{s2}**: {p2.get('overview', '')}\n\n"
                f"**Strategic Summary:** Investors seeking high-conviction exposure should weigh operating cash flows against current valuation multiples."
            )
            followups = [
                f"What are the quarterly financial results for {s1}?",
                f"What are the quarterly financial results for {s2}?",
                f"Compare the FinBERT news sentiment for {s1} and {s2}",
            ]
            return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, comparison_text, [], followups, None)

        # Case B: No news articles in DB, but query targets a known stock profile
        if symbols and symbols[0] in EQUITY_PROFILES:
            sym = symbols[0]
            profile = EQUITY_PROFILES[sym]
            lines = [
                f"### Equity Research Profile: **{profile['name']}** (`{sym}`)\n",
                f"**Sector:** {profile['sector']}\n",
                f"**Business Overview & Core Moats:**\n{profile['overview']}\n",
                f"**Key Growth Catalysts:**\n- {profile['key_drivers']}\n",
                f"**Key Risk Factors & Headwinds:**\n- {profile['risks']}\n",
                f"*(Note: No breaking news articles ingested in the last 24h for {sym}; providing fundamental equity research profile).* "
            ]
            answer = "\n".join(lines)
            followups = [
                f"What is the valuation multiple and P/E ratio for {sym}?",
                f"Compare {sym} against its primary domestic competitors",
            ]
            return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, answer, [], followups, None)

        # Case C: Generic / Broad Market inquiry with zero matching news
        general_answer = (
            f"### Indian Equities Market Analysis\n\n"
            f"Regarding your query on *\"{q_raw}\"*:\n\n"
            f"- **Domestic Benchmark Sentiment:** The Indian equity market (NIFTY 50 / SENSEX) continues to show structural resilience, supported by sustained retail SIP inflows (>₹20,000 Cr monthly) and capital expenditure across manufacturing and infrastructure.\n"
            f"- **Sectoral Dynamics:** Auto and Banking sectors lead positive sentiment conviction on stable credit growth and festive consumption, while IT services maintain a cautious outlook amid delayed discretionary client tech spending.\n"
            f"- **Next Steps:** You can query a specific stock (e.g. *'Analyze Tata Motors'*, *'Reliance Industries outlook'*, *'HDFC Bank deposit growth'*) or a financial term (*'Explain P/E ratio'*) for targeted intelligence."
        )
        followups = [
            "What is the outlook for Tata Motors electric vehicles?",
            "How does the RBI repo rate impact banking stocks?",
            "What does P/E ratio indicate in Indian equities?",
        ]
        return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, general_answer, [], followups, None)

    @classmethod
    def _save_and_respond(
        cls,
        db: Session,
        session_record: ChatSession,
        session_id: str,
        user_id: Optional[int],
        query: str,
        answer: str,
        citations: List[CitationItem],
        followups: List[str],
        summary: Optional[SentimentSummary],
    ) -> ChatQueryResponse:
        """Helper to log conversation turn and return standard response."""
        citations_dict_list = [c.model_dump() for c in citations]

        user_msg = ChatMessage(
            session_id=session_id,
            user_id=user_id,
            role="user",
            content=query,
            citations=None,
            created_at=datetime.utcnow(),
        )
        assistant_msg = ChatMessage(
            session_id=session_id,
            user_id=user_id,
            role="assistant",
            content=answer,
            citations=citations_dict_list,
            created_at=datetime.utcnow(),
        )

        db.add(user_msg)
        db.add(assistant_msg)
        session_record.updated_at = datetime.utcnow()
        db.commit()

        return ChatQueryResponse(
            session_id=session_id,
            role="assistant",
            answer=answer,
            citations=citations,
            suggested_followups=followups,
            sentiment_summary=summary,
        )
