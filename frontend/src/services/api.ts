export interface HealthResponse {
  status: string
}

export interface BackendPreferences {
  id?: number
  experience_level: string
  risk_tolerance: string
  investment_horizon: string
  tracked_sectors: string[]
  tracked_symbols: string[]
  sentiment_alert_threshold: number
  email_alerts: boolean
  daily_digest: boolean
  digest_time: string
  enable_ai_suggestions: boolean
}

export interface BackendWatchlistItem {
  id?: number
  symbol: string
  name: string
  sector: string
  notes?: string
  added_at?: string
}

export interface BackendArticle {
  id: number
  external_id: string
  title: string
  summary: string
  content: string
  source: string
  url: string
  published_at: string
  sector: string
  symbols: string[]
  sentiment: 'Positive' | 'Neutral' | 'Negative'
  sentiment_score: number
  sentiment_confidence: number
  key_takeaways: string[]
  market_impact?: string
}

export interface BackendOverview {
  composite_score: number
  overall_sentiment: string
  total_articles: number
  polarity: {
    positive: number
    neutral: number
    negative: number
    positive_percentage: number
    neutral_percentage: number
    negative_percentage: number
  }
  trajectory: Array<{
    date: string
    score: number
    source: string
    title: string
  }>
}

export interface BackendSectorAnalytics {
  sectors: Array<{
    sector: string
    score: number
    article_count: number
    status: string
    momentum: string
  }>
}

export interface BackendCompanyAnalytics {
  symbol: string
  score: number
  status: string
  article_count: number
  catalysts: string[]
  recent_articles: Array<{
    title: string
    source: string
    score: number
    sentiment: string
    published_at: string
  }>
}

export interface BackendCitation {
  id: number
  title: string
  source: string
  url: string
  published_at?: string
  sentiment: string
  sentiment_score: number
  symbols?: string[]
  sector?: string
}

export interface BackendSentimentSummary {
  aggregate_score: number
  sentiment_label: string
  article_count: number
  positive_count: number
  neutral_count: number
  negative_count: number
}

export interface BackendChatResponse {
  session_id: string
  role: string
  answer: string
  citations: BackendCitation[]
  suggested_followups: string[]
  sentiment_summary?: BackendSentimentSummary
}

export interface BackendChatMessageRecord {
  id: number
  session_id: string
  role: 'user' | 'assistant'
  content: string
  citations?: BackendCitation[]
  created_at: string
}

export interface BackendChatHistory {
  session_id: string
  messages: BackendChatMessageRecord[]
}

export interface BackendChatSessionSummary {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
  last_message_preview?: string | null
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export function getAuthToken(): string | null {
  try {
    return localStorage.getItem('emvest_token')
  } catch {
    return null
  }
}

export function setAuthToken(token: string): void {
  try {
    localStorage.setItem('emvest_token', token)
  } catch {
    // ignore
  }
}

export function clearAuthToken(): void {
  try {
    localStorage.removeItem('emvest_token')
  } catch {
    // ignore
  }
}

export function authHeaders(extraHeaders: Record<string, string> = {}): Record<string, string> {
  const token = getAuthToken()
  if (token) {
    return {
      ...extraHeaders,
      Authorization: `Bearer ${token}`,
    }
  }
  return extraHeaders
}

export interface AuthUser {
  id: number
  email: string
  full_name: string
  is_active?: boolean
  created_at?: string
}

export interface AuthTokenResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

export async function apiLogin(email: string, password: string): Promise<AuthTokenResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
  })
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    throw new Error(errorBody.detail || 'Incorrect email or password.')
  }
  const data: AuthTokenResponse = await response.json()
  setAuthToken(data.access_token)
  return data
}

export async function apiSignup(fullName: string, email: string, password: string): Promise<AuthTokenResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ full_name: fullName.trim(), email: email.trim().toLowerCase(), password }),
  })
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    throw new Error(errorBody.detail || 'Failed to create account.')
  }
  const data: AuthTokenResponse = await response.json()
  setAuthToken(data.access_token)
  return data
}

