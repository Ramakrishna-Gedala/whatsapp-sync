import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, Sparkles, Info } from 'lucide-react'
import ChatInput from '@/components/chat/ChatInput'
import ChatEventPreview from '@/components/chat/ChatEventPreview'
import FileUploadSection from '@/components/chat/FileUploadSection'
import { useChat } from '@/hooks/useChat'

const EXAMPLES = [
  "Tenant Mike in Unit 3A at Oak Village says the AC is broken. It's been 2 days and it's 95°F outside. Need urgent attention!",
  "John from Apt 7C hasn't paid rent for March. He owes $1,450 at Maple Heights.",
  "Hi, I'm interested in renting a 2-bedroom unit at Sunrise Commons. Is there availability?",
  "There's a loud party happening in Unit 12B at Cedar Grove at 2 AM. Multiple neighbors are complaining.",
]

export default function ChatPage() {
  const [text, setText] = useState('')
  const { submitMessage, isPending, lastCreatedEvent } = useChat()

  const handleSubmit = () => {
    if (!text.trim() || isPending) return
    submitMessage(text)
    setText('')
  }

  const loadExample = (example: string) => {
    setText(example)
  }

  return (
    <div className="min-h-full bg-lt-bg dark:bg-od-bg">
      <div className="max-w-2xl mx-auto px-6 py-8 space-y-6">
        {/* Header */}
        <div className="flex items-center gap-3">
          <Link
            to="/events"
            className="btn-ghost text-sm text-slate-500 dark:text-slate-400 -ml-2"
          >
            <ArrowLeft size={16} />
            Back to Events
          </Link>
        </div>

        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-1">
            Chat → Event Parser
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Enter any property management message in English. AI will parse it into a structured event.
          </p>
        </div>

        {/* Examples */}
        <div className="card p-4 space-y-2">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
            <Info size={12} />
            Try an example
          </div>
          <div className="flex flex-wrap gap-2">
            {EXAMPLES.map((ex, i) => (
              <button
                key={i}
                onClick={() => loadExample(ex)}
                className="text-xs px-3 py-1.5 rounded-full border border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-900/20 transition-colors"
              >
                Example {i + 1}
              </button>
            ))}
          </div>
        </div>

        {/* Input area */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles size={16} className="text-amber-500" />
            <h3 className="font-semibold text-slate-800 dark:text-slate-100 text-sm">
              Message Input
            </h3>
          </div>
          <ChatInput
            value={text}
            onChange={setText}
            onSubmit={handleSubmit}
            isPending={isPending}
          />
        </div>

        {/* AI processing indicator */}
        {isPending && (
          <div className="card p-4 animate-pulse">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-amber-100 dark:bg-amber-900/30 rounded-full flex items-center justify-center">
                <Sparkles size={16} className="text-amber-500 animate-spin" />
              </div>
              <div className="space-y-1.5 flex-1">
                <div className="h-3 bg-slate-200 dark:bg-od-border rounded w-3/4" />
                <div className="h-3 bg-slate-100 dark:bg-od-bg2 rounded w-1/2" />
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-2 ml-11">
              AI is analyzing your message and extracting structured data...
            </p>
          </div>
        )}

        {/* Event preview */}
        {lastCreatedEvent && !isPending && (
          <div>
            <h3 className="text-sm font-semibold text-slate-600 dark:text-slate-400 mb-3 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 inline-block" />
              Last Created Event
            </h3>
            <ChatEventPreview event={lastCreatedEvent} />
          </div>
        )}

        {/* Divider */}
        <div className="relative flex items-center py-2">
          <div className="flex-grow border-t border-slate-200 dark:border-od-border" />
          <span className="px-3 text-xs text-slate-400 uppercase tracking-wider">or</span>
          <div className="flex-grow border-t border-slate-200 dark:border-od-border" />
        </div>

        {/* File upload */}
        <FileUploadSection />
      </div>
    </div>
  )
}
