import React from 'react'
import { cn } from '../../lib/utils/cn'

export function Card({ className, children, ...props }) {
  return (
    <div
      className={cn('rounded-lg border border-slate-200 bg-white text-slate-900 shadow-sm', className)}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({ className, children, ...props }) {
  return (
    <div className={cn('flex flex-col space-y-1.5 p-6 border-b border-slate-100', className)} {...props}>
      {children}
    </div>
  )
}

export function CardTitle({ className, children, ...props }) {
  return (
    <h3
      className={cn('font-serif text-lg font-semibold leading-none tracking-tight text-slate-900', className)}
      {...props}
    >
      {children}
    </h3>
  )
}

export function CardDescription({ className, children, ...props }) {
  return (
    <p className={cn('text-sm text-slate-500 mt-1', className)} {...props}>
      {children}
    </p>
  )
}

export function CardContent({ className, children, ...props }) {
  return (
    <div className={cn('p-6 pt-4', className)} {...props}>
      {children}
    </div>
  )
}

export function CardFooter({ className, children, ...props }) {
  return (
    <div className={cn('flex items-center p-6 pt-0 border-t border-slate-100 bg-slate-50/50 rounded-b-lg', className)} {...props}>
      {children}
    </div>
  )
}
