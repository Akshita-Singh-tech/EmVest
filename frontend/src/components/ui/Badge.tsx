import type { HTMLAttributes } from 'react'

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'purple'
  size?: 'sm' | 'md'
  dot?: boolean
}

export function Badge({
  variant = 'default',
  size = 'md',
  dot = false,
  className = '',
  children,
  ...props
}: BadgeProps) {
  const baseStyles =
    'inline-flex items-center font-medium rounded-full border transition-colors'

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-[11px] gap-1',
    md: 'px-2.5 py-1 text-xs gap-1.5',
  }[size]

  const variantStyles = {
    default:
      'bg-slate-800 text-slate-300 border-slate-700',
    success:
      'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    warning:
      'bg-amber-500/10 text-amber-400 border-amber-500/30',
    danger:
      'bg-rose-500/10 text-rose-400 border-rose-500/30',
    info:
      'bg-sky-500/10 text-sky-400 border-sky-500/30',
    purple:
      'bg-purple-500/10 text-purple-400 border-purple-500/30',
  }[variant]

  const dotColors = {
    default: 'bg-slate-400',
    success: 'bg-emerald-400 animate-pulse',
    warning: 'bg-amber-400',
    danger: 'bg-rose-400',
    info: 'bg-sky-400',
    purple: 'bg-purple-400',
  }[variant]

  return (
    <span
      className={`${baseStyles} ${sizeStyles} ${variantStyles} ${className}`}
      {...props}
    >
      {dot && <span className={`h-1.5 w-1.5 rounded-full ${dotColors}`} />}
      {children}
    </span>
  )
}

