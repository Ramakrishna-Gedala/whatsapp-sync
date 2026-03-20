import { NavLink } from 'react-router-dom'
import { LayoutDashboard, MessageSquarePlus, Moon, Sun } from 'lucide-react'
import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'

export default function Sidebar() {
  const [dark, setDark] = useState(() =>
    document.documentElement.classList.contains('dark')
  )

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [dark])

  const navItem = ({ isActive }: { isActive: boolean }) =>
    cn(
      'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all',
      isActive
        ? 'bg-amber-500/20 text-amber-400 dark:text-amber-400'
        : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
    )

  return (
    <aside className="w-56 flex flex-col bg-lt-sidebar text-slate-300 shrink-0">
      {/* Logo */}
      <div className="px-5 py-6 border-b border-white/10">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🏠</span>
          <div>
            <h1 className="font-bold text-white leading-tight">PropSync</h1>
            <p className="text-xs text-slate-500">WhatsApp → Events</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <NavLink to="/events" className={navItem}>
          <LayoutDashboard size={18} />
          Events Dashboard
        </NavLink>
        <NavLink to="/chat" className={navItem}>
          <MessageSquarePlus size={18} />
          Chat Parser
        </NavLink>
      </nav>

      {/* Theme toggle */}
      <div className="px-3 py-4 border-t border-white/10">
        <button
          onClick={() => setDark(!dark)}
          className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-all"
        >
          {dark ? <Sun size={16} /> : <Moon size={16} />}
          {dark ? 'Light mode' : 'Dark mode'}
        </button>
      </div>
    </aside>
  )
}
