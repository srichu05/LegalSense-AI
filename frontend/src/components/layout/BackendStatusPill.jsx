import React from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { checkHealth, getBaseUrl } from '../../lib/api/client'

export function BackendStatusPill({ className }) {
  const { data, isPending, isError, refetch } = useQuery({
    queryKey: ['backendHealth', getBaseUrl()],
    queryFn: () => checkHealth(4000),
    refetchInterval: 12000,
    retry: 1,
  })

  let statusText = 'Checking...'
  let badgeClasses = 'bg-slate-800 text-slate-300 border-slate-700'
  let dotColor = 'bg-slate-400'

  if (isPending) {
    statusText = 'Connecting...'
    badgeClasses = 'bg-amber-950/40 text-amber-300 border-amber-800'
    dotColor = 'bg-amber-400 animate-pulse'
  } else if (isError || !data || data.status !== 'ok') {
    statusText = 'Backend Disconnected'
    badgeClasses = 'bg-rose-950/50 text-rose-200 border-rose-800'
    dotColor = 'bg-rose-500'
  } else if (data.status === 'ok') {
    statusText = data.wsd_ready ? 'Backend Online (WSD Ready)' : 'Backend Online (WSD Initializing)'
    badgeClasses = 'bg-emerald-950/60 text-emerald-200 border-emerald-800'
    dotColor = 'bg-emerald-400'
  }

  return (
    <div className={`inline-flex items-center gap-2 text-xs ${className || ''}`}>
      <Link
        to="/settings"
        title={`Connected to: ${getBaseUrl()} (Click to change)`}
        className={`inline-flex items-center gap-2 px-2.5 py-1 rounded-full border transition-colors hover:opacity-90 ${badgeClasses}`}
      >
        <span className={`w-2 h-2 rounded-full ${dotColor}`} />
        <span className="font-medium tracking-tight">{statusText}</span>
      </Link>
      <button
        type="button"
        onClick={() => refetch()}
        title="Refresh backend status"
        className="text-slate-400 hover:text-white transition-colors p-1 rounded-sm"
      >
        <RefreshCw className="w-3 h-3" />
      </button>
    </div>
  )
}
