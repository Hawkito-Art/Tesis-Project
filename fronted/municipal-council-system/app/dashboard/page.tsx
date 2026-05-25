import {
  Building2,
  Wallet,
  BarChart3,
  FileText,
  Upload,
  Calculator,
  ArrowRight,
} from 'lucide-react'
import Link from 'next/link'

const modules = [
  {
    title: 'Catálogo',
    description: 'Gestione entidades, períodos, roles y usuarios del sistema.',
    href: '/dashboard/catalog/entities',
    icon: <Building2 className="w-5 h-5" />,
    color: 'bg-blue-500/10 text-blue-600',
  },
  {
    title: 'Presupuesto',
    description: 'Consulte y administre presupuestos por entidad y período.',
    href: '/dashboard/budget',
    icon: <Wallet className="w-5 h-5" />,
    color: 'bg-emerald-500/10 text-emerald-600',
  },
  {
    title: 'Importación',
    description: 'Cargue archivos Excel y supervise trabajos de importación.',
    href: '/dashboard/ingestion/upload',
    icon: <Upload className="w-5 h-5" />,
    color: 'bg-amber-500/10 text-amber-600',
  },
  {
    title: 'Indicadores',
    description: 'Gestione grupos, indicadores, variables y registros.',
    href: '/dashboard/indicators',
    icon: <BarChart3 className="w-5 h-5" />,
    color: 'bg-violet-500/10 text-violet-600',
  },
  {
    title: 'Cálculos',
    description: 'Ejecute cálculos y consulte resultados exportables.',
    href: '/dashboard/calculations/run',
    icon: <Calculator className="w-5 h-5" />,
    color: 'bg-cyan-500/10 text-cyan-600',
  },
  {
    title: 'Reportes',
    description: 'Visualice reportes, estadísticas y clasificaciones.',
    href: '/dashboard/reports',
    icon: <FileText className="w-5 h-5" />,
    color: 'bg-rose-500/10 text-rose-600',
  },
]

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-foreground">Bienvenido</h2>
        <p className="text-muted-foreground text-sm mt-0.5">
          Seleccione un módulo para comenzar a trabajar.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {modules.map((mod) => (
          <Link
            key={mod.href}
            href={mod.href}
            className="group bg-card border border-border rounded-xl p-5 hover:border-primary/40 hover:shadow-sm transition-all"
          >
            <div className="flex items-start justify-between">
              <div className={`p-2.5 rounded-lg ${mod.color}`}>{mod.icon}</div>
              <ArrowRight className="w-4 h-4 text-muted-foreground/40 group-hover:text-primary group-hover:translate-x-0.5 transition-all" />
            </div>
            <h3 className="mt-3 font-semibold text-sm text-foreground">{mod.title}</h3>
            <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{mod.description}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
