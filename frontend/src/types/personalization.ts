export type RiskTolerance = 'Conservative' | 'Moderate' | 'Aggressive'
export type InvestmentHorizon = 'Intraday' | 'Swing' | 'Medium-Term' | 'Long-Term'
export type InvestorExperience = 'Beginner' | 'Intermediate' | 'Advanced' | 'Institutional'

export interface MasterCompany {
  symbol: string
  name: string
  sector: string
  exchange: 'NSE' | 'BSE' | 'NSE/BSE'
  marketCapCategory: 'Large Cap' | 'Mid Cap' | 'Small Cap'
  basePrice?: number
}

export interface UserProfile {
  fullName: string
  email: string
  experienceLevel: InvestorExperience
  riskTolerance: RiskTolerance
  investmentHorizon: InvestmentHorizon
}

export interface UserPreferences {
  trackedSectors: string[]
  trackedSymbols: string[]
  sentimentAlertThreshold: number // -1.0 to 1.0 (e.g. 0.7 triggers alert)
  emailAlerts: boolean
  dailyDigest: boolean
  digestTime: string // e.g. "08:30"
  enableAiSuggestions: boolean
}

export interface WatchlistRecord {
  symbol: string
  name: string
  sector: string
  addedAt: string
  price: string
  change: string
  sentiment: 'Bullish' | 'Neutral' | 'Bearish'
  sentimentScore: number
  notes?: string
}

export interface ProfileFormErrors {
  fullName?: string
  email?: string
  trackedSectors?: string
  trackedSymbols?: string
}

