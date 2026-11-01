import React from 'react'
import { BookMarked, AlertCircle, Info, Landmark } from 'lucide-react'
import { Badge } from '../ui/Badge'

export function LegalGlossaryCard({ glossaryEntry }) {
  if (!glossaryEntry) return null

  return (
    <div className="rounded-lg border border-amber-300 bg-gradient-to-b from-amber-50/70 to-amber-50/30 p-5 shadow-xs transition-all">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-amber-200/80 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-md bg-amber-700 text-white shadow-2xs">
            <Landmark className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-serif font-bold text-amber-950 text-base capitalize">
                {glossaryEntry.term}
              </span>
              <Badge variant="amberSolid" className="text-[10px] uppercase tracking-wider py-0 px-2">
                Curated Legal Glossary
              </Badge>
            </div>
            <p className="text-[11px] text-amber-800/90 font-medium">
              Source: {glossaryEntry.source || "Black's Law Concept Summary"}
            </p>
          </div>
        </div>

        {glossaryEntry.jurisdiction && (
          <Badge variant="amber" className="text-xs">
            Jurisdiction: {glossaryEntry.jurisdiction}
          </Badge>
        )}
      </div>

      <div className="mt-3.5 space-y-3 text-sm text-slate-800">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-amber-900 block mb-1">
            Authoritative Legal Definition
          </span>
          <p className="leading-relaxed text-slate-900 font-serif text-[15px] bg-white/70 p-3 rounded-md border border-amber-200/60 shadow-2xs">
            "{glossaryEntry.definition}"
          </p>
        </div>

        {glossaryEntry.usage_example && (
          <div className="text-xs text-slate-700 bg-amber-100/40 p-2.5 rounded border border-amber-200/40">
            <span className="font-semibold text-amber-900 mr-1.5">Usage Example:</span>
            <span className="italic">"{glossaryEntry.usage_example}"</span>
          </div>
        )}

        {glossaryEntry.limitations && (
          <div className="flex items-start gap-2 text-xs text-amber-800 bg-amber-50 p-2.5 rounded border border-amber-200/70">
            <Info className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <span className="leading-normal">{glossaryEntry.limitations}</span>
          </div>
        )}
      </div>
    </div>
  )
}
