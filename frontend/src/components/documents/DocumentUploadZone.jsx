import React, { useRef, useState } from 'react'
import { UploadCloud, FileText, CheckCircle2, AlertCircle, X } from 'lucide-react'
import { Button } from '../ui/Button'
import { formatBytes } from '../../lib/utils/formatters'
import { cn } from '../../lib/utils/cn'

export function DocumentUploadZone({ onFileSelect, selectedFile, onClear, isLoading }) {
  const fileInputRef = useRef(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [errorMsg, setErrorMsg] = useState(null)

  const validateAndSet = file => {
    setErrorMsg(null)
    if (!file) return

    const maxBytes = 10 * 1024 * 1024 // 10MB
    if (file.size > maxBytes) {
      setErrorMsg(`File exceeds maximum size of 10 MB (selected: ${formatBytes(file.size)})`)
      return
    }

    const name = file.name.toLowerCase()
    if (!name.endsWith('.txt') && !name.endsWith('.pdf')) {
      setErrorMsg('Unsupported format. Only .txt and .pdf files are accepted.')
      return
    }

    onFileSelect(file)
  }

  const handleDrop = e => {
    e.preventDefault()
    setIsDragOver(false)
    if (isLoading) return
    const file = e.dataTransfer.files?.[0]
    validateAndSet(file)
  }

  const handleDragOver = e => {
    e.preventDefault()
    if (!isLoading) setIsDragOver(true)
  }

  const handleDragLeave = () => {
    setIsDragOver(false)
  }

  const handleFileInputChange = e => {
    const file = e.target.files?.[0]
    validateAndSet(file)
  }

  return (
    <div className="space-y-3">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !selectedFile && !isLoading && fileInputRef.current?.click()}
        className={cn(
          'relative border-2 border-dashed rounded-xl p-8 text-center transition-all flex flex-col items-center justify-center cursor-pointer',
          isDragOver
            ? 'border-amber-500 bg-amber-50/50'
            : selectedFile
            ? 'border-emerald-300 bg-emerald-50/20 cursor-default'
            : 'border-slate-300 bg-white hover:border-slate-400 hover:bg-slate-50/50'
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.pdf"
          onChange={handleFileInputChange}
          disabled={isLoading}
          className="hidden"
        />

        {selectedFile ? (
          <div className="flex items-center justify-between w-full max-w-md bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
            <div className="flex items-center gap-3 truncate">
              <div className="w-10 h-10 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center shrink-0">
                <FileText className="w-5 h-5" />
              </div>
              <div className="text-left truncate">
                <p className="text-sm font-semibold text-slate-900 truncate">{selectedFile.name}</p>
                <p className="text-xs text-slate-500 font-mono">{formatBytes(selectedFile.size)}</p>
              </div>
            </div>

            {!isLoading && (
              <button
                type="button"
                onClick={e => {
                  e.stopPropagation()
                  if (fileInputRef.current) fileInputRef.current.value = ''
                  onClear?.()
                }}
                className="p-1.5 rounded-md hover:bg-slate-100 text-slate-500 hover:text-slate-800 transition-colors ml-2"
                title="Remove selected file"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center mx-auto mb-3">
              <UploadCloud className="w-6 h-6 text-slate-600" />
            </div>
            <p className="text-sm font-semibold text-slate-900">
              Drag & drop your legal document here, or <span className="text-amber-800 underline">browse</span>
            </p>
            <p className="text-xs text-slate-500">
              Accepted formats: <code className="font-mono bg-slate-100 px-1 py-0.5 rounded">.txt</code>, <code className="font-mono bg-slate-100 px-1 py-0.5 rounded">.pdf</code> (Max 10 MB). Processed in-memory without persistent retention.
            </p>
          </div>
        )}
      </div>

      {errorMsg && (
        <div className="flex items-center gap-2 text-xs text-rose-700 bg-rose-50 p-3 rounded-md border border-rose-200">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}
    </div>
  )
}