export async function apiGetMe(): Promise<AuthUser> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: authHeaders(),
  })
  if (!response.ok) {
    throw new Error(`Authentication check failed: ${response.status}`)
  }
  return response.json()
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`)
  if (!response.ok) {
    throw new Error(`Health check request failed with status ${response.status}`)
  }
  return response.json()
}

// ============================================================================
// Preferences & Watchlists (Phase 6)
// ============================================================================

export async function apiGetPreferences(): Promise<BackendPreferences> {
  const response = await fetch(`${API_BASE_URL}/preferences`, {
    headers: authHeaders(),
  })
  if (!response.ok) {
    throw new Error(`Failed to fetch preferences: ${response.status}`)
  }
  return response.json()
}

export async function apiUpdatePreferences(data: BackendPreferences): Promise<BackendPreferences> {
  const response = await fetch(`${API_BASE_URL}/preferences`, {
    method: 'PUT',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    throw new Error(`Failed to update preferences: ${response.status}`)
  }
  return response.json()
}

export async function apiGetWatchlist(): Promise<BackendWatchlistItem[]> {
  const response = await fetch(`${API_BASE_URL}/watchlist`, {
    headers: authHeaders(),
  })
  if (!response.ok) {
    throw new Error(`Failed to fetch watchlist: ${response.status}`)
  }
  return response.json()
}

export async function apiAddWatchlist(item: {
  symbol: string
  name?: string
  sector?: string
  notes?: string
}): Promise<BackendWatchlistItem> {
  const response = await fetch(`${API_BASE_URL}/watchlist`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(item),
  })
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    throw new Error(errorBody.detail || `Failed to add item: ${response.status}`)
  }
  return response.json()
}

export async function apiDeleteWatchlist(symbol: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/watchlist/${symbol.toUpperCase()}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  if (!response.ok && response.status !== 404) {
    throw new Error(`Failed to delete item: ${response.status}`)
  }
}

// ============================================================================
// Real Ingested News & Analytics (Phase 7)
// ============================================================================

export async function apiGetNewsArticles(options: {
  search?: string
  sentiment?: string
  sector?: string
  source?: string
  symbol?: string
} = {}): Promise<BackendArticle[]> {
  const params = new URLSearchParams()
  if (options.search) params.set('search', options.search)
  if (options.sentiment && options.sentiment !== 'All') params.set('sentiment', options.sentiment)
  if (options.sector && options.sector !== 'All Sectors') params.set('sector', options.sector)
  if (options.source && options.source !== 'All Publishers') params.set('source', options.source)
  if (options.symbol) params.set('symbol', options.symbol)

  const url = `${API_BASE_URL}/news?${params.toString()}`
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`Failed to fetch news feed: ${response.status}`)
  }
  return response.json()
}

export async function apiGetAnalyticsOverview(): Promise<BackendOverview> {
  const response = await fetch(`${API_BASE_URL}/analytics/overview`)
  if (!response.ok) {
    throw new Error(`Failed to fetch analytics overview: ${response.status}`)
  }
  return response.json()
}

export async function apiGetSectorAnalytics(): Promise<BackendSectorAnalytics> {
  const response = await fetch(`${API_BASE_URL}/analytics/sectors`)
  if (!response.ok) {
    throw new Error(`Failed to fetch sector analytics: ${response.status}`)
  }
  return response.json()
}

export async function apiGetCompanyAnalytics(symbol: string): Promise<BackendCompanyAnalytics> {
  const response = await fetch(`${API_BASE_URL}/analytics/company/${symbol.toUpperCase()}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch company analytics for ${symbol}: ${response.status}`)
  }
  return response.json()
}

export async function apiTriggerIngestion(): Promise<{ status: string; newly_ingested: number; total_articles: number }> {
  const response = await fetch(`${API_BASE_URL}/news/ingest`, { method: 'POST' })
  if (!response.ok) {
    throw new Error(`Failed to trigger ingestion: ${response.status}`)
  }
  return response.json()
}

export async function apiSendChatQuery(payload: {
  query: string;
  session_id?: string;
  symbols?: string[];
}): Promise<BackendChatResponse> {
  const token = getAuthToken()
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const response = await fetch(`${API_BASE_URL}/chat/query`, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(8000),
  })
  if (!response.ok) {
    throw new Error(`Chat query failed with status ${response.status}`)
  }
  return response.json()
}

export async function apiGetChatHistory(sessionId: string): Promise<BackendChatHistory> {
  const response = await fetch(`${API_BASE_URL}/chat/history/${sessionId}`, {
    signal: AbortSignal.timeout(8000),
  })
  if (!response.ok) {
    throw new Error(`Failed to fetch chat history: ${response.status}`)
  }
  return response.json()
}

export async function apiClearChatHistory(sessionId: string): Promise<{ status: string; session_id: string }> {
  const response = await fetch(`${API_BASE_URL}/chat/history/${sessionId}`, {
    method: 'DELETE',
    signal: AbortSignal.timeout(8000),
  })
  if (!response.ok) {
    throw new Error(`Failed to clear chat history: ${response.status}`)
  }
  return response.json()
}

export async function apiGetChatSessions(): Promise<BackendChatSessionSummary[]> {
  const token = getAuthToken()
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`

  const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
    headers,
    signal: AbortSignal.timeout(8000),
  })
  if (!response.ok) {
    throw new Error(`Failed to fetch chat sessions: ${response.status}`)
  }
  return response.json()
}

export async function apiCreateChatSession(title: string = 'New Conversation'): Promise<BackendChatSessionSummary> {
  const token = getAuthToken()
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ title }),
    signal: AbortSignal.timeout(8000),
  })
  if (!response.ok) {
    throw new Error(`Failed to create chat session: ${response.status}`)
  }
  return response.json()
}

export async function apiDeleteChatSession(sessionId: string): Promise<{ status: string; session_id: string }> {
  return apiClearChatHistory(sessionId)
}


export interface MarketQuoteIndex {
  name: string
  value: string
  raw_price: number
  change: string
  positive: boolean
  sentiment: string
}

export interface MarketQuoteEquity {
  symbol: string
  name: string
  price: string
  raw_price: number
  change: string
  positive: boolean
  sentiment: string
}

export interface MarketQuotesResponse {
  status: string
  last_updated: string
  indices: MarketQuoteIndex[]
  watchlist: MarketQuoteEquity[]
}

export async function apiGetMarketQuotes(symbols?: string[]): Promise<MarketQuotesResponse> {
  const url = symbols && symbols.length > 0
    ? `${API_BASE_URL}/analytics/quotes?symbols=${encodeURIComponent(symbols.join(','))}`
    : `${API_BASE_URL}/analytics/quotes`
  const response = await fetch(url, {
    signal: AbortSignal.timeout(6000),
  })
  if (!response.ok) {
    throw new Error(`Failed to fetch market quotes: ${response.status}`)
  }
  return response.json()
}
