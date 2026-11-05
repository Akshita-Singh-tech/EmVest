import { Link, useLocation } from 'react-router-dom'
import { Menu, Search, Bell, Sparkles } from '../ui/Icons'
import { Badge } from '../ui/Badge'

interface NavbarProps {
  onToggleSidebar: () => void
}

const pageTitles: Record<string, string> = {
  '/': 'Market Overview',
  '/analytics': 'Sentiment & Sector Analytics',
  '/news': 'Real-Time News Feed',
  '/watchlist': 'Tracked Watchlists',
  '/chat': 'AI Investment Assistant',
  '/profile': 'Investor Profile',
  '/settings': 'System Settings',
}

export function Navbar({ onToggleSidebar }: NavbarProps) {
  const location = useLocation()
  const title = pageTitles[location.pathname] || 'Dashboard'

  return (
    <header className="sticky top-0 z-30 h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800/80 px-4 sm:px-6 flex items-center justify-between gap-4">
      {/* Left: Mobile Toggle & Page Title */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onToggleSidebar}
          className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          aria-label="Open sidebar"
        >
          <Menu size={20} />
        </button>
        <div>
          <h2 className="text-base sm:text-lg font-bold text-white tracking-tight leading-tight">
            {title}
          </h2>
          <p className="hidden sm:block text-xs text-slate-400">
            Emvest Intelligence Platform
          </p>
        </div>
      </div>

      {/* Middle: Quick Search Input */}
      <div className="hidden md:flex flex-1 max-w-md mx-4">
        <div className="relative w-full">
          <Search
            size={16}
            className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
          />
          <input
            type="text"
            placeholder="Search equities, e.g. RELIANCE, TCS, HDFCBANK..."
            className="w-full pl-9 pr-4 py-1.5 bg-slate-950/60 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition"
          />
        </div>
      </div>

      {/* Right: Market Status & Profile Pill */}
      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2">
          <Badge variant="success" size="sm" dot>
            NSE / BSE
          </Badge>
        </div>

        <Link
          to="/chat"
          className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-600/30 transition"
        >
          <Sparkles size={14} />
          <span>Ask Agent</span>
        </Link>

        <button
          type="button"
          className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          aria-label="Notifications"
        >
          <Bell size={18} />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-indigo-500" />
        </button>

        <Link
          to="/profile"
          className="flex items-center gap-2 pl-2 border-l border-slate-800 hover:opacity-90 transition"
        >
          <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-xs font-semibold text-white shadow-sm ring-1 ring-slate-700">
            AS
          </div>
        </Link>
      </div>
    </header>
  )
}

