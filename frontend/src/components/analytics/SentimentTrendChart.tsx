import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'
import type { SentimentTimePoint } from '../../types/analytics'
import { EmptyState } from '../common/EmptyState'
import { TrendingUp } from '../ui/Icons'

interface SentimentTrendChartProps {
  data: SentimentTimePoint[] | null | undefined
  timeframe: string
  title?: string
}

interface CustomTooltipProps {
  active?: boolean
  payload?: Array<{
    value: number
    payload: SentimentTimePoint
  }>
  label?: string
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (active && payload && payload.length) {
    const pt = payload[0].payload
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-900/95 p-3 shadow-xl backdrop-blur-md text-xs">
        <p className="font-bold text-white mb-1.5">{label}</p>
        <div className="space-y-1 font-mono">
          <div className="flex items-center justify-between gap-4">
            <span className="text-slate-400">FinBERT Score:</span>
            <span className="font-semibold text-emerald-400">{pt.score.toFixed(2)}</span>
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-emerald-400">Positive:</span>
            <span>{pt.positive}</span>
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-slate-400">Neutral:</span>
            <span>{pt.neutral}</span>
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-rose-400">Negative:</span>
            <span>{pt.negative}</span>
          </div>
          <div className="flex items-center justify-between gap-4 pt-1 border-t border-slate-800">
            <span className="text-slate-400">Ingested Volume:</span>
            <span className="text-indigo-400 font-semibold">{pt.volume} articles</span>
          </div>
        </div>
      </div>
    )
  }
  return null
}

export function SentimentTrendChart({
  data,
  timeframe,
  title = 'FinBERT Sentiment Score Trajectory',
}: SentimentTrendChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-[320px] flex items-center justify-center">
        <EmptyState
          icon={<TrendingUp size={24} />}
          title="No Timeframe Data Available"
          description={`No articles were ingested or scored for ${timeframe}. Re-run the scraper worker or select a different interval.`}
        />
      </div>
    )
  }

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-semibold text-white">{title}</h4>
        <span className="text-xs text-slate-400 font-mono">Interval: {timeframe}</span>
      </div>

      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
          >
            <defs>
              <linearGradient id="sentimentGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#334155"
              vertical={false}
              opacity={0.4}
            />
            <XAxis
              dataKey="date"
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
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="score"
              stroke="#818cf8"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#sentimentGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
