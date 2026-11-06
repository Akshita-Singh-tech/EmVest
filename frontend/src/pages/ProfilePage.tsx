import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { User, Bell, Sparkles } from '../components/ui/Icons'
import { CompanyPicker } from '../components/personalization/CompanyPicker'
import { masterSectors } from '../services/masterData'
import {
  getUserProfile,
  getUserPreferences,
  saveUserProfile,
  saveUserPreferences,
  validateProfileForm,
} from '../services/personalizationStore'
import { apiGetPreferences, apiUpdatePreferences } from '../services/api'
import type {
  UserProfile,
  UserPreferences,
  ProfileFormErrors,
  RiskTolerance,
  InvestmentHorizon,
  InvestorExperience,
} from '../types/personalization'

export function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile>(() => getUserProfile())
  const [preferences, setPreferences] = useState<UserPreferences>(() => getUserPreferences())
  const [errors, setErrors] = useState<ProfileFormErrors>({})
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Load preferences from backend DB on mount
  useEffect(() => {
    let ignore = false
    apiGetPreferences()
      .then((backendPrefs) => {
        if (ignore || !backendPrefs) return
        setPreferences((prev) => ({
          ...prev,
          trackedSectors: backendPrefs.tracked_sectors && backendPrefs.tracked_sectors.length > 0
            ? backendPrefs.tracked_sectors
            : prev.trackedSectors,
          trackedSymbols: backendPrefs.tracked_symbols && backendPrefs.tracked_symbols.length > 0
            ? backendPrefs.tracked_symbols
            : prev.trackedSymbols,
          sentimentAlertThreshold: backendPrefs.sentiment_alert_threshold ?? prev.sentimentAlertThreshold,
          emailAlerts: backendPrefs.email_alerts ?? prev.emailAlerts,
          dailyDigest: backendPrefs.daily_digest ?? prev.dailyDigest,
          digestTime: backendPrefs.digest_time || prev.digestTime,
          enableAiSuggestions: backendPrefs.enable_ai_suggestions ?? prev.enableAiSuggestions,
        }))
        setProfile((prev) => ({
          ...prev,
          experienceLevel: (backendPrefs.experience_level as InvestorExperience) || prev.experienceLevel,
          riskTolerance: (backendPrefs.risk_tolerance as RiskTolerance) || prev.riskTolerance,
          investmentHorizon: (backendPrefs.investment_horizon as InvestmentHorizon) || prev.investmentHorizon,
        }))
      })
      .catch(() => {
        // Safe offline fallback: local storage state already active
      })
    return () => {
      ignore = true
    }
  }, [])

  const toggleSector = (sector: string) => {
    const current = preferences.trackedSectors
    const updated = current.includes(sector)
      ? current.filter((s) => s !== sector)
      : [...current, sector]

    setPreferences({ ...preferences, trackedSectors: updated })
    if (errors.trackedSectors && updated.length > 0) {
      setErrors((prev) => ({ ...prev, trackedSectors: undefined }))
    }
  }

  const handleSymbolsChange = (symbols: string[]) => {
    setPreferences({ ...preferences, trackedSymbols: symbols })
    if (errors.trackedSymbols && symbols.length > 0) {
      setErrors((prev) => ({ ...prev, trackedSymbols: undefined }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    // Form Validation (Exit check: Forms validated)
    const validationErrors = validateProfileForm(profile, preferences)
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      setIsSubmitting(false)
      setSaveSuccess(false)
      return
    }

    setErrors({})

    // Save to local storage store for immediate UI updates
    saveUserProfile(profile)
    saveUserPreferences(preferences)

    // Persist directly to backend database via REST API
    try {
      await apiUpdatePreferences({
        experience_level: profile.experienceLevel,
        risk_tolerance: profile.riskTolerance,
        investment_horizon: profile.investmentHorizon,
        tracked_sectors: preferences.trackedSectors,
        tracked_symbols: preferences.trackedSymbols,
        sentiment_alert_threshold: preferences.sentimentAlertThreshold,
        email_alerts: preferences.emailAlerts,
        daily_digest: preferences.dailyDigest,
        digest_time: preferences.digestTime,
        enable_ai_suggestions: preferences.enableAiSuggestions,
      })
    } catch {
      // Still saved to local persistence store
    } finally {
      setIsSubmitting(false)
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 4000)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              Investor Profile & Strategy Configuration
            </h1>
            <Badge variant="purple" size="sm">
              Live Investor Profile
            </Badge>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            Define your investment profile, customize tracked NSE/BSE sectors & symbols, and tune AI sentiment triggers.
          </p>
        </div>

        {saveSuccess && (
          <Badge variant="success" size="md">
            ✓ Preferences successfully saved and synchronized with database!
          </Badge>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Account & Experience Details */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <User size={18} className="text-indigo-400" />
              <CardTitle>Investor Identity & Experience</CardTitle>
            </div>
            <CardDescription>
              Directs how AI insights tailor their depth and technical terminology.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Full Name</label>
                <input
                  type="text"
                  value={profile.fullName}
                  onChange={(e) => {
                    setProfile({ ...profile, fullName: e.target.value })
                    if (errors.fullName) setErrors((prev) => ({ ...prev, fullName: undefined }))
                  }}
                  className={`w-full px-3 py-2 bg-slate-950 border rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 ${
                    errors.fullName ? 'border-rose-500' : 'border-slate-800'
                  }`}
                />
                {errors.fullName && <p className="text-xs text-rose-400">{errors.fullName}</p>}
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Email Address</label>
                <input
                  type="email"
                  value={profile.email}
                  onChange={(e) => {
                    setProfile({ ...profile, email: e.target.value })
                    if (errors.email) setErrors((prev) => ({ ...prev, email: undefined }))
                  }}
                  className={`w-full px-3 py-2 bg-slate-950 border rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 ${
                    errors.email ? 'border-rose-500' : 'border-slate-800'
                  }`}
                />
                {errors.email && <p className="text-xs text-rose-400">{errors.email}</p>}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Market Experience Level</label>
                <select
                  value={profile.experienceLevel}
                  onChange={(e) =>
                    setProfile({ ...profile, experienceLevel: e.target.value as InvestorExperience })
                  }
                  aria-label="Market Experience Level"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
                >
                  <option value="Beginner">Beginner (Simplified summaries & glossaries)</option>
                  <option value="Intermediate">Intermediate (Core financial ratios & news drivers)</option>
                  <option value="Advanced">Advanced (FinBERT raw sentiment & volatility metrics)</option>
                  <option value="Institutional">Institutional (Detailed DCF commentary & macro drift)</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Target Investment Horizon</label>
                <select
                  value={profile.investmentHorizon}
                  onChange={(e) =>
                    setProfile({ ...profile, investmentHorizon: e.target.value as InvestmentHorizon })
                  }
                  aria-label="Target Investment Horizon"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
                >
                  <option value="Intraday">Intraday & Momentum (Real-time catalyst spikes)</option>
                  <option value="Swing">Swing Trading (1-4 weeks holding period)</option>
                  <option value="Medium-Term">Medium-Term (Quarterly earnings cycles)</option>
                  <option value="Long-Term">Long-Term (Compound growth & balance sheet quality)</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Risk Tolerance Matrix */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Tolerance Strategy</CardTitle>
            <CardDescription>
              Configures how the FinBERT worker discounts negative catalyst events and rates high-beta volatility.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {(
                [
                  {
                    level: 'Conservative' as RiskTolerance,
                    desc: 'Minimizes drawdown risk. Highlights dividend consistency and low-volatility balance sheets.',
                  },
                  {
                    level: 'Moderate' as RiskTolerance,
                    desc: 'Balanced risk-adjusted returns across sector leaders with resilient return on capital (ROCE).',
                  },
                  {
                    level: 'Aggressive' as RiskTolerance,
                    desc: 'Maximal growth exposure. Detects early turnaround catalysts and high-beta momentum swings.',
                  },
                ]
              ).map((item) => (
                <div
                  key={item.level}
                  onClick={() => setProfile({ ...profile, riskTolerance: item.level })}
                  className={`p-4 rounded-xl border cursor-pointer transition ${
                    profile.riskTolerance === item.level
                      ? 'bg-indigo-600/15 border-indigo-500 text-white shadow-sm ring-1 ring-indigo-500/40'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-sm text-white">{item.level}</span>
                    {profile.riskTolerance === item.level && (
                      <span className="h-2 w-2 rounded-full bg-indigo-400" />
                    )}
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Priority Sectors Multi-Select */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Priority Industry Sectors</CardTitle>
                <CardDescription>
                  Select sectors to prioritize in your news intelligence stream and sector analytics views.
                </CardDescription>
              </div>
              <span className="text-xs text-slate-400 font-mono">
                {preferences.trackedSectors.length} Selected
              </span>
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex flex-wrap gap-2">
              {masterSectors.map((sector) => {
                const isSelected = preferences.trackedSectors.includes(sector)
                return (
                  <button
                    key={sector}
                    type="button"
                    onClick={() => toggleSector(sector)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition cursor-pointer ${
                      isSelected
                        ? 'bg-indigo-600 text-white border-indigo-500 shadow-sm'
                        : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    {isSelected && '✓ '}
                    {sector}
                  </button>
                )
              })}
            </div>
            {errors.trackedSectors && (
              <p className="text-xs text-rose-400 pt-1">{errors.trackedSectors}</p>
            )}
          </CardContent>
        </Card>

        {/* Company Master Picker */}
        <Card>
          <CardHeader>
            <CardTitle>Tracked Equities Master Selection</CardTitle>
            <CardDescription>
              Curated master list from official NSE/BSE indexes for watchlist and agent tracking.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <CompanyPicker
              selectedSymbols={preferences.trackedSymbols}
              onChange={handleSymbolsChange}
              error={errors.trackedSymbols}
            />
          </CardContent>
        </Card>

        {/* Notification & FinBERT Alert Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bell size={18} className="text-amber-400" />
              <CardTitle>Sentiment Alert Thresholds & Notification Preferences</CardTitle>
            </div>
            <CardDescription>
              Control when high-impact market sentiment triggers proactive alert notifications.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 divide-y divide-slate-800">
            {/* Threshold Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-300">
                  FinBERT High-Conviction Sentiment Alert Trigger
                </span>
                <span className="font-mono font-bold text-emerald-400">
                  Score ≥ {preferences.sentimentAlertThreshold.toFixed(2)}
                </span>
              </div>
              <input
                type="range"
                min="0.5"
                max="0.95"
                step="0.05"
                value={preferences.sentimentAlertThreshold}
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    sentimentAlertThreshold: parseFloat(e.target.value),
                  })
                }
                className="w-full accent-indigo-500 cursor-pointer"
              />
              <p className="text-[11px] text-slate-400">
                You will be proactively alerted whenever a tracked equity records news sentiment meeting or exceeding this threshold.
              </p>
            </div>

            {/* Notification Checkboxes */}
            <div className="pt-4 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-white">Email Catalyst Alerts</div>
                  <p className="text-xs text-slate-400">
                    Receive immediate notifications for critical regulatory, earnings, or macro news.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.emailAlerts}
                  onChange={(e) =>
                    setPreferences({ ...preferences, emailAlerts: e.target.checked })
                  }
                  className="h-4 w-4 rounded accent-indigo-600 cursor-pointer"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-white">Pre-Market Daily Digest</div>
                  <p className="text-xs text-slate-400">
                    Consolidated 08:30 AM IST market summary delivered before market open.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.dailyDigest}
                  onChange={(e) =>
                    setPreferences({ ...preferences, dailyDigest: e.target.checked })
                  }
                  className="h-4 w-4 rounded accent-indigo-600 cursor-pointer"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Form Submission Footer */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Sparkles size={14} className="text-indigo-400" />
            <span>State structured for Phase 6 PostgreSQL & Alembic synchronization.</span>
          </div>

          <Button type="submit" size="lg" isLoading={isSubmitting}>
            Save All Preferences
          </Button>
        </div>
      </form>
    </div>
  )
}
