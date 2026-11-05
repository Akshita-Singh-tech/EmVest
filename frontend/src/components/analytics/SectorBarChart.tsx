import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from 'recharts'
import type { SectorSentiment } from '../../types/analytics'
import { EmptyState } from '../common/EmptyState'
import { TrendingUp } from '../ui/Icons'

interface SectorBarChartProps {
  data: SectorSentiment[] | null | undefined
}

interface CustomTooltipProps {
  active?: boolean
  payload?: Array<{
    value: number
    payload: SectorSentiment
  }>
}

function CustomBarTooltip({ active, payload }: CustomTooltipProps) {
  if (active && payload && payload.length) {
    const item = payload[0].payload
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-900/95 p-3 shadow-xl backdrop-blur-md text-xs">
        <p className="font-bold text-white mb-1">{item.sector}</p>
        <div className="space-y-1 font-mono">
          <div className="flex items-center justify-between gap-4">
            <span className="text-slate-400">FinBERT Score:</span>
            <span className="font-semibold text-white">{item.score.toFixed(2)}</span>
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-slate-400">Market Outlook:</span>
            <span
              className={
                item.status === 'Bullish'
                  ? 'text-emerald-400'
                  : item.status === 'Cautious'
                  ? 'text-rose-400'
                  : 'text-amber-400'
              }
            >
              {item.status}
            </span>
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-slate-400">Scored Articles:</span>
            <span className="text-slate-200">{item.articleCount}</span>
          </div>
          <div className="flex items-center justify-between gap-4 pt-1 border-t border-slate-800">
            <span className="text-slate-400">Weekly Drift:</span>
            <span className="font-semibold text-emerald-400">{item.momentum}</span>
          </div>
        </div>
      </div>
    )
  }
  return null
}

export function SectorBarChart({ data }: SectorBarChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-[280px] flex items-center justify-center">
        <EmptyState
          icon={<TrendingUp size={24} />}
          title="No Sector Data Found"
          description="Sector aggregations are not available for the active query. No fabricated numbers will be presented."
        />
      </div>
    )
  }

  // Format sector label for compact x-axis
  const formattedData = data.map((d) => ({
    ...d,
    shortName: d.sector.split(' ')[0],
  }))

  const getBarColor = (score: number) => {
    if (score >= 0.65) return '#10b981' // emerald-500
    if (score >= 0.5) return '#6366f1'  // indigo-500
    if (score >= 0.45) return '#f59e0b' // amber-500
    return '#f43f5e'                    // rose-500
  }

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-semibold text-white">Comparative Sector Sentiment</h4>
        <span className="text-xs text-slate-400">Score Range [0.0 - 1.0]</span>
      </div>

      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={formattedData}
            margin={{ top: 10, right: 10, left: -20, bottom: 20 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#334155"
              vertical={false}
              opacity={0.4}
            />
            <XAxis
              dataKey="shortName"
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
            />
            <YAxis
              domain={[0, 1]}
              ticks={[0, 0.25, 0.5, 0.75, 1.0]}
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
            />
            <Tooltip content={<CustomBarTooltip />} />
            <Bar dataKey="score" radius={[6, 6, 0, 0]}>
              {formattedData.map((entry) => (
                <Cell key={entry.sector} fill={getBarColor(entry.score)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

