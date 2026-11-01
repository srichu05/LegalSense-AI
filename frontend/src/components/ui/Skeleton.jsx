import React from 'react'
import { cn } from '../../lib/utils/cn'

export function Skeleton({ className, ...props }) {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-slate-200/80', className)}
      {...props}
    />
  )
}
