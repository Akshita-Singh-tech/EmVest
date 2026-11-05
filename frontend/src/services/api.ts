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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`)
  if (!response.ok) {
    throw new Error(`Health check request failed with status ${response.status}`)
  }
  return response.json()
}

export async function apiGetPreferences(): Promise<BackendPreferences> {
  const response = await fetch(`${API_BASE_URL}/preferences`)
  if (!response.ok) {
    throw new Error(`Failed to fetch preferences: ${response.status}`)
  }
  return response.json()
}

export async function apiUpdatePreferences(data: BackendPreferences): Promise<BackendPreferences> {
  const response = await fetch(`${API_BASE_URL}/preferences`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    throw new Error(`Failed to update preferences: ${response.status}`)
  }
  return response.json()
}

export async function apiGetWatchlist(): Promise<BackendWatchlistItem[]> {
  const response = await fetch(`${API_BASE_URL}/watchlist`)
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
    headers: { 'Content-Type': 'application/json' },
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
  })
  if (!response.ok && response.status !== 404) {
    throw new Error(`Failed to delete item: ${response.status}`)
  }
}
