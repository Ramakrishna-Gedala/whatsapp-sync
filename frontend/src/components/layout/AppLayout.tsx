import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import { Toaster } from 'sonner'

export default function AppLayout() {
  return (
    <div className="flex h-screen bg-lt-bg dark:bg-od-bg overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
      <Toaster position="top-right" richColors closeButton />
    </div>
  )
}
