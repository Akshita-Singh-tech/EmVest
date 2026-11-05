import type { NewsArticle, NewsFilterOptions } from '../types/news'

export const sampleArticles: NewsArticle[] = [
  {
    id: 'art-1',
    title: 'RBI Monetary Policy Committee maintains repo rate at 6.5%, signals accommodative stance',
    summary: 'The central bank opted to retain key interest rates while highlighting resilient domestic economic momentum and controlled core inflation trajectory.',
    content: [
      'The Reserve Bank of India’s Monetary Policy Committee (MPC) unanimously decided to keep the benchmark repo rate unchanged at 6.50% for the tenth consecutive meeting, maintaining an accommodative liquidity stance.',
      'Governor Shaktikanta Das noted that while food price volatility warrants continuous vigilance, underlying core inflation has moderated sustainably within the target band of 4% (+/- 2%). Domestic consumption and high-frequency indicators such as GST collections, power consumption, and credit growth continue to demonstrate strong economic fundamentals.',
      'Banking analysts anticipate that stable repo rates will protect Net Interest Margins (NIMs) for private lenders, allowing them to balance credit disbursement with steady deposit mobilization in the upcoming fiscal quarters.',
    ],
    source: 'LiveMint',
    publishedAt: '25 mins ago',
    readTime: '3 min read',
    url: 'https://www.livemint.com',
    sector: 'Banking & Macro',
    symbols: ['HDFCBANK', 'SBIN', 'ICICIBANK', 'KOTAKBANK'],
    sentiment: 'Positive',
    sentimentScore: 0.82,
    sentimentConfidence: 94,
    keyTakeaways: [
      'Repo rate held steady at 6.50% by unanimous MPC vote.',
      'Core inflation remains well-anchored within the target tolerance band.',
      'Supportive environment for bank lending margins and bond market yields.',
    ],
    marketImpact: 'Bullish for large private and PSU banks; credit growth outlook reaffirmed at 14-16% YoY.',
  },
  {
    id: 'art-2',
    title: 'Tata Motors passenger EV registrations climb 18% YoY in October festive sales surge',
    summary: 'Strong demand for Punch.ev and Nexon.ev helped consolidate domestic EV market share above 65%, driven by expanding charging infrastructure.',
    content: [
      'Tata Motors Passenger Vehicles reported a robust 18% year-on-year increase in retail electric vehicle registrations during October, spurred by festive demand and rapid urban adoption.',
      'The newly launched Punch.ev emerged as the highest-selling electric compact SUV in India, complementing strong replacement volumes for the flagship Nexon.ev across Tier-1 and Tier-2 metropolitan hubs.',
      'Management emphasized that localized battery cell assembly partnerships and dedicated EV showroom rollouts have significantly lowered ownership barriers, reinforcing the company’s target to achieve positive operational EBITDA across the e-mobility division by FY26.',
    ],
    source: 'Economic Times',
    publishedAt: '1 hour ago',
    readTime: '4 min read',
    url: 'https://economictimes.indiatimes.com',
    sector: 'Automobile',
    symbols: ['TATAMOTORS', 'M&M'],
    sentiment: 'Positive',
    sentimentScore: 0.76,
    sentimentConfidence: 91,
    keyTakeaways: [
      'Domestic passenger EV registrations up 18% YoY during festive month.',
      'EV market share sustained solidly above 65%.',
      'Punch.ev driving penetration in suburban and Tier-2 markets.',
    ],
    marketImpact: 'Bullish for Tata Motors equity; reinforces leadership ahead of rival EV launches.',
  },
  {
    id: 'art-3',
    title: 'IT services sector anticipates cautious Q4 client guidance amid deferred discretionary tech spends',
    summary: 'Tier-1 technology majors report extended deal decision cycles as BFSI and retail enterprise clients optimize existing cloud infrastructure budgets.',
    content: [
      'Leading Indian IT services firms, including Infosys, TCS, and Wipro, have signaled a measured revenue growth trajectory for the upcoming fourth quarter as corporate clients across the US and Europe scrutinize discretionary software spending.',
      'While cost-takeout and vendor consolidation contracts remain active, greenfield digital transformation initiatives have experienced deferrals. BFSI and healthcare verticals continue to show selective resilience.',
      'Analysts point out that although generative AI advisory mandates are scaling rapidly, they currently constitute a modest portion of total contract value (TCV), leaving near-term margin expansion constrained by wage revisions and subcontractor costs.',
    ],
    source: 'Moneycontrol',
    publishedAt: '2 hours ago',
    readTime: '5 min read',
    url: 'https://www.moneycontrol.com',
    sector: 'Information Tech',
    symbols: ['INFY', 'TCS', 'WIPRO', 'HCLTECH'],
    sentiment: 'Negative',
    sentimentScore: -0.42,
    sentimentConfidence: 87,
    keyTakeaways: [
      'Discretionary cloud and software spends facing extended review cycles.',
      'GenAI deal pipeline growing rapidly but represents low initial revenue contribution.',
      'EBIT margin expansion likely muted over the next 1-2 quarters.',
    ],
    marketImpact: 'Cautious / Bearish near-term bias for NIFTY IT index; potential valuation multiple contraction.',
  },
  {
    id: 'art-4',
    title: 'Reliance Retail expands omnichannel distribution footprint with 120 new store additions',
    summary: 'Accelerated expansion in Tier-2 and Tier-3 cities expected to unlock higher operating leverage and expand consumer electronics and grocery fulfillment.',
    content: [
      'Reliance Retail Ventures Limited (RRVL) announced the operational rollout of 120 new retail storefronts across consumer electronics, fashion, and grocery formats during the last quarter.',
      'The company’s digital integration with JioMart has scaled daily order fulfillment capacity by 22%, leveraging dark-store micro-fulfillment centers embedded within existing supermarket footprints.',
      'Institutional brokerages highlighted that the aggressive retail buildout strengthens EBITDA margins through higher private-label penetration, positioning the retail subsidiary favorably for potential equity value-unlocking events.',
    ],
    source: 'Business Standard',
    publishedAt: '4 hours ago',
    readTime: '3 min read',
    url: 'https://www.business-standard.com',
    sector: 'Retail & Conglomerate',
    symbols: ['RELIANCE'],
    sentiment: 'Positive',
    sentimentScore: 0.69,
    sentimentConfidence: 89,
    keyTakeaways: [
      '120 new storefronts opened across Tier-2/3 regional markets.',
      'JioMart omnichannel fulfillment capacity expanded by 22%.',
      'Positive operational leverage enhancing retail segmental EBITDA.',
    ],
    marketImpact: 'Bullish for Reliance Industries (RELIANCE); supports sum-of-the-parts (SOTP) valuation uplift.',
  },
  {
    id: 'art-5',
    title: 'Brent crude stabilizes near $74/bbl as OPEC+ confirms delayed unwinding of voluntary production curbs',
    summary: 'Energy marketers and OMCs face balanced refining crack spread dynamics as global crude benchmarks trade within an orderly range.',
    content: [
      'Global oil benchmark Brent crude hovered around $74.20 per barrel in London trading after the OPEC+ alliance announced it would defer its planned monthly output increase by another two months.',
      'For Indian downstream oil marketing companies (OMCs) like IOC, BPCL, and HPCL, range-bound crude prices provide pricing predictability for auto fuel marketing margins while refining gross margins remain supported by middle distillate demand.',
      'Upstream exploration majors such as ONGC and Oil India maintain steady realization metrics with statutory windfall tax adjustments reflecting normalized global petroleum crack spreads.',
    ],
    source: 'Reuters Financial',
    publishedAt: '6 hours ago',
    readTime: '4 min read',
    url: 'https://www.reuters.com',
    sector: 'Energy & Commodities',
    symbols: ['ONGC', 'BPCL', 'IOC'],
    sentiment: 'Neutral',
    sentimentScore: 0.04,
    sentimentConfidence: 82,
    keyTakeaways: [
      'Brent crude trades range-bound near $74/barrel.',
      'OPEC+ postpones planned output ramp-up by two months.',
      'Downstream OMC auto fuel marketing margins remain protected.',
    ],
    marketImpact: 'Neutral for downstream refiners; protects current quarterly cash flow visibility.',
  },
  {
    id: 'art-6',
    title: 'Sun Pharma secures US FDA clearance for novel dermatological formulation with zero inspection observations',
    summary: 'The clearance paves the way for commercial launch in the US market by Q2 FY26, strengthening the specialty pharmaceutical portfolio.',
    content: [
      'Sun Pharmaceutical Industries announced that the United States Food and Drug Administration (US FDA) has issued an Establishment Inspection Report (EIR) with a clean compliance status (Voluntary Action Indicated) for its manufacturing facility.',
      'The regulatory clearance facilitates commercial production of its proprietary dermatological therapy, which addresses an estimated $850 million addressable US specialty segment.',
      'Healthcare analysts noted that specialty business growth continues to outpace generic market dynamics, yielding gross margins in excess of 75% and reducing domestic price regulation sensitivity.',
    ],
    source: 'Economic Times',
    publishedAt: '8 hours ago',
    readTime: '3 min read',
    url: 'https://economictimes.indiatimes.com',
    sector: 'Pharmaceuticals',
    symbols: ['SUNPHARMA'],
    sentiment: 'Positive',
    sentimentScore: 0.88,
    sentimentConfidence: 96,
    keyTakeaways: [
      'US FDA EIR received with zero 483 inspection observations.',
      'Opens access to an estimated $850 million US specialty dermatology market.',
      'Substantial booster for specialty segment operating margins.',
    ],
    marketImpact: 'Strongly Bullish for Sun Pharma; analyst upgrades expected on specialty revenue trajectory.',
  },
]

