import { useState, useMemo } from 'react'
import { Badge } from '../ui/Badge'
import { Search, X, Plus } from '../ui/Icons'
import { masterCompanyList } from '../../services/masterData'
import type { MasterCompany } from '../../types/personalization'

interface CompanyPickerProps {
  selectedSymbols: string[]
  onChange: (symbols: string[]) => void
  error?: string
}

export function CompanyPicker({
  selectedSymbols,
  onChange,
  error,
}: CompanyPickerProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterSector, setFilterSector] = useState('All')

  // Filter master list
  const filtered = useMemo(() => {
    let list = masterCompanyList
    if (filterSector !== 'All') {
      list = list.filter((c) => c.sector.includes(filterSector))
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim()
      list = list.filter(
        (c) =>
          c.symbol.toLowerCase().includes(q) ||
          c.name.toLowerCase().includes(q) ||
          c.sector.toLowerCase().includes(q)
      )
    }
    return list
  }, [searchQuery, filterSector])

  const toggleSymbol = (symbol: string) => {
    if (selectedSymbols.includes(symbol)) {
      onChange(selectedSymbols.filter((s) => s !== symbol))
    } else {
      onChange([...selectedSymbols, symbol])
    }
  }

  const removeSymbol = (symbol: string) => {
    onChange(selectedSymbols.filter((s) => s !== symbol))
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold text-slate-300">
          Tracked Equities (Official NSE/BSE Master Index)
        </label>
        <span className="text-xs text-slate-400 font-mono">
          {selectedSymbols.length} Selected
        </span>
      </div>

      {/* Selected Tags Container */}
      <div className="flex flex-wrap items-center gap-1.5 p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 min-h-[44px]">
        {selectedSymbols.length > 0 ? (
          selectedSymbols.map((sym) => (
            <span
              key={sym}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 text-xs font-mono font-semibold"
            >
              <span>{sym}</span>
              <button
                type="button"
                onClick={() => removeSymbol(sym)}
                className="text-indigo-400 hover:text-white cursor-pointer"
                aria-label={`Remove ${sym}`}
              >
                <X size={12} />
              </button>
            </span>
          ))
        ) : (
          <span className="text-xs text-slate-500 italic">
            No symbols selected. Search and add from the master list below.
          </span>
        )}
      </div>

      {error && <p className="text-xs text-rose-400">{error}</p>}

      {/* Search and Quick Filters */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
        <div className="sm:col-span-2 relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search master list by ticker, company, or sector..."
            className="w-full pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <select
          value={filterSector}
          onChange={(e) => setFilterSector(e.target.value)}
          aria-label="Filter companies by sector"
          className="px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none cursor-pointer"
        >
          <option value="All">All Sectors</option>
          <option value="Banking">Banking & Finance</option>
          <option value="Information Tech">Information Tech</option>
          <option value="Auto">Automobile</option>
          <option value="Energy">Energy & Power</option>
          <option value="Pharma">Pharmaceuticals</option>
          <option value="FMCG">FMCG</option>
        </select>
      </div>

      {/* Master List Scrollable Grid */}
      <div className="max-h-56 overflow-y-auto rounded-lg border border-slate-800 bg-slate-950/40 p-2 divide-y divide-slate-850 space-y-1">
        {filtered.map((company: MasterCompany) => {
          const isSelected = selectedSymbols.includes(company.symbol)
          return (
            <div
              key={company.symbol}
              onClick={() => toggleSymbol(company.symbol)}
              className={`p-2 rounded-lg flex items-center justify-between cursor-pointer transition ${
                isSelected
                  ? 'bg-indigo-600/15 border border-indigo-500/30 text-white'
                  : 'hover:bg-slate-800/40 text-slate-300'
              }`}
            >
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-xs text-white">
                    {company.symbol}
                  </span>
                  <Badge variant="default" size="sm">
                    {company.exchange}
                  </Badge>
                  <span className="text-[11px] text-slate-400 truncate max-w-[200px] sm:max-w-xs">
                    {company.name}
                  </span>
                </div>
                <div className="text-[10px] text-slate-400">
                  {company.sector} • {company.marketCapCategory}
                </div>
              </div>

              <button
                type="button"
                className={`p-1 rounded text-xs transition ${
                  isSelected
                    ? 'text-indigo-400 hover:text-rose-400'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {isSelected ? <X size={15} /> : <Plus size={15} />}
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}

