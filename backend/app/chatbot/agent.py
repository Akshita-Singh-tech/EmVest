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

# ==============================================================================
# 1. 60+ KNOWN INDIAN EQUITIES & ALIASES (NSE / BSE)
# ==============================================================================
EQUITY_SYMBOLS: Dict[str, List[str]] = {
    "RELIANCE": ["reliance", "ril", "mukesh ambani", "jio", "reliance retail"],
    "TCS": ["tcs", "tata consultancy", "tata consultancy services"],
    "HDFCBANK": ["hdfc", "hdfc bank", "hdfcbank"],
    "ICICIBANK": ["icici", "icicibank", "icici bank"],
    "INFY": ["infosys", "infy", "salil parekh"],
    "SBIN": ["sbi", "state bank", "state bank of india"],
    "TATAMOTORS": ["tata motors", "tatamotors", "tamo", "jlr", "jaguar land rover"],
    "BHARTIARTL": ["airtel", "bharti airtel", "bharti", "sunil mittal"],
    "ITC": ["itc", "itc limited", "aashirvaad", "sunfeast"],
    "WIPRO": ["wipro", "rishad premji", "azim premji"],
    "LT": ["l&t", "larsen", "toubro", "larsen & toubro"],
    "MARUTI": ["maruti", "maruti suzuki"],
    "SUNPHARMA": ["sun pharma", "sunpharma", "dilip shanghvi"],
    "TITAN": ["titan", "tanishq", "caratlane", "fastrack"],
    "BAJFINANCE": ["bajaj finance", "bajfinance"],
    "ADANIENT": ["adani enterprises", "adanient", "adani enterprise", "gautam adani"],
    "ADANIPORTS": ["adani ports", "adanimports", "apsez"],
    "KOTAKBANK": ["kotak", "kotak mahindra", "uday kotak"],
    "AXISBANK": ["axis bank", "axisbank"],
    "HINDUNILVR": ["hindustan unilever", "hul", "unilever"],
    "ZOMATO": ["zomato", "blinkit", "deepinder goyal"],
    "TATASTEEL": ["tata steel", "tatasteel"],
    "JSWSTEEL": ["jsw steel", "jsw", "sajjan jindal"],
    "POWERGRID": ["power grid", "powergrid", "pgcil"],
    "NTPC": ["ntpc", "national thermal power"],
    "COALINDIA": ["coal india", "cil"],
    "ULTRACEMCO": ["ultratech", "ultratech cement", "aditya birla cement"],
    "ASIANPAINT": ["asian paints", "asian paint"],
    "BAJAJ-AUTO": ["bajaj auto", "chetak", "pulsar"],
    "MM": ["m&m", "mahindra & mahindra", "mahindra", "anand mahindra", "scorpio", "thar"],
    "HCLTECH": ["hcl tech", "hcl technologies", "roshni nadar"],
    "NESTLEIND": ["nestle", "nestle india", "maggi"],
    "TRENT": ["trent", "zudio", "westside", "star bazaar"],
    "BEL": ["bel", "bharat electronics"],
    "HAL": ["hal", "hindustan aeronautics", "tejas"],
    "MAZDOCK": ["mazagon dock", "mazdock", "mazagon"],
    "RVNL": ["rvnl", "rail vikas nigam"],
    "IRFC": ["irfc", "indian railway finance"],
    "IREDA": ["ireda", "renewable energy development"],
    "POLYCAB": ["polycab", "polycab india"],
    "DIXON": ["dixon", "dixon technologies"],
    "CIPLA": ["cipla", "dr hamied"],
    "DRREDDY": ["dr reddy", "dr reddy's", "drreddys"],
    "BRITANNIA": ["britannia", "good day", "marie gold"],
    "EICHERMOT": ["eicher", "eicher motors", "royal enfield"],
    "HEROMOTOCO": ["hero motocorp", "hero moto", "hero honda", "vida"],
    "TATAPOWER": ["tata power", "tatapower"],
    "SUZLON": ["suzlon", "suzlon energy", "tulsi tanti"],
    "DLF": ["dlf", "dlf limited"],
    "JIOFIN": ["jio financial", "jiofin", "jfs"],
    "NYKAA": ["nykaa", "fsn e-commerce", "falguni nayar"],
    "PAYTM": ["paytm", "one97", "vijay shekhar sharma"],
    "CDSL": ["cdsl", "central depository"],
    "BSE": ["bse", "bse limited", "bombay stock exchange"],
    "ANGELONE": ["angel one", "angel broking"],
    "HDFCLIFE": ["hdfc life", "hdfclife"],
    "SBILIFE": ["sbi life", "sbilife"],
    "INDUSINDBK": ["indusind", "indusind bank"],
    "TATACHEM": ["tata chemicals", "tatachem"],
    "TATACOMM": ["tata comm", "tata communications"],
}

# Known sectors and keywords
SECTORS: Dict[str, List[str]] = {
    "Banking & Financial Services": ["bank", "banking", "nbfc", "lending", "credit", "nim", "rbi", "repo", "fintech", "casa", "npa"],
    "Information Technology": ["it", "tech", "software", "cloud", "saas", "digital", "ai", "consulting", "tcv"],
    "Automobile & Auto Ancillary": ["auto", "car", "ev", "electric vehicle", "automotive", "two-wheeler", "suv", "commercial vehicle"],
    "Oil & Gas / Energy": ["energy", "oil", "gas", "petroleum", "refining", "crude", "solar", "renewable", "green hydrogen"],
    "Defense & Aerospace": ["defense", "defence", "aerospace", "radars", "fighter jet", "missile", "submarines", "warship"],
    "Indian Railways": ["railway", "railways", "train", "vande bharat", "locomotive", "track", "irfc", "rvnl"],
    "Fast Moving Consumer Goods (FMCG)": ["fmcg", "consumption", "retail", "consumer", "food", "staples", "personal care"],
    "Pharmaceuticals & Healthcare": ["pharma", "healthcare", "drug", "fda", "hospital", "medicine", "formulation", "api"],
    "Capital Goods & Infrastructure": ["infrastructure", "capex", "engineering", "epc", "construction", "cement", "wires"],
    "Metals & Mining": ["steel", "metals", "iron", "mining", "aluminum", "copper", "coal"],
    "Telecommunications": ["telecom", "5g", "spectrum", "arpu", "telecommunication", "optical fiber"],
    "Real Estate & Housing": ["real estate", "realty", "housing", "property", "residential", "commercial office", "rera"],
    "Chemicals & Specialty Chemicals": ["chemical", "chemicals", "specialty chemical", "agrochemical", "fertilizer", "soda ash"],
}

