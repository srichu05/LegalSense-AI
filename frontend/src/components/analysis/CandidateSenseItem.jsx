import React from 'react'
import { Award, CheckCircle2 } from 'lucide-react'
import { Badge } from '../ui/Badge'
import { LexicalRelationsList } from './LexicalRelationsList'
import { formatScore } from '../../lib/utils/formatters'
import { cn } from '../../lib/utils/cn'

export function CandidateSenseItem({
  candidate,
  isSelected = false,
  isTopRank = false,
  onSelect = null,
  isHighlighted = false,
}) {
  if (!candidate) return null

  return (
    <div
      onClick={() => onSelect?.(candidate)}
      className={cn(
        'p-4 rounded-lg border transition-all text-sm cursor-pointer relative',
        isSelected
          ? 'bg-slate-50/80 border-slate-900 ring-1 ring-slate-900 shadow-xs'
          : isTopRank
          ? 'bg-amber-50/20 border-amber-300 shadow-2xs'
          : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/40',
        isHighlighted && 'ring-2 ring-amber-500'
      )}
    >
      <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center w-6 h-6 rounded-full bg-slate-100 text-slate-800 text-xs font-bold font-mono border border-slate-200">
            #{candidate.rank || 1}
          </span>
          <span className="font-mono font-semibold text-slate-900 text-sm">
            {candidate.synset_id}
          </span>
          {candidate.pos && (
            <Badge variant="outline" className="text-[10px] uppercase font-mono py-0">
              {candidate.pos}
            </Badge>
          )}
          {isSelected && (
            <Badge variant="default" className="text-[10px] gap-1 py-0 bg-slate-900 text-white">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              Selected Sense
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-medium">Lesk Score:</span>
          <span className="font-mono font-bold text-slate-900 text-sm bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
            {formatScore(candidate.score)}
          </span>
        </div>
      </div>

      {/* Definition */}
      <p className="text-slate-800 leading-relaxed font-sans text-sm pl-8">
        {candidate.definition}
      </p>

      {/* Relations */}
      <div className="pl-8">
        <LexicalRelationsList relations={candidate.relations} />
      </div>
    </div>
  )
}
