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
} from '../components/ui/Icons'

const marketIndices = [
  { name: 'NIFTY 50', value: '24,320.15', change: '+0.78%', positive: true, sentiment: 'Bullish (0.74)' },
  { name: 'SENSEX', value: '79,890.40', change: '+0.65%', positive: true, sentiment: 'Bullish (0.69)' },
  { name: 'BANK NIFTY', value: '51,840.90', change: '-0.21%', positive: false, sentiment: 'Neutral (0.51)' },
  { name: 'INDIA VIX', value: '13.45', change: '-3.12%', positive: true, sentiment: 'Low Volatility' },
]

const recentNews = [
  {
    id: 1,
    title: 'RBI Monetary Policy Committee maintains repo rate at 6.5%, signals accommodative stance',
    source: 'LiveMint',
    time: '20 mins ago',
    sentiment: 'Positive',
    sentimentScore: '+0.82',
    sector: 'Banking',
  },
  {
    id: 2,
    title: 'Tata Motors reports 18% YoY growth in EV registrations for Q3; commercial segment steady',
    source: 'Economic Times',
    time: '1 hour ago',
    sentiment: 'Positive',
    sentimentScore: '+0.76',
    sector: 'Automotive',
  },
  {
    id: 3,
    title: 'IT services sector anticipates cautious Q4 client guidance amid deferred discretionary tech spends',
    source: 'Moneycontrol',
    time: '3 hours ago',
    sentiment: 'Neutral',
    sentimentScore: '0.49',
    sector: 'IT Services',
  },
]

const watchlistHighlights = [
  { symbol: 'RELIANCE', name: 'Reliance Industries', price: '₹1,328.40', change: '+1.4%', sentiment: 'Bullish' },
  { symbol: 'TCS', name: 'Tata Consultancy Services', price: '₹4,120.00', change: '+0.3%', sentiment: 'Neutral' },
  { symbol: 'HDFCBANK', name: 'HDFC Bank Ltd', price: '₹1,745.80', change: '-0.5%', sentiment: 'Bearish' },
  { symbol: 'INFY', name: 'Infosys Ltd', price: '₹1,890.15', change: '+2.1%', sentiment: 'Bullish' },
]

export function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-900/60 via-slate-900 to-slate-900 border border-indigo-500/30 p-6 sm:p-8">
        <div className="relative z-10 max-w-2xl space-y-3">
          <Badge variant="purple" size="md">
            Phase 2 • UI Shell Active
          </Badge>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Financial Intelligence & Real-Time Sentiment
          </h1>
          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
            Emvest combines automated news ingestion, FinBERT natural language scoring, and agentic LLM retrieval to accelerate your equity research across Indian markets.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <Link to="/chat">
              <Button leftIcon={<Bot size={16} />}>Start AI Analysis</Button>
            </Link>
            <Link to="/analytics">
              <Button variant="outline" leftIcon={<TrendingUp size={16} />}>
                View Sector Sentiment
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Market Indices Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {marketIndices.map((idx) => (
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
              <h3 className="text-base font-bold text-white">Live News Intelligence</h3>
            </div>
            <Link to="/news" className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1">
              View all feed <ChevronRight size={14} />
            </Link>
          </div>

          <div className="space-y-3">
            {recentNews.map((news) => (
              <Card key={news.id} className="hover:border-slate-700 transition">
                <CardContent className="p-4 space-y-2">
                  <div className="flex items-center justify-between gap-2 text-xs">
                    <span className="text-slate-400 font-medium">{news.source} • {news.time}</span>
                    <div className="flex items-center gap-1.5">
                      <Badge variant="default" size="sm">{news.sector}</Badge>
                      <Badge variant={news.sentiment === 'Positive' ? 'success' : 'default'} size="sm">
                        {news.sentimentScore}
                      </Badge>
                    </div>
                  </div>
                  <h4 className="text-sm font-semibold text-slate-100 hover:text-indigo-300 transition cursor-pointer">
                    {news.title}
                  </h4>
                </CardContent>
              </Card>
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
              {watchlistHighlights.map((stock) => (
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
                <span>AI Prompt of the Day</span>
              </div>
              <CardTitle className="text-sm font-bold text-white pt-1">
                "Compare Nifty IT vs Banking sentiment trends"
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-1">
              <Link to="/chat">
                <Button variant="secondary" size="sm" className="w-full" rightIcon={<ChevronRight size={14} />}>
                  Run in AI Assistant
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
