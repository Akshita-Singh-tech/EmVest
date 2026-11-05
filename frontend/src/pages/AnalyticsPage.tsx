import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { EmptyState } from '../components/common/EmptyState'
import { TrendingUp, RefreshCw } from '../components/ui/Icons'

const sectors = ['All Sectors', 'Banking & Finance', 'Information Tech', 'Automobile', 'Energy & Power', 'Pharma']
const timeframes = ['1D', '1W', '1M', '3M', '1Y']

const sampleSectorData = [
  { sector: 'Banking & Finance', score: 0.72, status: 'Bullish', articles: 142, change: '+4.2%' },
  { sector: 'Automobile', score: 0.68, status: 'Bullish', articles: 89, change: '+2.1%' },
  { sector: 'Energy & Power', score: 0.54, status: 'Neutral', articles: 110, change: '-0.4%' },
  { sector: 'Information Tech', score: 0.46, status: 'Cautious', articles: 95, change: '-1.8%' },
  { sector: 'Pharma & Healthcare', score: 0.61, status: 'Bullish', articles: 64, change: '+1.5%' },
]

export function AnalyticsPage() {
  const [selectedSector, setSelectedSector] = useState('All Sectors')
  const [selectedTimeframe, setSelectedTimeframe] = useState('1W')
  const [showEmptyState, setShowEmptyState] = useState(false)

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Market Sentiment Analytics
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            FinBERT NLP aggregate scoring across Indian equity sectors and news sources.
          </p>
        </div>

        {/* Timeframe Buttons */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-lg">
          {timeframes.map((tf) => (
            <button
              key={tf}
              type="button"
              onClick={() => setSelectedTimeframe(tf)}
              className={`px-3 py-1 rounded text-xs font-semibold transition ${
                selectedTimeframe === tf
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Sector Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        {sectors.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setSelectedSector(s)}
            className={`whitespace-nowrap px-3 py-1.5 rounded-full border transition cursor-pointer ${
              selectedSector === s
                ? 'bg-slate-800 border-indigo-500 text-indigo-300 font-semibold'
                : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Top Aggregate Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-5 space-y-1">
            <span className="text-xs text-slate-400">Average Composite Sentiment</span>
            <div className="text-2xl font-bold text-emerald-400">0.64 / 1.00</div>
            <div className="flex items-center gap-1.5 text-xs text-slate-400 pt-1">
              <Badge variant="success" size="sm">Moderately Bullish</Badge>
              <span>Across 500+ articles</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5 space-y-1">
            <span className="text-xs text-slate-400">Bullish vs Bearish Ratio</span>
            <div className="text-2xl font-bold text-white">2.8 : 1</div>
            <div className="text-xs text-slate-400 pt-1">
              <span className="text-emerald-400 font-medium">68% Bullish</span> •{' '}
              <span className="text-rose-400 font-medium">24% Bearish</span> • 8% Neutral
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5 space-y-1">
            <span className="text-xs text-slate-400">Ingestion Velocity</span>
            <div className="text-2xl font-bold text-indigo-400">38 Articles / hr</div>
            <div className="text-xs text-slate-400 pt-1">
              <span>RSS feeds active from 12 publishers</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sector Sentiment Breakdown Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Sector Sentiment Breakdown</CardTitle>
            <CardDescription>
              Real-time sentiment indices calculated via FinBERT weighted inference.
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowEmptyState((prev) => !prev)}
          >
            {showEmptyState ? 'Show Sample Data' : 'Toggle No-Data State'}
          </Button>
        </CardHeader>
        <CardContent>
          {showEmptyState ? (
            <EmptyState
              icon={<TrendingUp size={24} />}
              title="No sentiment data available for this sector"
              description="Articles for this sector have not yet been scored by the FinBERT worker pipeline. Check back after the next scheduled ingestion run."
              action={
                <Button variant="secondary" size="sm" leftIcon={<RefreshCw size={14} />}>
                  Run On-Demand Scoring
                </Button>
              }
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="border-b border-slate-800 text-xs uppercase text-slate-400 bg-slate-900/40">
                  <tr>
                    <th className="py-3 px-4">Sector</th>
                    <th className="py-3 px-4">FinBERT Score</th>
                    <th className="py-3 px-4">Market Outlook</th>
                    <th className="py-3 px-4">Scored Articles</th>
                    <th className="py-3 px-4 text-right">Weekly Drift</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80">
                  {sampleSectorData.map((row) => (
                    <tr key={row.sector} className="hover:bg-slate-800/30 transition">
                      <td className="py-3.5 px-4 font-semibold text-white">
                        {row.sector}
                      </td>
                      <td className="py-3.5 px-4 font-mono font-medium">
                        {row.score.toFixed(2)}
                      </td>
                      <td className="py-3.5 px-4">
                        <Badge
                          variant={
                            row.status === 'Bullish'
                              ? 'success'
                              : row.status === 'Cautious'
                              ? 'warning'
                              : 'default'
                          }
                          size="sm"
                        >
                          {row.status}
                        </Badge>
                      </td>
                      <td className="py-3.5 px-4 text-slate-400">
                        {row.articles}
                      </td>
                      <td
                        className={`py-3.5 px-4 text-right font-medium ${
                          row.change.startsWith('+')
                            ? 'text-emerald-400'
                            : 'text-rose-400'
                        }`}
                      >
                        {row.change}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