export function getNewsArticles(options: NewsFilterOptions = {}): NewsArticle[] {
  let list = [...sampleArticles]

  // Filter by sentiment
  if (options.sentiment && options.sentiment !== 'All') {
    list = list.filter((a) => a.sentiment === options.sentiment)
  }

  // Filter by sector
  if (options.sector && options.sector !== 'All Sectors') {
    list = list.filter((a) => a.sector.toLowerCase().includes(options.sector!.toLowerCase()))
  }

  // Filter by source
  if (options.source && options.source !== 'All Publishers') {
    list = list.filter((a) => a.source.toLowerCase() === options.source!.toLowerCase())
  }

  // Filter by search query (title, summary, symbols, sector)
  if (options.searchQuery && options.searchQuery.trim()) {
    const q = options.searchQuery.toLowerCase().trim()
    list = list.filter(
      (a) =>
        a.title.toLowerCase().includes(q) ||
        a.summary.toLowerCase().includes(q) ||
        a.sector.toLowerCase().includes(q) ||
        a.symbols.some((s) => s.toLowerCase().includes(q))
    )
  }

  // Sorting
  if (options.sortBy === 'highest-sentiment') {
    list.sort((a, b) => b.sentimentScore - a.sentimentScore)
  } else if (options.sortBy === 'lowest-sentiment') {
    list.sort((a, b) => a.sentimentScore - b.sentimentScore)
  }

  return list
}

export function getArticleById(id: string): NewsArticle | undefined {
  return sampleArticles.find((a) => a.id === id)
}

export function getUniqueSectors(): string[] {
  const set = new Set(sampleArticles.map((a) => a.sector))
  return Array.from(set)
}

export function getUniqueSources(): string[] {
  const set = new Set(sampleArticles.map((a) => a.source))
  return Array.from(set)
}
