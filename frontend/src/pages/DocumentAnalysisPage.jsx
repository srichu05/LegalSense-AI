import React, { useState } from 'react'
import { FileText, UploadCloud, AlertCircle, Sparkles, Bot, Layers } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Alert, AlertTitle, AlertDescription } from '../components/ui/Alert'
import { Skeleton } from '../components/ui/Skeleton'
import { DocumentUploadZone } from '../components/documents/DocumentUploadZone'
import { DocumentMetadataCard } from '../components/documents/DocumentMetadataCard'
import { PassageOccurrenceViewer } from '../components/documents/PassageOccurrenceViewer'
import { useMutation } from '@tanstack/react-query'
import { analyzeDocument } from '../lib/api/client'

export function DocumentAnalysisPage() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [useLlm, setUseLlm] = useState(false)

  const documentMutation = useMutation({
    mutationFn: () => analyzeDocument(selectedFile, useLlm),
  })

  const handleSubmit = e => {
    e.preventDefault()
    if (!selectedFile) return
    documentMutation.mutate()
  }

  // Pre-load bundled sample document for immediate one-click testing
  const handleLoadBundledSample = async (filename, contentText) => {
    const blob = new Blob([contentText], { type: 'text/plain' })
    const file = new File([blob], filename, { type: 'text/plain' })
    setSelectedFile(file)
  }

  const sampleContractText = `STANDARD COMMERCIAL SERVICES AGREEMENT
This Commercial Services Agreement is entered into by and between Acme Corp and Beta LLC.

1. CONSIDERATION AND FEES
In consideration of the mutual covenants contained herein and other good and valuable consideration,
the receipt and sufficiency of which are hereby acknowledged, Client agrees to pay Provider the stated fees.

2. EXECUTION AND COMMENCEMENT
The execution of this instrument by authorized representatives of both parties gives immediate legal effect.
Either party may seek equitable relief, including injunction or specific performance, in the event of breach.

3. GOVERNING LAW AND ACTIONS
Any formal legal action or suit arising out of this agreement shall be brought exclusively in the courts of law.`

  const sampleCourtRulingText = `APPELLATE COURT OPINION & RULING
IN THE APPELLATE COURT OF CIVIL JURISDICTION
Case No. 2026-CV-889

OPINION OF THE COURT
The plaintiff-appellant appeals from an order of the district court granting defendant's motion to dismiss.
The primary dispute concerns whether adequate consideration was provided to bind the parties under the deed.

Having examined the formal legal instrument and the record of proceedings, the court finds sufficient
grounds to sustain the action. The appellant's prayer for injunctive relief is remanded for further hearing.`

  const resultData = documentMutation.data

  return (
    <div className="space-y-6 animate-fadeIn max-w-5xl mx-auto">
      {/* Editorial Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <FileText className="w-5 h-5 text-amber-700" />
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Document Intelligence & Passage Analysis
          </h1>
        </div>
        <p className="text-sm text-slate-600 font-sans leading-relaxed">
          Upload commercial agreements, contracts, or court opinions (<code className="font-mono bg-slate-100 px-1 py-0.5 rounded">.txt</code> or <code className="font-mono bg-slate-100 px-1 py-0.5 rounded">.pdf</code>).
          The engine segments text into sentence-respecting passages, detects polysemous legal terms, and computes disambiguation evidence.
        </p>
      </div>

      {/* Upload Zone Card */}
      <Card className="border-slate-200 bg-white shadow-xs">
        <form onSubmit={handleSubmit}>
          <CardContent className="p-6 space-y-4">
            <DocumentUploadZone
              selectedFile={selectedFile}
              onFileSelect={file => setSelectedFile(file)}
              onClear={() => { setSelectedFile(null); documentMutation.reset(); }}
              isLoading={documentMutation.isPending}
            />

            {/* Quick-Load Sample Document Buttons */}
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 text-xs">
              <span className="flex items-center gap-1 text-slate-500 font-medium mr-1">
                <Sparkles className="w-3.5 h-3.5 text-amber-600" /> Preload Bundled Sample:
              </span>
              <button
                type="button"
                onClick={() => handleLoadBundledSample('sample_contract.txt', sampleContractText)}
                disabled={documentMutation.isPending}
                className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-medium transition-colors border border-slate-200"
              >
                Commercial Services Agreement (.txt)
              </button>
              <button
                type="button"
                onClick={() => handleLoadBundledSample('sample_court_ruling.txt', sampleCourtRulingText)}
                disabled={documentMutation.isPending}
                className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-medium transition-colors border border-slate-200"
              >
                Appellate Court Ruling (.txt)
              </button>
            </div>

            {/* Actions & LLM Toggle */}
            <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useLlm}
                    onChange={e => setUseLlm(e.target.checked)}
                    disabled={documentMutation.isPending}
                    className="sr-only peer"
                  />
                  <div className="w-9 h-5 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-slate-900" />
                </label>
                <span className="text-xs text-slate-700 font-medium">
                  Enable optional Groq advisory for document terms
                </span>
              </div>

              <Button
                type="submit"
                isLoading={documentMutation.isPending}
                disabled={!selectedFile || documentMutation.isPending}
                size="lg"
                className="px-8 gap-2 bg-slate-900 text-white hover:bg-slate-800"
              >
                <UploadCloud className="w-4 h-4" />
                <span>Analyze Document</span>
              </Button>
            </div>
          </CardContent>
        </form>
      </Card>

      {/* Error Feedback */}
      {documentMutation.isError && (
        <Alert variant="destructive">
          <AlertTitle>Extraction & Ingestion Error</AlertTitle>
          <AlertDescription>
            {documentMutation.error?.message || 'Failed to process document.'}
          </AlertDescription>
        </Alert>
      )}

      {/* Loading Skeletons */}
      {documentMutation.isPending && (
        <div className="space-y-4">
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-96 w-full rounded-xl" />
        </div>
      )}

      {/* Results Workspace */}
      {resultData && (
        <div className="space-y-6 pt-2">
          {/* Metadata Card */}
          <DocumentMetadataCard metadata={resultData} />

          {/* Occurrences & Passage Browser */}
          <div>
            <div className="flex items-center justify-between mb-3 border-b border-slate-200 pb-2">
              <h2 className="font-serif text-xl font-bold text-slate-900 flex items-center gap-2">
                <Layers className="w-5 h-5 text-amber-700" />
                <span>Detected Legal Term Occurrences ({(resultData.occurrences_analyzed || []).length})</span>
              </h2>
              <span className="text-xs text-slate-500 font-mono">
                {resultData.passage_count} Passages Extracted
              </span>
            </div>

            <PassageOccurrenceViewer occurrences={resultData.occurrences_analyzed || []} />
          </div>
        </div>
      )}
    </div>
  )
}