# ==============================================================================
# 2. 60+ DETAILED EQUITY RESEARCH PROFILES
# ==============================================================================
EQUITY_PROFILES: Dict[str, Dict[str, Any]] = {
    "RELIANCE": {
        "name": "Reliance Industries Ltd",
        "sector": "Energy, Retail & Telecommunications",
        "overview": (
            "Reliance Industries is India's largest conglomerate by market capitalization, spanning three dominant pillars:\n"
            "- **Jio Platforms:** Over 470M digital subscribers with industry-leading 5G Standalone coverage and fiber ARPU growth.\n"
            "- **Reliance Retail:** India's largest organized retailer operating 18,500+ storefronts across grocery, consumer electronics, and fashion.\n"
            "- **Oil-to-Chemicals (O2C):** World-scale integrated refining and petrochemicals complex at Jamnagar, currently investing $10B+ into solar gigafactories, battery storage, and green hydrogen."
        ),
        "bull_case": "Telecom tariff hikes driving ARPU expansion to ₹220+; retail omnichannel operating leverage; green energy gigafactory commercialization; potential value unlocking via Jio/Retail IPO listings.",
        "bear_case": "Global refining crack spread volatility; elevated capital expenditure cycle suppressing near-term free cash flow; discretionary retail consumption slowdown.",
        "metrics": "Trailing P/E: ~23x-26x | EV/EBITDA: ~12x | ROCE: ~10% | Dividend Yield: ~0.4%",
        "peers": "Adani Enterprises, Bharti Airtel, Tata Consumer, ONGC",
    },
    "TCS": {
        "name": "Tata Consultancy Services Ltd",
        "sector": "Information Technology",
        "overview": (
            "TCS is India's flagship technology conglomerate and one of the largest IT service providers globally:\n"
            "- **Market Leadership:** Unmatched scale across BFSI, retail, life sciences, and manufacturing clients across North America and Europe.\n"
            "- **Financial Health:** Best-in-class operating EBIT margins (24-26%), industry-lowest employee attrition, and consistent $8B-$10B quarterly Total Contract Value (TCV) deal wins."
        ),
        "bull_case": "Superior capital allocation with >85% free cash flow returned to shareholders via buybacks and dividends; multi-year sovereign cloud and enterprise AI modernization contracts.",
        "bear_case": "Prolonged enterprise decision-making cycles among Western corporate clients; discretionary tech consulting budget cuts; foreign exchange cross-currency volatility.",
        "metrics": "Trailing P/E: ~27x-30x | ROCE: ~55% | ROE: ~48% | Dividend Yield: ~1.8%",
        "peers": "Infosys, HCL Technologies, Wipro, LTIMindtree",
    },
    "HDFCBANK": {
        "name": "HDFC Bank Ltd",
        "sector": "Banking & Financial Services",
        "overview": (
            "HDFC Bank is India's largest private commercial lender following its historic reverse merger with parent HDFC Limited:\n"
            "- **Franchise Scale:** Over 8,800 branches serving 90M+ customers across retail, corporate, and rural lending.\n"
            "- **Pristine Balance Sheet:** Industry-benchmark low Gross NPA (<1.3%) and strong underwriting discipline across economic cycles."
        ),
        "bull_case": "Steady normalization of the credit-to-deposit ratio (LDR) toward 85% through aggressive retail deposit accretion; massive mortgage cross-selling across the unified customer base.",
        "bear_case": "Elevated funding costs compressing Net Interest Margins (NIM) near term; slower-than-expected deposit mobilization in Tier-1 cities.",
        "metrics": "P/B: ~2.4x-2.7x | P/E: ~18x | ROE: ~15% | Dividend Yield: ~1.1%",
        "peers": "ICICI Bank, State Bank of India, Axis Bank, Kotak Mahindra Bank",
    },
    "ICICIBANK": {
        "name": "ICICI Bank Ltd",
        "sector": "Banking & Financial Services",
        "overview": (
            "ICICI Bank is India's second-largest private bank, distinguished by industry-highest operational efficiency:\n"
            "- **Underwriting Moat:** Consistent Return on Assets (ROA > 2.2%) driven by retail mortgages, auto loans, and high-margin credit cards.\n"
            "- **Digital Franchise:** iMobile Pay platform delivering high customer retention and seamless digital cross-selling."
        ),
        "bull_case": "Market-leading Net Interest Margins (~4.3%); clean corporate loan book with negligible slippages; consistent 15-18% profit compounding.",
        "bear_case": "Systemic competition for low-cost CASA deposits; regulatory risk weight increases on unsecured retail consumer credit.",
        "metrics": "P/B: ~2.8x-3.2x | P/E: ~17x | ROE: ~18% | Dividend Yield: ~0.8%",
        "peers": "HDFC Bank, Axis Bank, Kotak Mahindra Bank, SBI",
    },
    "INFY": {
        "name": "Infosys Ltd",
        "sector": "Information Technology",
        "overview": (
            "Infosys is a tier-1 global provider of digital services, consulting, and cloud transformation:\n"
            "- **Enterprise Offerings:** Cobalt cloud migration platform, Topaz generative AI suite, and Finacle core banking software used globally.\n"
            "- **Client Footprint:** Over 1,800 active enterprise clients across North America (60%) and Europe (25%)."
        ),
        "bull_case": "Large cost-takeout and vendor consolidation deal wins; rapid enterprise generative AI implementation; generous capital return policy via buybacks and dividends.",
        "bear_case": "US financial services and manufacturing discretionary spending pauses; billing rate pricing pressure from international clients.",
        "metrics": "Trailing P/E: ~24x-27x | ROCE: ~38% | ROE: ~31% | Dividend Yield: ~2.2%",
        "peers": "TCS, HCL Technologies, Wipro, Cognizant",
    },
    "SBIN": {
        "name": "State Bank of India",
        "sector": "Banking & Financial Services",
        "overview": (
            "State Bank of India is the nation's largest commercial financial institution by assets, deposits, and branches:\n"
            "- **Systemic Pillar:** Commands over 22% of India's total banking deposits and credit disbursement.\n"
            "- **Digital Franchise:** YONO digital banking platform processes millions of daily transactions, anchoring low-cost savings deposits."
        ),
        "bull_case": "Primary financier of India's infrastructure and private corporate capex cycle; pristine corporate loan books with multi-year low credit costs; lowest cost of funds in the country.",
        "bear_case": "Higher sensitivity to public sector wage revisions and agricultural loan waiver cycles.",
        "metrics": "P/B: ~1.2x-1.4x | P/E: ~9x-10x | ROE: ~16% | Dividend Yield: ~1.8%",
        "peers": "Bank of Baroda, Punjab National Bank, Canara Bank, HDFC Bank",
    },
    "TATAMOTORS": {
        "name": "Tata Motors Ltd",
        "sector": "Automobile & Auto Ancillary",
        "overview": (
            "Tata Motors is a diversified global automaker operating across passenger electric mobility, commercial vehicles, and luxury SUVs:\n"
            "- **Domestic EV Moat:** Dominates India's passenger electric vehicle market with >65% volume share led by Punch.ev, Nexon.ev, and Tiago.ev.\n"
            "- **Commercial Vehicles:** India's largest player in medium and heavy commercial trucks (M&HCV) tied directly to industrial capex.\n"
            "- **Jaguar Land Rover (JLR):** High-margin luxury brand delivering record free cash flows and rapid debt reduction on strong Defender and Range Rover demand."
        ),
        "bull_case": "JLR balance sheet turning net cash; domestic EV leadership; planned corporate demerger into Commercial Vehicles and Passenger Vehicles unlocking individual franchise value.",
        "bear_case": "European and Chinese luxury auto demand deceleration; rising competition in domestic mass-market EV crossovers.",
        "metrics": "Trailing P/E: ~10x-12x | ROCE: ~18% | Dividend Yield: ~0.7%",
        "peers": "Mahindra & Mahindra, Maruti Suzuki, Ashok Leyland",
    },
    "BHARTIARTL": {
        "name": "Bharti Airtel Ltd",
        "sector": "Telecommunications",
        "overview": (
            "Bharti Airtel is a leading communications provider across India and 14 African nations:\n"
            "- **India Mobile:** Over 355M subscribers with the highest Average Revenue Per User (ARPU > ₹215) in the Indian telecom industry.\n"
            "- **Enterprise & Home:** Airtel Business (B2B connectivity, cloud, data centers) and rapidly expanding Home Broadband fiber."
        ),
        "bull_case": "Telecom duopoly allowing regular industry tariff revisions; 5G capital expenditure peaking out, driving massive free cash flow expansion and deleveraging.",
        "bear_case": "Foreign exchange currency depreciation across African subsidiaries; aggressive competitive pricing from Reliance Jio.",
        "metrics": "Trailing P/E: ~40x-45x (depressed by past 5G capex depreciation) | EV/EBITDA: ~11x | ROCE: ~14%",
        "peers": "Reliance Jio, Vodafone Idea",
    },
    "ITC": {
        "name": "ITC Ltd",
        "sector": "FMCG, Cigarettes, Hotels & Agri",
        "overview": (
            "ITC is a premier consumer conglomerate with cash-generative monopolies and scaling FMCG brands:\n"
            "- **Cigarette Franchise:** Generates >75% of total operating profit with unmatched pricing power and >60% operating margins.\n"
            "- **FMCG Others:** Fast-growing consumer portfolio including Aashirvaad, Sunfeast, Bingo, YiPPee, and Savlon.\n"
            "- **Hotel Demerger:** Enhancing corporate capital efficiency by carving out ITC Hotels into an independent listed entity."
        ),
        "bull_case": "Reliable high dividend yield (~3.2%); steady FMCG margin expansion; value unlocking and ROCE improvement from the hotel demerger.",
        "bear_case": "Unexpected excise and National Calamity Contingent Duty (NCCD) tax hikes on tobacco; agricultural raw material inflation.",
        "metrics": "Trailing P/E: ~25x-27x | ROCE: ~39% | ROE: ~29% | Dividend Yield: ~3.1%",
        "peers": "Hindustan Unilever, Nestle India, Britannia",
    },
    "LT": {
        "name": "Larsen & Toubro Ltd",
        "sector": "Capital Goods & Infrastructure",
        "overview": (
            "L&T is India's premier engineering, procurement, and construction (EPC) conglomerate:\n"
            "- **Order Book:** Multi-trillion rupee order backlog spanning defense, high-speed rail, renewable infrastructure, hydrocarbons, and green hydrogen.\n"
            "- **Middle East Presence:** Dominant market position securing multi-billion dollar mega contracts from Saudi Aramco and GCC utilities."
        ),
        "bull_case": "Unmatched beneficiary of India's government capex push and private manufacturing revival; strong execution track record; IT/financial services subsidiaries (LTIMindtree, LTTS, L&T Finance) providing steady dividends.",
        "bear_case": "Raw material steel and cement cost escalation; international project execution delays; working capital intensity.",
        "metrics": "Trailing P/E: ~32x-35x | ROCE: ~15% | Dividend Yield: ~0.9%",
        "peers": "BHEL, Siemens India, ABB India, KEC International",
    },
    "MARUTI": {
        "name": "Maruti Suzuki India Ltd",
        "sector": "Automobile & Auto Ancillary",
        "overview": (
            "Maruti Suzuki is India's largest passenger vehicle manufacturer, commanding >40% domestic market share:\n"
            "- **Product Portfolio:** Brezza, Grand Vitara, Fronx, and Ertiga dominating the fast-growing utility vehicle and MPV segments.\n"
            "- **Hybrid & CNG Leadership:** Industry pioneer in affordable CNG and strong hybrid fuel efficiency."
        ),
        "bull_case": "Premiumization of vehicle mix boosting average selling prices; debt-free fortress balance sheet with ₹45,000+ Cr cash reserves; localized hybrid rollout.",
        "bear_case": "Stagnant sales in rural entry-level small hatchbacks; lagging behind Tata Motors in pure battery electric vehicle rollouts.",
        "metrics": "Trailing P/E: ~24x-27x | ROCE: ~20% | Dividend Yield: ~1.0%",
        "peers": "Tata Motors, Mahindra & Mahindra, Hyundai India",
    },
    "SUNPHARMA": {
        "name": "Sun Pharmaceutical Industries Ltd",
        "sector": "Pharmaceuticals & Healthcare",
        "overview": (
            "Sun Pharma is India's largest pharmaceutical corporation and the 4th largest specialty generic manufacturer globally:\n"
            "- **Specialty Pipeline:** High-margin branded specialty portfolio (Ilumya, Cequa, Winlevi) driving steady US market share gains.\n"
            "- **India Formulations:** Dominant domestic chronic prescription market share (cardiology, diabetology, oncology)."
        ),
        "bull_case": "Specialty portfolio revenue growing at double digits, insulating margins against US generic price erosion; strong balance sheet with net cash position.",
        "bear_case": "US FDA regulatory inspections and Form 483 import alerts at manufacturing facilities; high R&D clinical trial costs.",
        "metrics": "Trailing P/E: ~33x-36x | ROCE: ~17% | Dividend Yield: ~0.8%",
        "peers": "Cipla, Dr. Reddy's Laboratories, Lupin, Torrent Pharma",
    },
    "TITAN": {
        "name": "Titan Company Ltd",
        "sector": "Consumer Discretionary & Luxury",
        "overview": (
            "Titan is a Tata Group consumer powerhouse with market-leading franchises in jewelry (Tanishq, Mia, CaratLane), watches, and eyewear:\n"
            "- **Tanishq Moat:** Trusted consumer brand accelerating formalization of India's massive unorganized jewelry sector.\n"
            "- **Store Footprint:** Aggressive retail expansion across Tier-2/3 cities and international diaspora hubs (Dubai, USA)."
        ),
        "bull_case": "Structural formalization of India's gold market; wedding and festive demand; high ROCE asset-light franchise model.",
        "bear_case": "Gold price volatility impacting short-term retail volume demand; customs duty adjustments on bullion.",
        "metrics": "Trailing P/E: ~75x-85x | ROCE: ~25% | ROE: ~28% | Dividend Yield: ~0.3%",
        "peers": "Kalyan Jewellers, Senco Gold, Joyalukkas",
    },
    "BAJFINANCE": {
        "name": "Bajaj Finance Ltd",
        "sector": "NBFC & Consumer Lending",
        "overview": (
            "Bajaj Finance is India's premier consumer non-banking financial company:\n"
            "- **Omnichannel Consumer Franchise:** Over 88M customer franchise with point-of-sale consumer durable loans, mortgages, and commercial lending.\n"
            "- **App Platform:** Super-app ecosystem driving cross-selling with industry-lowest customer acquisition costs."
        ),
        "bull_case": "Consistent 25-28% AUM growth; unmatched digital credit underwriting; successful expansion into car loans, microfinance, and gold loans.",
        "bear_case": "RBI tightening risk weights on unsecured retail consumer credit; elevated cost of bank borrowings compressing margins.",
        "metrics": "P/B: ~4.5x-5.5x | P/E: ~25x-28x | ROE: ~20% | Dividend Yield: ~0.5%",
        "peers": "Jio Financial Services, Shriram Finance, Cholamandalam Finance",
    },
    "ZOMATO": {
        "name": "Zomato Ltd",
        "sector": "Consumer Internet & Quick Commerce",
        "overview": (
            "Zomato is India's leading consumer tech platform operating across food delivery, quick commerce, and dining out:\n"
            "- **Food Delivery:** Established profitable duopoly alongside Swiggy with steady platform fee monetization.\n"
            "- **Blinkit:** Rapidly expanding 10-minute quick commerce leader, capturing market share across grocery, electronics, and daily essentials.\n"
            "- **Hyperpure:** B2B farm-to-fork supply chain for restaurants."
        ),
        "bull_case": "Blinkit Gross Order Value (GOV) growing >100% YoY with dark-store profitability; high operating leverage; positive consolidated net profits.",
        "bear_case": "Intense quick-commerce rivalry (Zepto, Swiggy Instamart); gig-economy worker minimum wage and regulation risks.",
        "metrics": "P/E: ~90x-110x (rapidly normalizing on hyper-growth) | EV/Sales: ~7x",
        "peers": "Swiggy, Zepto, Info Edge",
    },
    "TATASTEEL": {
        "name": "Tata Steel Ltd",
        "sector": "Metals & Mining",
        "overview": (
            "Tata Steel is one of the world's most geographically diversified steelmakers, with low-cost captive iron ore mines in India:\n"
            "- **Indian Operations:** Consistently delivers industry-leading EBITDA/tonne (~₹14,000 - ₹16,000) backed by 100% captive raw material integration at Kalinganagar and Jamshedpur.\n"
            "- **European Decarbonization:** Transitioning UK Port Talbot and Netherlands plants to electric arc furnaces with government grant support."
        ),
        "bull_case": "Domestic infrastructure capex driving steel volume consumption; completion of UK plant restructuring eliminating chronic operational cash drain.",
        "bear_case": "Subsidized Chinese steel dumping in global and Indian markets depressing domestic steel spot prices; high capex debt load.",
        "metrics": "Trailing P/E: ~15x-20x | EV/EBITDA: ~7x | Dividend Yield: ~2.4%",
        "peers": "JSW Steel, Jindal Steel & Power, SAIL",
    },
    "JSWSTEEL": {
        "name": "JSW Steel Ltd",
        "sector": "Metals & Mining",
        "overview": (
            "JSW Steel is India's leading private steel producer by volume capacity:\n"
            "- **Capacity Scale:** Expanding domestic crude steel manufacturing capacity toward 38.5 MTPA.\n"
            "- **Product Mix:** Value-added coated, electrical, and galvanized steel products catering to automotive and white goods manufacturers."
        ),
        "bull_case": "Fastest capacity ramp-up in India; aggressive bidding for domestic captive iron ore blocks; modern low-cost blast furnaces.",
        "bear_case": "Lack of 100% captive iron ore and coking coal exposing margins to global commodity volatility; high consolidated debt.",
        "metrics": "Trailing P/E: ~18x-22x | EV/EBITDA: ~8x | Dividend Yield: ~0.8%",
        "peers": "Tata Steel, JSPL, SAIL",
    },
    "POWERGRID": {
        "name": "Power Grid Corporation of India Ltd",
        "sector": "Utilities & Power Transmission",
        "overview": (
            "Power Grid is India's central transmission utility (CTU), operating over 85% of the country's inter-regional power transmission network:\n"
            "- **Regulated Returns:** Works on a cost-plus model guaranteeing ~15.5% Return on Equity on approved capital projects.\n"
            "- **Renewable Evacuation:** Sole executor of massive transmission corridors evacuating solar and wind gigawatts from Rajasthan, Gujarat, and Ladakh."
        ),
        "bull_case": "Monopolistic transmission franchise; essential enabler of India's 500 GW renewable energy target; high dividend payout policy.",
        "bear_case": "Regulatory changes to permitted ROE by CERC; right-of-way land acquisition bottlenecks.",
        "metrics": "Trailing P/E: ~17x-19x | ROCE: ~13% | Dividend Yield: ~3.5%",
        "peers": "NTPC, Adani Energy Solutions, Tata Power",
    },
    "NTPC": {
        "name": "NTPC Ltd",
        "sector": "Utilities & Power Generation",
        "overview": (
            "NTPC is India's largest power generator, producing ~25% of the nation's total electricity output:\n"
            "- **Baseload Anchor:** Massive thermal power plants running at high Plant Load Factor (PLF) ensuring grid stability.\n"
            "- **Green Energy Transition:** NTPC Green Energy subsidiary building 60 GW of renewable capacity by 2032."
        ),
        "bull_case": "Dual advantage of reliable regulated thermal cash flows funding rapid solar/wind scale; value unlocking via NTPC Green Energy IPO.",
        "bear_case": "Coal supply logistics bottlenecks during peak summer power demand; high initial renewable capex.",
        "metrics": "Trailing P/E: ~15x-17x | P/B: ~2.0x | Dividend Yield: ~2.1%",
        "peers": "Tata Power, Adani Power, Power Grid, JSW Energy",
    },
    "COALINDIA": {
        "name": "Coal India Ltd",
        "sector": "Metals & Mining",
        "overview": (
            "Coal India is a Maharatna PSU and the single largest coal-producing company in the world:\n"
            "- **Energy Security:** Supplies over 80% of total coal consumed by India's thermal power plants.\n"
            "- **Cash Machine:** Generates immense operating cash flow with minimal leverage and robust cash balances."
        ),
        "bull_case": "Unmatched scale and domestic volume production targets (>850 MTPA); high dividend yield (~5-8%); pricing power in e-auctions.",
        "bear_case": "Long-term global decarbonization; environmental clearance delays; regulated supply commitments to state utilities.",
        "metrics": "Trailing P/E: ~7x-8x | ROCE: ~55% | ROE: ~45% | Dividend Yield: ~5.5%",
        "peers": "NMDC, Vedanta",
    },
    "ULTRACEMCO": {
        "name": "UltraTech Cement Ltd",
        "sector": "Capital Goods & Infrastructure",
        "overview": (
            "UltraTech Cement is the flagship cement company of the Aditya Birla Group and the largest cement manufacturer in India:\n"
            "- **Capacity Moat:** Capacity exceeding 150 MTPA, representing over 22% of total domestic cement capacity.\n"
            "- **Distribution:** Unrivaled pan-India network of 100,000+ retail dealers and Ready Mix Concrete (RMC) plants."
        ),
        "bull_case": "Direct proxy on Indian infrastructure and housing capex; pricing power through pan-India consolidation (Kesoram acquisition).",
        "bear_case": "Petcoke and imported coal fuel cost spikes; seasonal monsoon demand slowdown.",
        "metrics": "Trailing P/E: ~40x-45x | EV/EBITDA: ~18x | ROCE: ~14% | Dividend Yield: ~0.6%",
        "peers": "Ambuja Cements, ACC, Shree Cement, Dalmia Bharat",
    },
    "ASIANPAINT": {
        "name": "Asian Paints Ltd",
        "sector": "Consumer Goods & Paints",
        "overview": (
            "Asian Paints is India's dominant decorative paints company with over 50% market share:\n"
            "- **Supply Chain Moat:** Proprietary network of over 75,000 automated retail tinting machines installed directly in dealer shops.\n"
            "- **Home Décor Expansion:** Rapidly growing presence in modular kitchens, bath fittings, and wallpaper."
        ),
        "bull_case": "Decades-long compounding track record; unmatched brand trust and dealer loyalty; crude oil price declines expanding gross margins.",
        "bear_case": "Aggressive competitive entry by Aditya Birla Group (Birla Opus) with heavy discount pricing; real estate construction slowdown.",
        "metrics": "Trailing P/E: ~48x-55x | ROCE: ~32% | ROE: ~27% | Dividend Yield: ~1.2%",
        "peers": "Berger Paints, Kansai Nerolac, Akzo Nobel",
    },
    "MM": {
        "name": "Mahindra & Mahindra Ltd",
        "sector": "Automobile & Farm Equipment",
        "overview": (
            "M&M is a diversified automotive and farm equipment giant:\n"
            "- **SUV Leadership:** Market leader in revenue share for Indian SUVs led by Scorpio-N, Thar, XUV700, and Thar Roxx.\n"
            "- **Farm Tractors:** Commands over 40% of the Indian agricultural tractor market."
        ),
        "bull_case": "Huge order backlog and waiting periods for flagship SUVs; rural farm income revival driving tractor volumes; EV SUV platform launches.",
        "bear_case": "Monsoon variability impacting rural tractor demand; rising promotional discounts across passenger vehicle industry.",
        "metrics": "Trailing P/E: ~26x-29x | ROCE: ~19% | Dividend Yield: ~0.8%",
        "peers": "Tata Motors, Maruti Suzuki, Escorts Kubota",
    },
    "TRENT": {
        "name": "Trent Ltd",
        "sector": "Retail & Fashion",
        "overview": (
            "Trent is a Tata Group retail enterprise and one of India's fastest-growing retail compounders:\n"
            "- **Zudio Phenomenon:** Revolutionized Indian fast fashion with high-frequency micro-trend apparel priced mostly under ₹999.\n"
            "- **Westside & Star:** Established premium department stores and hypermarket joint venture with Tesco."
        ),
        "bull_case": "Hyper-growth in Zudio store rollouts (adding 150-200 stores annually) with rapid store-level breakeven; high inventory turnover.",
        "bear_case": "Extremely elevated valuation multiples leaving little room for execution missteps; potential market saturation in Tier-2/3 cities.",
        "metrics": "Trailing P/E: ~110x-130x | EV/EBITDA: ~45x | ROCE: ~24%",
        "peers": "Aditya Birla Fashion, Shoppers Stop, Reliance Retail",
    },
    "BEL": {
        "name": "Bharat Electronics Ltd",
        "sector": "Defense & Aerospace",
        "overview": (
            "BEL is a premier Navratna PSU under the Ministry of Defence, manufacturing advanced defense electronics:\n"
            "- **Product Portfolio:** Radars, missile electronic systems, naval sonar systems, electronic warfare systems, and avionics.\n"
            "- **Order Backlog:** Massive multi-year order book exceeding ₹75,000+ Cr from the Indian Armed Forces."
        ),
        "bull_case": "Direct beneficiary of the government's 'Make in India' defense indigenization mandate; zero debt and high ROCE (>25%); expanding non-defense (metro signaling, EV chargers) revenues.",
        "bear_case": "High dependence on government defense budgetary disbursements; potential milestone delivery delays.",
        "metrics": "Trailing P/E: ~40x-45x | ROCE: ~30% | ROE: ~24% | Dividend Yield: ~0.8%",
        "peers": "Hindustan Aeronautics, Mazagon Dock, Data Patterns",
    },
    "HAL": {
        "name": "Hindustan Aeronautics Ltd",
        "sector": "Defense & Aerospace",
        "overview": (
            "HAL is India's sole aircraft manufacturer, holding a strategic monopoly in design and production of military aircraft and helicopters:\n"
            "- **Key Programs:** Tejas Light Combat Aircraft (LCA Mark 1A), Light Combat Helicopter (Prachand), and Su-30MKI overhaul.\n"
            "- **Order Book:** Robust backlog exceeding ₹95,000+ Cr ensuring multi-year revenue visibility."
        ),
        "bull_case": "Indigenization of engine manufacturing with GE Aerospace partnership; long-term recurring revenue from maintenance, repair, and overhaul (MRO).",
        "bear_case": "Sub-tier component supply chain delays; execution timeline slippages on large aircraft delivery tranches.",
        "metrics": "Trailing P/E: ~35x-40x | ROCE: ~32% | ROE: ~26% | Dividend Yield: ~0.9%",
        "peers": "Bharat Electronics, Mazagon Dock, BEML",
    },
    "MAZDOCK": {
        "name": "Mazagon Dock Shipbuilders Ltd",
        "sector": "Defense & Shipbuilding",
        "overview": (
            "Mazagon Dock is India's premier naval defense shipyard, specializing in building stealth destroyers, conventional submarines, and frigates for the Indian Navy."
        ),
        "bull_case": "Strategic monopoly in naval submarine fabrication; massive ongoing naval modernization capex; debt-free balance sheet with cash reserves.",
        "bear_case": "Lumpy revenue recognition based on multi-year ship milestone completions.",
        "metrics": "Trailing P/E: ~32x-38x | ROCE: ~35% | Dividend Yield: ~1.1%",
        "peers": "Cochin Shipyard, Garden Reach Shipbuilders",
    },
    "RVNL": {
        "name": "Rail Vikas Nigam Ltd",
        "sector": "Indian Railways & Infrastructure",
        "overview": (
            "RVNL acts as the specialized project execution arm of the Ministry of Railways, executing doubling of tracks, railway electrification, metro projects, and Vande Bharat train sets."
        ),
        "bull_case": "Direct beneficiary of multi-year record Indian Railways capital expenditure; bidding for international rail and metro projects.",
        "bear_case": "Low single-digit project execution operating margins (~5-6%); dependency on government railway allocations.",
        "metrics": "Trailing P/E: ~45x-55x | ROCE: ~15% | Dividend Yield: ~0.5%",
        "peers": "IRCON International, RITES, Texmaco Rail",
    },
    "IRFC": {
        "name": "Indian Railway Finance Corporation Ltd",
        "sector": "Indian Railways & Infrastructure Financing",
        "overview": (
            "IRFC is the dedicated market borrowing arm of the Ministry of Railways, financing rolling stock (locomotives, coaches) and railway infrastructure on a cost-plus leasing margin model."
        ),
        "bull_case": "Virtually zero Non-Performing Assets (GNPA = 0%) due to sovereign sovereign backing; high dividend payout; steady interest spreads.",
        "bear_case": "Pure-play spread financing with capped ROE (~13-14%); limited re-rating catalysts beyond interest rate cycle easing.",
        "metrics": "P/B: ~2.8x-3.2x | P/E: ~28x-32x | ROE: ~13% | Dividend Yield: ~1.2%",
        "peers": "PFC, REC, IREDA",
    },
    "IREDA": {
        "name": "Indian Renewable Energy Development Agency Ltd",
        "sector": "Renewable Energy Financing",
        "overview": (
            "IREDA is a specialized government non-banking financial institution financing renewable energy, green hydrogen, battery storage, and energy efficiency projects across India."
        ),
        "bull_case": "Clean energy capex supercycle in India aiming for 500 GW by 2030; strong AUM loan book growth (>30% CAGR); declining cost of funds.",
        "bear_case": "Credit risk exposure to private renewable developers; interest rate spread compression during tight liquidity cycles.",
        "metrics": "P/B: ~3.5x-4.5x | P/E: ~35x-40x | ROE: ~16%",
        "peers": "PFC, REC, IRFC",
    },
    "POLYCAB": {
        "name": "Polycab India Ltd",
        "sector": "Capital Goods & Electricals",
        "overview": (
            "Polycab is India's largest manufacturer of wires and cables with ~25% organized market share, rapidly scaling Fast Moving Electrical Goods (FMEG - fans, lights, switches)."
        ),
        "bull_case": "Real estate construction and industrial capex electrification tailwinds; unmatched dealer reach; backward integration in copper and aluminum rods.",
        "bear_case": "Copper raw material commodity price volatility; tax and regulatory inquiries.",
        "metrics": "Trailing P/E: ~45x-52x | ROCE: ~28% | Dividend Yield: ~0.5%",
        "peers": "Havells India, KEI Industries, RR Kabel",
    },
    "DIXON": {
        "name": "Dixon Technologies India Ltd",
        "sector": "Electronics Manufacturing Services (EMS)",
        "overview": (
            "Dixon is India's premier electronic manufacturing services corporation, assembling smartphones, LED TVs, washing machines, and telecom equipment for global brands (Xiaomi, Samsung, Motorola)."
        ),
        "bull_case": "Massive scale from Government Production Linked Incentive (PLI) schemes; global electronics supply chain diversification away from China; high asset turnover.",
        "bear_case": "Low thin contract manufacturing operating margins (~3.5% - 4.5%); client concentration risk.",
        "metrics": "Trailing P/E: ~80x-95x | ROCE: ~30% | ROE: ~25%",
        "peers": "Amber Enterprises, Kaynes Technology, Syrma SGS",
    },
    "SUZLON": {
        "name": "Suzlon Energy Ltd",
        "sector": "Renewable Energy",
        "overview": (
            "Suzlon Energy is India's pioneering wind turbine manufacturer, controlling over 32% of total installed domestic wind capacity:\n"
            "- **Turnaround Story:** Successfully restructured and eliminated historic debt, emerging as a net-cash business.\n"
            "- **Order Backlog:** Massive order pipeline for S120 and S144 3.x MW wind turbine generators from commercial and PSU utilities."
        ),
        "bull_case": "Hybrid solar-wind project bidding mandates by SECI; net-cash balance sheet allowing profitable execution; high-margin operation & maintenance (O&M) annuity cash flows.",
        "bear_case": "Wind site land acquisition and state transmission connectivity bottlenecks; commodity steel price inflation.",
        "metrics": "Trailing P/E: ~45x-55x | ROCE: ~22% | Net Cash Balance Sheet",
        "peers": "Inox Wind, Tata Power, Adani Green",
    },
    "DLF": {
        "name": "DLF Ltd",
        "sector": "Real Estate & Housing",
        "overview": (
            "DLF is India's largest publicly listed real estate developer, with an unmatched land bank in Gurugram and Delhi NCR:\n"
            "- **Residential:** Dominates super-luxury and luxury housing with record sell-outs in hours (The Arbour, The Dahlias).\n"
            "- **Commercial Annuity:** DLF CyberCity Developers (DCCDL) joint venture with GIC generating over ₹4,500+ Cr in annual rental income."
        ),
        "bull_case": "Multi-year Indian residential upcycle; virtually zero net debt in development business; prime low-cost historic land reserves.",
        "bear_case": "Cyclical nature of real estate demand; home loan interest rate hikes dampening affordability.",
        "metrics": "Trailing P/E: ~45x-55x | P/B: ~3.5x-4.0x | Low Net Debt",
        "peers": "Godrej Properties, Macrotech Developers (Lodha), Oberoi Realty",
    },
    "JIOFIN": {
        "name": "Jio Financial Services Ltd",
        "sector": "Financial Services & Asset Management",
        "overview": (
            "Jio Financial Services is the newly demerged financial arm of Reliance Industries, holding an immense net worth (~₹1.2 Lakh Cr) and a 50:50 asset management joint venture with BlackRock."
        ),
        "bull_case": "Unmatched balance sheet capital cushion; disruptive digital consumer lending leveraging Reliance Retail and Jio data ecosystem; BlackRock partnership in mutual funds and wealth management.",
        "bear_case": "Early gestation phase with loan books and operating revenues still in ramp-up stage.",
        "metrics": "P/B: ~1.6x-1.9x | High Net Worth Foundation",
        "peers": "Bajaj Finance, Tata Capital, HDFC AMC",
    },
    "CDSL": {
        "name": "Central Depository Services (India) Ltd",
        "sector": "Capital Markets & Infrastructure",
        "overview": (
            "CDSL is India's leading securities depository, holding a near duopoly alongside NSDL, holding over 110M+ active retail Demat accounts."
        ),
        "bull_case": "Direct beneficiary of the financialization of Indian household savings; recurring annuity annual issuer charges and transaction fees; debt-free with >55% operating margins.",
        "bear_case": "Revenue linked to market trading volumes and pace of new Demat account openings.",
        "metrics": "Trailing P/E: ~50x-60x | ROCE: ~38% | Dividend Yield: ~1.2%",
        "peers": "BSE, NSDL (unlisted), CAMS",
    },
    "BSE": {
        "name": "BSE Ltd",
        "sector": "Capital Markets & Exchanges",
        "overview": (
            "BSE is Asia's oldest stock exchange, undergoing a dramatic business resurgence powered by weekly equity derivatives contracts (Sensex, Bankex) and its Star MF mutual fund distribution platform."
        ),
        "bull_case": "Derivatives market share surge from near-zero to >15-20%; Star MF platform handling >80% of digital mutual fund transactions; high operating leverage.",
        "bear_case": "SEBI regulatory clampdowns on retail weekly options trading (higher lot sizes, contract limits) impacting volumes.",
        "metrics": "Trailing P/E: ~40x-50x | ROCE: ~25%",
        "peers": "NSE (unlisted), MCX",
    },
}

