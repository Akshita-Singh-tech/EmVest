import { Link } from 'react-router-dom'
import { Card, CardContent } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Bot, ChevronRight, ExternalLink } from '../ui/Icons'
import type { NewsArticle } from '../../types/news'

interface ArticleCardProps {
  article: NewsArticle
  onSelectArticle: (article: NewsArticle) => void
}

export function ArticleCard({ article, onSelectArticle }: ArticleCardProps) {
  const getBadgeVariant = (sentiment: string) => {
    if (sentiment === 'Positive') return 'success'
    if (sentiment === 'Negative') return 'danger'
    return 'default'
  }

  const formattedScore = article.sentimentScore > 0 ? `+${article.sentimentScore.toFixed(2)}` : article.sentimentScore.toFixed(2)

  return (
    <Card className="hover:border-slate-700 transition duration-150">
      <CardContent className="p-5 space-y-3.5">
        {/* Top Header: Source, Time, Sector, Sentiment Badge */}
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-200">{article.source}</span>
            <span className="text-slate-600">•</span>
            <span className="text-slate-400">{article.publishedAt}</span>
            <span className="text-slate-600">•</span>
            <span className="text-slate-400">{article.readTime}</span>
            <span className="text-slate-600">•</span>
            <Badge variant="default" size="sm">
              {article.sector}
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant={getBadgeVariant(article.sentiment)} size="sm">
              FinBERT: {formattedScore} ({article.sentimentConfidence}% conf)
            </Badge>
          </div>
        </div>

        {/* Title and Summary */}
        <div className="space-y-1.5">
          <h3
            onClick={() => onSelectArticle(article)}
            className="text-base font-bold text-white hover:text-indigo-300 transition cursor-pointer leading-snug"
          >
            {article.title}
          </h3>
          <p className="text-sm text-slate-400 leading-relaxed line-clamp-2">
            {article.summary}
          </p>
        </div>

        {/* Stock Symbol Tags & Market Impact Preview */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">Cited Symbols:</span>
            {article.symbols.map((sym) => (
              <span
                key={sym}
                className="px-2 py-0.5 rounded bg-slate-800/90 text-slate-300 font-mono text-[11px] font-semibold border border-slate-700/60"
              >
                {sym}
              </span>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/chat"
              className="text-slate-400 hover:text-indigo-300 flex items-center gap-1 font-medium transition"
            >
              <Bot size={14} />
              <span>Ask AI</span>
            </Link>

            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-white transition"
              title="Open source publisher"
            >
              <ExternalLink size={14} />
            </a>

            <button
              type="button"
              onClick={() => onSelectArticle(article)}
              className="text-indigo-400 hover:text-indigo-300 flex items-center gap-0.5 font-semibold cursor-pointer"
            >
              <span>View Analysis</span>
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

