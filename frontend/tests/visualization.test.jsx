import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { LexicalNetwork3D } from '../src/components/visualizations/LexicalNetwork3D'

describe('LexicalNetwork3D Visualization', () => {
  const mockCandidates = [
    {
      synset_id: 'relief.n.03',
      definition: 'the disclosure of financial or other assistance granted by a court',
      score: 2.5,
      rank: 1,
      relations: {
        synonyms: ['remedy'],
        hypernyms: ['redress'],
        hyponyms: ['injunction'],
      },
    },
    {
      synset_id: 'relief.n.01',
      definition: 'the feeling that comes when something unpleasant stops',
      score: 0.5,
      rank: 2,
      relations: {
        synonyms: ['comfort'],
        hypernyms: [],
        hyponyms: [],
      },
    },
  ]

  it('renders LexicalNetwork3D header with term and controls', () => {
    render(<LexicalNetwork3D term="relief" candidateSenses={mockCandidates} />)
    expect(screen.getByText(/Lexical Network 3D:/i)).toBeInTheDocument()
    expect(screen.getByText(/"relief"/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /View 2D Table/i })).toBeInTheDocument()
  })

  it('toggles to accessible 2D table fallback on demand', () => {
    render(<LexicalNetwork3D term="relief" candidateSenses={mockCandidates} />)

    const toggleBtn = screen.getByRole('button', { name: /View 2D Table/i })
    fireEvent.click(toggleBtn)

    expect(screen.getByText(/Accessible Lexical Relation Table/i)).toBeInTheDocument()
    expect(screen.getByText(/relief\.n\.03/i)).toBeInTheDocument()
    expect(screen.getByText(/relief\.n\.01/i)).toBeInTheDocument()

    // Can toggle back to 3D WebGL
    const webglBtn = screen.getByRole('button', { name: /View 3D WebGL/i })
    fireEvent.click(webglBtn)
    expect(screen.queryByText(/Accessible Lexical Relation Table/i)).not.toBeInTheDocument()
  })

  it('handles empty candidate list gracefully', () => {
    render(<LexicalNetwork3D term="unknownword" candidateSenses={[]} />)
    expect(screen.getByText(/No candidate senses available/i)).toBeInTheDocument()
  })
})
