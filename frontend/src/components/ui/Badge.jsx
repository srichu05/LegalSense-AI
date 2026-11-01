import React from 'react'
import { cn } from '../../lib/utils/cn'

export function Badge({ className, variant = 'default', children, ...props }) {
  const baseStyles = 'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold tracking-wide transition-colors'

  const variants = {
    default: 'bg-slate-900 text-slate-100',
    secondary: 'bg-slate-100 text-slate-800 border border-slate-200',
    outline: 'border border-slate-300 text-slate-700 bg-white',
    amber: 'bg-amber-100 text-amber-900 border border-amber-300 font-medium',
    amberSolid: 'bg-amber-700 text-white',
    success: 'bg-emerald-50 text-emerald-800 border border-emerald-300',
    warning: 'bg-amber-50 text-amber-900 border border-amber-300',
    destructive: 'bg-rose-100 text-rose-800 border border-rose-300',
    navy: 'bg-slate-800 text-slate-100',
  }

  return (
    <span className={cn(baseStyles, variants[variant], className)} {...props}>
      {children}
    </span>
  )
}
