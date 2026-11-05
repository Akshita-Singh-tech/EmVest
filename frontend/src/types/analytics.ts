export interface SentimentTimePoint {
  date: string
  score: number // -1.0 to +1.0 or 0 to 1
  positive: number
  neutral: number
  negative: number
  volume: number
}

export interface SectorSentiment {
  sector: string
  score: number
  momentum: string
  articleCount: number
  status: 'Bullish' | 'Cautious' | 'Bearish' | 'Neutral'
  history: SentimentTimePoint[]
}

export interface CompanySentiment {
  symbol: string
  name: string
  sector: string
  score: number
  delta: string
  newsCount: number
  status: 'Bullish' | 'Neutral' | 'Bearish'
  keyCatalyst: string
  trend: SentimentTimePoint[]
}

export interface PolarityData {
  name: string
  value: number
  color: string
}

