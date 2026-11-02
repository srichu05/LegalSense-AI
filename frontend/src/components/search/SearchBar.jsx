import React from 'react'
import { Search, Sparkles } from 'lucide-react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'

export function SearchBar({
  query,
  setQuery,
  topK,
  setTopK,
  onSearch,
  isLoading,
}) {
  const exampleQueries = [
    'consideration exchanged under agreement',
    'motion to dismiss court ruling',
    'equitable relief and injunction',
    'execution of formal instrument deed',
  ]

  const handleSubmit = e => {
    e.preventDefault()
    onSearch()
  }

  return (
    <div className="space-y-3">
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search bundled legal corpus (e.g. 'adequate consideration upon execution')..."
            disabled={isLoading}
            className="pl-10 h-11 text-base font-sans"
          />
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 bg-white border border-slate-300 rounded-md px-3 h-11 text-xs text-slate-700 shadow-xs">
            <span className="font-semibold text-slate-500">top_k:</span>
            <select
              value={topK}
              onChange={e => setTopK(parseInt(e.target.value, 10))}
              disabled={isLoading}
              className="bg-transparent font-mono font-bold text-slate-900 focus:outline-none cursor-pointer"
            >
              <option value={3}>3</option>
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={20}>20</option>
            </select>
          </div>

          <Button
            type="submit"
            isLoading={isLoading}
            disabled={!query.trim() || isLoading}
            variant="default"
            className="h-11 px-6 gap-2 bg-slate-900 text-white hover:bg-slate-800"
          >
            <Search className="w-4 h-4" />
            <span>Search</span>
          </Button>
        </div>
      </form>

      {/* Example Query Pills */}
      <div className="flex items-center gap-2 flex-wrap text-xs text-slate-600">
        <span className="flex items-center gap-1 text-slate-500 font-medium">
          <Sparkles className="w-3.5 h-3.5 text-amber-600" /> Examples:
        </span>
        {exampleQueries.map(eq => (
          <button
            key={eq}
            type="button"
            onClick={() => { setQuery(eq); }}
            className="px-2.5 py-1 rounded-md bg-white border border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700 text-xs transition-colors"
          >
            "{eq}"
          </button>
        ))}
      </div>
    </div>
  )
}
