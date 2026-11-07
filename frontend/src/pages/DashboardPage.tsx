import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import {
  TrendingUp,
  Newspaper,
  Star,
  Bot,
  Sparkles,
  ChevronRight,
  RefreshCw,
} from '../components/ui/Icons'
import { getNewsArticles, fetchLiveNewsArticles } from '../services/newsData'
import { apiGetMarketQuotes, type MarketQuoteIndex, type MarketQuoteEquity } from '../services/api'
import type { NewsArticle } from '../types/news'

const defaultIndices: MarketQuoteIndex[] = [
  { name: 'NIFTY 50', value: '25,030.35', raw_price: 25030.35, change: '+2.01%', positive: true, sentiment: 'Bullish (+2.01%)' },
  { name: 'SENSEX', value: '81,028.02', raw_price: 81028.02, change: '+2.17%', positive: true, sentiment: 'Bullish (+2.17%)' },
  { name: 'BANK NIFTY', value: '59,086.00', raw_price: 59086.00, change: '+2.27%', positive: true, sentiment: 'Bullish (+2.27%)' },
  { name: 'INDIA VIX', value: '17.46', raw_price: 17.46, change: '+12.10%', positive: true, sentiment: 'Low Volatility' },
]

const defaultWatchlist: MarketQuoteEquity[] = [
  { symbol: 'RELIANCE', name: 'Reliance Industries', price: '₹1,320.00', raw_price: 1320.0, change: '+0.50%', positive: true, sentiment: 'Bullish' },
  { symbol: 'TCS', name: 'Tata Consultancy Services', price: '₹2,498.50', raw_price: 2498.5, change: '+0.11%', positive: true, sentiment: 'Neutral' },
  { symbol: 'HDFCBANK', name: 'HDFC Bank Ltd', price: '₹788.25', raw_price: 788.25, change: '+3.72%', positive: true, sentiment: 'Bullish' },
  { symbol: 'INFY', name: 'Infosys Ltd', price: '₹1,181.40', raw_price: 1181.4, change: '+1.20%', positive: true, sentiment: 'Bullish' },
  { symbol: 'SBIN', name: 'State Bank of India', price: '₹1,018.50', raw_price: 1018.5, change: '+1.85%', positive: true, sentiment: 'Bullish' },
]

