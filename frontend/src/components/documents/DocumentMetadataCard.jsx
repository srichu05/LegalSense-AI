import React from 'react'
import { FileCheck, FileText, Layers, Hash, AlertTriangle, ShieldCheck } from 'lucide-react'
import { Card, CardContent } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Alert, AlertDescription } from '../ui/Alert'

export function DocumentMetadataCard({ metadata }) {
  if (!metadata) return null

  const warnings = metadata.warnings || []

  return (
    <div className="space-y-4">
      <Card className="border-slate-200 bg-white">
        <CardContent className="p-5">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3 mb-4">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-md bg-slate-900 text-white flex items-center justify-center font-bold text-xs uppercase font-mono">
                {metadata.file_type || 'DOC'}
              </div>
              <div>
                <h4 className="font-serif font-bold text-slate-900 text-base">{metadata.filename}</h4>
                <p className="text-[11px] text-slate-500 font-mono">ID: {metadata.document_id}</p>
              </div>
            </div>

            <Badge variant="success" className="gap-1 text-xs">
              <ShieldCheck className="w-3.5 h-3.5" />
              In-Memory Parsed (No Disk Retention)
            </Badge>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div className="bg-slate-50 p-2.5 rounded-md border border-slate-200">
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">Characters</span>
              <span className="font-mono text-base font-bold text-slate-900">
                {(metadata.character_count || 0).toLocaleString()}
              </span>
            </div>

            <div className="bg-slate-50 p-2.5 rounded-md border border-slate-200">
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">Pages</span>
              <span className="font-mono text-base font-bold text-slate-900">
                {metadata.page_count || 1}
              </span>
            </div>

            <div className="bg-slate-50 p-2.5 rounded-md border border-slate-200">
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">Passages</span>
              <span className="font-mono text-base font-bold text-slate-900">
                {metadata.passage_count || 0}
              </span>
            </div>

            <div className="bg-amber-50/70 p-2.5 rounded-md border border-amber-200">
              <span className="text-[10px] font-semibold text-amber-800 uppercase tracking-wider block">Analyzed Terms</span>
              <span className="font-mono text-base font-bold text-amber-900">
                {(metadata.occurrences_analyzed || []).length}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {warnings.length > 0 && (
        <Alert variant="amber">
          <div className="space-y-1">
            <span className="font-semibold block text-amber-900">Document Processing Notice:</span>
            {warnings.map((w, idx) => (
              <AlertDescription key={idx} className="text-amber-800 text-xs">
                • {w}
              </AlertDescription>
            ))}
          </div>
        </Alert>
      )}
    </div>
  )
}
