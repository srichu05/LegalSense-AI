import React from 'react'
import { cn } from '../../lib/utils/cn'

export function Tabs({ value, onValueChange, children, className }) {
  return (
    <div className={cn('w-full', className)}>
      {React.Children.map(children, child => {
        if (!React.isValidElement(child)) return null
        return React.cloneElement(child, { activeValue: value, onValueChange })
      })}
    </div>
  )
}

export function TabsList({ children, activeValue, onValueChange, className }) {
  return (
    <div className={cn('inline-flex h-10 items-center justify-center rounded-lg bg-slate-100 p-1 text-slate-500 border border-slate-200', className)}>
      {React.Children.map(children, child => {
        if (!React.isValidElement(child)) return null
        return React.cloneElement(child, {
          isActive: child.props.value === activeValue,
          onClick: () => onValueChange?.(child.props.value),
        })
      })}
    </div>
  )
}

export function TabsTrigger({ value, isActive, onClick, children, className }) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={isActive}
      onClick={onClick}
      className={cn(
        'inline-flex items-center justify-center whitespace-nowrap rounded-md px-3.5 py-1.5 text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900',
        isActive
          ? 'bg-white text-slate-900 shadow-xs font-semibold'
          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50',
        className
      )}
    >
      {children}
    </button>
  )
}

export function TabsContent({ value, activeValue, children, className }) {
  if (value !== activeValue) return null
  return <div role="tabpanel" className={cn('mt-4 focus-visible:outline-none', className)}>{children}</div>
}
