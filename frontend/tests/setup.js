import '@testing-library/jest-dom'

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
})

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
import { vi } from 'vitest'

// Mock Three.js WebGLRenderer in jsdom environment
vi.mock('three', async (importOriginal) => {
  const actual = await importOriginal()
  class MockWebGLRenderer {
    constructor() {
      this.domElement = document.createElement('canvas')
    }
    setSize() {}
    setPixelRatio() {}
    render() {}
    dispose() {}
  }
  return {
    ...actual,
    WebGLRenderer: MockWebGLRenderer,
  }
})
