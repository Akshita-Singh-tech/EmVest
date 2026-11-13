import { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  TrendingUp,
  Newspaper,
  Star,
  Bot,
  User,
  X,
  Sparkles,
} from '../ui/Icons'
import { Badge } from '../ui/Badge'
import { fetchHealth } from '../../services/api'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Analytics', path: '/analytics', icon: TrendingUp },
  { name: 'News Feed', path: '/news', icon: Newspaper },
  { name: 'Watchlist', path: '/watchlist', icon: Star },
  { name: 'AI Assistant', path: '/chat', icon: Bot, badge: 'Agentic' },
  { name: 'Profile', path: '/profile', icon: User },
]

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null)

  useEffect(() => {
    let ignore = false
    const check = async () => {
      try {
        const res = await fetchHealth()
        if (!ignore) {
          setBackendHealthy(res.status === 'ok')
        }
      } catch {
        if (!ignore) {
          setBackendHealthy(false)
        }
      }
    }

    void check()
    const interval = setInterval(() => {
      void check()
    }, 10000)

    return () => {
      ignore = true
      clearInterval(interval)
    }
  }, [])

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          role="presentation"
          onClick={onClose}
          className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm lg:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-slate-900 border-r border-slate-800 flex flex-col transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-slate-800/80">
          <NavLink
            to="/"
            onClick={onClose}
            className="flex items-center gap-2.5 group"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 text-white font-bold text-lg shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              E
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-white tracking-tight text-lg">
                  Emvest
                </span>
                <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                  AI
                </span>
              </div>
              <p className="text-[11px] text-slate-400 -mt-0.5">Market Agent</p>
            </div>
          </NavLink>

          <button
            type="button"
            onClick={onClose}
            className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            aria-label="Close sidebar"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Platform
          </div>
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-indigo-600/15 text-indigo-300 font-semibold border border-indigo-500/30'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon size={18} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <Badge variant="purple" size="sm">
                    {item.badge}
                  </Badge>
                )}
              </NavLink>
            )
          })}
        </nav>

        {/* Pro / Agent CTA Banner */}
        <div className="p-3">
          <div className="rounded-xl p-3 bg-gradient-to-br from-slate-800/80 to-slate-800/30 border border-slate-700/60">
            <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold">
              <Sparkles size={14} />
              <span>FinBERT + Agent</span>
            </div>
            <p className="mt-1 text-[11px] text-slate-400 leading-normal">
              Real-time sentiment scoring & contextual financial reasoning.
            </p>
          </div>
        </div>

        {/* Live Backend Connection Status Indicator */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-950/40">
          <div className="flex items-center justify-between px-2 py-1.5 text-xs">
            <span className="text-slate-400">FastAPI Backend</span>
            {backendHealthy === null && (
              <span className="inline-flex items-center gap-1 text-[11px] text-slate-400">
                <span className="h-2 w-2 rounded-full bg-slate-500 animate-pulse" />
                Checking
              </span>
            )}
            {backendHealthy === true && (
              <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                Connected
              </span>
            )}
            {backendHealthy === false && (
              <span className="inline-flex items-center gap-1 text-[11px] text-rose-400 font-medium">
                <span className="h-2 w-2 rounded-full bg-rose-400" />
                Unreachable
              </span>
            )}
          </div>
        </div>
      </aside>
    </>
  )
}

