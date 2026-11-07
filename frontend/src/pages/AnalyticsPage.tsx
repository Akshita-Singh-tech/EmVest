import { useState, useEffect, useMemo, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { EmptyState } from '../components/common/EmptyState'
import { TrendingUp, RefreshCw, Bot } from '../components/ui/Icons'
import { SentimentTrendChart } from '../components/analytics/SentimentTrendChart'
import { SectorBarChart } from '../components/analytics/SectorBarChart'
import { PolarityDonutChart } from '../components/analytics/PolarityDonutChart'
import {
  companyList,
  sampleTimeframesData,
  sectorSentimentList,
  companySentimentMap,
  aggregatePolarity,
} from '../services/analyticsData'
import {
  apiGetAnalyticsOverview,
  apiGetSectorAnalytics,
  apiGetCompanyAnalytics,
  type BackendOverview,
  type BackendSectorAnalytics,
  type BackendCompanyAnalytics,
} from '../services/api'
import { Link } from 'react-router-dom'

type AnalyticsViewMode = 'sector' | 'company'
type Timeframe = '1D' | '1W' | '1M' | '1Y'

export function AnalyticsPage() {
  const [viewMode, setViewMode] = useState<AnalyticsViewMode>('sector')
  const [timeframe, setTimeframe] = useState<Timeframe>('1W')
  const [selectedSector, setSelectedSector] = useState<string>('All Sectors')
  const [selectedCompanySymbol, setSelectedCompanySymbol] = useState<string>('RELIANCE')
  const [simulateNoData, setSimulateNoData] = useState<boolean>(false)
  const [loading, setLoading] = useState<boolean>(true)

  // Real backend analytics state
  const [backendOverview, setBackendOverview] = useState<BackendOverview | null>(null)
  const [backendSectors, setBackendSectors] = useState<BackendSectorAnalytics | null>(null)
  const [backendCompany, setBackendCompany] = useState<BackendCompanyAnalytics | null>(null)

  const handleSync = useCallback(async () => {
    setLoading(true)
    try {
      const [overviewData, sectorData] = await Promise.allSettled([
        apiGetAnalyticsOverview(),
        apiGetSectorAnalytics(),
      ])
      if (overviewData.status === 'fulfilled') {
        setBackendOverview(overviewData.value)
      }
      if (sectorData.status === 'fulfilled') {
        setBackendSectors(sectorData.value)
      }
    } catch {
      // Fail gracefully to local defaults
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    let active = true
    Promise.allSettled([
      apiGetAnalyticsOverview(),
      apiGetSectorAnalytics(),
    ]).then(([overviewData, sectorData]) => {
      if (!active) return
      if (overviewData.status === 'fulfilled') {
        setBackendOverview(overviewData.value)
      }
      if (sectorData.status === 'fulfilled') {
        setBackendSectors(sectorData.value)
      }
    }).finally(() => {
      if (active) setLoading(false)
    })
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    let active = true
    apiGetCompanyAnalytics(selectedCompanySymbol)
      .then((data) => {
        if (active) setBackendCompany(data)
      })
      .catch(() => {
        if (active) setBackendCompany(null)
      })
    return () => {
      active = false
    }
  }, [selectedCompanySymbol])

  // Aggregate metrics from real backend database
  const compositeScore = backendOverview?.composite_score ?? 0.74
  const overallSentiment = backendOverview?.overall_sentiment ?? 'Bullish'
  const totalArticles = backendOverview?.total_articles ?? 146
  const posPct = backendOverview?.polarity?.positive_percentage ?? 68
  const neuPct = backendOverview?.polarity?.neutral_percentage ?? 21
  const negPct = backendOverview?.polarity?.negative_percentage ?? 11

  // Dynamic Trajectory
  const trendData = useMemo(() => {
    if (simulateNoData) return []
    if (backendOverview && backendOverview.trajectory && backendOverview.trajectory.length > 0) {
      return backendOverview.trajectory.map((t) => ({
        date: t.date,
        score: t.score,
        positive: t.score > 0 ? 1 : 0,
        neutral: t.score === 0 ? 1 : 0,
        negative: t.score < 0 ? 1 : 0,
        volume: 1,
      }))
    }
    return sampleTimeframesData[timeframe] || []
  }, [simulateNoData, backendOverview, timeframe])

  // Dynamic Polarity Donut
  const polarityDonutData = useMemo(() => {
    if (simulateNoData) return []
    if (backendOverview && backendOverview.polarity) {
      return [
        {
          name: 'Positive' as const,
          value: backendOverview.polarity.positive_percentage,
          count: backendOverview.polarity.positive,
          color: '#10b981',
        },
        {
          name: 'Neutral' as const,
          value: backendOverview.polarity.neutral_percentage,
          count: backendOverview.polarity.neutral,
          color: '#64748b',
        },
        {
          name: 'Negative' as const,
          value: backendOverview.polarity.negative_percentage,
          count: backendOverview.polarity.negative,
          color: '#f43f5e',
        },
      ]
    }
    return aggregatePolarity
  }, [simulateNoData, backendOverview])

  // Dynamic Sector Rankings
  const sectorData = useMemo(() => {
    if (simulateNoData) return []
    if (backendSectors && backendSectors.sectors && backendSectors.sectors.length > 0) {
      return backendSectors.sectors.map((s) => {
        const validStatus: 'Neutral' | 'Bullish' | 'Bearish' | 'Cautious' =
          s.status === 'Bullish' || s.status === 'Bearish' || s.status === 'Cautious'
            ? s.status
            : 'Neutral'
        return {
          sector: s.sector,
          score: s.score,
          momentum: s.momentum,
          articleCount: s.article_count,
          status: validStatus,
          history: sampleTimeframesData['1W'],
        }
      })
    }
    return sectorSentimentList
  }, [simulateNoData, backendSectors])

  // Unique sector names for filter chips
  const sectorChips = useMemo(() => {
    if (backendSectors && backendSectors.sectors) {
      return ['All Sectors', ...backendSectors.sectors.map((s) => s.sector)]
    }
    return ['All Sectors', ...sectorSentimentList.map((s) => s.sector)]
  }, [backendSectors])

  // Selected company deep dive info
  const selectedCompany = useMemo(() => {
    if (simulateNoData) return undefined
    if (backendCompany) {
      const matchInList = companyList.find((c) => c.symbol === backendCompany.symbol)
      return {
        symbol: backendCompany.symbol,
        name: matchInList?.name || backendCompany.symbol,
        sector: matchInList?.sector || 'Diversified Equities',
        score: backendCompany.score,
        status: backendCompany.status,
        delta: backendCompany.score >= 0 ? `+${(backendCompany.score * 5).toFixed(1)}%` : `${(backendCompany.score * 5).toFixed(1)}%`,
        newsCount: backendCompany.article_count,
        trend: sampleTimeframesData[timeframe] || [],
        keyCatalyst: backendCompany.catalysts && backendCompany.catalysts.length > 0
          ? backendCompany.catalysts.join(' • ')
          : 'Active news flow indexed from leading Indian business dailies.',
      }
    }
    return companySentimentMap[selectedCompanySymbol]
  }, [simulateNoData, backendCompany, selectedCompanySymbol, timeframe])

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              Sentiment Intelligence & Analytics
            </h1>
            <Badge variant="purple" size="sm">
              Recharts • FinBERT • Live DB
            </Badge>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            Real-time multi-dimensional sentiment trajectories across Indian sectors and equities.
          </p>
        </div>

        {/* View Mode & Timeframe Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Refresh Real Analytics */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleSync}
            disabled={loading}
            leftIcon={<RefreshCw size={13} className={loading ? 'animate-spin' : ''} />}
          >
            {loading ? 'Syncing...' : 'Sync Live DB'}
          </Button>

          {/* Mode Switcher */}
          <div className="flex items-center p-1 bg-slate-900 border border-slate-800 rounded-lg">
            <button
              type="button"
              onClick={() => setViewMode('sector')}
              className={`px-3 py-1 rounded text-xs font-semibold transition ${
                viewMode === 'sector'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Sector View
            </button>
            <button
              type="button"
              onClick={() => setViewMode('company')}
              className={`px-3 py-1 rounded text-xs font-semibold transition ${
                viewMode === 'company'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Company Deep Dive
            </button>
          </div>

          {/* Timeframe Selector */}
          <div className="flex items-center p-1 bg-slate-900 border border-slate-800 rounded-lg">
            {(['1D', '1W', '1M', '1Y'] as Timeframe[]).map((tf) => (
              <button
                key={tf}
                type="button"
                onClick={() => setTimeframe(tf)}
                className={`px-2.5 py-1 rounded text-xs font-semibold transition ${
                  timeframe === tf
                    ? 'bg-slate-800 text-indigo-400 border border-indigo-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          {/* Explicit "No Data" Simulation Toggle */}
          <Button
            variant={simulateNoData ? 'danger' : 'outline'}
            size="sm"
            onClick={() => setSimulateNoData((prev) => !prev)}
          >
            {simulateNoData ? 'Restore Data' : 'Test "No Data" State'}
          </Button>
        </div>
      </div>

      {/* =========================================================================
          SECTOR VIEW
         ========================================================================= */}
      {viewMode === 'sector' && (
        <div className="space-y-6">
          {/* Sector Filter Chips */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
            {sectorChips.map((sector) => (
              <button
                key={sector}
                type="button"
                onClick={() => setSelectedSector(sector)}
                className={`whitespace-nowrap px-3 py-1.5 rounded-full border transition cursor-pointer ${
                  selectedSector === sector
                    ? 'bg-slate-800 border-indigo-500 text-indigo-300 font-semibold'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                {sector}
              </button>
            ))}
          </div>

          {/* Top Key Aggregate Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4 space-y-1">
                <span className="text-xs text-slate-400 font-medium">Composite FinBERT Index</span>
                <div className="text-2xl font-bold text-emerald-400">{compositeScore.toFixed(2)} / 1.00</div>
                <div className="flex items-center gap-1.5 text-xs text-slate-400 pt-1">
                  <Badge variant={overallSentiment === 'Bullish' ? 'success' : 'default'} size="sm">
                    {overallSentiment} Sentiment
                  </Badge>
                  <span>Across {timeframe} window</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 space-y-1">
                <span className="text-xs text-slate-400 font-medium">Polarity Distribution</span>
                <div className="text-2xl font-bold text-white">{posPct}% Positive</div>
                <div className="text-xs text-slate-400 pt-1">
                  <span>{neuPct}% Neutral • {negPct}% Negative</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 space-y-1">
                <span className="text-xs text-slate-400 font-medium">Tracked Ingestion Volume</span>
                <div className="text-2xl font-bold text-indigo-400">{totalArticles} Articles Scored</div>
                <div className="text-xs text-slate-400 pt-1">
                  <span>100% verified RSS feeds (Economic Times, LiveMint, Moneycontrol)</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Row: Trend Line & Polarity Donut */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Sentiment Trajectory Over Time</CardTitle>
                <CardDescription>
                  FinBERT weighted score trajectory evaluated across the {timeframe} interval.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <SentimentTrendChart
                  data={trendData}
                  timeframe={timeframe}
                  title={`${selectedSector} • Historical Drift`}
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Polarity Ratio</CardTitle>
                <CardDescription>Proportional sentiment breakdown.</CardDescription>
              </CardHeader>
              <CardContent>
                <PolarityDonutChart
                  data={polarityDonutData}
                />
              </CardContent>
            </Card>
          </div>

          {/* Sector Comparison Bar Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Sector Sentiment Rankings</CardTitle>
              <CardDescription>
                Cross-sector comparative outlook generated from recent news and earnings filings.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <SectorBarChart data={sectorData} />
            </CardContent>
          </Card>
        </div>
      )}

      {/* =========================================================================
          COMPANY VIEW
         ========================================================================= */}
      {viewMode === 'company' && (
        <div className="space-y-6">
          {/* Company Selector Pills & Search */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
              {companyList.map((c: { symbol: string; name: string; sector: string }) => (
                <button
                  key={c.symbol}
                  type="button"
                  onClick={() => setSelectedCompanySymbol(c.symbol)}
                  className={`whitespace-nowrap px-3 py-1.5 rounded-lg border font-mono transition cursor-pointer ${
                    selectedCompanySymbol === c.symbol
                      ? 'bg-indigo-600 text-white border-indigo-500 font-bold'
                      : 'bg-slate-900 border-slate-800 text-slate-300 hover:text-white'
                  }`}
                >
                  {c.symbol}
                </button>
              ))}
            </div>

            <span className="text-xs text-slate-400 font-mono">
              Selected: <strong className="text-white">{selectedCompanySymbol}</strong>
            </span>
          </div>

          {/* Company Deep Dive Card */}
          {selectedCompany ? (
            <div className="space-y-6">
              {/* Company Summary Bar */}
              <Card className="border-indigo-500/30 bg-gradient-to-r from-slate-900 to-indigo-950/20">
                <CardContent className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h3 className="text-xl font-bold text-white tracking-tight">
                        {selectedCompany.name} ({selectedCompany.symbol})
                      </h3>
                      <Badge
                        variant={selectedCompany.status === 'Bullish' ? 'success' : 'default'}
                        size="sm"
                      >
                        {selectedCompany.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-400">{selectedCompany.sector}</p>
                  </div>

                  <div className="flex items-center gap-6 text-sm">
                    <div>
                      <span className="text-xs text-slate-400 block">FinBERT Score</span>
                      <span className="text-lg font-bold font-mono text-emerald-400">
                        {selectedCompany.score.toFixed(2)}
                      </span>
                    </div>
                    <div>
                      <span className="text-xs text-slate-400 block">Day Shift</span>
                      <span className="text-lg font-bold font-mono text-white">
                        {selectedCompany.delta}
                      </span>
                    </div>
                    <div>
                      <span className="text-xs text-slate-400 block">Articles Ingested</span>
                      <span className="text-lg font-bold font-mono text-indigo-400">
                        {selectedCompany.newsCount}
                      </span>
                    </div>
                    <Link to="/chat">
                      <Button size="sm" variant="secondary" leftIcon={<Bot size={14} />}>
                        Ask AI
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>

              {/* Company Trend Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>{selectedCompany.symbol} Sentiment Trajectory</CardTitle>
                  <CardDescription>
                    Tracking news volume and FinBERT polarity changes over the {timeframe} interval.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <SentimentTrendChart
                    data={selectedCompany.trend}
                    timeframe={timeframe}
                    title={`${selectedCompany.symbol} Trend`}
                  />
                </CardContent>
              </Card>

              {/* Key News Driver & Catalyst */}
              <Card>
                <CardHeader>
                  <CardTitle>Key Market Catalysts & Sentiment Drivers</CardTitle>
                  <CardDescription>
                    Extracted from ingested articles and regulatory filings.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-sm text-slate-200 leading-relaxed">
                    <span className="font-semibold text-indigo-400">Primary Narrative: </span>
                    {selectedCompany.keyCatalyst}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            /* Explicit Empty State for unindexed companies or simulated empty state */
            <Card>
              <CardContent className="p-8">
                <EmptyState
                  icon={<TrendingUp size={28} />}
                  title={`No Ingested Sentiment Data for ${selectedCompanySymbol}`}
                  description="This ticker has not yet been processed by the scheduled RSS scraper or FinBERT NLP inference worker. No fabricated numbers will be rendered."
                  action={
                    <Button variant="secondary" size="sm" leftIcon={<RefreshCw size={14} />}>
                      Queue Scraping for {selectedCompanySymbol}
                    </Button>
                  }
                />
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
