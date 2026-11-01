import React, { useState } from 'react'
import { Filter, Layers, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react'
import { Badge } from '../ui/Badge'
import { WsdResultCard } from '../analysis/WsdResultCard'
import { cn } from '../../lib/utils/cn'

export function PassageOccurrenceViewer({ occurrences = [] }) {
  const [selectedTermFilter, setSelectedTermFilter] = useState('ALL')
  const [selectedOccurrenceIdx, setSelectedOccurrenceIdx] = useState(0)

  if (!occurrences || occurrences.length === 0) {
    return (
      <div className="p-8 text-center bg-white rounded-lg border border-slate-200">
        <p className="text-sm text-slate-500">No ambiguous legal terms detected in this document.</p>
      </div>
    )
  }

  // Unique terms for filter
  const uniqueTerms = Array.from(new Set(occurrences.map(o => o.term)))

  const filtered = selectedTermFilter === 'ALL'
    ? occurrences
    : occurrences.filter(o => o.term === selectedTermFilter)

  const activeOccurrence = filtered[selectedOccurrenceIdx] || filtered[0]

  return (
    <div className="space-y-4">
      {/* Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-3 rounded-lg border border-slate-200">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
          <Filter className="w-3.5 h-3.5 text-slate-500" />
          <span>Filter by Term:</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          <button
            type="button"
            onClick={() => { setSelectedTermFilter('ALL'); setSelectedOccurrenceIdx(0); }}
            className={cn(
              'px-2.5 py-1 rounded text-xs font-medium transition-colors',
              selectedTermFilter === 'ALL'
                ? 'bg-slate-900 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            )}
          >
            All Terms ({occurrences.length})
          </button>
          {uniqueTerms.map(t => {
            const count = occurrences.filter(o => o.term === t).length
            return (
              <button
                key={t}
                type="button"
                onClick={() => { setSelectedTermFilter(t); setSelectedOccurrenceIdx(0); }}
                className={cn(
                  'px-2.5 py-1 rounded text-xs font-medium transition-colors font-mono',
                  selectedTermFilter === t
                    ? 'bg-amber-700 text-white'
                    : 'bg-amber-50 text-amber-900 hover:bg-amber-100 border border-amber-200'
                )}
              >
                {t} ({count})
              </button>
            )
          })}
        </div>
      </div>

      {/* Master-Detail Occurrence Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Occurrences list */}
        <div className="lg:col-span-5 space-y-2 max-h-[650px] overflow-y-auto pr-1">
          {filtered.map((occ, idx) => {
            const isSelected = (filtered[selectedOccurrenceIdx] || filtered[0]) === occ
            return (
              <div
                key={`${occ.passage_id}_${occ.term}_${idx}`}
                onClick={() => setSelectedOccurrenceIdx(idx)}
                className={cn(
                  'p-3.5 rounded-lg border transition-all text-xs cursor-pointer',
                  isSelected
                    ? 'bg-slate-900 text-white border-slate-900 shadow-sm ring-1 ring-slate-900'
                    : 'bg-white text-slate-800 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                )}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-1.5 font-mono font-bold text-sm">
                    <span className={isSelected ? 'text-amber-300' : 'text-amber-800'}>
                      "{occ.term}"
                    </span>
                    <span className={`text-[10px] font-normal ${isSelected ? 'text-slate-400' : 'text-slate-500'}`}>
                      {occ.page ? `p.${occ.page}` : occ.passage_id}
                    </span>
                  </div>

                  {occ.uncertain ? (
                    <Badge variant="warning" className="text-[10px] py-0">
                      Uncertain
                    </Badge>
                  ) : (
                    <Badge variant="success" className="text-[10px] py-0">
                      Confident
                    </Badge>
                  )}
                </div>

                <p className={`line-clamp-2 leading-relaxed ${isSelected ? 'text-slate-300' : 'text-slate-600'}`}>
                  "{occ.sentence}"
                </p>

                {occ.selected_sense && (
                  <div className={`mt-2 text-[10px] flex items-center justify-between border-t pt-1.5 ${isSelected ? 'border-slate-800 text-slate-400' : 'border-slate-100 text-slate-500'}`}>
                    <span>Top: <code className="font-mono">{occ.selected_sense.synset_id}</code></span>
                    <span className="font-semibold text-emerald-500">Score: {occ.selected_sense.score.toFixed(2)}</span>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Right Column: Detailed Result Card */}
        <div className="lg:col-span-7">
          {activeOccurrence ? (
            <WsdResultCard result={activeOccurrence} />
          ) : (
            <div className="p-8 text-center bg-white rounded-lg border border-slate-200 text-slate-500 text-sm">
              Select an occurrence from the list to inspect candidate senses and evidence.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
