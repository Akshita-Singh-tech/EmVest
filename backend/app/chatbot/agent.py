from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.core.config import settings
from app.models.article import Article
from app.models.chat import ChatMessage
from app.schemas.chat import (
    CitationItem,
    ChatQueryRequest,
    ChatQueryResponse,
    SentimentSummary,
    ChatMessageRecord,
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


class ChatAgent:
    """Agentic financial research assistant with DB retrieval, FinBERT scoring, and citation grounding."""

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
        """Retrieve most relevant stored articles from DB based on entities and text."""
        detected_symbols, detected_sectors, tokens = cls.extract_entities(query)
        target_symbols = list(set((symbols_override or []) + detected_symbols))

        # Base query
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

            # Base score for inclusion
            if score > 0:
                scored_articles.append((score, art))

        # Sort by relevance score descending
        scored_articles.sort(key=lambda x: x[0], reverse=True)
        results = [art for _, art in scored_articles[:limit]]

        # Fallback to latest articles if no specific entities or matches were found
        if not results:
            results = all_articles[:limit]

        return results

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

    @classmethod
    def generate_deterministic_response(
        cls,
        query: str,
        articles: List[Article],
        summary: Optional[SentimentSummary],
        symbols: List[str],
        sectors: List[str],
    ) -> str:
        """Synthesize a structured financial intelligence report strictly citing stored articles."""
        if not articles:
            return (
                "I could not locate any stored news or intelligence articles in the database matching your criteria. "
                "Please ensure the data ingestion pipeline has completed or query an Indian market benchmark like "
                "HDFC Bank, Reliance, Tata Motors, or RBI policy."
            )

        symbol_header = f" for **{', '.join(symbols)}**" if symbols else ""
        sector_header = f" across **{', '.join(sectors)}**" if sectors and not symbols else ""

        lines: List[str] = []

        # Section 1: Overview
        if summary:
            sign = "+" if summary.aggregate_score > 0 else ""
            score_formatted = f"{sign}{summary.aggregate_score:.2f}"
            lines.append(
                f"### Market Intelligence Synthesis{symbol_header}{sector_header}\n\n"
                f"Based on real-time ingestion of **{summary.article_count} verified financial publications**, "
                f"current composite sentiment stands at **{summary.sentiment_label}** "
                f"(*FinBERT Conviction: {score_formatted}* | {summary.positive_count} Bullish, "
                f"{summary.neutral_count} Neutral, {summary.negative_count} Bearish)."
            )
        else:
            lines.append(f"### Market Intelligence Synthesis{symbol_header}{sector_header}\n")

        # Section 2: Key Takeaways from matching articles
        lines.append("\n**Key Takeaways & Empirical Evidence:**")
        cited_count = 0
        for art in articles[:4]:
            cited_count += 1
            takeaway = (art.key_takeaways[0] if art.key_takeaways and len(art.key_takeaways) > 0 else art.summary)
            sign = "+" if art.sentiment_score > 0 else ""
            lines.append(
                f"- **{art.source}** (*{art.sentiment}, {sign}{art.sentiment_score:.2f}*): "
                f"{takeaway} [Source: *{art.title}*]"
            )

        # Section 3: Market Impact & Sector Implications
        lines.append("\n**Market Impact & Near-Term Trajectory:**")
        impacts = [art.market_impact for art in articles if art.market_impact]
        if impacts:
            for imp in impacts[:2]:
                lines.append(f"- {imp}")
        else:
            lines.append(
                "- Sustained domestic institutional buying and stable macroeconomic parameters "
                "continue to anchor valuation multiples across domestic equities."
            )

        # Section 4: Risk Factors & Watch Triggers
        lines.append("\n**Key Triggers to Monitor:**")
        lines.append("- Upcoming quarterly earnings commentary and operating margin guidance.")
        lines.append("- Global commodity spreads, currency fluctuations, and foreign institutional flows (FII).")

        return "\n".join(lines)

    @classmethod
    def generate_followup_prompts(
        cls,
        symbols: List[str],
        sectors: List[str],
        articles: List[Article],
    ) -> List[str]:
        """Generate smart context-aware follow-up queries."""
        prompts: List[str] = []

        if symbols:
            sym = symbols[0]
            prompts.append(f"What are the primary risk factors for {sym} over the next quarter?")
            prompts.append(f"How does {sym}'s FinBERT sentiment compare with its industry peers?")

        if sectors:
            sec = sectors[0]
            prompts.append(f"Which equities in {sec} currently carry the highest positive conviction?")

        if not prompts:
            prompts = [
                "Summarize recent RBI monetary policy statements and bank impact",
                "Compare IT sector outlook against Automobile manufacturers",
                "Show me top sentiment gainers in NIFTY 50",
            ]

        return prompts[:3]

    @classmethod
    def process_query(
        cls,
        db: Session,
        request: ChatQueryRequest,
        user_id: Optional[int] = None,
    ) -> ChatQueryResponse:
        """Main agent entrypoint: handles retrieval, synthesis, citation generation, and message logging."""
        session_id = request.session_id or str(uuid.uuid4())

        # 1. Retrieve articles from DB
        articles = cls.retrieve_articles(db, request.query, request.symbols)

        # 2. Extract entities for synthesis & followups
        symbols, sectors, _ = cls.extract_entities(request.query)
        if request.symbols:
            symbols = list(set(symbols + request.symbols))

        # 3. Calculate FinBERT sentiment summary
        sentiment_summary = cls.calculate_sentiment_summary(articles)

        # 4. Generate structured citations
        citations = cls.build_citations(articles)

        # 5. Synthesize answer
        # If external LLM key is configured, external generation could be plugged in;
        # otherwise our comprehensive grounded deterministic research synthesizer is used.
        answer = cls.generate_deterministic_response(
            query=request.query,
            articles=articles,
            summary=sentiment_summary,
            symbols=symbols,
            sectors=sectors,
        )

        # 6. Generate followups
        suggested_followups = cls.generate_followup_prompts(symbols, sectors, articles)

        # 7. Persist user message and assistant response to chat_messages table
        citations_dict_list = [c.model_dump() for c in citations]

        user_msg = ChatMessage(
            session_id=session_id,
            user_id=user_id,
            role="user",
            content=request.query,
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
        db.commit()

        return ChatQueryResponse(
            session_id=session_id,
            role="assistant",
            answer=answer,
            citations=citations,
            suggested_followups=suggested_followups,
            sentiment_summary=sentiment_summary,
        )
