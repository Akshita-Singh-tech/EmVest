import type { ReactNode } from 'react'

export interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
  className?: string
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className = '',
}: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center text-center p-8 rounded-xl border border-dashed border-slate-800 bg-slate-900/40 ${className}`}
    >
      {icon && (
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800/80 text-slate-400 mb-4 border border-slate-700/60">
          {icon}
        </div>
      )}
      <h4 className="text-base font-semibold text-slate-200">{title}</h4>
      {description && (
        <p className="mt-1.5 max-w-sm text-sm text-slate-400 leading-relaxed">
          {description}
        </p>
      )}
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}
