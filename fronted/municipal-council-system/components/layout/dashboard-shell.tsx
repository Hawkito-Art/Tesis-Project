'use client'

import { usePathname } from 'next/navigation'
import { Header } from './header'

const ROUTE_TITLES: Record<string, string> = {
  '/dashboard': 'Panel principal',
  '/dashboard/catalog/entities': 'Entidades',
  '/dashboard/catalog/periods': 'Períodos',
  '/dashboard/catalog/roles': 'Roles',
  '/dashboard/catalog/users': 'Usuarios',
  '/dashboard/budget': 'Presupuestos',
  '/dashboard/ingestion/upload': 'Cargar archivo',
  '/dashboard/ingestion/jobs': 'Trabajos de importación',
  '/dashboard/indicators/groups': 'Grupos de indicadores',
  '/dashboard/indicators': 'Indicadores',
  '/dashboard/indicators/variables': 'Variables',
  '/dashboard/indicators/records': 'Registros de indicadores',
  '/dashboard/calculations/run': 'Ejecutar cálculo',
  '/dashboard/calculations/results': 'Resultados de cálculos',
  '/dashboard/reports': 'Reportes',
  '/dashboard/reports/stats': 'Estadísticas',
  '/dashboard/reports/classifications': 'Clasificaciones',
}

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  // Find title: exact match or longest prefix match
  const title =
    ROUTE_TITLES[pathname] ??
    Object.entries(ROUTE_TITLES)
      .filter(([k]) => pathname.startsWith(k + '/'))
      .sort((a, b) => b[0].length - a[0].length)[0]?.[1] ??
    'SIGCAM'

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      <Header title={title} />
      <main className="flex-1 overflow-y-auto p-6">{children}</main>
    </div>
  )
}
