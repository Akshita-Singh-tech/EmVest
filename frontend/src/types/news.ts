export type SentimentPolarity = 'Positive' | 'Neutral' | 'Negative'

export interface NewsArticle {
  id: string
  title: string
  summary: string
  content: string[]
  source: string
  publishedAt: string
  readTime: string
  url: string
  sector: string
  symbols: string[]
  sentiment: SentimentPolarity
  sentimentScore: number // -1.0 to +1.0
  sentimentConfidence: number // 0% to 100%
  keyTakeaways: string[]
  marketImpact: string
}

export interface NewsFilterOptions {
  searchQuery?: string
  sentiment?: 'All' | SentimentPolarity
  sector?: string
  source?: string
  sortBy?: 'newest' | 'highest-sentiment' | 'lowest-sentiment'
}

