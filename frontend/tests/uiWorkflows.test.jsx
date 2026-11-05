import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { OverviewPage } from '../src/pages/OverviewPage'
import { TextAnalysisPage } from '../src/pages/TextAnalysisPage'
import { DocumentAnalysisPage } from '../src/pages/DocumentAnalysisPage'
import { CorpusSearchPage } from '../src/pages/CorpusSearchPage'
import { SettingsPage } from '../src/pages/SettingsPage'
import { WsdResultCard } from '../src/components/analysis/WsdResultCard'

function renderWithProviders(ui) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{ui}</BrowserRouter>
    </QueryClientProvider>
  )
}

describe('UI Workflows & Pages', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  it('renders OverviewPage with editorial heading and verified benchmark metrics', () => {
    renderWithProviders(<OverviewPage />)
    expect(screen.getByText(/Context-Aware Legal Document Analysis/i)).toBeInTheDocument()
    expect(screen.getByText(/80.0%/i)).toBeInTheDocument()
    expect(screen.getByText(/Interactive Text Analysis/i)).toBeInTheDocument()
    expect(screen.getByText(/Document Intelligence/i)).toBeInTheDocument()
    expect(screen.getByText(/Corpus Passage Search/i)).toBeInTheDocument()
  })

  it('renders TextAnalysisPage and populates text when clicking a sample clause button', () => {
    renderWithProviders(<TextAnalysisPage />)
    expect(screen.getByText(/Word Sense Disambiguation Workspace/i)).toBeInTheDocument()

    const sampleBtn = screen.getByRole('button', { name: /Contract Consideration/i })
    expect(sampleBtn).toBeInTheDocument()

    fireEvent.click(sampleBtn)

    const textarea = screen.getByPlaceholderText(/Enter or paste a legal clause/i)
    expect(textarea.value).toContain('consideration')
  })

  it('renders DocumentAnalysisPage with dropzone and format hints', () => {
    renderWithProviders(<DocumentAnalysisPage />)
    expect(screen.getByText(/Document Intelligence & Passage Analysis/i)).toBeInTheDocument()
    expect(screen.getByText(/Drag & drop your legal document here/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Commercial Services Agreement \(\.txt\)/i })).toBeInTheDocument()
  })

  it('renders CorpusSearchPage with query input and example query buttons', () => {
    renderWithProviders(<CorpusSearchPage />)
    expect(screen.getByText(/Corpus Passage Retrieval/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Search bundled legal corpus/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Search/i })).toBeInTheDocument()
  })

  it('renders SettingsPage and allows updating API base URL', () => {
    renderWithProviders(<SettingsPage />)
    expect(screen.getByText(/Target Flask API Base URL/i)).toBeInTheDocument()

    const input = screen.getByPlaceholderText('http://127.0.0.1:5000')
    fireEvent.change(input, { target: { value: 'http://custom-host:8080' } })

    const saveBtn = screen.getByRole('button', { name: /Save & Apply/i })
    fireEvent.click(saveBtn)

    expect(localStorage.getItem('legalsense_api_base_url')).toBe('http://custom-host:8080')
  })

  it('renders WsdResultCard cleanly distinguishing WordNet candidates and curated legal glossary', () => {
    const mockResult = {
      term: 'party',
      pos: 'NOUN',
      lemma: 'party',
      sentence: 'Both parties signed the contract in court.',
      selection_method: 'extended_lesk',
      uncertain: false,
      selected_sense: {
        synset_id: 'party.n.05',
        definition: 'a person involved in legal proceedings',
        score: 3.5,
        rank: 1,
      },
      candidate_senses: [
        {
          synset_id: 'party.n.05',
          definition: 'a person involved in legal proceedings',
          score: 3.5,
          rank: 1,
          pos: 'NOUN',
          relations: {
            synonyms: ['litigant'],
            hypernyms: ['person'],
            hyponyms: ['plaintiff', 'defendant'],
          },
        },
        {
          synset_id: 'party.n.01',
          definition: 'an occasion on which people gather to talk and have fun',
          score: 0.2,
          rank: 2,
          pos: 'NOUN',
          relations: { synonyms: [], hypernyms: [], hyponyms: [] },
        },
      ],
      legal_glossary_entry: {
        term: 'party',
        definition: 'A person, group, or entity involved in a legal proceeding, contract, or transaction.',
        source: "Black's Law Dictionary",
        jurisdiction: 'Common law (general)',
        usage_example: 'Both parties to the agreement must sign the contract.',
      },
      evidence: [
        {
          candidate_synset_id: 'party.n.05',
          overlap_source: 'gloss',
          overlap_tokens: ['court', 'contract'],
          contribution: 2.0,
        },
      ],
    }

    renderWithProviders(<WsdResultCard result={mockResult} />)

    // Check term title and badges
    expect(screen.getByText(/"party"/i)).toBeInTheDocument()
    expect(screen.getByText(/High Confidence/i)).toBeInTheDocument()

    // Check curated legal glossary section
    expect(screen.getByText(/Curated Legal Glossary/i)).toBeInTheDocument()
    expect(screen.getByText(/A person, group, or entity involved in a legal proceeding/i)).toBeInTheDocument()

    // Check WordNet candidate list
    expect(screen.getByText(/party\.n\.05/i)).toBeInTheDocument()
    expect(screen.getByText(/a person involved in legal proceedings/i)).toBeInTheDocument()

    // Check Extended Lesk evidence section trigger
    expect(screen.getByText(/Extended Lesk Overlap Evidence/i)).toBeInTheDocument()
  })
})
