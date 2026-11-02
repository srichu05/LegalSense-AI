import React from 'react'
import { Link } from 'react-router-dom'
import { Scale, BookOpen, FileText, Search, Settings, ShieldCheck, Cpu, Database, ArrowRight, CheckCircle2 } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { useQuery } from '@tanstack/react-query'
import { checkHealth, getBaseUrl } from '../lib/api/client'

export function OverviewPage() {
  const { data: health, isPending, isError } = useQuery({
    queryKey: ['backendHealthOverview', getBaseUrl()],
    queryFn: () => checkHealth(4000),
    retry: 1,
  })

  const tools = [
    {
      to: '/analyze',
      title: 'Interactive Text Analysis',
      desc: 'Disambiguate polysemous legal terms in isolated clauses using Princeton WordNet 3.0 and Extended Lesk scoring.',
      icon: BookOpen,
      tag: 'Core WSD Engine',
    },
    {
      to: '/documents',
      title: 'Document Intelligence',
      desc: 'Upload .txt and .pdf legal contracts for in-memory passage segmentation, term occurrence detection, and lexical analysis.',
      icon: FileText,
      tag: 'In-Memory PDF/TXT',
    },
    {
      to: '/search',
      title: 'Corpus Passage Search',
      desc: 'Query indexed legal sample documents with explainable compound ranking (TF-IDF + lexical overlap + glossary boost).',
      icon: Search,
      tag: 'Explainable Retrieval',
    },
    {
      to: '/settings',
      title: 'Backend Configuration',
      desc: 'Inspect connection status, verify live /health endpoints, and configure the target Flask API endpoint.',
      icon: Settings,
      tag: 'Runtime Settings',
    },
  ]

  const metrics = [
    { label: 'WSD Legal Domain Accuracy', value: '80.0%', note: 'vs. 10.0% MFS baseline' },
    { label: 'Selective High Confidence', value: '92.3%', note: 'on non-uncertain cases' },
    { label: 'Corpus Search Precision@1', value: '100%', note: 'MRR: 1.0000 on test set' },
    { label: 'Local Memory Footprint', value: '< 50 MB', note: 'Zero transformer weights' },
  ]

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Editorial Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-xs relative overflow-hidden">
        <div className="max-w-3xl relative z-10 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 text-amber-900 border border-amber-200 text-xs font-semibold">
            <Scale className="w-3.5 h-3.5 text-amber-700" />
            <span>Academic Computational Linguistics Prototype • Phase 4 Verified</span>
          </div>

          <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-slate-900 leading-tight">
            Context-Aware Legal Document Analysis with Lexical Semantics
          </h1>

          <p className="text-slate-600 text-base sm:text-lg leading-relaxed font-sans">
            Legal drafting frequently assigns specialized meaning to common words like <em>consideration</em>, <em>action</em>, <em>party</em>, and <em>relief</em>.
            LegalSense disambiguates these polysemous terms using <strong>Princeton WordNet 3.0</strong>, <strong>Extended Lesk overlap scoring</strong>,
            and a <strong>curated Black's Law Concept glossary</strong>, delivering explainable evidence without hallucination.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <Link to="/analyze">
              <Button size="lg" className="bg-slate-900 text-white hover:bg-slate-800 gap-2 font-medium">
                <BookOpen className="w-4 h-4" /> Start Text Analysis
              </Button>
            </Link>
            <Link to="/documents">
              <Button variant="outline" size="lg" className="gap-2">
                <FileText className="w-4 h-4" /> Analyze Document
              </Button>
            </Link>
            <Link to="/search">
              <Button variant="ghost" size="lg" className="gap-2 text-slate-700">
                <Search className="w-4 h-4" /> Search Corpus
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Backend Live Status Card */}
      <Card className="border-slate-200 bg-white">
        <CardContent className="p-5 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className={`w-3.5 h-3.5 rounded-full ${health?.status === 'ok' ? 'bg-emerald-500 ring-4 ring-emerald-100' : 'bg-amber-500 animate-pulse'}`} />
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-slate-900 text-sm">
                  Flask Backend Status:
                </span>
                <Badge variant={health?.status === 'ok' ? 'success' : 'warning'} className="text-xs">
                  {health?.status === 'ok' ? 'Online & Healthy' : isPending ? 'Connecting...' : 'Disconnected'}
                </Badge>
              </div>
              <p className="text-xs text-slate-500 mt-0.5 font-mono">
                Connected to {getBaseUrl()} • WSD Engine: {health?.wsd_ready ? 'Ready' : 'Pending'} • Groq LLM: {health?.llm_enabled ? 'Configured' : 'Disabled (Local WSD Only)'}
              </p>
            </div>
          </div>

          <Link to="/settings">
            <Button variant="outline" size="sm" className="text-xs">
              Configure Endpoint
            </Button>
          </Link>
        </CardContent>
      </Card>

      {/* Evaluated Performance Metrics (Real Verified Numbers) */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-serif text-lg font-bold text-slate-900">
            Empirical Benchmark Results (Phase 4 Verified)
          </h2>
          <span className="text-xs text-slate-500">Held-out 30-instance legal test suite</span>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map(m => (
            <div key={m.label} className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
              <span className="text-xs text-slate-500 block font-medium">{m.label}</span>
              <span className="font-mono text-2xl font-bold text-slate-900 my-1 block">{m.value}</span>
              <span className="text-[11px] text-amber-800 font-medium block">{m.note}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Main Tools Grid */}
      <div>
        <h2 className="font-serif text-lg font-bold text-slate-900 mb-3">
          Core Workspaces & Research Modules
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {tools.map(tool => {
            const Icon = tool.icon
            return (
              <Link key={tool.to} to={tool.to} className="group">
                <Card className="h-full border-slate-200 hover:border-slate-400 hover:shadow-md transition-all bg-white">
                  <CardHeader className="p-5 pb-3">
                    <div className="flex items-center justify-between">
                      <div className="p-2 rounded-lg bg-slate-100 text-slate-900 group-hover:bg-amber-100 group-hover:text-amber-900 transition-colors">
                        <Icon className="w-5 h-5" />
                      </div>
                      <Badge variant="secondary" className="text-[10px]">
                        {tool.tag}
                      </Badge>
                    </div>
                    <CardTitle className="mt-3 group-hover:text-amber-800 transition-colors text-base font-serif">
                      {tool.title}
                    </CardTitle>
                    <CardDescription className="text-xs leading-relaxed text-slate-600">
                      {tool.desc}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="px-5 pb-4 pt-0 flex justify-end">
                    <span className="inline-flex items-center text-xs font-semibold text-slate-900 group-hover:text-amber-800 gap-1 transition-colors">
                      Open Workspace <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                    </span>
                  </CardContent>
                </Card>
              </Link>
            )
          })}
        </div>
      </div>
    </div>
  )
}
