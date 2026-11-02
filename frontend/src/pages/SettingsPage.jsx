import React, { useState } from 'react'
import { Settings, Server, RefreshCw, CheckCircle2, AlertCircle, RotateCcw, Link2, Shield } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Badge } from '../components/ui/Badge'
import { Alert, AlertTitle, AlertDescription } from '../components/ui/Alert'
import { getBaseUrl, setBaseUrl, resetBaseUrl, checkHealth, DEFAULT_API_BASE_URL } from '../lib/api/client'
import { useQueryClient } from '@tanstack/react-query'

export function SettingsPage() {
  const queryClient = useQueryClient()
  const [urlInput, setUrlInput] = useState(getBaseUrl())
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [testResult, setTestResult] = useState(null)
  const [isTesting, setIsTesting] = useState(false)

  const handleSave = e => {
    e.preventDefault()
    const saved = setBaseUrl(urlInput)
    setUrlInput(saved)
    setSaveSuccess(true)
    setTimeout(() => setSaveSuccess(false), 3000)
    queryClient.invalidateQueries({ queryKey: ['backendHealth'] })
    queryClient.invalidateQueries({ queryKey: ['backendHealthOverview'] })
  }

  const handleReset = () => {
    const defaultUrl = resetBaseUrl()
    setUrlInput(defaultUrl)
    setSaveSuccess(true)
    setTimeout(() => setSaveSuccess(false), 3000)
    queryClient.invalidateQueries({ queryKey: ['backendHealth'] })
    queryClient.invalidateQueries({ queryKey: ['backendHealthOverview'] })
  }

  const handleTestConnection = async () => {
    setIsTesting(true)
    setTestResult(null)
    const startTime = performance.now()
    try {
      const data = await checkHealth(5000)
      const duration = Math.round(performance.now() - startTime)
      setTestResult({
        success: true,
        data,
        duration,
      })
      queryClient.invalidateQueries({ queryKey: ['backendHealth'] })
      queryClient.invalidateQueries({ queryKey: ['backendHealthOverview'] })
    } catch (err) {
      const duration = Math.round(performance.now() - startTime)
      setTestResult({
        success: false,
        error: err.message,
        duration,
      })
    } finally {
      setIsTesting(false)
    }
  }

  return (
    <div className="space-y-6 animate-fadeIn max-w-4xl mx-auto">
      {/* Editorial Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Settings className="w-5 h-5 text-amber-700" />
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Backend Endpoint & Runtime Settings
          </h1>
        </div>
        <p className="text-sm text-slate-600 font-sans leading-relaxed">
          Configure the target Flask REST API server URL. All client requests (text analysis, file uploads, and corpus searches)
          target this base URL. Changes are immediately applied and persisted in browser storage.
        </p>
      </div>

      {/* Main Settings Card */}
      <Card className="border-slate-200 bg-white shadow-xs">
        <form onSubmit={handleSave}>
          <CardHeader className="p-6 pb-4 border-b border-slate-100">
            <CardTitle className="flex items-center gap-2 text-base">
              <Server className="w-4 h-4 text-slate-700" />
              <span>Target Flask API Base URL</span>
            </CardTitle>
            <CardDescription className="text-xs">
              Enter the URL of your local or deployed Flask service (e.g. <code className="font-mono text-slate-700">http://127.0.0.1:5000</code> or <code className="font-mono text-slate-700">https://legalsense-api.onrender.com</code>).
            </CardDescription>
          </CardHeader>

          <CardContent className="p-6 space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                API Base URL
              </label>
              <div className="flex gap-2">
                <Input
                  value={urlInput}
                  onChange={e => setUrlInput(e.target.value)}
                  placeholder="http://127.0.0.1:5000"
                  className="font-mono text-sm"
                />
                <Button type="submit" variant="default" className="bg-slate-900 text-white shrink-0">
                  Save & Apply
                </Button>
              </div>
            </div>

            {/* Quick Switch Presets */}
            <div className="flex items-center gap-2 flex-wrap text-xs pt-1">
              <span className="text-slate-500 font-medium">Quick Presets:</span>
              <button
                type="button"
                onClick={() => setUrlInput('http://127.0.0.1:5000')}
                className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-800 font-mono text-xs transition-colors border border-slate-200"
              >
                Local Flask (127.0.0.1:5000)
              </button>
              <button
                type="button"
                onClick={() => setUrlInput('http://localhost:5000')}
                className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-800 font-mono text-xs transition-colors border border-slate-200"
              >
                localhost:5000
              </button>
            </div>

            {saveSuccess && (
              <div className="flex items-center gap-2 text-xs text-emerald-800 bg-emerald-50 p-2.5 rounded border border-emerald-200">
                <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
                <span>Base URL saved and applied successfully.</span>
              </div>
            )}

            {/* Test Connection Button */}
            <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
              <Button
                type="button"
                variant="ghost"
                onClick={handleReset}
                className="text-xs text-slate-600 gap-1.5"
              >
                <RotateCcw className="w-3.5 h-3.5" /> Restore Default ({DEFAULT_API_BASE_URL})
              </Button>

              <Button
                type="button"
                variant="outline"
                isLoading={isTesting}
                onClick={handleTestConnection}
                className="gap-2 text-xs"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Test Connection (GET /health)</span>
              </Button>
            </div>

            {/* Test Result Display */}
            {testResult && (
              <div className="mt-3">
                {testResult.success ? (
                  <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-950 space-y-2">
                    <div className="flex items-center justify-between font-semibold">
                      <span className="flex items-center gap-1.5 text-emerald-800">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        Backend Verified Online & Responsive
                      </span>
                      <span className="font-mono text-emerald-700">{testResult.duration}ms latency</span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 pt-2 border-t border-emerald-200/60 font-mono text-[11px]">
                      <div>Service: <span className="font-bold">{testResult.data.service}</span></div>
                      <div>WSD Ready: <span className="font-bold">{testResult.data.wsd_ready ? 'Yes' : 'No'}</span></div>
                      <div>LLM Enabled: <span className="font-bold">{testResult.data.llm_enabled ? 'Yes' : 'No'}</span></div>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-950 space-y-1">
                    <div className="flex items-center gap-1.5 font-semibold text-rose-800">
                      <AlertCircle className="w-4 h-4 text-rose-600" />
                      Failed to Reach Backend ({testResult.duration}ms)
                    </div>
                    <p className="text-rose-700">{testResult.error}</p>
                    <p className="text-[11px] text-slate-600 mt-2">
                      Check that the Flask API is running locally via <code className="font-mono bg-white px-1 py-0.5 rounded border">python wsgi.py</code> or that CORS is allowed.
                    </p>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </form>
      </Card>

      {/* Security & Architecture Card */}
      <Card className="border-slate-200 bg-white shadow-xs">
        <CardHeader className="p-5 pb-3">
          <CardTitle className="flex items-center gap-2 text-sm">
            <Shield className="w-4 h-4 text-amber-700" />
            <span>Architecture & Security Boundaries</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-5 pt-0 text-xs text-slate-600 space-y-2 leading-relaxed">
          <p>
            • <strong>Zero Secret Exposure:</strong> The frontend client operates exclusively in the browser and never contains, stores, or transmits API keys or credentials.
            Optional Groq assistance is handled strictly on the server via server-side environment variables.
          </p>
          <p>
            • <strong>Ephemeral Document Uploads:</strong> Document bytes are transmitted via standard multipart form data and parsed in-memory by Flask. No documents are retained in localStorage or permanent disk storage.
          </p>
          <p>
            • <strong>Environment Variable Override:</strong> In production deployments, configure <code className="font-mono text-slate-800">VITE_API_BASE_URL</code> during the build to set the default remote endpoint.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
