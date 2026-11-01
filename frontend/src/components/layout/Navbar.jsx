import React from 'react'
import { NavLink, Link } from 'react-router-dom'
import { Scale, BookOpen, FileText, Search, Settings, Compass } from 'lucide-react'
import { BackendStatusPill } from './BackendStatusPill'
import { cn } from '../../lib/utils/cn'

export function Navbar() {
  const navItems = [
    { to: '/', label: 'Overview', icon: Compass },
    { to: '/analyze', label: 'Text Analysis', icon: BookOpen },
    { to: '/documents', label: 'Document Analysis', icon: FileText },
    { to: '/search', label: 'Corpus Search', icon: Search },
    { to: '/settings', label: 'Settings', icon: Settings },
  ]

  return (
    <header className="sticky top-0 z-40 w-full bg-[#0f172a] text-slate-100 border-b border-slate-800 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Product Descriptor */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-600 to-amber-700 flex items-center justify-center text-white shadow-sm ring-1 ring-amber-400/30 group-hover:ring-amber-400 transition-all">
              <Scale className="w-5 h-5 text-amber-100" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-serif text-lg font-bold tracking-tight text-white">LegalSense</span>
                <span className="text-[10px] font-semibold tracking-wider uppercase px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  WSD AI
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block tracking-normal">
                Context-Aware Legal Document & Lexical Semantics Analysis
              </p>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            {navItems.map(item => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-2 px-3 py-2 rounded-md text-xs lg:text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-slate-800 text-amber-300 shadow-inner'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    )
                  }
                >
                  <Icon className="w-4 h-4 text-amber-400/80" />
                  <span>{item.label}</span>
                </NavLink>
              )
            })}
          </nav>

          {/* Right Header Status Pill */}
          <div className="flex items-center gap-3">
            <BackendStatusPill />
          </div>
        </div>
      </div>

      {/* Mobile Nav Bar */}
      <div className="md:hidden border-t border-slate-800 bg-slate-900/90 px-4 py-2 flex items-center justify-around overflow-x-auto">
        {navItems.map(item => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                cn(
                  'flex flex-col items-center gap-1 px-2 py-1 rounded text-[11px] font-medium transition-colors whitespace-nowrap',
                  isActive ? 'text-amber-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
                )
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </div>
    </header>
  )
}
