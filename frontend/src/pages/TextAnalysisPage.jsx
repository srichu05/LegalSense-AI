import React, { useState } from 'react'
import { BookOpen, Sparkles, AlertCircle, Bot, ArrowRight, RotateCcw } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Textarea } from '../components/ui/Textarea'
import { Badge } from '../components/ui/Badge'
import { Alert, AlertTitle, AlertDescription } from '../components/ui/Alert'
import { Skeleton } from '../components/ui/Skeleton'
import { WsdResultCard } from '../components/analysis/WsdResultCard'
import { useMutation } from '@tanstack/react-query'
import { analyzeText } from '../lib/api/client'

export function TextAnalysisPage() {
  const [text, setText] = useState('')
  const [targetWord, setTargetWord] = useState('')
  const [useLlm, setUseLlm] = useState(false)

  const sampleClauses = [
    {
      title: 'Contract Consideration',
      text: 'The buyer provided good and valuable consideration by agreeing to execute the commercial deed upon closing.',
      target: 'consideration',
    },
    {
      title: 'Appellate Action & Relief',
      text: 'The plaintiff commenced a formal action in district court seeking equitable relief against the defaulting party.',
      target: 'action',
    },
    {
      title: 'Instrument Execution',
      text: 'Both named parties executed the legal instrument in good faith under applicable state statutes.',
      target: 'instrument',
    },
    {
      title: 'Motion to Dismiss',
      text: 'The court reviewed the defendant’s motion to dismiss for lack of subject matter jurisdiction.',
      target: 'motion',
    },
  ]

  const analysisMutation = useMutation({
    mutationFn: () => analyzeText(text, targetWord, useLlm),
  })

  const handleSubmit = e => {
    e.preventDefault()
    if (!text.trim()) return
    analysisMutation.mutate()
  }

  const handleLoadSample = sample => {
    setText(sample.text)
    setTargetWord(sample.target)
  }

  const handleReset = () => {
    setText('')
    setTargetWord('')
    analysisMutation.reset()
  }

  const results = analysisMutation.data?.results || []
  const warnings = analysisMutation.data?.warnings || []

  return (
    <div className="space-y-6 animate-fadeIn max-w-5xl mx-auto">
      {/* Editorial Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <BookOpen className="w-5 h-5 text-amber-700" />
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Word Sense Disambiguation Workspace
          </h1>
        </div>
        <p className="text-sm text-slate-600 font-sans leading-relaxed">
          Analyze legal clauses to identify and disambiguate polysemous terminology. Results combine Princeton WordNet 3.0 candidate senses,
          itemized token overlap evidence, and curated Black's Law glossary definitions.
        </p>
      </div>

      {/* Main Input Form Card */}
      <Card className="border-slate-200 bg-white shadow-xs">
        <form onSubmit={handleSubmit}>
          <CardContent className="p-6 space-y-4">
            {/* Clause Textarea */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                  Legal Clause or Sentence Context <span className="text-rose-500">*</span>
                </label>
                <span className="text-[11px] text-slate-400 font-mono">
                  {text.length.toLocaleString()} / 50,000 chars
                </span>
              </div>
              <Textarea
                value={text}
                onChange={e => setText(e.target.value)}
                placeholder="Enter or paste a legal clause (e.g. 'The parties provided adequate consideration under the agreement upon execution...')"
                className="h-32 text-sm leading-relaxed"
                disabled={analysisMutation.isPending}
              />
            </div>

            {/* Target Word & Optional LLM Toggle Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-center">
              <div>
                <label className="text-xs font-semibold text-slate-700 uppercase tracking-wide block mb-1.5">
                  Target Word for Disambiguation <span className="text-slate-400 font-normal lowercase">(optional — auto-detects if blank)</span>
                </label>
                <Input
                  value={targetWord}
                  onChange={e => setTargetWord(e.target.value)}
                  placeholder="e.g. consideration, action, party, relief"
                  disabled={analysisMutation.isPending}
                  className="h-10 text-sm font-mono"
                />
              </div>

              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 flex items-center justify-between sm:mt-4">
                <div className="flex items-center gap-2">
                  <Bot className="w-4 h-4 text-indigo-700" />
                  <div>
                    <span className="text-xs font-semibold text-slate-900 block">Optional Groq Assistance</span>
                    <span className="text-[10px] text-slate-500 block">Server-side LLM advisory with local fallback</span>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useLlm}
                    onChange={e => setUseLlm(e.target.checked)}
                    disabled={analysisMutation.isPending}
                    className="sr-only peer"
                  />
                  <div className="w-9 h-5 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-slate-900" />
                </label>
              </div>
            </div>

            {/* Sample Inputs */}
            <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center gap-2 text-xs">
              <span className="flex items-center gap-1 text-slate-500 font-medium mr-1">
                <Sparkles className="w-3.5 h-3.5 text-amber-600" /> Sample Clauses:
              </span>
              {sampleClauses.map(sc => (
                <button
                  key={sc.title}
                  type="button"
                  onClick={() => handleLoadSample(sc)}
                  disabled={analysisMutation.isPending}
                  className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-medium transition-colors border border-slate-200"
                >
                  {sc.title}
                </button>
              ))}
            </div>

            {/* Action Buttons */}
            <div className="pt-3 flex items-center justify-between border-t border-slate-100">
              <Button
                type="button"
                variant="ghost"
                onClick={handleReset}
                disabled={(!text && !targetWord && !analysisMutation.data) || analysisMutation.isPending}
                className="gap-1.5 text-xs text-slate-600"
              >
                <RotateCcw className="w-3.5 h-3.5" /> Clear Form
              </Button>

              <Button
                type="submit"
                isLoading={analysisMutation.isPending}
                disabled={!text.trim() || analysisMutation.isPending}
                variant="default"
                size="lg"
                className="px-8 gap-2 bg-slate-900 text-white hover:bg-slate-800"
              >
                <BookOpen className="w-4 h-4" />
                <span>Disambiguate Text</span>
              </Button>
            </div>
          </CardContent>
        </form>
      </Card>

      {/* Error Banner */}
      {analysisMutation.isError && (
        <Alert variant="destructive">
          <AlertTitle>Analysis Error</AlertTitle>
          <AlertDescription>
            {analysisMutation.error?.message || 'Failed to complete disambiguation request.'}
          </AlertDescription>
        </Alert>
      )}

      {/* Warnings Banner */}
      {warnings.length > 0 && (
        <Alert variant="warning">
          <div className="space-y-1">
            <AlertTitle>Analysis Advisory</AlertTitle>
            {warnings.map((w, idx) => (
              <AlertDescription key={idx}>• {w}</AlertDescription>
            ))}
          </div>
        </Alert>
      )}

      {/* Loading Skeletons */}
      {analysisMutation.isPending && (
        <div className="space-y-4">
          <Skeleton className="h-48 w-full rounded-xl" />
          <Skeleton className="h-64 w-full rounded-xl" />
        </div>
      )}

      {/* Results List */}
      {results.length > 0 && (
        <div className="space-y-6 pt-2">
          <div className="flex items-center justify-between border-b border-slate-200 pb-2">
            <h2 className="font-serif text-xl font-bold text-slate-900">
              Disambiguation Results ({results.length} {results.length === 1 ? 'Term' : 'Terms'})
            </h2>
            <span className="text-xs text-slate-500 font-mono">
              Request ID: {analysisMutation.data?.request_id}
            </span>
          </div>

          <div className="space-y-6">
            {results.map((res, idx) => (
              <WsdResultCard key={`${res.term}_${idx}`} result={res} index={idx} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