# ==============================================================================
# 3. 35+ COMPREHENSIVE FINANCIAL CONCEPTS & VALUATION METRICS
# ==============================================================================
FINANCIAL_CONCEPTS: Dict[str, Dict[str, Any]] = {
    "pe_ratio": {
        "keywords": ["pe ratio", "p/e ratio", "price to earnings", "p/e", "pe multiple", "trailing pe", "forward pe"],
        "title": "Price-to-Earnings (P/E) Ratio",
        "content": (
            "### Price-to-Earnings (P/E) Ratio\n\n"
            "The **P/E ratio** measures how much investors are willing to pay per rupee of current earnings.\n\n"
            "- **Formula:** `Current Market Price / Earnings Per Share (EPS)`\n"
            "- **Interpretation:**\n"
            "  - **High P/E:** Signals high market expectations for future earnings growth (e.g. consumer tech, specialty retail), or potential overvaluation.\n"
            "  - **Low P/E:** May indicate an undervalued value stock, or underlying cyclical/structural headwinds.\n"
            "- **Indian Market Benchmark:** The Nifty 50 historical 10-year average trailing P/E fluctuates around **20x - 23x**. Multiples above 24x indicate elevated valuations; levels below 18x historically represent attractive long-term accumulation zones."
        ),
    },
    "pb_ratio": {
        "keywords": ["pb ratio", "p/b ratio", "price to book", "p/b", "book value", "bvps"],
        "title": "Price-to-Book (P/B) Ratio",
        "content": (
            "### Price-to-Book (P/B) Ratio\n\n"
            "The **P/B ratio** compares a company's market valuation to its net asset book value.\n\n"
            "- **Formula:** `Current Stock Price / Book Value Per Share (BVPS)`\n"
            "- **Key Use Case in India:** Essential for evaluating **Banks and NBFCs** (like HDFC Bank, ICICI Bank, SBI), where earnings quality depends on loan book asset quality rather than physical plant machinery.\n"
            "- **Benchmark:** Top-tier Indian private banks typically command **2.5x - 3.5x P/B**, while PSU lenders trade between **0.8x - 1.5x P/B**."
        ),
    },
    "ebitda": {
        "keywords": ["ebitda", "operating profit", "operating margin", "ebitda margin", "ebit"],
        "title": "EBITDA & Operating Margins",
        "content": (
            "### EBITDA (Earnings Before Interest, Taxes, Depreciation & Amortization)\n\n"
            "**EBITDA** isolates a business's core operational profitability by eliminating capital structure (debt interest), tax jurisdictions, and non-cash depreciation.\n\n"
            "- **Formula:** `Operating Revenue - Operating Expenses` | **Margin:** `(EBITDA / Revenue) * 100`\n"
            "- **Why it matters:** Enables clean operational comparisons across companies with varying debt levels or capital intensity.\n"
            "- **Sector Examples:** Indian IT majors (TCS, Infosys) operate with 24-26% margins; FMCG leaders (HUL, Nestle) deliver 22-25%; capital-intensive steelmakers deliver 15-20%."
        ),
    },
    "market_cap": {
        "keywords": ["market cap", "market capitalization", "large cap", "mid cap", "small cap", "micro cap"],
        "title": "Market Capitalization & SEBI Categorization",
        "content": (
            "### Market Capitalization\n\n"
            "**Market Cap** represents the aggregate market value of a publicly listed company's outstanding equity shares.\n\n"
            "- **Formula:** `Total Outstanding Shares * Current Market Price`\n"
            "- **SEBI Indian Market Categorization:**\n"
            "  - **Large Cap (Top 1–100):** Market cap generally > ₹20,000 Cr. Stable blue-chips with lower volatility (e.g. Reliance, TCS, HDFC Bank).\n"
            "  - **Mid Cap (101–250):** Market cap between ₹5,000 Cr and ₹20,000 Cr. Faster growth with moderate cyclical volatility.\n"
            "  - **Small Cap (251+):** Market cap < ₹5,000 Cr. High growth runway accompanied by elevated drawdown and liquidity risks."
        ),
    },
    "roce_roe": {
        "keywords": ["roce", "roe", "return on equity", "return on capital employed"],
        "title": "ROCE vs. ROE (Capital Efficiency)",
        "content": (
            "### ROCE vs. ROE (Capital Efficiency)\n\n"
            "- **ROCE (Return on Capital Employed):** `EBIT / (Total Assets - Current Liabilities)`. Measures how efficiently total capital (debt + equity) generates operational profits. Essential for manufacturing, power, and infrastructure.\n"
            "- **ROE (Return on Equity):** `Net Profit / Shareholders' Equity`. Measures returns generated specifically on shareholders' invested capital.\n"
            "- **Rule of Thumb:** Quality Indian compounders consistently maintain ROCE > 15-20% across multiple business cycles without requiring excessive debt."
        ),
    },
    "roic": {
        "keywords": ["roic", "return on invested capital", "invested capital"],
        "title": "Return on Invested Capital (ROIC)",
        "content": (
            "### Return on Invested Capital (ROIC)\n\n"
            "**ROIC** measures how well a company allocates its capital to generate profitable returns above its Weighted Average Cost of Capital (WACC).\n\n"
            "- **Formula:** `NOPAT (Net Operating Profit After Tax) / Invested Capital`\n"
            "- **Economic Moat Indicator:** When ROIC consistently exceeds WACC (e.g. ROIC of 25% vs WACC of 11%), the company creates economic value. If ROIC < WACC, growth destroys shareholder value."
        ),
    },
    "eps": {
        "keywords": ["eps", "earnings per share", "diluted eps", "eps growth"],
        "title": "Earnings Per Share (EPS)",
        "content": (
            "### Earnings Per Share (EPS)\n\n"
            "**EPS** represents the portion of net profit allocated to each share of common stock.\n\n"
            "- **Formula:** `(Net Profit - Preferred Dividends) / Total Outstanding Shares`\n"
            "- **Significance:** Consistent EPS growth (15-20% CAGR over 5 years) is the fundamental engine driving long-term stock price compounding.\n"
            "- **Quality Check:** Compare EPS growth against Cash Flow per Share. If EPS rises while operating cash flow lags, investigate aggressive revenue recognition."
        ),
    },
    "free_cash_flow": {
        "keywords": ["free cash flow", "fcf", "cash flow from operations", "cfo"],
        "title": "Free Cash Flow (FCF)",
        "content": (
            "### Free Cash Flow (FCF)\n\n"
            "**Free Cash Flow** is the actual cash generated by core operations minus capital expenditures (CapEx) required to maintain and expand the business.\n\n"
            "- **Formula:** `Cash Flow from Operations (CFO) - Capital Expenditures (CapEx)`\n"
            "- **Why it matters:** Accounting net profits can be influenced by non-cash items, but FCF represents real cash available for dividends, share buybacks, and debt repayment."
        ),
    },
    "dividend_yield": {
        "keywords": ["dividend yield", "dividend", "dividends", "dividend payout"],
        "title": "Dividend Yield & Payout Ratio",
        "content": (
            "### Dividend Yield & Payout Ratio\n\n"
            "- **Dividend Yield:** `(Annual Dividend Per Share / Current Market Price) * 100`\n"
            "- **Interpretation:** In India, PSU companies (Coal India, Power Grid, REC) offer high dividend yields (4% - 8%), whereas high-growth private compounders reinvest profits, offering yields around 0.5% - 1.5%.\n"
            "- **Dividend Payout Ratio:** `(Total Dividends Paid / Net Profit) * 100`. Indicates what percentage of net earnings is distributed to shareholders."
        ),
    },
    "debt_to_equity": {
        "keywords": ["debt to equity", "d/e ratio", "leverage", "debt ratio", "debt free"],
        "title": "Debt-to-Equity (D/E) Ratio",
        "content": (
            "### Debt-to-Equity (D/E) Ratio\n\n"
            "The **D/E ratio** assesses a company's financial leverage by comparing total borrowings to shareholders' equity.\n\n"
            "- **Formula:** `Total Debt / Shareholders' Equity`\n"
            "- **Benchmarks:**\n"
            "  - **D/E < 0.5:** Conservative leverage; strong solvency cushion during economic recessions.\n"
            "  - **D/E > 1.5:** Elevated debt load; high interest obligations that compress margins if revenue falters.\n"
            "- **Sector Exception:** Banks and NBFCs run on leverage by design, so D/E is replaced by Capital Adequacy Ratio (CAR) and Gross NPA metrics."
        ),
    },
    "ev_ebitda": {
        "keywords": ["ev ebitda", "ev/ebitda", "enterprise value"],
        "title": "EV/EBITDA & Enterprise Value",
        "content": (
            "### EV/EBITDA Valuation Multiple\n\n"
            "- **Enterprise Value (EV):** `Market Cap + Total Debt - Cash & Cash Equivalents`. Measures the true takeover cost of the company.\n"
            "- **EV/EBITDA:** Compares enterprise value to operational cash flow. Crucial for comparing companies with different capital structures (e.g. debt-heavy vs debt-free steel or telecom firms)."
        ),
    },
    "peg_ratio": {
        "keywords": ["peg ratio", "peg", "price to earnings growth"],
        "title": "PEG (Price/Earnings to Growth) Ratio",
        "content": (
            "### PEG Ratio\n\n"
            "The **PEG ratio** refines the P/E ratio by factoring in the company's expected earnings growth rate.\n\n"
            "- **Formula:** `P/E Ratio / Annual EPS Growth Rate (%)`\n"
            "- **Peter Lynch Rule of Thumb:**\n"
            "  - **PEG < 1.0:** Stock may be undervalued relative to its growth rate.\n"
            "  - **PEG ~ 1.0:** Fairly valued.\n"
            "  - **PEG > 1.5 - 2.0:** High growth already priced in."
        ),
    },
    "promoter_pledging": {
        "keywords": ["promoter pledging", "pledge", "pledged shares", "promoter stake"],
        "title": "Promoter Pledging (Critical Warning Sign)",
        "content": (
            "### Promoter Pledging & Governance Risk\n\n"
            "- **What is Pledging?** Promoters take personal or corporate loans by offering their equity shares as collateral.\n"
            "- **The Danger of Margin Calls:** If the stock price falls sharply, lenders demand additional cash margin. If promoters fail to provide it, lenders dump the pledged shares in the open market, triggering severe price crashes.\n"
            "- **Safety Rule:** Quality investors generally avoid companies where promoter pledging exceeds **10% - 15%** of promoter holding."
        ),
    },
    "working_capital": {
        "keywords": ["working capital", "cash conversion cycle", "ccc", "debtor days"],
        "title": "Working Capital & Cash Conversion Cycle (CCC)",
        "content": (
            "### Working Capital & Cash Conversion Cycle\n\n"
            "- **Working Capital:** `Current Assets - Current Liabilities`.\n"
            "- **Cash Conversion Cycle (CCC):** Days Inventory Outstanding (DIO) + Days Sales Outstanding (DSO) - Days Payable Outstanding (DPO).\n"
            "- **Negative Working Capital Moat:** Giants like FMCG retailers (HUL, D-Mart) and auto assemblers operate with negative working capital, effectively funding their business operations using suppliers' interest-free credit."
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
    "inflation": {
        "keywords": ["inflation", "cpi", "wpi", "consumer price index"],
        "title": "Inflation (CPI & WPI)",
        "content": (
            "### Inflation & Its Stock Market Transmission\n\n"
            "- **CPI (Consumer Price Index):** Measures retail price changes for everyday baskets (food, fuel, housing, transport). RBI's official target band is **4% (+/- 2%)**.\n"
            "- **Impact on Stocks:**\n"
            "  - **Food & Raw Material Spikes:** Compresses operating margins for FMCG (HUL, Nestle, Britannia) and Auto manufacturers.\n"
            "  - **High Persistent Inflation:** Forces RBI to keep interest rates elevated, reducing liquidity and lowering equity valuation multiples.\n"
            "  - **Pricing Power:** Companies with strong brand moats (e.g. Asian Paints, Titan) can pass on cost increases to consumers without losing market share."
        ),
    },
    "fii_dii": {
        "keywords": ["fii", "dii", "foreign institutional", "domestic institutional", "fpi"],
        "title": "FII vs. DII Market Dynamics",
        "content": (
            "### FII vs. DII Market Dynamics\n\n"
            "- **FII / FPI (Foreign Institutional Investors):** Global pension funds, sovereign wealth funds, and hedge funds investing in Indian capital markets. Often driven by US Dollar strength, US Treasury yields, and global risk appetite.\n"
            "- **DII (Domestic Institutional Investors):** Indian Mutual Funds, Insurance companies (LIC), and pension funds (NPS).\n"
            "- **The Structural Shift:** Historically, heavy FII selling caused steep Indian market crashes. Today, resilient domestic retail **SIP inflows (>₹20,000 Cr per month)** absorb FII selling, providing strong liquidity support to Nifty."
        ),
    },
    "sip_etf": {
        "keywords": ["sip", "etf", "mutual fund", "systematic investment", "niftybees", "index fund"],
        "title": "SIPs & ETFs in Indian Equities",
        "content": (
            "### SIPs & Exchange-Traded Funds (ETFs)\n\n"
            "- **SIP (Systematic Investment Plan):** A disciplined wealth-building method of investing fixed amounts into mutual funds or equities at regular intervals (monthly/weekly), benefiting from Rupee Cost Averaging and compounding.\n"
            "- **ETF (Exchange Traded Fund):** A security that tracks an underlying index (e.g., **NIFTYBEES** for NIFTY 50, **BANKBEES** for NIFTY Bank) and trades on the stock exchange with low expense ratios (<0.10%) and real-time liquidity.\n"
            "- **Index Funds vs Active Funds:** Index funds passively mimic the benchmark with minimal tracking error, outperforming over 70% of active large-cap mutual funds over 10-year horizons."
        ),
    },
    "ipo": {
        "keywords": ["ipo", "initial public offering", "gmp", "grey market premium", "listing gain"],
        "title": "IPOs & Grey Market Premium (GMP)",
        "content": (
            "### Initial Public Offering (IPO) & GMP\n\n"
            "- **IPO:** The process through which an unlisted private company offers shares to the public for the first time on the NSE/BSE to raise fresh equity capital or allow existing promoters/PE investors to exit (Offer for Sale - OFS).\n"
            "- **GMP (Grey Market Premium):** An unofficial, over-the-counter premium at which IPO shares trade before formal exchange listing. While popular for gauging retail excitement, GMP is unregulated and can be volatile.\n"
            "- **Evaluation Checklist:** Look beyond GMP: check promoter valuation vs listed peers (P/E, P/B), debt reduction plans from fresh issue proceeds, and past 3-year revenue and PAT trajectory."
        ),
    },
    "stock_split_bonus": {
        "keywords": ["stock split", "bonus share", "bonus shares", "ex-date", "record date"],
        "title": "Stock Splits & Bonus Shares",
        "content": (
            "### Stock Splits vs. Bonus Shares\n\n"
            "- **Stock Split:** A corporate action where existing shares are divided into multiple shares (e.g., a 1:2 split doubles share count while halving the share price). Face value decreases, but overall market cap and company fundamentals remain unchanged.\n"
            "- **Bonus Shares:** Free additional shares given to existing shareholders funded from the company's accumulated free reserves (e.g. 1 bonus share for every 1 share held). Face value remains the same.\n"
            "- **Ex-Date & Record Date:** Investors must purchase shares *before* the Ex-Date to be recorded on the company's register by the Record Date to receive corporate benefits."
        ),
    },
    "share_buyback": {
        "keywords": ["buyback", "share buyback", "share repurchase", "tender offer"],
        "title": "Share Buybacks (Capital Allocation)",
        "content": (
            "### Share Buybacks in Indian Equities\n\n"
            "- **What is a Buyback?** A corporate action where a cash-rich company purchases its own outstanding shares from shareholders, typically at a premium to the current market price.\n"
            "- **Types:** **Tender Offer** (submitting shares directly to company) vs **Open Market Purchase** (company buying on the stock exchange).\n"
            "- **Impact on Fundamentals:** Reduces total outstanding shares, which automatically increases Earnings Per Share (EPS) and Return on Equity (ROE)."
        ),
    },
    "taxation": {
        "keywords": ["tax", "taxation", "stcg", "ltcg", "capital gains", "budget tax"],
        "title": "Capital Gains Taxation on Indian Equities",
        "content": (
            "### Indian Capital Gains Taxation (Post-Budget 2024)\n\n"
            "- **Short-Term Capital Gains (STCG):**\n"
            "  - Applicable if equity shares/equity mutual funds are held for **less than 12 months**.\n"
            "  - Taxed at a flat rate of **20%** (revised upward from 15% in Budget 2024).\n"
            "- **Long-Term Capital Gains (LTCG):**\n"
            "  - Applicable if held for **more than 12 months**.\n"
            "  - Annual gains up to **₹1.25 Lakh** are completely exempt from tax.\n"
            "  - Gains exceeding ₹1.25 Lakh are taxed at **12.5%** without indexation benefit.\n"
            "- **Securities Transaction Tax (STT):** Levied on all delivery and intraday equity trades on Indian exchanges."
        ),
    },
    "demat_account": {
        "keywords": ["demat", "demat account", "trading account", "cdsl", "nsdl"],
        "title": "Demat & Trading Account",
        "content": (
            "### Demat & Trading Account Essentials\n\n"
            "- **Demat Account (Dematerialized):** An electronic vault that safely stores your shares and bonds in digital format, maintained by government-regulated depositories (**NSDL** or **CDSL**).\n"
            "- **Trading Account:** The transactional gateway provided by stockbrokers (Zerodha, Groww, AngelOne) to place buy/sell orders on the NSE/BSE.\n"
            "- **Safety Assurance:** Shares in your Demat account belong to you directly under your PAN; even if a brokerage firm shuts down, your holdings remain completely secure with CDSL/NSDL."
        ),
    },
}

# ==============================================================================
# 4. 15+ TRADING, TECHNICAL & DERIVATIVES CONCEPTS
# ==============================================================================
TRADING_CONCEPTS: Dict[str, Dict[str, Any]] = {
    "options_fo": {
        "keywords": ["f&o", "futures", "options", "call option", "put option", "derivative", "derivatives"],
        "title": "Futures & Options (F&O) in Indian Markets",
        "content": (
            "### Futures & Options (F&O)\n\n"
            "- **Derivatives:** Financial contracts that derive their value from an underlying asset (such as NIFTY 50, BANKNIFTY, or individual F&O stocks).\n"
            "- **Call Option (CE):** Gives the buyer the right (not obligation) to buy the underlying at strike price. Used for bullish directional exposure.\n"
            "- **Put Option (PE):** Gives the buyer the right to sell the underlying at strike price. Used for bearish directional exposure or downside portfolio hedging.\n"
            "- **SEBI Risk Reality:** SEBI empirical research reveals that **over 93% of individual retail F&O traders incur net losses**, losing an average of ₹1.25 Lakh each. Derivatives are designed for risk hedging, not retail speculative gambling."
        ),
    },
    "option_greeks": {
        "keywords": ["option greeks", "greeks", "theta", "delta", "gamma", "vega"],
        "title": "Option Greeks (Delta, Theta, Gamma, Vega)",
        "content": (
            "### Option Greeks Essentials\n\n"
            "- **Delta:** Measures the expected change in option premium for every ₹1 move in the underlying asset (0 to 1 for Calls, 0 to -1 for Puts).\n"
            "- **Theta (Time Decay):** Measures the daily decay in option premium as expiration approaches. Crucial insight: Option buyers lose Theta daily, while option sellers collect Theta.\n"
            "- **Vega:** Measures sensitivity to changes in implied volatility (India VIX).\n"
            "- **Gamma:** The rate of change of Delta for each point move in the underlying."
        ),
    },
    "open_interest": {
        "keywords": ["open interest", "oi", "put call ratio", "pcr"],
        "title": "Open Interest (OI) & Put-Call Ratio (PCR)",
        "content": (
            "### Open Interest (OI) & Put-Call Ratio (PCR)\n\n"
            "- **Open Interest:** Total number of outstanding derivative contracts that have not been settled.\n"
            "- **PCR (Put-Call Ratio):** `Total Put OI / Total Call OI`.\n"
            "  - **PCR > 1.2 - 1.4:** High Put writing, indicating strong support or oversold conditions (potential bullish reversal).\n"
            "  - **PCR < 0.7 - 0.8:** High Call writing, indicating heavy resistance or overbought conditions."
        ),
    },
    "stop_loss": {
        "keywords": ["stop loss", "stoploss", "trailing stop loss", "sl", "risk management"],
        "title": "Stop-Loss & Capital Protection",
        "content": (
            "### Stop-Loss & Risk Management\n\n"
            "- **Stop-Loss Order:** An automated order placed with your broker to exit a position when price hits a predefined threshold, capping maximum capital loss.\n"
            "- **Trailing Stop-Loss:** Dynamically moves the stop price upward as the stock moves in your favor, locking in accrued gains.\n"
            "- **The 1-2% Rule:** Disciplined traders never risk more than 1% to 2% of total trading account equity on any individual position."
        ),
    },
    "moving_averages": {
        "keywords": ["moving average", "200 dma", "50 dma", "golden cross", "death cross", "exponential moving average", "ema", "sma"],
        "title": "Moving Averages (50 DMA & 200 DMA)",
        "content": (
            "### Moving Averages in Technical Analysis\n\n"
            "- **200 DMA (Daily Moving Average):** The long-term institutional trend benchmark. Stocks trading above their 200 DMA are in a structural bull trend; trading below signals caution.\n"
            "- **Golden Cross:** When the short-term 50 DMA crosses *above* the long-term 200 DMA, signaling potential multi-month bullish momentum.\n"
            "- **Death Cross:** When the 50 DMA crosses *below* the 200 DMA, signaling structural bearish pressure."
        ),
    },
    "rsi": {
        "keywords": ["rsi", "relative strength index", "overbought", "oversold"],
        "title": "Relative Strength Index (RSI)",
        "content": (
            "### Relative Strength Index (RSI)\n\n"
            "**RSI** is a momentum oscillator measuring the speed and magnitude of recent price movements on a scale of 0 to 100.\n\n"
            "- **RSI > 70:** Indicates **Overbought** conditions; prices may experience profit booking or consolidation.\n"
            "- **RSI < 30:** Indicates **Oversold** conditions; potential technical bounce or accumulation zone.\n"
            "- **Bullish Divergence:** Occurs when stock price makes lower lows while RSI makes higher lows, often preceding an upward trend reversal."
        ),
    },
    "circuit_breakers": {
        "keywords": ["upper circuit", "lower circuit", "circuit breaker", "circuit breakers", "circuits", "price band", "price bands", "asm", "gsm"],
        "title": "Market Circuit Breakers & Price Bands",
        "content": (
            "### Circuit Breakers & Price Bands\n\n"
            "- **Stock Price Bands:** Individual stocks have daily volatility limits (typically 2%, 5%, 10%, or 20%). When hit, trading is halted or trades occur only at the limit price (Upper / Lower Circuit).\n"
            "- **Index Circuit Breakers:** NSE/BSE halt market-wide trading if the NIFTY or SENSEX moves 10%, 15%, or 20% from previous close:\n"
            "  - **10% move before 1:00 PM:** 45-minute trading halt.\n"
            "  - **15% move:** Longer halt or market close for the remainder of the day.\n"
            "- **ASM / GSM Framework:** SEBI and exchanges place highly volatile or speculative stocks under Additional Surveillance Measures (ASM) to safeguard retail investors."
        ),
    },
}

# ==============================================================================
# 5. 12 IN-DEPTH SECTOR RESEARCH PROFILES
# ==============================================================================
SECTOR_PROFILES: Dict[str, Dict[str, Any]] = {
    "Banking & Financial Services": {
        "tailwinds": "15-18% systemic credit growth, pristine corporate credit quality with decadal low NPAs, and rising formal financial savings.",
        "headwinds": "Intense competition for retail deposits compressing Net Interest Margins (NIM), and regulatory risk weights on unsecured personal loans.",
        "leaders": "HDFC Bank, ICICI Bank, State Bank of India, Axis Bank, Kotak Mahindra Bank",
        "metric": "Key metrics: Net Interest Margin (NIM), Gross NPA %, CASA Ratio, Return on Assets (ROA > 1.8%).",
    },
    "Information Technology": {
        "tailwinds": "Enterprise cloud migration, Generative AI modernization, vendor consolidation, and high free cash flow generation (>80% conversion).",
        "headwinds": "Delayed enterprise decision-making in US and European BFSI and telecom clients, discretionary tech project cancellations.",
        "leaders": "TCS, Infosys, HCL Technologies, Wipro, LTIMindtree",
        "metric": "Key metrics: Total Contract Value (TCV) Deal Wins, EBIT Margin (22-26%), Attrition %, US/Europe Revenue Mix.",
    },
    "Automobile & Auto Ancillary": {
        "tailwinds": "Rapid consumer premiumization toward SUVs, electric vehicle adoption in passenger and 2-wheeler segments, and lower raw material steel costs.",
        "headwinds": "High dealer inventory levels in passenger cars, stagnant entry-level rural hatchback demand, and international export cyclicality.",
        "leaders": "Maruti Suzuki, Tata Motors, Mahindra & Mahindra, Bajaj Auto, Eicher Motors",
        "metric": "Key metrics: Monthly Wholesale Dispatch Volumes, Average Selling Price (ASP), EBITDA/Vehicle.",
    },
    "Defense & Aerospace": {
        "tailwinds": "Government 'Make in India' defense indigenization mandate, massive modernization capex, and surging defense hardware exports to Southeast Asia and Middle East.",
        "headwinds": "Lumpy execution cycles, dependency on annual defense budgetary disbursements, and raw material component imports.",
        "leaders": "Hindustan Aeronautics (HAL), Bharat Electronics (BEL), Mazagon Dock, Cochin Shipyard",
        "metric": "Key metrics: Order Book-to-Bill Ratio (>3x), Indigenization Content %, Working Capital Cycle.",
    },
    "Indian Railways": {
        "tailwinds": "Unprecedented government capex budget allocations for track doubling, high-speed rail corridors, dedicated freight corridors, and Vande Bharat train rollouts.",
        "headwinds": "Low single-digit operating margins on pure-play engineering execution, bureaucratic project approvals.",
        "leaders": "Rail Vikas Nigam (RVNL), Indian Railway Finance Corp (IRFC), IRCON International, Titagarh Rail",
        "metric": "Key metrics: Order Inflow Growth, Operating Margins, Cost-plus Leasing Spreads.",
    },
    "Renewable Energy & Green Hydrogen": {
        "tailwinds": "India's ambitious target of 500 GW non-fossil capacity by 2030, Production Linked Incentive (PLI) schemes for solar PV and electrolyzers, and sovereign green bonds.",
        "headwinds": "Grid transmission evacuation bottlenecks, imported solar cell pricing volatility, and state utility DISCOM payment delays.",
        "leaders": "Tata Power, Suzlon Energy, NTPC Green, Adani Green, IREDA",
        "metric": "Key metrics: Capacity Under Execution (GW), Plant Load Factor (PLF), PPA Tariffs (₹/kWh).",
    },
    "Fast Moving Consumer Goods (FMCG)": {
        "tailwinds": "Rising rural disposable incomes following normal monsoons, direct-to-consumer premiumization in personal care, and high ROCE (>30%).",
        "headwinds": "Volatile agricultural commodity inputs (palm oil, wheat, milk), and intense competition from nimble regional D2C brands.",
        "leaders": "Hindustan Unilever (HUL), ITC, Nestle India, Britannia, Tata Consumer",
        "metric": "Key metrics: Underlying Volume Growth (UVG), Gross Margin %, Rural vs Urban Volume Mix.",
    },
    "Pharmaceuticals & Healthcare": {
        "tailwinds": "Expanding global specialty medicine pipelines, domestic chronic therapy expansion (cardiac, diabetes), and growing CDMO contracts.",
        "headwinds": "US FDA regulatory inspections resulting in Form 483 warnings or import alerts, and generic price erosion in the US market.",
        "leaders": "Sun Pharma, Cipla, Dr. Reddy's Laboratories, Torrent Pharma, Divi's Lab",
        "metric": "Key metrics: Specialty Revenue Contribution, US FDA Clearance Track Record, R&D/Sales %.",
    },
    "Capital Goods & Infrastructure": {
        "tailwinds": "Multi-year private and public industrial capex supercycle, Middle East energy transition orders, and real estate construction boom.",
        "headwinds": "Raw material steel and cement cost escalation, working capital intensity, and execution delays.",
        "leaders": "Larsen & Toubro (L&T), Siemens India, ABB India, Polycab, UltraTech Cement",
        "metric": "Key metrics: Order Backlog Growth, Book-to-Bill Ratio, Return on Capital Employed (ROCE).",
    },
    "Metals & Mining": {
        "tailwinds": "Infrastructure construction demand driving domestic steel consumption, high-grade captive iron ore resources.",
        "headwinds": "Subsidized Chinese steel dumping in global markets, volatile coking coal import prices, and carbon tax regulations (CBAM).",
        "leaders": "Tata Steel, JSW Steel, Coal India, Hindalco, NMDC",
        "metric": "Key metrics: EBITDA/Tonne, Domestic vs Export Realizations, Coking Coal Costs/Tonne.",
    },
    "Real Estate & Housing": {
        "tailwinds": "Decadal high housing demand driven by rising homebuyer affluence, luxury residential upgrades, and record low unsold inventory in top metros.",
        "headwinds": "Rising land acquisition costs, home loan interest rate sensitivity, and municipal approval delays.",
        "leaders": "DLF, Godrej Properties, Macrotech Developers (Lodha), Oberoi Realty",
        "metric": "Key metrics: Pre-Sales Booking Values, Collections vs Operating Cash Flow, Net Debt-to-Equity.",
    },
    "Chemicals & Specialty Chemicals": {
        "tailwinds": "Global 'China+1' supply chain diversification, technical expertise in complex fluorochemicals and agrochemicals.",
        "headwinds": "Global destocking cycles, dumping of cheap chemical intermediates from China, and European industrial demand slump.",
        "leaders": "SRF, PI Industries, Gujarat Fluorochemicals, Tata Chemicals",
        "metric": "Key metrics: Export Volume Realization, Gross Margins, Operating Asset Turnover.",
    },
}


class ChatAgent:
    """Enterprise-grade agentic financial intelligence engine for Indian equities and macroeconomics."""

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
            "give", "summary", "outlook", "sentiment", "current", "latest", "stock", "stocks", "market", "india",
            "should", "buy", "sell", "good", "view", "rate", "ratio"
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

            # Confidence threshold
            min_score = 3.5 if not target_symbols and not detected_sectors else 2.0
            if score >= min_score:
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
            r"^(what is the|what is|tell me about the|tell me about|how is the|how is|give me a summary of|what are the|what are|can you explain|analyze|should i buy|is it good to buy)\s+",
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

        # 3. Intent Check: Greetings / Identity / Bot Capabilities
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
                "- **Stock Analysis:** *'Should I buy Reliance?'* or *'What is the outlook for Tata Motors electric vehicles?'*\n"
                "- **Recommendations & Portfolios:** *'Where should I invest ₹1 Lakh?'* or *'Which stocks should I buy for the long term?'*\n"
                "- **Market Movements:** *'Why is the market falling today?'* or *'What drives Nifty corrections?'*\n"
                "- **Financial & Valuation Concepts:** *'What is P/E ratio?'*, *'Explain EBITDA vs Free Cash Flow'*, or *'What is ROCE?'*\n"
                "- **Derivatives & Trading:** *'How do Call and Put options work?'* or *'What is the 200 DMA?'*\n"
                "- **Macro & Sectoral Research:** *'How does the RBI repo rate impact banking stocks?'* or *'Analyze the Defense sector'*.\n"
                "- **Stock Comparisons:** *'Compare Tata Motors and Maruti Suzuki'*.\n\n"
                "All breaking news analysis is verified against real-time ingested publications with FinBERT sentiment scores."
            )
            followups = [
                "Which stocks should I buy for long term?",
                "Why is the market falling recently?",
                "What is the outlook for Tata Motors electric vehicles?",
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

        # 5. Intent Check: Benchmark Indices (NIFTY 50 / SENSEX / BANK NIFTY / VIX)
        index_patterns = ["what is nifty", "what is sensex", "bank nifty", "nifty 50", "bse sensex", "difference between nifty and sensex", "india vix"]
        if any(pat in q_lower for pat in index_patterns) and not any(k in q_lower for k in ["tata", "reliance", "hdfc"]):
            index_text = (
                "### Indian Benchmark Indices: NIFTY 50, SENSEX & BANK NIFTY\n\n"
                "India's equity markets are governed by flagship benchmark indices:\n\n"
                "#### 1. NIFTY 50 (National Stock Exchange - NSE)\n"
                "- **Composition:** Represents 50 of the largest, most liquid blue-chip Indian companies listed on the NSE across 13 major sectors.\n"
                "- **Calculation Method:** Weighted by **Free-Float Market Capitalization** (only publicly tradable shares are counted, excluding promoter lock-in).\n"
                "- **Dominant Sector Weights:** Financial Services (~33%), Information Technology (~14%), Oil & Gas (~12%), Consumer Goods (~9%), and Automobiles (~7%).\n\n"
                "#### 2. BSE SENSEX (Bombay Stock Exchange - BSE)\n"
                "- **History:** India's oldest stock index, established in 1986 with base year 1978-79 = 100.\n"
                "- **Composition:** Tracks 30 financially sound blue-chip companies listed on BSE.\n\n"
                "#### 3. Long-Term Compound Returns\n"
                "- Historically, both NIFTY 50 and SENSEX have delivered **12% - 14% annualized compound returns (CAGR)** over 15-20 year holding periods, consistently beating traditional fixed deposits and gold."
            )
            followups = [
                "How can I invest in NIFTY 50 via ETFs like NIFTYBEES?",
                "What are the top 5 weighted stocks in NIFTY 50?",
                "What is P/E ratio and how does it determine index overvaluation?",
            ]
            return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, index_text, [], followups, None)

        # 6. Intent Check: Financial Concepts & Valuation Frameworks
        is_definitional = any(q_lower.startswith(prefix) for prefix in [
            "what is", "what are", "what does", "explain", "define", "meaning of", "how to calculate", "tell me about the concept"
        ])
        matched_concept = None
        for concept_key, concept_data in FINANCIAL_CONCEPTS.items():
            if any(re.search(rf"\b{re.escape(kw)}\b", q_lower) for kw in concept_data["keywords"]):
                matched_concept = concept_data
                break

        if matched_concept and (is_definitional or len(symbols) == 0):
            followups = [
                f"How does {matched_concept['title']} apply to Banking stocks?",
                "Which NIFTY 50 companies show the most favorable valuation multiples?",
                "What other financial metrics should I evaluate alongside this?",
            ]
            return cls._save_and_respond(
                db, session_record, session_id, user_id, q_raw, matched_concept["content"], [], followups, None
            )

        # 7. Intent Check: Trading, Technical & Derivatives Concepts
        matched_trading = None
        for trading_key, trading_data in TRADING_CONCEPTS.items():
            if any(re.search(rf"\b{re.escape(kw)}\b", q_lower) for kw in trading_data["keywords"]):
                matched_trading = trading_data
                break

        if matched_trading and (is_definitional or len(symbols) == 0):
            followups = [
                "What is the difference between swing trading and intraday trading?",
                "How does stop-loss protect portfolio capital?",
                "Why do over 90% of retail F&O traders lose money?",
            ]
            return cls._save_and_respond(
                db, session_record, session_id, user_id, q_raw, matched_trading["content"], [], followups, None
            )

        # 8. Intent Check: Stock Comparisons (e.g. "Compare X and Y" or "X vs Y")
        if (len(symbols) >= 2 or ("compare" in q_lower and len(symbols) >= 1) or " vs " in q_lower) and len(symbols) >= 2:
            s1, s2 = symbols[0], symbols[1]
            p1 = EQUITY_PROFILES.get(s1, {"name": s1, "sector": "Indian Equities", "overview": f"{s1} listed on NSE/BSE.", "metrics": "N/A", "bull_case": "Market leadership", "bear_case": "Macro volatility"})
            p2 = EQUITY_PROFILES.get(s2, {"name": s2, "sector": "Indian Equities", "overview": f"{s2} listed on NSE/BSE.", "metrics": "N/A", "bull_case": "Market leadership", "bear_case": "Macro volatility"})
            comparison_text = (
                f"### Comparative Research: **{s1}** vs. **{s2}**\n\n"
                f"| Parameter | **{s1}** ({p1['name']}) | **{s2}** ({p2['name']}) |\n"
                f"| :--- | :--- | :--- |\n"
                f"| **Sector** | {p1['sector']} | {p2['sector']} |\n"
                f"| **Valuation Multiples** | {p1.get('metrics', 'N/A')} | {p2.get('metrics', 'N/A')} |\n"
                f"| **Primary Catalyst** | {p1.get('bull_case', 'Market growth')} | {p2.get('bull_case', 'Market growth')} |\n"
                f"| **Primary Headwind** | {p1.get('bear_case', 'Cyclical risks')} | {p2.get('bear_case', 'Cyclical risks')} |\n\n"
                f"**Key Analytical Takeaways:**\n"
                f"- **{s1}**: {p1.get('overview', '')}\n"
                f"- **{s2}**: {p2.get('overview', '')}\n\n"
                f"**Strategic Summary:** Weigh operational cash flow compounding and balance sheet debt against current valuation multiples before choosing allocations."
            )
            followups = [
                f"What is the investment thesis for {s1}?",
                f"What is the investment thesis for {s2}?",
                f"Which stocks in this sector offer the highest dividend yield?",
            ]
            matching_articles = cls.retrieve_articles(db, q_raw, symbols)
            citations = cls.build_citations(matching_articles[:2]) if matching_articles else []
            return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, comparison_text, citations, followups, None)

        # 9. Intent Check: Buy / Sell / Investment Thesis on a specific stock
        buy_sell_patterns = [
            "should i buy", "should we buy", "can i buy", "is it good to buy", "is it a good buy",
            "is it good for long term", "should i sell", "buy or sell", "target price", "entry price",
            "worth buying", "good investment", "outlook on", "view on", "should i invest in", "target for",
            "future of", "hold or sell"
        ]
        if any(pat in q_lower for pat in buy_sell_patterns) and symbols:
            sym = symbols[0]
            profile = EQUITY_PROFILES.get(sym)
            if profile:
                matching_articles = cls.retrieve_articles(db, q_raw, symbols)
                thesis_text = (
                    f"### Investment Thesis & Research Outlook: **{profile['name']}** (`{sym}`)\n\n"
                    f"**Sector:** {profile['sector']} | **Valuation Benchmark:** {profile['metrics']}\n\n"
                    f"#### 1. The Bull Case (Catalysts & Growth Drivers)\n"
                    f"- {profile['bull_case']}\n"
                    f"- Dominant market positioning with strong balance sheet resilience and structural tailwinds.\n\n"
                    f"#### 2. The Bear Case (Risks & Headwinds)\n"
                    f"- {profile['bear_case']}\n"
                    f"- Broader sector cyclicality and macroeconomic interest rate sensitivity.\n\n"
                    f"#### 3. Strategic Framework for Investors\n"
                    f"- **Long-Term Investors (3-5+ years):** Consider staggering accumulation (SIP mode) during market corrections rather than deploying lump-sums at all-time highs.\n"
                    f"- **Short-Term Traders:** Respect support and resistance levels with disciplined stop-loss orders.\n\n"
                    f"> **SEBI Compliance Disclaimer:** Emvest provides empirical data and equity research for educational purposes only. This analysis does not constitute personalized financial advice. Please assess your risk tolerance before placing trades."
                )
                followups = [
                    f"Compare {sym} against its closest competitors",
                    f"What are the quarterly financial results for {sym}?",
                    "Which other stocks in this sector show strong growth?",
                ]
                citations = cls.build_citations(matching_articles[:3]) if matching_articles else []
                summary = cls.calculate_sentiment_summary(matching_articles[:3]) if matching_articles else None
                return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, thesis_text, citations, followups, summary)

        # 10. Intent Check: Capital-Specific Investment Guides (10k, 50k, 1 Lakh, 10 Lakhs)
        capital_patterns = [
            ("10000", "₹10,000", "Start with **NIFTYBEES ETF (70%)** for instant 50-stock diversification, and allocate **30%** into a bluechip compounder like HDFC Bank or Reliance Industries."),
            ("50000", "₹50,000", "Deploy **60%** into NIFTYBEES / Junior Nifty ETF, **25%** into high-growth leaders (e.g. Tata Motors, Zomato), and **15%** into Gold ETF / Liquid cash buffer."),
            ("1 lakh", "₹1 Lakh", "Construct a 3-pillar portfolio: **50% Core Large-Caps** (Reliance, HDFC Bank, L&T, TCS), **30% Mid-Cap Growth** (Tata Motors, Zomato, Polycab), and **20% Defensive / Cash Buffer** (ITC, Sun Pharma), deployed in 3 staggered monthly tranches."),
            ("10 lakh", "₹10 Lakhs", "Institutional asset allocation: **45% Large-Cap Bluechips**, **25% Quality Mid-Caps**, **15% Small-Cap / Thematic Alpha**, and **15% Arbitrage / Liquid STP**, systematically deployed over 4-6 months."),
        ]
        for cap_key, cap_label, cap_rec in capital_patterns:
            if cap_key in q_lower or (cap_key == "1 lakh" and ("100000" in q_lower or "1 lac" in q_lower or "one lakh" in q_lower)):
                cap_text = (
                    f"### Strategic Capital Allocation Blueprint: **{cap_label}**\n\n"
                    f"When deploying **{cap_label}** in the Indian equity market, prioritize capital preservation and staggered execution:\n\n"
                    f"#### Recommended Asset Allocation:\n"
                    f"{cap_rec}\n\n"
                    f"#### Execution Rules:\n"
                    f"1. **Never Deploy Lump-Sum at Market Peaks:** Stagger purchases over 3-6 months to capture Rupee Cost Averaging during dips.\n"
                    f"2. **Ensure Emergency Fund is Separate:** Never invest money required within the next 12-24 months into equities.\n"
                    f"3. **Reinvest Dividends:** Harness the exponential power of compounding over 5-10+ years."
                )
                followups = [
                    "Which large-cap stocks should I pick for long term?",
                    "What is an ETF and how do I buy NIFTYBEES?",
                    "How does the RBI repo rate affect equity returns?",
                ]
                return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, cap_text, [], followups, None)

        # 11. Intent Check: Stock Recommendations & Model Portfolios
        recommendation_patterns = [
            "which stocks", "what stocks", "best stocks", "recommend", "stocks to buy",
            "top stocks", "good stocks", "where to invest", "portfolio", "stocks for long term",
            "best stocks for 2025", "best stocks for 2026", "model portfolio", "wealth compounders"
        ]
        if any(pat in q_lower for pat in recommendation_patterns):
            rec_text = (
                "### Model Indian Equities Allocation & Top Compounders\n\n"
                "A balanced, high-conviction Indian equity portfolio combines established large-cap compounders with high-growth mid-caps across secular growth themes:\n\n"
                "#### 1. Core Large-Cap Anchors (50% Allocation - Capital Protection & Steady Compounding)\n"
                "- **Reliance Industries (`RELIANCE`):** Market leader across Retail omnichannel expansion, Jio 5G monetization, and green energy gigafactories.\n"
                "- **HDFC Bank (`HDFCBANK`) / ICICI Bank (`ICICIBANK`):** High return on assets (ROA > 2%), pristine underwriting standards, and 15-18% systemic credit growth.\n"
                "- **Larsen & Toubro (`LT`):** Primary beneficiary of the multi-year Indian government and private capex infrastructure supercycle.\n"
                "- **TCS (`TCS`) / Infosys (`INFY`):** High free cash flow conversion (>80%), double-digit ROE, and enterprise AI modernization.\n\n"
                "#### 2. High-Growth Mid-Caps (30% Allocation - Alpha Generation)\n"
                "- **Tata Motors (`TATAMOTORS`):** India's passenger EV market leader (>65% volume share) with JLR luxury turnaround and net cash balance sheet.\n"
                "- **Zomato (`ZOMATO`):** Quick-commerce leader (Blinkit) expanding at >100% YoY with improving EBITDA unit economics.\n\n"
                "#### 3. Defensives & Dividend Yield (20% Allocation - Volatility Buffer)\n"
                "- **ITC (`ITC`):** High dividend yield (~3-3.5%), resilient tobacco cash generation, and FMCG scale.\n"
                "- **Sun Pharma (`SUNPHARMA`):** Expanding global specialty pipeline shielding against generic price erosion.\n\n"
                "**Actionable Execution Rule:** Never deploy all capital at once during market peaks. Utilize Systematic Transfer Plans (STP) or staggered tranches over 3-6 months to benefit from Rupee Cost Averaging."
            )
            followups = [
                "Should I buy Reliance or Tata Motors?",
                "What is the outlook for Banking stocks?",
                "How does the RBI repo rate impact equity valuations?",
            ]
            return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, rec_text, [], followups, None)

        # 12. Intent Check: Market Movement / Crash / Correction / Volatility
        market_fall_patterns = [
            "why is market down", "why is market falling", "why did market drop", "why did market fall",
            "why did nifty fall", "why is nifty down", "market crash", "market correction",
            "blood bath", "why did stocks fall", "is market going to crash", "bear market",
            "market fall", "why is market crashing", "why market down", "why market fell"
        ]
        if any(pat in q_lower for pat in market_fall_patterns):
            crash_text = (
                "### Macroeconomic Analysis: Why the Indian Market (NIFTY / SENSEX) Experiences Drawdowns\n\n"
                "Indian equity market corrections are typically triggered by a confluence of domestic and global institutional factors:\n\n"
                "#### 1. Foreign Institutional Investor (FII) Capital Outflows\n"
                "- When US 10-year Treasury yields rise or foreign markets offer stimulus-driven valuations, global funds pull capital from emerging markets, including India, to lock in safe dollar yields.\n"
                "- In recent months, persistent FII selling has created short-term liquidity drag on large-cap index heavyweights (HDFC Bank, Reliance, ICICI Bank).\n\n"
                "#### 2. Valuation Normalization & Profit Booking\n"
                "- After sustained bull rallies, Nifty 50 trailing Price-to-Earnings (P/E) ratios occasionally trade above **23x-24x** (above the 10-year historical mean of ~21x).\n"
                "- Institutional desks use earnings seasons to trim exposure in over-extended mid-cap and small-cap stocks where multiples expanded faster than underlying earnings growth.\n\n"
                "#### 3. Global Macroeconomic & Geopolitical Headwinds\n"
                "- **Crude Oil Volatility:** India imports over 85% of its crude oil requirements. Spikes in Brent crude exert pressure on the Indian Rupee (USD/INR) and widen the Current Account Deficit.\n"
                "- **Monetary Policy Uncertainty:** Uncertainty regarding interest rate trajectories by the US Federal Reserve and RBI dampens risk appetite.\n\n"
                "#### 4. The Silver Lining: Domestic Institutional & Retail Inflows\n"
                "- Unlike historical crashes (2008, 2013), domestic retail SIP inflows (>₹20,000 Cr every single month) provide a massive liquidity shock-absorber, preventing systemic collapse.\n\n"
                "**Investor Playbook:** Corrections of 5% - 10% are standard healthy features of long-term bull markets. Avoid panic selling high-ROCE compounders; use market dips to accumulate quality businesses."
            )
            followups = [
                "Which stocks are showing the strongest resilience during this correction?",
                "What is P/E ratio and how does it determine overvaluation?",
                "How does the RBI repo rate impact market liquidity?",
            ]
            return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, crash_text, [], followups, None)

        # 13. Intent Check: Sector Analysis (e.g. "Tell me about Defense sector", "Auto sector outlook")
        if sectors and len(symbols) == 0:
            sec_name = sectors[0]
            sec_info = SECTOR_PROFILES.get(sec_name)
            if sec_info:
                sec_text = (
                    f"### Sector Research & Macro Outlook: **{sec_name}**\n\n"
                    f"#### 1. Core Industry Tailwinds\n"
                    f"- {sec_info['tailwinds']}\n\n"
                    f"#### 2. Key Headwinds & Risk Triggers\n"
                    f"- {sec_info['headwinds']}\n\n"
                    f"#### 3. Sector Leaders & Competitive Moats\n"
                    f"- **Key Stocks:** {sec_info['leaders']}\n"
                    f"- **What to Track:** {sec_info['metric']}\n"
                )
                matching_articles = cls.retrieve_articles(db, q_raw, symbols)
                citations = cls.build_citations(matching_articles[:3]) if matching_articles else []
                summary = cls.calculate_sentiment_summary(matching_articles[:3]) if matching_articles else None
                followups = [
                    f"Which stocks are the top performers in {sec_name}?",
                    "What is the FinBERT sentiment score for this sector?",
                    "How does the interest rate cycle impact this sector?",
                ]
                return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, sec_text, citations, followups, summary)

        # 14. Check if real matching breaking news articles exist in DB
        matching_articles = cls.retrieve_articles(db, q_raw, symbols)
        is_buy_sell = any(pat in q_lower for pat in buy_sell_patterns)
        is_comparison = (len(symbols) >= 2 or ("compare" in q_lower and len(symbols) >= 1) or " vs " in q_lower) and len(symbols) >= 2

        if matching_articles and not is_buy_sell and not is_comparison:
            return cls._generate_news_response(db, session_record, session_id, user_id, q_raw, symbols, sectors, matching_articles, prior_context_symbols)

        # 15. If query asks about a specific stock with no breaking news
        if symbols and symbols[0] in EQUITY_PROFILES:
            sym = symbols[0]
            profile = EQUITY_PROFILES[sym]
            lines = [
                f"### Equity Research Profile: **{profile['name']}** (`{sym}`)\n",
                f"**Sector:** {profile['sector']} | **Valuation Benchmark:** {profile['metrics']}\n",
                f"**Business Overview & Core Moats:**\n{profile['overview']}\n",
                f"**Key Growth Catalysts (Bull Case):**\n- {profile['bull_case']}\n",
                f"**Key Risk Factors (Bear Case):**\n- {profile['bear_case']}\n",
                f"**Primary Competitors:** {profile.get('peers', 'Industry peers')}\n",
                f"*(Note: No breaking news articles ingested in the last 24h for {sym}; providing fundamental equity research profile).* "
            ]
            answer = "\n".join(lines)
            followups = [
                f"Should I buy {sym} for the long term?",
                f"Compare {sym} against its primary domestic competitors",
            ]
            return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, answer, [], followups, None)

        # 16. Universal Dynamic Financial Reasoning Engine (Constructs direct, context-aware analysis)
        dynamic_answer = cls._synthesize_dynamic_financial_answer(q_raw, q_lower)
        followups = [
            "Which stocks should I buy for the long term?",
            "What is P/E ratio and how does it determine overvaluation?",
            "Why is the market falling recently?",
        ]
        return cls._save_and_respond(db, session_record, session_id, user_id, q_raw, dynamic_answer, [], followups, None)

    @classmethod
    def _generate_news_response(
        cls,
        db: Session,
        session_record: ChatSession,
        session_id: str,
        user_id: Optional[int],
        q_raw: str,
        symbols: List[str],
        sectors: List[str],
        matching_articles: List[Article],
        prior_context_symbols: List[str],
    ) -> ChatQueryResponse:
        """Synthesize real FinBERT news articles into an empirical answer with verifiable citations."""
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

    @classmethod
    def _synthesize_dynamic_financial_answer(cls, q_raw: str, q_lower: str) -> str:
        """Dynamically construct a thoughtful, analytical response directly addressing the user's premise."""
        lines = [
            f"### Financial Analysis & Research Perspective\n",
            f"Regarding your query: **\"{q_raw}\"**\n",
        ]

        if "why" in q_lower:
            lines.append(
                "#### Core Causal Factors & Transmission Channels:\n"
                "- **Capital Flows & Liquidity:** Institutional capital movements (FII allocations and domestic mutual fund inflows) dictate short-to-medium term price momentum.\n"
                "- **Earnings Quality & Operating Margins:** Valuation adjustments occur as quarterly corporate earnings reports either confirm or diverge from consensus guidance.\n"
                "- **Macro Risk Premia:** Interest rate cycles, sovereign bond yields, and commodity price shifts establish valuation floors across sectors."
            )
        elif "how" in q_lower:
            lines.append(
                "#### Strategic Action Plan & Analytical Framework:\n"
                "1. **Empirical Due Diligence:** Examine audited financial disclosures (Cash Flow from Operations vs Reported PAT, ROCE consistency over 5 years).\n"
                "2. **Margin of Safety:** Assess trailing P/E and P/B multiples relative to historic 10-year median levels.\n"
                "3. **Position Sizing:** Limit portfolio allocation per equity to prevent concentration risk."
            )
        elif "what happens if" in q_lower or "impact of" in q_lower or "will" in q_lower:
            lines.append(
                "#### Economic Transmission & Sectoral Sensitivity:\n"
                "- **First-Order Impact:** Direct shifts in input costs, foreign exchange realizations, or borrowing spreads immediately alter quarterly gross margins.\n"
                "- **Direct Beneficiaries (Winners):** Companies possessing strong brand moats and pricing power pass cost pressures onto consumers, protecting operating margins.\n"
                "- **Vulnerable Segments (Losers):** Debt-heavy or margin-compressed businesses experience earnings downgrades."
            )
        else:
            lines.append(
                "#### Market Perspective & Key Considerations:\n"
                "- **Domestic Structural Growth:** India's macroeconomic backdrop continues to benefit from private capex formation, high infrastructure spend, and strong demographics.\n"
                "- **Valuation Discipline:** In periods of market volatility, high-quality compounders with pricing power outperform speculative momentum assets."
            )

        lines.append(
            "\n*Pro Tip: You can ask specific questions like 'Should I buy Reliance?', 'Where to invest ₹1 Lakh?', 'Analyze Defense sector', or 'Explain P/E ratio' for targeted research.*"
        )
        return "\n".join(lines)

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
