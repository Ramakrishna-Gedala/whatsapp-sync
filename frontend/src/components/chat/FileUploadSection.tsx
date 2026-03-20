import { useRef, useState, useCallback } from 'react'
import { Upload, FileText, X, Loader2, CheckCircle2, AlertCircle, FolderOpen } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useFileUpload } from '@/hooks/useFileUpload'
import { useGroups } from '@/hooks/useGroups'
import type { FileUploadResult } from '@/types/upload'

const MAX_FILE_SIZE_MB = 10
const ACCEPTED_EXTENSIONS = ['.txt']

function validateFile(file: File): string | null {
  const ext = '.' + (file.name.split('.').pop()?.toLowerCase() ?? '')
  if (!ACCEPTED_EXTENSIONS.includes(ext)) {
    return `Unsupported type "${ext}". Accepted: ${ACCEPTED_EXTENSIONS.join(', ')}`
  }
  if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
    return `File too large. Maximum: ${MAX_FILE_SIZE_MB} MB`
  }
  return null
}

export default function FileUploadSection() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedGroupId, setSelectedGroupId] = useState('')
  const [clientError, setClientError] = useState<string | null>(null)

  const { uploadFile, isPending, lastResult, reset } = useFileUpload()
  const { groups, isLoading: groupsLoading } = useGroups()

  const handleFileSelect = useCallback(
    (file: File) => {
      const err = validateFile(file)
      if (err) {
        setClientError(err)
        setSelectedFile(null)
      } else {
        setClientError(null)
        setSelectedFile(file)
        reset()
      }
    },
    [reset]
  )

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFileSelect(file)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFileSelect(file)
  }

  const handleUpload = () => {
    if (!selectedFile || isPending) return
    uploadFile({ file: selectedFile, groupId: selectedGroupId || undefined })
  }

  const handleClear = () => {
    setSelectedFile(null)
    setClientError(null)
    reset()
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div className="card p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <FolderOpen size={16} className="text-amber-500" />
        <h3 className="font-semibold text-slate-800 dark:text-slate-100 text-sm">
          Upload WhatsApp Export File
        </h3>
        <span className="badge bg-slate-100 text-slate-500 dark:bg-od-border dark:text-od-fg text-xs">
          .txt
        </span>
      </div>

      {/* Group selector */}
      <div className="space-y-1">
        <label className="text-xs text-slate-500 dark:text-slate-400">
          Assign to group <span className="italic">(optional)</span>
        </label>
        <select
          value={selectedGroupId}
          onChange={(e) => setSelectedGroupId(e.target.value)}
          disabled={groupsLoading || isPending}
          className="w-full text-sm bg-white dark:bg-od-bg2 border border-slate-200 dark:border-od-border rounded-lg px-3 py-2 text-slate-700 dark:text-od-fg focus:outline-none focus:ring-2 focus:ring-amber-500 disabled:opacity-50"
        >
          <option value="">
            {groupsLoading ? 'Loading groups...' : '— No group (unassigned) —'}
          </option>
          {groups.map((g) => (
            <option key={g.group_id} value={g.group_id}>
              {g.name}
            </option>
          ))}
        </select>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !selectedFile && !isPending && inputRef.current?.click()}
        className={cn(
          'relative border-2 border-dashed rounded-xl p-6 text-center transition-all',
          dragOver
            ? 'border-amber-400 bg-amber-50 dark:bg-amber-950/20'
            : selectedFile
            ? 'border-emerald-400 bg-emerald-50 dark:bg-emerald-950/20'
            : 'border-slate-300 dark:border-od-border hover:border-amber-400 hover:bg-slate-50 dark:hover:bg-od-border/30 cursor-pointer'
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(',')}
          onChange={handleInputChange}
          className="hidden"
        />

        {selectedFile ? (
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              <FileText size={28} className="text-emerald-500 shrink-0" />
              <div className="text-left min-w-0">
                <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-slate-400">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
            </div>
            {!isPending && (
              <button
                onClick={(e) => { e.stopPropagation(); handleClear() }}
                className="p-1.5 rounded-md hover:bg-slate-200 dark:hover:bg-od-border shrink-0"
              >
                <X size={14} className="text-slate-500" />
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-2 py-2">
            <Upload size={28} className="mx-auto text-slate-400" />
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Drag & drop your WhatsApp export here, or{' '}
              <span className="text-amber-600 dark:text-amber-400 font-medium">browse</span>
            </p>
            <p className="text-xs text-slate-400">
              Supports Android &amp; iOS export format · Max {MAX_FILE_SIZE_MB} MB
            </p>
          </div>
        )}
      </div>

      {/* Client-side error */}
      {clientError && (
        <div className="flex items-center gap-2 text-red-600 dark:text-red-400 text-sm">
          <AlertCircle size={14} className="shrink-0" />
          {clientError}
        </div>
      )}

      {/* Upload button */}
      {selectedFile && !lastResult && (
        <button
          onClick={handleUpload}
          disabled={isPending}
          className="btn-primary w-full justify-center disabled:opacity-60"
        >
          {isPending ? (
            <><Loader2 size={16} className="animate-spin" /> Processing file…</>
          ) : (
            <><Upload size={16} /> Parse &amp; Create Events</>
          )}
        </button>
      )}

      {/* Processing status */}
      {isPending && (
        <p className="text-xs text-center text-slate-400 animate-pulse">
          Calling OpenAI for each message — this may take a moment…
        </p>
      )}

      {/* Result summary */}
      {lastResult && !isPending && (
        <UploadResultPanel result={lastResult} onReset={handleClear} />
      )}
    </div>
  )
}

function UploadResultPanel({
  result,
  onReset,
}: {
  result: FileUploadResult
  onReset: () => void
}) {
  return (
    <div className="rounded-xl border border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950/20 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CheckCircle2 size={16} className="text-emerald-600" />
          <span className="text-sm font-semibold text-emerald-700 dark:text-emerald-400">
            File processed
          </span>
        </div>
        <button
          onClick={onReset}
          className="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 hover:underline"
        >
          Upload another
        </button>
      </div>

      <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
        {result.file_name}
      </p>

      <div className="grid grid-cols-3 gap-2 text-center">
        <StatCell label="Found" value={result.total_messages_found} />
        <StatCell label="Created" value={result.events_created} color="text-emerald-600 dark:text-emerald-400" />
        <StatCell
          label="Failed"
          value={result.events_failed}
          color={result.events_failed > 0 ? 'text-red-500' : 'text-slate-400'}
        />
      </div>

      {result.parse_errors.length > 0 && (
        <p className="text-xs text-amber-600 dark:text-amber-400 leading-relaxed">
          ⚠️ {result.parse_errors.slice(0, 3).join(' · ')}
          {result.parse_errors.length > 3 && ` +${result.parse_errors.length - 3} more`}
        </p>
      )}
    </div>
  )
}

function StatCell({
  label,
  value,
  color = 'text-slate-700 dark:text-slate-300',
}: {
  label: string
  value: number
  color?: string
}) {
  return (
    <div className="bg-white dark:bg-od-bg rounded-lg py-2">
      <p className={cn('text-xl font-bold', color)}>{value}</p>
      <p className="text-xs text-slate-400">{label}</p>
    </div>
  )
}
