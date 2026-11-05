import { Link } from 'react-router-dom'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { X, Bot, ExternalLink, Sparkles } from '../ui/Icons'
import type { NewsArticle } from '../../types/news'

interface ArticleDetailModalProps {
  article: NewsArticle | null
  onClose: () => void
}

export function ArticleDetailModal({ article, onClose }: ArticleDetailModalProps) {
  if (!article) return null

  const getBadgeVariant = (sentiment: string) => {
    if (sentiment === 'Positive') return 'success'
    if (sentiment === 'Negative') return 'danger'
    return 'default'
  }

  const formattedScore =
    article.sentimentScore > 0
      ? `+${article.sentimentScore.toFixed(2)}`
      : article.sentimentScore.toFixed(2)

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 animate-in fade-in duration-150">
      <div
        role="presentation"
        onClick={onClose}
        className="fixed inset-0"
      />

      <div className="relative w-full max-w-3xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] z-10">
        {/* Modal Top Bar */}
        <div className="flex items-center justify-between p-5 border-b border-slate-800/80 bg-slate-950/60">
          <div className="flex items-center gap-2 text-xs">
            <span className="font-bold text-white">{article.source}</span>
            <span className="text-slate-600">•</span>
            <span className="text-slate-400">{article.publishedAt}</span>
            <span className="text-slate-600">•</span>
            <Badge variant="default" size="sm">
              {article.sector}
            </Badge>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            aria-label="Close article modal"
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Scrollable Content */}
        <div className="overflow-y-auto p-6 space-y-6 flex-1">
          {/* Article Title */}
          <div className="space-y-3">
            <h2 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight leading-snug">
              {article.title}
            </h2>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant={getBadgeVariant(article.sentiment)} size="md">
                FinBERT Score: {formattedScore} ({article.sentiment})
              </Badge>
              <Badge variant="purple" size="md">
                {article.sentimentConfidence}% Model Confidence
              </Badge>
            </div>
          </div>

          {/* FinBERT AI Intelligence Panel */}
          <div className="rounded-xl border border-indigo-500/30 bg-gradient-to-br from-indigo-950/30 via-slate-900 to-slate-900 p-5 space-y-4">
            <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider">
              <Sparkles size={15} />
              <span>FinBERT Ingestion & Market Impact Intelligence</span>
            </div>

            <div className="space-y-2">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Market Impact Analysis
              </div>
              <p className="text-sm font-medium text-slate-200 leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                {article.marketImpact}
              </p>
            </div>

            {/* Key Takeaways */}
            <div className="space-y-2 pt-1">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Key Strategic Takeaways
              </div>
              <ul className="space-y-1.5 text-xs text-slate-300">
                {article.keyTakeaways.map((takeaway) => (
                  <li key={takeaway} className="flex items-start gap-2">
                    <span className="text-indigo-400 font-bold">•</span>
                    <span>{takeaway}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Full Article Body Paragraphs */}
          <div className="space-y-4 text-sm text-slate-300 leading-relaxed border-t border-slate-800/80 pt-5">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Full Ingested Story
            </div>
            {article.content.map((p, idx) => (
              <p key={idx} className="text-slate-300 leading-relaxed">
                {p}
              </p>
            ))}
          </div>

          {/* Cited Stock Symbols */}
          <div className="flex flex-wrap items-center gap-2 pt-4 border-t border-slate-800 text-xs">
            <span className="text-slate-400 font-medium">Mentioned Equities:</span>
            {article.symbols.map((sym) => (
              <span
                key={sym}
                className="px-2.5 py-1 rounded bg-slate-800 text-slate-200 font-mono font-bold border border-slate-700"
              >
                {sym}
              </span>
            ))}
          </div>
        </div>

        {/* Modal Footer Actions */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-950/80 flex flex-wrap items-center justify-between gap-3">
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition"
          >
            <span>Read on {article.source}</span>
            <ExternalLink size={14} />
          </a>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={onClose}>
              Close
            </Button>
            <Link to="/chat">
              <Button size="sm" leftIcon={<Bot size={14} />}>
                Ask AI Assistant
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
