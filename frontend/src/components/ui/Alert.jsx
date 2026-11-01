import React from 'react'
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react'
import { cn } from '../../lib/utils/cn'

export function Alert({ className, variant = 'info', children, ...props }) {
  const variants = {
    info: 'bg-slate-50 text-slate-800 border-slate-200',
    amber: 'bg-amber-50/80 text-amber-950 border-amber-300',
    warning: 'bg-amber-50 text-amber-900 border-amber-300',
    destructive: 'bg-rose-50 text-rose-900 border-rose-200',
    success: 'bg-emerald-50 text-emerald-900 border-emerald-200',
  }

  const icons = {
    info: <Info className="h-4 w-4 text-slate-600 mt-0.5 shrink-0" />,
    amber: <AlertTriangle className="h-4 w-4 text-amber-700 mt-0.5 shrink-0" />,
    warning: <AlertTriangle className="h-4 w-4 text-amber-700 mt-0.5 shrink-0" />,
    destructive: <AlertCircle className="h-4 w-4 text-rose-600 mt-0.5 shrink-0" />,
    success: <CheckCircle2 className="h-4 w-4 text-emerald-600 mt-0.5 shrink-0" />,
  }

  return (
    <div
      role="alert"
      className={cn(
        'relative w-full rounded-md border p-4 text-sm flex items-start gap-3 shadow-2xs',
        variants[variant],
        className
      )}
      {...props}
    >
      {icons[variant]}
      <div className="flex-1 leading-relaxed">{children}</div>
    </div>
  )
}

export function AlertTitle({ className, children, ...props }) {
  return (
    <h5 className={cn('font-semibold leading-none tracking-tight mb-1', className)} {...props}>
      {children}
    </h5>
  )
}

export function AlertDescription({ className, children, ...props }) {
  return (
    <div className={cn('text-sm opacity-90', className)} {...props}>
      {children}
    </div>
  )
}
