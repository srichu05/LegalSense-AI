import React from 'react'
import { cn } from '../../lib/utils/cn'

export const Input = React.forwardRef(function Input(
  { className, type = 'text', disabled = false, ...props },
  ref
) {
  return (
    <input
      type={type}
      ref={ref}
      disabled={disabled}
      className={cn(
        'flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 disabled:cursor-not-allowed disabled:opacity-50 transition-colors shadow-xs',
        className
      )}
      {...props}
    />
  )
})
