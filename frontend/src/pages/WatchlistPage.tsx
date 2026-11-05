import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Star, Plus, Bot, X } from '../components/ui/Icons'
import { Link } from 'react-router-dom'

interface WatchlistStock {
  symbol: string
  name: string
  sector: string
  price: string
  change: string
  sentiment: 'Bullish' | 'Neutral' | 'Bearish'
  sentimentScore: number
}

const initialStocks: WatchlistStock[] = [
  { symbol: 'RELIANCE', name: 'Reliance Industries Ltd', sector: 'Energy & Retail', price: '₹1,328.40', change: '+1.42%', sentiment: 'Bullish', sentimentScore: 0.74 },
  { symbol: 'TCS', name: 'Tata Consultancy Services', sector: 'IT Services', price: '₹4,120.00', change: '+0.31%', sentiment: 'Neutral', sentimentScore: 0.52 },
  { symbol: 'HDFCBANK', name: 'HDFC Bank Limited', sector: 'Banking & Finance', price: '₹1,745.80', change: '-0.52%', sentiment: 'Bearish', sentimentScore: 0.38 },
  { symbol: 'INFY', name: 'Infosys Limited', sector: 'IT Services', price: '₹1,890.15', change: '+2.14%', sentiment: 'Bullish', sentimentScore: 0.69 },
  { symbol: 'ICICIBANK', name: 'ICICI Bank Ltd', sector: 'Banking & Finance', price: '₹1,265.50', change: '+0.88%', sentiment: 'Bullish', sentimentScore: 0.78 },
  { symbol: 'BHARTIARTL', name: 'Bharti Airtel Ltd', sector: 'Telecom', price: '₹1,610.20', change: '+1.05%', sentiment: 'Bullish', sentimentScore: 0.67 },
]

export function WatchlistPage() {
  const [stocks, setStocks] = useState<WatchlistStock[]>(initialStocks)
  const [newSymbol, setNewSymbol] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)

  const handleAddStock = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newSymbol.trim()) return

    const symbolUpper = newSymbol.trim().toUpperCase()
    if (stocks.some((s) => s.symbol === symbolUpper)) {
      setNewSymbol('')
      setShowAddForm(false)
      return
    }

    const added: WatchlistStock = {
      symbol: symbolUpper,
      name: `${symbolUpper} Corporation`,
      sector: 'Diversified',
      price: '₹1,000.00',
      change: '+0.00%',
      sentiment: 'Neutral',
      sentimentScore: 0.5,
    }

    setStocks([added, ...stocks])
    setNewSymbol('')
    setShowAddForm(false)
  }

  const handleRemoveStock = (symbol: string) => {
    setStocks(stocks.filter((s) => s.symbol !== symbol))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Portfolio Watchlist
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Real-time equity monitoring enhanced with autonomous sentiment signals.
          </p>
        </div>

        <Button
          leftIcon={<Plus size={16} />}
          onClick={() => setShowAddForm(true)}
        >
          Add Ticker
        </Button>
      </div>

      {/* Add Ticker Drawer / Card */}
      {showAddForm && (
        <Card className="border-indigo-500/40 bg-slate-900/90">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-sm">Add New Symbol to Watchlist</CardTitle>
              <CardDescription>Enter a valid NSE or BSE listed symbol.</CardDescription>
            </div>
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="text-slate-400 hover:text-white"
            >
              <X size={18} />
            </button>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleAddStock} className="flex gap-2">
              <input
                type="text"
                value={newSymbol}
                onChange={(e) => setNewSymbol(e.target.value)}
                placeholder="e.g. WIPRO, MARUTI, SBIN"
                className="flex-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                autoFocus
              />
              <Button type="submit" size="sm">
                Add to List
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Watchlist Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Tracked Equities ({stocks.length})</CardTitle>
              <CardDescription>
                Live prices paired with FinBERT continuous news scoring.
              </CardDescription>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-slate-400">
              <Star size={14} className="text-amber-400 fill-amber-400" />
              <span>Priority tracking active</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="border-b border-slate-800 text-xs uppercase text-slate-400 bg-slate-900/40">
                <tr>
                  <th className="py-3 px-4">Symbol & Name</th>
                  <th className="py-3 px-4">Sector</th>
                  <th className="py-3 px-4">Last Price</th>
                  <th className="py-3 px-4">Day Change</th>
                  <th className="py-3 px-4">Sentiment Outlook</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {stocks.map((stock) => (
                  <tr key={stock.symbol} className="hover:bg-slate-800/30 transition">
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-white flex items-center gap-2">
                        <span>{stock.symbol}</span>
                      </div>
                      <div className="text-xs text-slate-400">{stock.name}</div>
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      {stock.sector}
                    </td>
                    <td className="py-3.5 px-4 font-mono font-semibold text-white">
                      {stock.price}
                    </td>
                    <td
                      className={`py-3.5 px-4 font-medium ${
                        stock.change.startsWith('+')
                          ? 'text-emerald-400'
                          : 'text-rose-400'
                      }`}
                    >
                      {stock.change}
                    </td>
                    <td className="py-3.5 px-4">
                      <Badge
                        variant={
                          stock.sentiment === 'Bullish'
                            ? 'success'
                            : stock.sentiment === 'Bearish'
                            ? 'danger'
                            : 'default'
                        }
                        size="sm"
                      >
                        {stock.sentiment} ({stock.sentimentScore.toFixed(2)})
                      </Badge>
                    </td>
                    <td className="py-3.5 px-4 text-right space-x-2">
                      <Link to="/chat">
                        <button
                          type="button"
                          className="px-2 py-1 rounded bg-indigo-600/20 text-indigo-300 hover:bg-indigo-600/30 text-xs font-medium transition cursor-pointer"
                        >
                          <span className="inline-flex items-center gap-1">
                            <Bot size={13} />
                            Ask
                          </span>
                        </button>
                      </Link>
                      <button
                        type="button"
                        onClick={() => handleRemoveStock(stock.symbol)}
                        className="px-2 py-1 rounded text-slate-400 hover:text-rose-400 hover:bg-slate-800 text-xs transition cursor-pointer"
                        aria-label={`Remove ${stock.symbol}`}
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
