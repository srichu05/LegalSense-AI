import React, { useState } from 'react'
import { Search, Database, Layers, Sparkles, AlertCircle } from 'lucide-react'
import { SearchBar } from '../components/search/SearchBar'
import { SearchResultCard } from '../components/search/SearchResultCard'
import { EmptySearchState } from '../components/search/EmptySearchState'
import { Alert, AlertTitle, AlertDescription } from '../components/ui/Alert'
import { Skeleton } from '../components/ui/Skeleton'
import { useMutation } from '@tanstack/react-query'
import { searchCorpus } from '../lib/api/client'

export function CorpusSearchPage() {
  const [query, setQuery] = useState('consideration exchanged under agreement')
  const [topK, setTopK] = useState(5)
  const [hasSearched, setHasSearched] = useState(false)

  const searchMutation = useMutation({
    mutationFn: () => searchCorpus(query, topK),
    onSuccess: () => setHasSearched(true),
  })

  const handleSearch = () => {
    if (!query.trim()) return
    searchMutation.mutate()
  }

  const results = searchMutation.data?.results || []
  const warnings = searchMutation.data?.warnings || []

  return (
    <div className="space-y-6 animate-fadeIn max-w-5xl mx-auto">
      {/* Editorial Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Search className="w-5 h-5 text-amber-700" />
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Corpus Passage Retrieval
          </h1>
        </div>
        <p className="text-sm text-slate-600 font-sans leading-relaxed">
          Search the bundled repository corpus using explainable multi-signal ranking (60% TF-IDF + 30% Lexical Overlap + 10% Glossary Boost).
          Passages are ranked transparently with itemized matched legal terms and source document origins.
        </p>
      </div>

      {/* Search Input Bar */}
      <SearchBar
        query={query}
        setQuery={setQuery}
        topK={topK}
        setTopK={setTopK}
        onSearch={handleSearch}
        isLoading={searchMutation.isPending}
      />

      {/* Error Alert */}
      {searchMutation.isError && (
        <Alert variant="destructive">
          <AlertTitle>Search Query Failed</AlertTitle>
          <AlertDescription>
            {searchMutation.error?.message || 'Failed to search corpus.'}
          </AlertDescription>
        </Alert>
      )}

      {/* Warnings Alert */}
      {warnings.length > 0 && (
        <Alert variant="warning">
          <div className="space-y-1">
            <AlertTitle>Search Note</AlertTitle>
            {warnings.map((w, idx) => (
              <AlertDescription key={idx}>• {w}</AlertDescription>
            ))}
          </div>
        </Alert>
      )}

      {/* Loading Skeletons */}
      {searchMutation.isPending && (
        <div className="space-y-3">
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-32 w-full rounded-xl" />
        </div>
      )}

      {/* Search Results */}
      {!searchMutation.isPending && (
        <div>
          {results.length > 0 ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Ranked Hits ({results.length} Passages Found)
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  Method: tfidf_lexical_wsd
                </span>
              </div>

              <div className="space-y-3">
                {results.map((res, idx) => (
                  <SearchResultCard key={`${res.document_id}_${res.passage_id}_${idx}`} result={res} rank={idx + 1} />
                ))}
              </div>
            </div>
          ) : (
            <EmptySearchState hasSearched={hasSearched} query={query} />
          )}
        </div>
      )}
    </div>
  )
}