export function DashboardPage() {
  const [articles, setArticles] = useState<NewsArticle[]>(() => getNewsArticles().slice(0, 4))
  const [indices, setIndices] = useState<MarketQuoteIndex[]>(defaultIndices)
  const [watchlist, setWatchlist] = useState<MarketQuoteEquity[]>(defaultWatchlist)
  const [lastRefreshed, setLastRefreshed] = useState<string>('Live')
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false)

  const fetchUpdatedData = async () => {
    const [quoteRes, newsRes] = await Promise.allSettled([
      apiGetMarketQuotes(),
      fetchLiveNewsArticles({ sortBy: 'newest' }),
    ])

    if (quoteRes.status === 'fulfilled' && quoteRes.value) {
      if (quoteRes.value.indices && quoteRes.value.indices.length > 0) {
        setIndices(quoteRes.value.indices)
      }
      if (quoteRes.value.watchlist && quoteRes.value.watchlist.length > 0) {
        setWatchlist(quoteRes.value.watchlist)
      }
    }

    if (newsRes.status === 'fulfilled' && newsRes.value && newsRes.value.length > 0) {
      setArticles(newsRes.value.slice(0, 4))
    }

    setLastRefreshed(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }))
  }

  const handleManualRefresh = async () => {
    setIsRefreshing(true)
    try {
      await fetchUpdatedData()
    } finally {
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    let isMounted = true

    const runSync = async () => {
      try {
        const [quoteRes, newsRes] = await Promise.allSettled([
          apiGetMarketQuotes(),
          fetchLiveNewsArticles({ sortBy: 'newest' }),
        ])

        if (!isMounted) return

        if (quoteRes.status === 'fulfilled' && quoteRes.value) {
          if (quoteRes.value.indices && quoteRes.value.indices.length > 0) {
            setIndices(quoteRes.value.indices)
          }
          if (quoteRes.value.watchlist && quoteRes.value.watchlist.length > 0) {
            setWatchlist(quoteRes.value.watchlist)
          }
        }

        if (newsRes.status === 'fulfilled' && newsRes.value && newsRes.value.length > 0) {
          setArticles(newsRes.value.slice(0, 4))
        }

        setLastRefreshed(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }))
      } catch {
        // Keep active cache
      }
    }

    void runSync()
    const timer = setInterval(() => { void runSync() }, 60000)
    return () => {
      isMounted = false
      clearInterval(timer)
    }
  }, [])

  return (
    <div className="space-y-6">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-900/60 via-slate-900 to-slate-900 border border-indigo-500/30 p-6 sm:p-8">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="flex items-center gap-2">
            <Badge variant="purple" size="md">
              Live Market Intelligence
            </Badge>
            <span className="text-[11px] text-slate-400 font-medium">
              Updated: {lastRefreshed}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Financial Intelligence & Real-Time Market Advisory
          </h1>
          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
            Emvest delivers verified real-time market feeds, sentiment analytics, and tailored equity research to guide your investment decisions across Indian markets.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <Link to="/chat">
              <Button leftIcon={<Bot size={16} />}>Ask Investment Advisor</Button>
            </Link>
            <Link to="/analytics">
              <Button variant="outline" leftIcon={<TrendingUp size={16} />}>
                View Sector Sentiment
              </Button>
            </Link>
            <Button
              variant="secondary"
              size="md"
              leftIcon={<RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />}
              onClick={handleManualRefresh}
            >
              Refresh Quotes
            </Button>
          </div>
        </div>
      </div>

      {/* Market Indices Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {indices.map((idx) => (
          <Card key={idx.name}>
            <CardContent className="p-4 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-semibold">{idx.name}</span>
                <Badge variant={idx.positive ? 'success' : 'danger'} size="sm">
                  {idx.change}
                </Badge>
              </div>
              <div className="text-xl font-bold text-white tracking-tight">
                {idx.value}
              </div>
              <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800">
                <span>Sentiment</span>
                <span className="font-medium text-slate-200">{idx.sentiment}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Two Column Layout: News & Watchlist */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* News Feed Highlights (2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Newspaper size={18} className="text-indigo-400" />
              <h3 className="text-base font-bold text-white">Live News Feed</h3>
            </div>
            <Link to="/news" className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1">
              View all feed <ChevronRight size={14} />
            </Link>
          </div>

          <div className="space-y-3">
            {articles.map((news) => (
              <Link to={`/news/${news.id}`} key={news.id} className="block group">
                <Card className="hover:border-slate-700 transition">
                  <CardContent className="p-4 space-y-2">
                    <div className="flex items-center justify-between gap-2 text-xs">
                      <span className="text-slate-400 font-medium">
                        {news.source} • {news.publishedAt}
                      </span>
                      <div className="flex items-center gap-1.5">
                        <Badge variant="default" size="sm">{news.sector}</Badge>
                        <Badge
                          variant={news.sentiment === 'Positive' ? 'success' : news.sentiment === 'Negative' ? 'danger' : 'default'}
                          size="sm"
                        >
                          {news.sentimentScore > 0 ? `+${news.sentimentScore}` : String(news.sentimentScore)}
                        </Badge>
                      </div>
                    </div>
                    <h4 className="text-sm font-semibold text-slate-100 group-hover:text-indigo-300 transition">
                      {news.title}
                    </h4>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>

        {/* Watchlist Quick View (1 Col) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Star size={18} className="text-amber-400" />
              <h3 className="text-base font-bold text-white">Watchlist Glance</h3>
            </div>
            <Link to="/watchlist" className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1">
              Manage <ChevronRight size={14} />
            </Link>
          </div>

          <Card>
            <CardContent className="p-3 divide-y divide-slate-800">
              {watchlist.map((stock) => (
                <div key={stock.symbol} className="py-3 flex items-center justify-between first:pt-1 last:pb-1">
                  <div>
                    <div className="font-bold text-sm text-white">{stock.symbol}</div>
                    <div className="text-xs text-slate-400">{stock.name}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-sm text-slate-100">{stock.price}</div>
                    <div className={`text-xs font-medium ${stock.change.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {stock.change}
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Quick AI Prompt Card */}
          <Card className="bg-gradient-to-br from-indigo-950/40 to-slate-900 border-indigo-500/30">
            <CardHeader className="p-4 pb-2">
              <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold">
                <Sparkles size={14} />
                <span>Investment Advisory Query</span>
              </div>
              <CardTitle className="text-sm font-bold text-white pt-1">
                "Compare Nifty IT vs Banking sentiment trends"
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-1">
              <Link to="/chat">
                <Button variant="secondary" size="sm" className="w-full" rightIcon={<ChevronRight size={14} />}>
                  Ask Investment Advisor
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
