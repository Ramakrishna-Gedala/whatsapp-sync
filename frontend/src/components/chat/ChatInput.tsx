import { useRef, KeyboardEvent } from 'react'
import { Sparkles, Loader2, X } from 'lucide-react'
import { cn } from '@/lib/utils'

const MAX_CHARS = 2000

interface ChatInputProps {
  value: string
  onChange: (val: string) => void
  onSubmit: () => void
  isPending: boolean
}

export default function ChatInput({ value, onChange, onSubmit, isPending }: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey) && !isPending) {
      e.preventDefault()
      onSubmit()
    }
  }

  const remaining = MAX_CHARS - value.length
  const isOverLimit = remaining < 0

  return (
    <div className="space-y-3">
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isPending}
          rows={5}
          maxLength={MAX_CHARS}
          placeholder="Describe the tenant issue, maintenance request, lease inquiry...
&#10;&#10;Example: Tenant Mike in Unit 3A at Oak Village says the AC is broken. It's been 2 days and it's 95°F outside. Urgent!"
          className={cn(
            'w-full resize-none rounded-xl border bg-white dark:bg-od-bg2',
            'text-sm text-slate-800 dark:text-od-fg placeholder:text-slate-400 dark:placeholder:text-slate-600',
            'px-4 py-3 focus:outline-none focus:ring-2 focus:ring-amber-500',
            'disabled:opacity-60 disabled:cursor-not-allowed',
            isOverLimit
              ? 'border-red-400 dark:border-red-600'
              : 'border-slate-200 dark:border-od-border'
          )}
        />
        {value && !isPending && (
          <button
            onClick={() => onChange('')}
            className="absolute top-3 right-3 p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-od-border"
          >
            <X size={14} />
          </button>
        )}
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={onSubmit}
            disabled={isPending || !value.trim() || isOverLimit}
            className={cn(
              'btn-primary',
              (isPending || !value.trim() || isOverLimit) && 'opacity-50 cursor-not-allowed'
            )}
          >
            {isPending ? (
              <><Loader2 size={16} className="animate-spin" /> Parsing...</>
            ) : (
              <><Sparkles size={16} /> Parse & Create Event</>
            )}
          </button>
          <span className="text-xs text-slate-400 hidden sm:block">
            {isPending ? 'Analyzing with AI...' : 'Ctrl+Enter to submit'}
          </span>
        </div>
        <span
          className={cn(
            'text-xs font-mono',
            remaining < 100
              ? 'text-orange-500'
              : remaining < 0
              ? 'text-red-500'
              : 'text-slate-400'
          )}
        >
          {remaining}
        </span>
      </div>
    </div>
  )
}
