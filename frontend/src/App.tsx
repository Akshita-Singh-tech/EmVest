import { useEffect, useState } from 'react'
import { fetchHealth, type HealthResponse } from './services/api'

type ConnectionStatus = 'checking' | 'connected' | 'unreachable'

export default function App() {
  const [status, setStatus] = useState<ConnectionStatus>('checking')
  const [data, setData] = useState<HealthResponse | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [lastChecked, setLastChecked] = useState<string>('Never')
  const [updateCount, setUpdateCount] = useState<number>(0)
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0)

  useEffect(() => {
    let ignore = false

    async function verifyBackend() {
      try {
        const res = await fetchHealth()
        if (!ignore) {
          setData(res)
          setStatus('connected')
          setErrorMsg(null)
        }
      } catch (err) {
        if (!ignore) {
          setData(null)
          setStatus('unreachable')
          setErrorMsg(err instanceof Error ? err.message : 'Failed to connect to backend')
        }
      } finally {
        if (!ignore) {
          setLastChecked(new Date().toLocaleTimeString())
          setUpdateCount((prev) => prev + 1)
        }
      }
    }

    void verifyBackend()
    const interval = setInterval(() => {
      void verifyBackend()
    }, 5000)

    return () => {
      ignore = true
      clearInterval(interval)
    }
  }, [refreshTrigger])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 antialiased">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-6">
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold tracking-tight text-white">Emvest</h1>
            <span className="text-xs uppercase tracking-wider font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-400">
              Phase 1
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Stock Market Intelligence & Agentic Research
          </p>
        </div>

        <div className="border border-slate-800 bg-slate-950/60 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-300">Backend API</span>
            {status === 'checking' && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse" />
                checking...
              </span>
            )}
            {status === 'connected' && (
              <span
                data-testid="status-connected"
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
              >
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                connected
              </span>
            )}
            {status === 'unreachable' && (
              <span
                data-testid="status-unreachable"
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30"
              >
                <span className="h-2 w-2 rounded-full bg-rose-400" />
                unreachable
              </span>
            )}
          </div>

          <div className="text-xs font-mono bg-slate-900 rounded p-2.5 text-slate-400 overflow-x-auto">
            {status === 'connected' && (
              <p className="text-emerald-400">Response: {JSON.stringify(data)}</p>
            )}
            {status === 'unreachable' && (
              <p className="text-rose-400">Error: {errorMsg}</p>
            )}
            {status === 'checking' && (
              <p className="text-slate-500">Pinging http://localhost:8000/api/v1/health...</p>
            )}
          </div>
        </div>

        <div className="border-t border-slate-800/80 pt-4 flex items-center justify-between text-xs text-slate-400">
          <div>
            <p>
              Last check: <span className="font-mono text-slate-200">{lastChecked}</span>
            </p>
            <p>
              Live updates: <span className="font-mono text-slate-200">{updateCount}</span>
            </p>
          </div>
          <button
            type="button"
            onClick={() => setRefreshTrigger((prev) => prev + 1)}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition cursor-pointer"
          >
            Refresh Now
          </button>
        </div>
      </div>
    </div>
  )
}
