import { Sidebar } from '@/components/layout/sidebar'
import { DashboardShell } from '@/components/layout/dashboard-shell'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <DashboardShell>{children}</DashboardShell>
    </div>
  )
}
