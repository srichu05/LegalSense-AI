import React from 'react'
import { ShieldAlert, BookOpen, ExternalLink } from 'lucide-react'

export function Footer() {
  return (
    <footer className="w-full border-t border-slate-200 bg-white py-6 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="rounded-lg border border-amber-200 bg-amber-50/60 p-4 text-xs text-amber-950 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-start gap-2.5">
            <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-amber-900 mr-1.5">Educational & Research Disclaimer:</span>
              <span>
                LegalSense is a computational linguistics research prototype demonstrating Word Sense Disambiguation using Princeton WordNet 3.0 and lexical relations.
                WordNet is a general-English lexical database, not an authoritative legal ontology. Output is provided strictly for academic analysis and navigation assistance,
                and does not constitute legal advice or formal statutory interpretation.
              </span>
            </div>
          </div>
          <div className="shrink-0 flex items-center gap-3 text-amber-800 font-medium">
            <span>Princeton WordNet 3.0</span>
            <span>•</span>
            <span>Black's Law Concepts</span>
          </div>
        </div>

        <div className="mt-4 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <p>© 2026 LegalSense NLP Project. All analysis executes locally via Flask backend.</p>
          <div className="flex items-center gap-4 text-slate-600">
            <span>REST API v1</span>
            <span>•</span>
            <span>Extended Lesk + Stopword Filtering</span>
            <span>•</span>
            <span>OpenJDK 21 → React+Vite Reconstructed</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
