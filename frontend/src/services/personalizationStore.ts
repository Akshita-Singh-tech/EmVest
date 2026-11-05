import type {
  UserProfile,
  UserPreferences,
  WatchlistRecord,
  ProfileFormErrors,
} from '../types/personalization'
import { getCompanyBySymbol } from './masterData'

const PROFILE_STORAGE_KEY = 'emvest_user_profile_v1'
const PREFERENCES_STORAGE_KEY = 'emvest_user_preferences_v1'
const WATCHLIST_STORAGE_KEY = 'emvest_watchlist_records_v1'

export const defaultProfile: UserProfile = {
  fullName: 'Akshita Singh',
  email: 'akshita.pb.singh@gmail.com',
  experienceLevel: 'Intermediate',
  riskTolerance: 'Moderate',
  investmentHorizon: 'Medium-Term',
}

export const defaultPreferences: UserPreferences = {
  trackedSectors: [
    'Banking & Financial Services',
    'Information Technology',
    'Automobile & Auto Ancillary',
  ],
  trackedSymbols: ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'TATAMOTORS'],
  sentimentAlertThreshold: 0.75,
  emailAlerts: true,
  dailyDigest: true,
  digestTime: '08:30',
  enableAiSuggestions: true,
}

export const defaultWatchlist: WatchlistRecord[] = [
  {
    symbol: 'RELIANCE',
    name: 'Reliance Industries Ltd',
    sector: 'Energy, Oil & Gas',
    addedAt: '2026-11-01',
    price: '₹1,328.40',
    change: '+1.42%',
    sentiment: 'Bullish',
    sentimentScore: 0.74,
    notes: 'Core long-term conglomerate holding; watch retail EBITDA expansion.',
  },
  {
    symbol: 'TCS',
    name: 'Tata Consultancy Services Ltd',
    sector: 'Information Technology',
    addedAt: '2026-11-02',
    price: '₹4,120.00',
    change: '+0.31%',
    sentiment: 'Neutral',
    sentimentScore: 0.52,
    notes: 'Defensive IT pick; tracking deal conversions in BFSI.',
  },
  {
    symbol: 'HDFCBANK',
    name: 'HDFC Bank Ltd',
    sector: 'Banking & Financial Services',
    addedAt: '2026-11-02',
    price: '₹1,745.80',
    change: '-0.52%',
    sentiment: 'Bearish',
    sentimentScore: 0.38,
    notes: 'Monitoring post-merger deposit growth and NIM recovery.',
  },
  {
    symbol: 'INFY',
    name: 'Infosys Ltd',
    sector: 'Information Technology',
    addedAt: '2026-11-03',
    price: '₹1,890.15',
    change: '+2.14%',
    sentiment: 'Bullish',
    sentimentScore: 0.69,
    notes: 'GenAI enterprise traction.',
  },
  {
    symbol: 'TATAMOTORS',
    name: 'Tata Motors Ltd',
    sector: 'Automobile & Auto Ancillary',
    addedAt: '2026-11-04',
    price: '₹840.10',
    change: '+1.85%',
    sentiment: 'Bullish',
    sentimentScore: 0.82,
    notes: 'Domestic EV dominance (>65% market share) & JLR cash generation.',
  },
]

// ============================================================================
// LocalStorage Read / Write operations (Drop-in ready for Phase 6 FastAPI REST)
// ============================================================================

export function getUserProfile(): UserProfile {
  try {
    const raw = localStorage.getItem(PROFILE_STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {
    // Ignore storage parse error
  }
  return defaultProfile
}

export function saveUserProfile(profile: UserProfile): void {
  try {
    localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile))
    window.dispatchEvent(new CustomEvent('emvest_profile_updated', { detail: profile }))
  } catch {
    // Ignore storage write error
  }
}

export function getUserPreferences(): UserPreferences {
  try {
    const raw = localStorage.getItem(PREFERENCES_STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {
    // Ignore storage parse error
  }
  return defaultPreferences
}

export function saveUserPreferences(prefs: UserPreferences): void {
  try {
    localStorage.setItem(PREFERENCES_STORAGE_KEY, JSON.stringify(prefs))
    window.dispatchEvent(new CustomEvent('emvest_preferences_updated', { detail: prefs }))
  } catch {
    // Ignore storage write error
  }
}

export function getWatchlistRecords(): WatchlistRecord[] {
  try {
    const raw = localStorage.getItem(WATCHLIST_STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {
    // Ignore storage parse error
  }
  return defaultWatchlist
}

export function saveWatchlistRecords(records: WatchlistRecord[]): void {
  try {
    localStorage.setItem(WATCHLIST_STORAGE_KEY, JSON.stringify(records))
    window.dispatchEvent(new CustomEvent('emvest_watchlist_updated', { detail: records }))
  } catch {
    // Ignore storage write error
  }
}

export function addSymbolToWatchlist(symbol: string, notes?: string): { success: boolean; error?: string } {
  const current = getWatchlistRecords()
  const upper = symbol.toUpperCase().trim()

  if (current.some((item) => item.symbol === upper)) {
    return { success: false, error: `${upper} is already in your watchlist.` }
  }

  const master = getCompanyBySymbol(upper)
  const item: WatchlistRecord = {
    symbol: upper,
    name: master ? master.name : `${upper} Corporation`,
    sector: master ? master.sector : 'Diversified Equities',
    addedAt: new Date().toISOString().split('T')[0],
    price: master && master.basePrice ? `₹${master.basePrice.toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '₹1,000.00',
    change: '+0.00%',
    sentiment: 'Neutral',
    sentimentScore: 0.5,
    notes: notes || undefined,
  }

  saveWatchlistRecords([item, ...current])
  return { success: true }
}

export function removeSymbolFromWatchlist(symbol: string): void {
  const current = getWatchlistRecords()
  const updated = current.filter((item) => item.symbol !== symbol.toUpperCase())
  saveWatchlistRecords(updated)
}

// ============================================================================
// Form Validation (Exit Check Requirement: "Forms validated, state structured")
// ============================================================================

export function validateProfileForm(
  profile: UserProfile,
  preferences: UserPreferences
): ProfileFormErrors {
  const errors: ProfileFormErrors = {}

  // Name validation
  if (!profile.fullName || profile.fullName.trim().length < 2) {
    errors.fullName = 'Full name must be at least 2 characters.'
  }

  // Email validation regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!profile.email || !emailRegex.test(profile.email.trim())) {
    errors.email = 'Please provide a valid email address.'
  }

  // Tracked sectors validation
  if (!preferences.trackedSectors || preferences.trackedSectors.length === 0) {
    errors.trackedSectors = 'Please select at least one priority industry sector.'
  }

  // Tracked symbols validation
  if (!preferences.trackedSymbols || preferences.trackedSymbols.length === 0) {
    errors.trackedSymbols = 'Please select at least one primary equity to track.'
  }

  return errors
}
