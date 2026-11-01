import React, { useState } from 'react'
import { Sparkles, ChevronDown, ChevronUp } from 'lucide-react'
import { Badge } from '../ui/Badge'
import { formatScore } from '../../lib/utils/formatters'

export function EvidencePanel({ evidence = [] }) {
  const [isExpanded, setIsExpanded] = useState(false)
  if (!evidence || evidence.length === 0) return null

  // Deduplicate or group evidence by candidate synset
  const bySynset = evidence.reduce((acc, item) => {
    const key = item.candidate_synset_id
    if (!acc[key]) acc[key] = []
    acc[key].push(item)
    return acc
  }, {})

  const synsetKeys = Object.keys(bySynset)

  return (
    <div className="mt-4 pt-3 border-t border-slate-200">
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-800 hover:text-slate-950 transition-colors"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-600" />
          <span>Extended Lesk Overlap Evidence ({evidence.length} items across {synsetKeys.length} senses)</span>
          {isExpanded ? <ChevronUp className="w-3.5 h-3.5 ml-1 text-slate-400" /> : <ChevronDown className="w-3.5 h-3.5 ml-1 text-slate-400" />}
        </button>
        <span className="text-[11px] text-slate-500 hidden sm:inline">
          Itemized token matches between context and candidate glosses/examples
        </span>
      </div>

      {isExpanded && (
        <div className="mt-3 space-y-3 bg-slate-50/80 p-3.5 rounded-lg border border-slate-200 text-xs">
          {synsetKeys.map(sid => {
            const items = bySynset[sid]
            const totalScore = items.reduce((sum, it) => sum + (it.contribution || 0), 0)
            return (
              <div key={sid} className="bg-white p-3 rounded-md border border-slate-200 shadow-2xs">
                <div className="flex items-center justify-between border-b border-slate-100 pb-1.5 mb-2">
                  <span className="font-mono font-medium text-slate-900">{sid}</span>
                  <Badge variant="secondary" className="text-[10px]">
                    Evidence Subtotal: +{formatScore(totalScore)}
                  </Badge>
                </div>
                <div className="space-y-1.5">
                  {items.map((ev, idx) => (
                    <div key={idx} className="flex flex-wrap items-center justify-between text-[11px] gap-2">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-mono text-[10px] border border-slate-200">
                          {ev.overlap_source}
                        </span>
                        <span className="text-slate-500">matched:</span>
                        <div className="flex flex-wrap gap-1">
                          {(ev.overlap_tokens || []).map(tok => (
                            <span key={tok} className="px-1.5 py-0.2 bg-amber-50 text-amber-900 border border-amber-200 rounded font-mono text-[10px] font-semibold">
                              "{tok}"
                            </span>
                          ))}
                        </div>
                      </div>
                      <span className="font-semibold text-emerald-700 shrink-0">
                        +{formatScore(ev.contribution)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
