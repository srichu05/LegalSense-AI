import React from 'react'
import { Search, AlertCircle } from 'lucide-react'

export function EmptySearchState({ hasSearched = false, query = '' }) {
  if (!hasSearched) {
    return (
      <div className="text-center py-12 px-4 bg-white rounded-xl border border-slate-200 shadow-xs max-w-lg mx-auto">
        <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center mx-auto mb-3">
          <Search className="w-6 h-6 text-slate-400" />
        </div>
        <h4 className="font-serif font-bold text-slate-900 text-base mb-1">
          Search the Indexed Legal Corpus
        </h4>
        <p className="text-xs text-slate-500 leading-relaxed max-w-sm mx-auto">
          Enter a query above to search bundled legal contracts and appellate rulings using explainable TF-IDF, lexical overlap, and domain glossary boosting.
        </p>
      </div>
    )
  }

  return (
    <div className="text-center py-12 px-4 bg-white rounded-xl border border-slate-200 shadow-xs max-w-lg mx-auto">
      <div className="w-12 h-12 rounded-full bg-amber-50 text-amber-600 flex items-center justify-center mx-auto mb-3 border border-amber-200">
        <AlertCircle className="w-6 h-6 text-amber-600" />
      </div>
      <h4 className="font-serif font-bold text-slate-900 text-base mb-1">
        No Matching Passages Found
      </h4>
      <p className="text-xs text-slate-500 leading-relaxed max-w-sm mx-auto">
        No passages in the bundled corpus exceeded the minimum relevance threshold for <code className="font-mono text-slate-700">"{query}"</code>.
        Try broader terms such as "consideration", "breach", or "equitable relief".
      </p>
    </div>
  )
}
