import { useState, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Search, RefreshCw, Newspaper } from '../components/ui/Icons'
import { EmptyState } from '../components/common/EmptyState'
import { ArticleCard } from '../components/news/ArticleCard'
import { ArticleDetailModal } from '../components/news/ArticleDetailModal'
import {
  getNewsArticles,
  getArticleById,
  getUniqueSectors,
  getUniqueSources,
} from '../services/newsData'
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

  const sectors = useMemo(() => ['All Sectors', ...getUniqueSectors()], [])
  const sources = useMemo(() => ['All Publishers', ...getUniqueSources()], [])

  // Filtered articles list
  const filteredArticles = useMemo(() => {
    return getNewsArticles({
      searchQuery,
      sentiment: selectedSentiment,
      sector: selectedSector,
      source: selectedSource,
      sortBy,
    })
  }, [searchQuery, selectedSentiment, selectedSector, selectedSource, sortBy])

  // Active article: either from URL params (e.g. /news/:id) or state
  const activeArticle = useMemo(() => {
    if (id) {
      return getArticleById(id) || null
    }
    return selectedArticleState
  }, [id, selectedArticleState])

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

        <div className="flex items-center gap-2">
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
