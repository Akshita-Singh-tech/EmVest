import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { EmptyState } from '../components/common/EmptyState'
import { Star, Plus, Bot, X, Search, Newspaper } from '../components/ui/Icons'
import { searchMasterCompanies } from '../services/masterData'
import {
  getWatchlistRecords,
  addSymbolToWatchlist,
  removeSymbolFromWatchlist,
} from '../services/personalizationStore'
import type { WatchlistRecord } from '../types/personalization'

export function WatchlistPage() {
  const [watchlist, setWatchlist] = useState<WatchlistRecord[]>(getWatchlistRecords())
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSentiment, setSelectedSentiment] = useState<'All' | 'Bullish' | 'Neutral' | 'Bearish'>('All')

  // Add symbol modal/drawer state
  const [showAddModal, setShowAddModal] = useState(false)
  const [tickerInput, setTickerInput] = useState('')
  const [notesInput, setNotesInput] = useState('')
  const [addError, setAddError] = useState<string | null>(null)
  const [addSuccess, setAddSuccess] = useState<string | null>(null)

  useEffect(() => {
    const handleUpdate = () => {
      setWatchlist(getWatchlistRecords())
    }
    window.addEventListener('emvest_watchlist_updated', handleUpdate)
    return () => window.removeEventListener('emvest_watchlist_updated', handleUpdate)
  }, [])

  // Autocomplete suggestions for adding symbols
  const symbolSuggestions = useMemo(() => {
    if (!tickerInput.trim()) return []
    return searchMasterCompanies(tickerInput).slice(0, 5)
  }, [tickerInput])

  // Filtered watchlist
  const filteredWatchlist = useMemo(() => {
    let list = [...watchlist]

    if (selectedSentiment !== 'All') {
      list = list.filter((item) => item.sentiment === selectedSentiment)
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim()
      list = list.filter(
        (item) =>
          item.symbol.toLowerCase().includes(q) ||
          item.name.toLowerCase().includes(q) ||
          item.sector.toLowerCase().includes(q)
      )
    }

    return list
  }, [watchlist, searchQuery, selectedSentiment])

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!tickerInput.trim()) return

    const res = addSymbolToWatchlist(tickerInput, notesInput)
    if (!res.success) {
      setAddError(res.error || 'Failed to add symbol.')
      return
    }

    setAddError(null)
    setAddSuccess(`Successfully added ${tickerInput.toUpperCase()} to watchlist!`)
    setTickerInput('')
    setNotesInput('')
    setTimeout(() => {
      setAddSuccess(null)
      setShowAddModal(false)
    }, 1200)
  }

  const handleSelectSuggestion = (symbol: string) => {
    setTickerInput(symbol)
  }

  const handleRemove = (symbol: string) => {
    removeSymbolFromWatchlist(symbol)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              Equity Watchlist
            </h1>
            <Badge variant="purple" size="sm">
              Phase 5
            </Badge>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            Real-time portfolio watchlist powered by official NSE/BSE master data and FinBERT alerts.
          </p>
        </div>

        <Button
          leftIcon={<Plus size={16} />}
          onClick={() => {
            setShowAddModal(true)
            setAddError(null)
            setAddSuccess(null)
          }}
        >
          Add Ticker
        </Button>
      </div>

      {/* Add Ticker Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Star size={18} className="text-amber-400" />
                <h3 className="text-base font-bold text-white">Add Equity to Watchlist</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-white"
                aria-label="Close modal"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleAddSubmit} className="space-y-4">
              <div className="space-y-1.5 relative">
                <label className="text-xs font-semibold text-slate-300">
                  Symbol or Company Name
                </label>
                <input
                  type="text"
                  value={tickerInput}
                  onChange={(e) => {
                    setTickerInput(e.target.value)
                    if (addError) setAddError(null)
                  }}
                  placeholder="e.g. RELIANCE, TCS, MARUTI, SBIN..."
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
                  autoFocus
                />

                {/* Suggestions drop-down */}
                {symbolSuggestions.length > 0 && (
                  <div className="absolute top-full left-0 right-0 mt-1 z-20 rounded-lg border border-slate-800 bg-slate-950/95 shadow-xl p-1.5 divide-y divide-slate-850">
                    {symbolSuggestions.map((s) => (
                      <div
                        key={s.symbol}
                        onClick={() => handleSelectSuggestion(s.symbol)}
                        className="p-2 hover:bg-slate-800/60 rounded cursor-pointer flex items-center justify-between text-xs"
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-white">{s.symbol}</span>
                          <span className="text-slate-400 truncate max-w-[200px]">{s.name}</span>
                        </div>
                        <Badge variant="default" size="sm">{s.sector.split(' ')[0]}</Badge>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">
                  Investment Thesis / Notes (Optional)
                </label>
                <input
                  type="text"
                  value={notesInput}
                  onChange={(e) => setNotesInput(e.target.value)}
                  placeholder="e.g. Monitoring Q4 margin recovery and EV volume growth"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              {addError && <p className="text-xs text-rose-400">{addError}</p>}
              {addSuccess && <p className="text-xs text-emerald-400">{addSuccess}</p>}

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" size="sm" disabled={!tickerInput.trim()}>
                  Confirm & Track
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-3 rounded-xl border border-slate-800 bg-slate-900/60">
        <div className="relative flex-1 max-w-md">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search watchlist symbols, names, or sectors..."
            className="w-full pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        {/* Polarity Pills */}
        <div className="flex items-center gap-1.5 text-xs">
          {(['All', 'Bullish', 'Neutral', 'Bearish'] as const).map((sent) => (
            <button
              key={sent}
              type="button"
              onClick={() => setSelectedSentiment(sent)}
              className={`px-3 py-1 rounded-full border transition cursor-pointer ${
                selectedSentiment === sent
                  ? 'bg-indigo-600 border-indigo-500 text-white font-semibold'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {sent}
            </button>
          ))}
        </div>
      </div>

      {/* Watchlist Table */}
      {filteredWatchlist.length > 0 ? (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Tracked Equities ({filteredWatchlist.length})</CardTitle>
              <CardDescription>
                Live prices integrated with continuous FinBERT sentiment signals.
              </CardDescription>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              NSE/BSE Real-Time Feed
            </span>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="border-b border-slate-800 text-xs uppercase text-slate-400 bg-slate-900/40">
                  <tr>
                    <th className="py-3 px-4">Symbol & Company</th>
                    <th className="py-3 px-4">Sector</th>
                    <th className="py-3 px-4">Last Price</th>
                    <th className="py-3 px-4">Day Change</th>
                    <th className="py-3 px-4">FinBERT Score</th>
                    <th className="py-3 px-4">Thesis / Notes</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80">
                  {filteredWatchlist.map((item) => (
                    <tr key={item.symbol} className="hover:bg-slate-800/30 transition">
                      <td className="py-3.5 px-4">
                        <div className="font-bold text-white font-mono flex items-center gap-1.5">
                          <Star size={13} className="text-amber-400 fill-amber-400" />
                          <span>{item.symbol}</span>
                        </div>
                        <div className="text-xs text-slate-400 truncate max-w-[180px]">
                          {item.name}
                        </div>
                      </td>

                      <td className="py-3.5 px-4 text-xs text-slate-400">
                        {item.sector}
                      </td>

                      <td className="py-3.5 px-4 font-mono font-semibold text-white">
                        {item.price}
                      </td>

                      <td
                        className={`py-3.5 px-4 font-medium font-mono text-xs ${
                          item.change.startsWith('+')
                            ? 'text-emerald-400'
                            : 'text-rose-400'
                        }`}
                      >
                        {item.change}
                      </td>

                      <td className="py-3.5 px-4">
                        <Badge
                          variant={
                            item.sentiment === 'Bullish'
                              ? 'success'
                              : item.sentiment === 'Bearish'
                              ? 'danger'
                              : 'default'
                          }
                          size="sm"
                        >
                          {item.sentiment} ({item.sentimentScore.toFixed(2)})
                        </Badge>
                      </td>

                      <td className="py-3.5 px-4 text-xs text-slate-400 max-w-xs truncate">
                        {item.notes || '—'}
                      </td>

                      <td className="py-3.5 px-4 text-right space-x-2 whitespace-nowrap">
                        <Link to="/chat">
                          <button
                            type="button"
                            className="px-2 py-1 rounded bg-indigo-600/20 text-indigo-300 hover:bg-indigo-600/30 text-xs font-medium transition cursor-pointer"
                            title="Analyze in AI Assistant"
                          >
                            <Bot size={13} />
                          </button>
                        </Link>

                        <Link to="/news">
                          <button
                            type="button"
                            className="px-2 py-1 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs font-medium transition cursor-pointer"
                            title="View News Feed"
                          >
                            <Newspaper size={13} />
                          </button>
                        </Link>

                        <button
                          type="button"
                          onClick={() => handleRemove(item.symbol)}
                          className="px-2 py-1 rounded text-slate-400 hover:text-rose-400 hover:bg-slate-800 text-xs transition cursor-pointer"
                          title="Remove from watchlist"
                          aria-label={`Remove ${item.symbol}`}
                        >
                          <X size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      ) : (
        <EmptyState
          icon={<Star size={28} className="text-amber-400" />}
          title="No Watchlist Equities Match"
          description="Your watchlist has no items matching the search query or sentiment filter. You can add new tickers using the button above."
          action={
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                setSearchQuery('')
                setSelectedSentiment('All')
              }}
            >
              Reset Search & Filters
            </Button>
          }
        />
      )}
    </div>
  )
}
