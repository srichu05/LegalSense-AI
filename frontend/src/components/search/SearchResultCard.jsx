import React from 'react'
import { FileText, Tag, Award, Sparkles } from 'lucide-react'
import { Card, CardContent } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { formatScore } from '../../lib/utils/formatters'

export function SearchResultCard({ result, rank = 1 }) {
  if (!result) return null

  const matchedTerms = result.matched_terms || []

  return (
    <Card className="border-slate-200 bg-white hover:border-slate-300 transition-all shadow-xs">
      <CardContent className="p-5 space-y-3">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2.5">
            <span className="flex items-center justify-center w-6 h-6 rounded-full bg-slate-900 text-white font-mono text-xs font-bold">
              #{rank}
            </span>
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-slate-500" />
              <span className="font-serif font-bold text-slate-900 text-sm">
                {result.document_name}
              </span>
              {result.page && (
                <Badge variant="outline" className="text-[10px] py-0">
                  Page {result.page}
                </Badge>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Compound Score:</span>
            <span className="font-mono text-sm font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              {formatScore(result.score)}
            </span>
            <Badge variant="secondary" className="text-[10px] font-mono">
              {result.score_method || 'tfidf_lexical_wsd'}
            </Badge>
          </div>
        </div>

        {/* Matched Legal Terms */}
        {matchedTerms.length > 0 && (
          <div className="flex items-center gap-2 flex-wrap text-xs">
            <span className="text-slate-500 flex items-center gap-1 text-[11px] font-medium">
              <Tag className="w-3 h-3 text-amber-600" /> Matched Terms:
            </span>
            {matchedTerms.map(t => (
              <span
                key={t}
                className="px-2 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-200 font-mono text-xs font-semibold"
              >
                {t}
              </span>
            ))}
          </div>
        )}

        {/* Passage Text */}
        <div className="bg-slate-50/70 p-3.5 rounded-md border border-slate-200 text-sm font-serif leading-relaxed text-slate-800">
          "{result.passage}"
        </div>

        {/* Informational score footnote */}
        <div className="text-[11px] text-slate-400 font-sans italic flex items-center justify-between">
          <span>Passage ID: <code className="font-mono text-slate-500">{result.passage_id || 'p_unknown'}</code></span>
          <span>Score is an algorithmic ranking signal (TF-IDF + lexical overlap + glossary boost), not a probability.</span>
        </div>
      </CardContent>
    </Card>
  )
}
