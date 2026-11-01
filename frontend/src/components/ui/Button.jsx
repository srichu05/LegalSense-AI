import React from 'react'
import { Loader2 } from 'lucide-react'
import { cn } from '../../lib/utils/cn'

export const Button = React.forwardRef(function Button(
  {
    className,
    variant = 'default',
    size = 'default',
    isLoading = false,
    disabled = false,
    children,
    type = 'button',
    ...props
  },
  ref
) {
  const baseStyles =
    'inline-flex items-center justify-center font-medium rounded-md text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none select-none active:scale-[0.98]'

  const variants = {
    default: 'bg-slate-900 text-slate-50 hover:bg-slate-800 shadow-sm',
    secondary: 'bg-slate-100 text-slate-900 hover:bg-slate-200 border border-slate-200',
    outline: 'border border-slate-300 bg-transparent text-slate-800 hover:bg-slate-100',
    ghost: 'hover:bg-slate-100 text-slate-700 hover:text-slate-900',
    amber: 'bg-amber-700 text-white hover:bg-amber-800 shadow-sm border border-amber-800',
    amberLight: 'bg-amber-50 text-amber-900 hover:bg-amber-100 border border-amber-300',
    destructive: 'bg-rose-700 text-white hover:bg-rose-800 shadow-sm',
  }

  const sizes = {
    sm: 'h-8 px-3 text-xs',
    default: 'h-10 px-4 py-2',
    lg: 'h-11 px-6 text-base',
    icon: 'h-10 w-10 p-0',
  }

  return (
    <button
      ref={ref}
      type={type}
      disabled={disabled || isLoading}
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      {...props}
    >
      {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin text-current" />}
      {children}
    </button>
  )
})
