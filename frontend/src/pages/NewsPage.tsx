import { useState } from 'react'
import { Card, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Search, ExternalLink, RefreshCw } from '../components/ui/Icons'

const filterCategories = ['All News', 'Positive Sentiment', 'Negative Sentiment', 'Earnings', 'Macro & Policy', 'Regulatory']

const articles = [
  {
    id: 1,
    title: 'RBI Monetary Policy Committee maintains repo rate at 6.5%, signals accommodative liquidity stance',
    summary: 'The central bank opted to retain key interest rates while highlighting resilient domestic economic momentum and controlled core inflation trajectory.',
    source: 'LiveMint',
    time: '25 mins ago',
    sector: 'Banking & Macro',
    sentiment: 'Positive',
    score: '+0.82',
    symbols: ['HDFCBANK', 'SBIN', 'ICICIBANK'],
  },
  {
    id: 2,
    title: 'Tata Motors passenger EV registrations climb 18% YoY in October festive sales surge',
    summary: 'Strong demand for the Punch.ev and Nexon.ev helped consolidate market share above 65% in domestic passenger electric mobility.',
    source: 'Economic Times',
    time: '1 hour ago',
    sector: 'Automobile',
    sentiment: 'Positive',
    score: '+0.76',
    symbols: ['TATAMOTORS'],
  },
  {
    id: 3,
    title: 'IT services sector anticipates cautious Q4 client guidance amid deferred discretionary tech spends',
    summary: 'Tier-1 tech companies report continued delays in large digital transformation deals as BFSI clients optimize existing cloud infrastructure budgets.',
    source: 'Moneycontrol',
    time: '2 hours ago',
    sector: 'Information Tech',
    sentiment: 'Negative',
    score: '-0.42',
    symbols: ['INFY', 'TCS', 'WIPRO'],
  },
  {
    id: 4,
    title: 'Reliance Retail expands omnichannel distribution footprint with 120 new store additions',
    summary: 'Rapid scaling in Tier-2 and Tier-3 cities expected to drive higher EBITDA margins and enhance warehouse supply chain fulfillment.',
    source: 'Business Standard',
    time: '4 hours ago',
    sector: 'Retail & Conglomerate',
    sentiment: 'Positive',
    score: '+0.69',
    symbols: ['RELIANCE'],
  },
  {
    id: 5,
    title: 'Brent crude stabilizes near $74/bbl as OPEC+ confirms delayed unwinding of voluntary production curbs',
    summary: 'Energy marketers and OMCs face modest margin adjustments following crude price volatility and refining crack spread shifts.',
    source: 'Reuters Financial',
    time: '6 hours ago',
    sector: 'Energy & Commodities',
    sentiment: 'Neutral',
    score: '0.04',
    symbols: ['BPCL', 'IOC', 'ONGC'],
  },
]

export function NewsPage() {
  const [activeFilter, setActiveFilter] = useState('All News')
  const [searchQuery, setSearchQuery] = useState('')

  const filteredArticles = articles.filter((art) => {
    if (activeFilter === 'Positive Sentiment' && art.sentiment !== 'Positive') return false
    if (activeFilter === 'Negative Sentiment' && art.sentiment !== 'Negative') return false
    if (activeFilter === 'Earnings' && !art.title.toLowerCase().includes('result') && !art.title.toLowerCase().includes('q')) return false
    if (activeFilter === 'Macro & Policy' && art.sector !== 'Banking & Macro') return false

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      return (
        art.title.toLowerCase().includes(q) ||
        art.summary.toLowerCase().includes(q) ||
        art.symbols.some((s) => s.toLowerCase().includes(q))
      )
    }
    return true
  })

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            News Intelligence Feed
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Real-time multi-publisher RSS ingestion tagged with FinBERT sentiment scores and ticker citations.
          </p>
        </div>

        <Button variant="secondary" size="sm" leftIcon={<RefreshCw size={14} />}>
          Refresh Feed
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          {filterCategories.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setActiveFilter(cat)}
              className={`whitespace-nowrap px-3 py-1.5 rounded-full border transition cursor-pointer ${
                activeFilter === cat
                  ? 'bg-indigo-600 border-indigo-500 text-white font-semibold'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative min-w-[240px]">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search news or symbol..."
            className="w-full pl-8 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Articles Feed */}
      <div className="space-y-4">
        {filteredArticles.map((article) => (
          <Card key={article.id} className="hover:border-slate-700 transition">
            <CardContent className="p-5 space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-slate-300">{article.source}</span>
                  <span className="text-slate-600">•</span>
                  <span className="text-slate-400">{article.time}</span>
                  <span className="text-slate-600">•</span>
                  <Badge variant="default" size="sm">
                    {article.sector}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <Badge
                    variant={
                      article.sentiment === 'Positive'
                        ? 'success'
                        : article.sentiment === 'Negative'
                        ? 'danger'
                        : 'default'
                    }
                    size="sm"
                  >
                    FinBERT: {article.score}
                  </Badge>
                </div>
              </div>

              <div className="space-y-1.5">
                <h3 className="text-base font-bold text-white hover:text-indigo-300 transition cursor-pointer flex items-start justify-between gap-4">
                  <span>{article.title}</span>
                  <ExternalLink size={16} className="text-slate-500 flex-shrink-0 mt-1" />
                </h3>
                <p className="text-sm text-slate-400 leading-relaxed">
                  {article.summary}
                </p>
              </div>

              <div className="pt-2 flex items-center justify-between border-t border-slate-800/80 text-xs">
                <div className="flex items-center gap-1.5">
                  <span className="text-slate-400">Related Symbols:</span>
                  {article.symbols.map((sym) => (
                    <span
                      key={sym}
                      className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[11px] font-semibold"
                    >
                      {sym}
                    </span>
                  ))}
                </div>
                <button
                  type="button"
                  className="text-indigo-400 hover:text-indigo-300 font-medium"
                >
                  Analyze with AI →
                </button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
