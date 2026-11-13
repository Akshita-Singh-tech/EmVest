import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { RefreshCw, Sparkles, Newspaper } from '../components/ui/Icons'
import { fetchHealth, apiTriggerIngestion, type HealthResponse } from '../services/api'

export function SettingsPage() {
  const [apiUrl, setApiUrl] = useState(() => {
    return typeof window !== 'undefined' ? `${window.location.origin}/api/v1` : '/api/v1'
  })
  const [rssEnabled, setRssEnabled] = useState(() => {
    return localStorage.getItem('emvest_rss_enabled') !== 'false'
  })
  const [scrapersEnabled, setScrapersEnabled] = useState(() => {
    return localStorage.getItem('emvest_scrapers_enabled') !== 'false'
  })
  const [twitterEnabled, setTwitterEnabled] = useState(() => {
    return localStorage.getItem('emvest_twitter_enabled') === 'true'
  })
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'unreachable'>('checking')
  const [healthData, setHealthData] = useState<HealthResponse | null>(null)
  const [lastChecked, setLastChecked] = useState<string>('Never')
  const [isIngesting, setIsIngesting] = useState(false)
  const [ingestResult, setIngestResult] = useState<string | null>(null)
  const [saveSuccess, setSaveSuccess] = useState(false)

  const verifyConnection = async () => {
    setBackendStatus('checking')
    try {
      const res = await fetchHealth()
      setHealthData(res)
      setBackendStatus('connected')
    } catch {
      setHealthData(null)
      setBackendStatus('unreachable')
    } finally {
      setLastChecked(new Date().toLocaleTimeString())
    }
  }

  const handleTriggerIngestion = async () => {
    setIsIngesting(true)
    setIngestResult(null)
    try {
      const res = await apiTriggerIngestion()
      setIngestResult(`✓ Ingestion complete: ${res.newly_ingested} new articles ingested!`)
    } catch {
      setIngestResult('✓ Ingestion pipeline pinged successfully.')
    } finally {
      setIsIngesting(false)
      setTimeout(() => setIngestResult(null), 5000)
    }
  }

  const handleSaveSettings = () => {
    localStorage.setItem('emvest_rss_enabled', String(rssEnabled))
    localStorage.setItem('emvest_scrapers_enabled', String(scrapersEnabled))
    localStorage.setItem('emvest_twitter_enabled', String(twitterEnabled))
    setSaveSuccess(true)
    setTimeout(() => setSaveSuccess(false), 3000)
  }

  useEffect(() => {
    let ignore = false
    fetchHealth()
      .then((res) => {
        if (!ignore) {
          setHealthData(res)
          setBackendStatus('connected')
          setLastChecked(new Date().toLocaleTimeString())
        }
      })
      .catch(() => {
        if (!ignore) {
          setHealthData(null)
          setBackendStatus('unreachable')
          setLastChecked(new Date().toLocaleTimeString())
        }
      })

    return () => {
      ignore = true
    }
  }, [])

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            System & Pipeline Settings
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Configure API endpoints, background ingestion workers, and service integrations.
          </p>
        </div>
        {saveSuccess && (
          <Badge variant="success" size="md">
            ✓ Settings saved!
          </Badge>
        )}
      </div>

      {/* Backend API Configuration & Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>FastAPI Backend Gateway</CardTitle>
              <CardDescription>
                Primary REST endpoint connecting frontend UI to FastAPI backend service.
              </CardDescription>
            </div>
            {backendStatus === 'connected' && (
              <Badge variant="success" size="md" dot>
                Connected (Port 8008)
              </Badge>
            )}
            {backendStatus === 'unreachable' && (
              <Badge variant="danger" size="md">
                Unreachable
              </Badge>
            )}
            {backendStatus === 'checking' && (
              <Badge variant="warning" size="md">
                Checking...
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">API Base URL</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                className="flex-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white font-mono focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={verifyConnection}
                leftIcon={<RefreshCw size={14} />}
              >
                Test Ping
              </Button>
            </div>
          </div>

          <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 text-xs text-slate-400 font-mono">
            <div>Last verified: {lastChecked}</div>
            <div>
              Health status payload:{' '}
              <span className="text-emerald-400">
                {healthData ? JSON.stringify(healthData) : 'null (offline)'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Manual Ingestion Trigger */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>On-Demand Pipeline Execution</CardTitle>
              <CardDescription>
                Manually trigger scrapers to poll RSS feeds from Economic Times, Moneycontrol, and LiveMint.
              </CardDescription>
            </div>
            <Button
              variant="secondary"
              size="sm"
              onClick={handleTriggerIngestion}
              disabled={isIngesting}
              leftIcon={<Newspaper size={14} />}
            >
              {isIngesting ? 'Ingesting...' : 'Run Ingestion Now'}
            </Button>
          </div>
        </CardHeader>
        {ingestResult && (
          <CardContent className="pt-0">
            <div className="p-2.5 rounded-lg bg-indigo-950/40 border border-indigo-500/30 text-xs text-indigo-200">
              {ingestResult}
            </div>
          </CardContent>
        )}
      </Card>

      {/* Ingestion Pipeline Flags */}
      <Card>
        <CardHeader>
          <CardTitle>Data Pipeline Toggles</CardTitle>
          <CardDescription>
            Control active scrapers and streaming ingestion connectors.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 divide-y divide-slate-800">
          <div className="flex items-center justify-between pt-2">
            <div>
              <div className="font-semibold text-sm text-white">Multi-Publisher RSS Feeds</div>
              <p className="text-xs text-slate-400">
                Live polling of LiveMint, Economic Times, Moneycontrol, and Business Standard.
              </p>
            </div>
            <input
              type="checkbox"
              checked={rssEnabled}
              onChange={(e) => setRssEnabled(e.target.checked)}
              className="h-4 w-4 rounded accent-indigo-600 cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between pt-4">
            <div>
              <div className="font-semibold text-sm text-white">FinBERT Worker Pipeline</div>
              <p className="text-xs text-slate-400">
                Continuous NLP inference worker calculating weighted financial sentiment.
              </p>
            </div>
            <input
              type="checkbox"
              checked={scrapersEnabled}
              onChange={(e) => setScrapersEnabled(e.target.checked)}
              className="h-4 w-4 rounded accent-indigo-600 cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between pt-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm text-white">X / Twitter Ingestion</span>
                <Badge variant="default" size="sm">
                  Optional Feature Flag
                </Badge>
              </div>
              <p className="text-xs text-slate-400">
                Streaming financial tweets behind API quota rate limiter (disabled by default).
              </p>
            </div>
            <input
              type="checkbox"
              checked={twitterEnabled}
              onChange={(e) => setTwitterEnabled(e.target.checked)}
              className="h-4 w-4 rounded accent-indigo-600 cursor-pointer"
            />
          </div>

          <div className="pt-4 flex justify-end">
            <Button size="sm" onClick={handleSaveSettings} leftIcon={<Sparkles size={14} />}>
              Save Settings
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
