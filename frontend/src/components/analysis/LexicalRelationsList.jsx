import React, { useState } from 'react'
import { ChevronDown, ChevronUp, Link as LinkIcon } from 'lucide-react'

export function LexicalRelationsList({ relations }) {
  const [isExpanded, setIsExpanded] = useState(false)
  if (!relations) return null

  const synonyms = relations.synonyms || []
  const hypernyms = relations.hypernyms || []
  const hyponyms = relations.hyponyms || []

  const totalRelations = synonyms.length + hypernyms.length + hyponyms.length
  if (totalRelations === 0) return null

  return (
    <div className="mt-2.5 pt-2.5 border-t border-slate-100 text-xs">
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="inline-flex items-center gap-1.5 text-slate-600 hover:text-slate-900 font-medium transition-colors"
      >
        <LinkIcon className="w-3 h-3 text-slate-400" />
        <span>Lexical Relations ({totalRelations})</span>
        {isExpanded ? <ChevronUp className="w-3 h-3 ml-0.5" /> : <ChevronDown className="w-3 h-3 ml-0.5" />}
      </button>

      {isExpanded && (
        <div className="mt-2 space-y-2 bg-slate-50 p-2.5 rounded-md border border-slate-200">
          {synonyms.length > 0 && (
            <div>
              <span className="font-semibold text-slate-700 block mb-1">Synonyms:</span>
              <div className="flex flex-wrap gap-1">
                {synonyms.map(syn => (
                  <span key={syn} className="px-2 py-0.5 bg-white border border-slate-200 rounded text-slate-800 text-[11px]">
                    {syn}
                  </span>
                ))}
              </div>
            </div>
          )}

          {hypernyms.length > 0 && (
            <div>
              <span className="font-semibold text-slate-700 block mb-1">Hypernyms (Broader):</span>
              <div className="flex flex-wrap gap-1">
                {hypernyms.map(hyp => (
                  <span key={hyp} className="px-2 py-0.5 bg-sky-50 border border-sky-200 text-sky-900 rounded text-[11px]">
                    ↑ {hyp}
                  </span>
                ))}
              </div>
            </div>
          )}

          {hyponyms.length > 0 && (
            <div>
              <span className="font-semibold text-slate-700 block mb-1">Hyponyms (Narrower):</span>
              <div className="flex flex-wrap gap-1">
                {hyponyms.map(hyp => (
                  <span key={hyp} className="px-2 py-0.5 bg-emerald-50 border border-emerald-200 text-emerald-900 rounded text-[11px]">
                    ↓ {hyp}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
