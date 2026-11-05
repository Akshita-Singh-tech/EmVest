import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
} from 'recharts'
import type { PolarityData } from '../../types/analytics'
import { EmptyState } from '../common/EmptyState'
import { TrendingUp } from '../ui/Icons'

interface PolarityDonutChartProps {
  data: PolarityData[] | null | undefined
}

interface CustomPieTooltipProps {
  active?: boolean
  payload?: Array<{
    name: string
    value: number
    payload: PolarityData
  }>
}

function CustomPieTooltip({ active, payload }: CustomPieTooltipProps) {
  if (active && payload && payload.length) {
    const item = payload[0].payload
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-900/95 p-2.5 shadow-xl backdrop-blur-md text-xs font-mono">
        <span className="font-bold text-white">{item.name}: </span>
        <span className="font-semibold text-emerald-400">{item.value}%</span>
      </div>
    )
  }
  return null
}

export function PolarityDonutChart({ data }: PolarityDonutChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-[220px] flex items-center justify-center">
        <EmptyState
          icon={<TrendingUp size={20} />}
          title="No Polarity Split"
          description="Insufficient sentiment classified articles."
        />
      </div>
    )
  }

  return (
    <div className="w-full">
      <div className="h-[180px] w-full relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip content={<CustomPieTooltip />} />
            <Pie
              data={data}
              innerRadius={55}
              outerRadius={75}
              paddingAngle={4}
              dataKey="value"
            >
              {data.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-xl font-bold text-white">68%</span>
          <span className="text-[10px] uppercase font-semibold text-emerald-400">
            Bullish
          </span>
        </div>
      </div>

      {/* Legend items */}
      <div className="flex items-center justify-center gap-4 text-xs pt-2">
        {data.map((item) => (
          <div key={item.name} className="flex items-center gap-1.5">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: item.color }}
            />
            <span className="text-slate-400">{item.name}:</span>
            <span className="font-mono font-medium text-slate-200">
              {item.value}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
