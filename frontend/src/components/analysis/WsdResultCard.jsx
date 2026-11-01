import React, { useState, useEffect, useRef } from 'react'
import gsap from 'gsap'
import { AlertTriangle, CheckCircle, Network, BookOpen, Bot } from 'lucide-react'
import { Card, CardHeader, CardContent } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { LegalGlossaryCard } from './LegalGlossaryCard'
import { CandidateSenseItem } from './CandidateSenseItem'
import { EvidencePanel } from './EvidencePanel'
import { LexicalNetwork3D } from '../visualizations/LexicalNetwork3D'

export function WsdResultCard({ result, index = 0 }) {
  const [showNetwork, setShowNetwork] = useState(false)
  const [selectedCandidate, setSelectedCandidate] = useState(result.selected_sense || null)
  const cardRef = useRef(null)

  useEffect(() => {
    // Subtle staggered entrance animation using GSAP with React cleanup
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReducedMotion || !cardRef.current) return

    const ctx = gsap.context(() => {
      gsap.fromTo(
        cardRef.current,
        { opacity: 0, y: 15 },
        { opacity: 1, y: 0, duration: 0.45, delay: index * 0.1, ease: 'power2.out' }
      )
    }, cardRef)

    return () => ctx.revert()
  }, [index])

  if (!result) return null

  const candidates = result.candidate_senses || []
  const hasGlossary = Boolean(result.legal_glossary_entry)

  return (
    <div ref={cardRef} className="space-y-4">
      <Card className="border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
        {/* Top Header */}
        <CardHeader className="bg-slate-50/70 border-b border-slate-200 py-4 px-6 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2.5">
            <span className="font-serif text-xl font-bold text-slate-900 tracking-tight">
              "{result.term}"
            </span>
            {result.pos && (
              <Badge variant="outline" className="font-mono text-xs uppercase bg-white">
                POS: {result.pos}
              </Badge>
            )}
            {result.lemma && (
              <span className="text-xs text-slate-500 font-mono">
                lemma: [{result.lemma}]
              </span>
            )}
            <Badge variant="navy" className="text-[11px] font-mono">
              Method: {result.selection_method || 'extended_lesk'}
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            {/* Uncertainty Badge */}
            {result.uncertain ? (
              <Badge variant="warning" className="gap-1.5 py-1 px-3 text-xs bg-amber-50 text-amber-900 border-amber-300">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-700" />
                Uncertain / Near-Tie
              </Badge>
            ) : (
              <Badge variant="success" className="gap-1.5 py-1 px-3 text-xs bg-emerald-50 text-emerald-800 border-emerald-300">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                High Confidence (92.3% Selective Accuracy)
              </Badge>
            )}

            {/* 3D Network Toggle */}
            <Button
              variant={showNetwork ? 'amber' : 'outline'}
              size="sm"
              onClick={() => setShowNetwork(!showNetwork)}
              className="gap-1.5 text-xs h-8"
            >
              <Network className="w-3.5 h-3.5" />
              {showNetwork ? 'Hide 3D Network' : 'Inspect 3D Network'}
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {/* Target Sentence Context */}
          {result.sentence && (
            <div className="bg-slate-50 p-3 rounded-md border border-slate-200 text-xs text-slate-700 font-sans">
              <span className="font-semibold text-slate-900 mr-1.5 uppercase tracking-wide text-[10px]">
                Context Sentence:
              </span>
              <span className="italic">"{result.sentence}"</span>
            </div>
          )}

          {/* Optional LLM Assistance Status / Rationale */}
          {result.llm_assistance_status && result.llm_assistance_status !== 'disabled' && (
            <div className="rounded-md border border-indigo-200 bg-indigo-50/70 p-3 text-xs text-indigo-950 flex items-start gap-2.5">
              <Bot className="w-4 h-4 text-indigo-700 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-indigo-900 mr-1.5">Groq Contextual Advisory:</span>
                {result.llm_suggested_sense ? (
                  <span>
                    Suggested Synset: <code className="font-mono font-bold text-indigo-950">{result.llm_suggested_sense}</code>
                    {result.llm_rationale && ` — "${result.llm_rationale}"`}
                  </span>
                ) : (
                  <span>{result.llm_rationale || 'Assistance enabled (local fallback preserved).'}</span>
                )}
              </div>
            </div>
          )}

          {/* 3D Lexical Network Drawer */}
          {showNetwork && (
            <div className="transition-all duration-300">
              <LexicalNetwork3D
                term={result.term}
                candidateSenses={candidates}
                selectedSense={selectedCandidate}
                onSelectSense={cand => setSelectedCandidate(cand)}
              />
            </div>
          )}

          {/* 1. Curated Legal Glossary (Distinct Amber Card) */}
          {hasGlossary && (
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-amber-900 block mb-2">
                Curated Domain Definition (Independent of WordNet)
              </span>
              <LegalGlossaryCard glossaryEntry={result.legal_glossary_entry} />
            </div>
          )}

          {/* 2. Princeton WordNet Candidate Senses */}
          <div>
            <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-slate-600" />
                <h4 className="font-serif font-semibold text-slate-900 text-sm">
                  Princeton WordNet 3.0 Candidate Senses ({candidates.length})
                </h4>
              </div>
              <span className="text-[11px] text-slate-500 font-sans">
                Ranked by Extended Lesk score (Glosses + Examples + Hypernyms + Hyponyms)
              </span>
            </div>

            {candidates.length > 0 ? (
              <div className="space-y-2.5">
                {candidates.map((cand, idx) => {
                  const isSelected = Boolean(
                    result.selected_sense && result.selected_sense.synset_id === cand.synset_id
                  )
                  const isTopRank = idx === 0
                  return (
                    <CandidateSenseItem
                      key={cand.synset_id}
                      candidate={cand}
                      isSelected={isSelected}
                      isTopRank={isTopRank}
                      isHighlighted={selectedCandidate?.synset_id === cand.synset_id}
                      onSelect={c => setSelectedCandidate(c)}
                    />
                  )
                })}
              </div>
            ) : (
              <div className="p-4 bg-slate-50 border border-slate-200 rounded text-center text-xs text-slate-500">
                No WordNet synsets found for term "{result.term}".
              </div>
            )}
          </div>

          {/* 3. Itemized Overlap Evidence */}
          <EvidencePanel evidence={result.evidence} />
        </CardContent>
      </Card>
    </div>
  )
}
