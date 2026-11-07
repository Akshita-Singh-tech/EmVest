import { useState, useMemo, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Search, RefreshCw, Newspaper, Sparkles } from '../components/ui/Icons'
import { EmptyState } from '../components/common/EmptyState'
import { ArticleCard } from '../components/news/ArticleCard'
import { ArticleDetailModal } from '../components/news/ArticleDetailModal'
import {
  getNewsArticles,
  getArticleById,
  getUniqueSectors,
  getUniqueSources,
  fetchLiveNewsArticles,
} from '../services/newsData'
import { getUserPreferences } from '../services/personalizationStore'
import { apiTriggerIngestion } from '../services/api'
import type { NewsArticle, SentimentPolarity } from '../types/news'

export function NewsPage() {
  const { id } = useParams<{ id?: string }>()
  const navigate = useNavigate()

  // State for filters
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSentiment, setSelectedSentiment] = useState<'All' | SentimentPolarity>('All')
  const [selectedSector, setSelectedSector] = useState('All Sectors')
  const [selectedSource, setSelectedSource] = useState('All Publishers')
  const [sortBy, setSortBy] = useState<'newest' | 'highest-sentiment' | 'lowest-sentiment'>('newest')
  const [selectedArticleState, setSelectedArticleState] = useState<NewsArticle | null>(null)
  const [liveArticles, setLiveArticles] = useState<NewsArticle[]>(() => getNewsArticles())
  const [onlyTracked, setOnlyTracked] = useState(false)
  const [isIngesting, setIsIngesting] = useState(false)
  const [ingestStatus, setIngestStatus] = useState<string | null>(null)
  const userPrefs = getUserPreferences()

  const handleLiveIngest = async () => {
    setIsIngesting(true)
    try {
      const res = await apiTriggerIngestion()
      setIngestStatus(`Fetched ${res.newly_ingested} new articles (${res.total_articles} active in database)`)
      const updated = await fetchLiveNewsArticles({
        searchQuery,
        sentiment: selectedSentiment,
        sector: selectedSector,
        source: selectedSource,
        sortBy,
      })
      if (updated && updated.length > 0) {
        setLiveArticles(updated)
      }
      setTimeout(() => setIngestStatus(null), 4500)
    } catch {
      setIngestStatus('Live fetch timed out or offline; keeping current database items.')
      setTimeout(() => setIngestStatus(null), 4000)
    } finally {
      setIsIngesting(false)
    }
  }

  const sectors = useMemo(() => ['All Sectors', ...getUniqueSectors()], [])
  const sources = useMemo(() => ['All Publishers', ...getUniqueSources()], [])

  useEffect(() => {
    let isCurrent = true
    fetchLiveNewsArticles({
      searchQuery,
      sentiment: selectedSentiment,
      sector: selectedSector,
      source: selectedSource,
      sortBy,
    })
      .then((items) => {
        if (isCurrent && items && items.length > 0) {
          setLiveArticles(items)
        }
      })
      .catch(() => {
        // Safe fallback already handled in service
      })
    return () => {
      isCurrent = false
    }
  }, [searchQuery, selectedSentiment, selectedSector, selectedSource, sortBy])

  // Filtered articles list factoring in user tracked symbols & sectors
  const filteredArticles = useMemo(() => {
    if (!onlyTracked) return liveArticles
    const trackedSymbols = userPrefs.trackedSymbols || []
    const trackedSectors = userPrefs.trackedSectors || []
    if (trackedSymbols.length === 0 && trackedSectors.length === 0) return liveArticles
    return liveArticles.filter((art) => {
      const matchSym = (art.symbols || []).some((s) => trackedSymbols.includes(s))
      const matchSec = trackedSectors.some(
        (sec) => art.sector && art.sector.toLowerCase().includes(sec.toLowerCase())
      )
      return matchSym || matchSec
    })
  }, [liveArticles, onlyTracked, userPrefs])

  // Active article: either from URL params (e.g. /news/:id) or state
  const activeArticle = useMemo(() => {
    if (id) {
      return liveArticles.find((a) => a.id === id) || getArticleById(id) || null
    }
    return selectedArticleState
  }, [id, liveArticles, selectedArticleState])

  const handleOpenArticle = (article: NewsArticle) => {
    setSelectedArticleState(article)
    navigate(`/news/${article.id}`, { replace: false })
  }

  const handleCloseArticle = () => {
    setSelectedArticleState(null)
    navigate('/news', { replace: false })
  }

  const handleResetFilters = () => {
    setSearchQuery('')
    setSelectedSentiment('All')
    setSelectedSector('All Sectors')
    setSelectedSource('All Publishers')
    setSortBy('newest')
  }

  // Count summaries
  const positiveCount = filteredArticles.filter((a) => a.sentiment === 'Positive').length
  const negativeCount = filteredArticles.filter((a) => a.sentiment === 'Negative').length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              News Intelligence Stream
            </h1>
            <Badge variant="purple" size="sm">
              Phase 4 • Live Feed
            </Badge>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            Real-time RSS ingestion from 5+ major financial publishers with FinBERT sentiment scoring.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {ingestStatus && (
            <span className="text-xs px-2.5 py-1 rounded bg-indigo-950/80 border border-indigo-500/40 text-indigo-300 font-mono animate-fade-in">
              {ingestStatus}
            </span>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={handleLiveIngest}
            disabled={isIngesting}
            leftIcon={<RefreshCw size={13} className={isIngesting ? 'animate-spin' : ''} />}
          >
            {isIngesting ? 'Scraping Live News...' : 'Fetch Live Market RSS'}
          </Button>
          <Button
            variant={onlyTracked ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setOnlyTracked((prev) => !prev)}
            leftIcon={<Sparkles size={13} />}
          >
            {onlyTracked ? 'Showing My Tracked Feed' : 'Filter by My Preferences'}
          </Button>
          <Badge variant="success" size="sm">
            {positiveCount} Bullish
          </Badge>
          <Badge variant="danger" size="sm">
            {negativeCount} Bearish
          </Badge>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleResetFilters}
            leftIcon={<RefreshCw size={13} />}
          >
            Reset
          </Button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="space-y-3 p-4 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm">
        {/* Search & Sort Row */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search news by headline, summary, sector, or symbol (e.g. HDFC, EV, RBI)..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400 whitespace-nowrap">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'newest' | 'highest-sentiment' | 'lowest-sentiment')}
              aria-label="Sort news articles"
              className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="newest">Newest First</option>
              <option value="highest-sentiment">Highest Sentiment</option>
              <option value="lowest-sentiment">Lowest Sentiment</option>
            </select>
          </div>
        </div>

        {/* Sentiment, Sector & Source Dropdowns / Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/80 text-xs">
          {/* Sentiment Filter Pills */}
          <div className="flex items-center gap-1.5">
            {(['All', 'Positive', 'Neutral', 'Negative'] as const).map((sent) => (
              <button
                key={sent}
                type="button"
                onClick={() => setSelectedSentiment(sent)}
                className={`px-2.5 py-1 rounded-full border transition cursor-pointer ${
                  selectedSentiment === sent
                    ? 'bg-indigo-600 border-indigo-500 text-white font-semibold'
                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                {sent}
              </button>
            ))}
          </div>

          <div className="h-4 w-px bg-slate-800 mx-1 hidden sm:block" />

          {/* Sector Select */}
          <select
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
            aria-label="Filter by industry sector"
            className="px-2.5 py-1 bg-slate-950 border border-slate-800 rounded-lg text-slate-300 text-xs focus:outline-none cursor-pointer"
          >
            {sectors.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>

          {/* Source Select */}
          <select
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
            aria-label="Filter by news publisher"
            className="px-2.5 py-1 bg-slate-950 border border-slate-800 rounded-lg text-slate-300 text-xs focus:outline-none cursor-pointer"
          >
            {sources.map((src) => (
              <option key={src} value={src}>
                {src}
              </option>
            ))}
          </select>

          <span className="ml-auto text-slate-500 text-[11px] font-mono">
            Showing {filteredArticles.length} articles
          </span>
        </div>
      </div>

      {/* Feed List */}
      {filteredArticles.length > 0 ? (
        <div className="space-y-3.5">
          {filteredArticles.map((article) => (
            <ArticleCard
              key={article.id}
              article={article}
              onSelectArticle={handleOpenArticle}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<Newspaper size={28} />}
          title="No articles match your filter criteria"
          description="Try clearing your search query or broadening the sector and sentiment filters."
          action={
            <Button variant="secondary" size="sm" onClick={handleResetFilters}>
              Reset All Filters
            </Button>
          }
        />
      )}

      {/* Article Detail Modal / Reader */}
      <ArticleDetailModal
        article={activeArticle}
        onClose={handleCloseArticle}
      />
    </div>
  )
}
