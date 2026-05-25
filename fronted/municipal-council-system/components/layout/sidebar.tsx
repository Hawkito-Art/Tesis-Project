'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import {
  Building2,
  LayoutDashboard,
  BookOpen,
  Wallet,
  Upload,
  BarChart3,
  Calculator,
  FileText,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface NavItem {
  label: string
  href?: string
  icon: React.ReactNode
  children?: { label: string; href: string }[]
}

const NAV_ITEMS: NavItem[] = [
  {
    label: 'Dashboard',
    href: '/dashboard',
    icon: <LayoutDashboard className="w-4 h-4" />,
  },
  {
    label: 'Catálogo',
    icon: <BookOpen className="w-4 h-4" />,
    children: [
      { label: 'Entidades', href: '/dashboard/catalog/entities' },
      { label: 'Períodos', href: '/dashboard/catalog/periods' },
      { label: 'Roles', href: '/dashboard/catalog/roles' },
      { label: 'Usuarios', href: '/dashboard/catalog/users' },
    ],
  },
  {
    label: 'Presupuesto',
    icon: <Wallet className="w-4 h-4" />,
    children: [
      { label: 'Presupuestos', href: '/dashboard/budget' },
    ],
  },
  {
    label: 'Importación',
    icon: <Upload className="w-4 h-4" />,
    children: [
      { label: 'Cargar archivo', href: '/dashboard/ingestion/upload' },
      { label: 'Trabajos', href: '/dashboard/ingestion/jobs' },
    ],
  },
  {
    label: 'Indicadores',
    icon: <BarChart3 className="w-4 h-4" />,
    children: [
      { label: 'Grupos', href: '/dashboard/indicators/groups' },
      { label: 'Indicadores', href: '/dashboard/indicators' },
      { label: 'Variables', href: '/dashboard/indicators/variables' },
      { label: 'Registros', href: '/dashboard/indicators/records' },
    ],
  },
  {
    label: 'Cálculos',
    icon: <Calculator className="w-4 h-4" />,
    children: [
      { label: 'Ejecutar', href: '/dashboard/calculations/run' },
      { label: 'Resultados', href: '/dashboard/calculations/results' },
    ],
  },
  {
    label: 'Reportes',
    icon: <FileText className="w-4 h-4" />,
    children: [
      { label: 'Reportes', href: '/dashboard/reports' },
      { label: 'Estadísticas', href: '/dashboard/reports/stats' },
      { label: 'Clasificaciones', href: '/dashboard/reports/classifications' },
    ],
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)
  const [openGroups, setOpenGroups] = useState<Set<string>>(
    () => new Set(NAV_ITEMS.filter((i) => i.children).map((i) => i.label)),
  )

  function toggleGroup(label: string) {
    setOpenGroups((prev) => {
      const next = new Set(prev)
      next.has(label) ? next.delete(label) : next.add(label)
      return next
    })
  }

  return (
    <aside
      className={cn(
        'flex flex-col bg-sidebar border-r border-sidebar-border transition-all duration-200',
        collapsed ? 'w-14' : 'w-60',
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-4 border-b border-sidebar-border min-h-[57px]">
        <div className="flex-shrink-0 w-7 h-7 rounded-lg bg-sidebar-primary flex items-center justify-center">
          <Building2 className="w-4 h-4 text-sidebar-primary-foreground" />
        </div>
        {!collapsed && (
          <span className="font-semibold text-sm text-sidebar-foreground leading-tight truncate">
            SIGCAM
          </span>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        {NAV_ITEMS.map((item) => {
          if (item.href) {
            const active = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-2.5 py-2 rounded-md text-sm transition-colors',
                  active
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium'
                    : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground',
                )}
              >
                {item.icon}
                {!collapsed && <span>{item.label}</span>}
              </Link>
            )
          }

          // Group with children
          const isOpen = openGroups.has(item.label)
          const isGroupActive = item.children?.some((c) => pathname.startsWith(c.href))

          return (
            <div key={item.label}>
              <button
                onClick={() => !collapsed && toggleGroup(item.label)}
                className={cn(
                  'w-full flex items-center gap-3 px-2.5 py-2 rounded-md text-sm transition-colors',
                  isGroupActive
                    ? 'text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground',
                )}
              >
                {item.icon}
                {!collapsed && (
                  <>
                    <span className="flex-1 text-left">{item.label}</span>
                    <ChevronDown
                      className={cn(
                        'w-3.5 h-3.5 transition-transform',
                        isOpen ? 'rotate-0' : '-rotate-90',
                      )}
                    />
                  </>
                )}
              </button>

              {!collapsed && isOpen && item.children && (
                <div className="ml-7 mt-0.5 space-y-0.5 border-l border-sidebar-border pl-2">
                  {item.children.map((child) => {
                    const active = pathname === child.href || pathname.startsWith(child.href + '/')
                    return (
                      <Link
                        key={child.href}
                        href={child.href}
                        className={cn(
                          'block px-2 py-1.5 rounded-md text-xs transition-colors',
                          active
                            ? 'text-sidebar-primary font-medium'
                            : 'text-sidebar-foreground/60 hover:text-sidebar-accent-foreground',
                        )}
                      >
                        {child.label}
                      </Link>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </nav>

      {/* Collapse toggle */}
      <div className="px-2 py-3 border-t border-sidebar-border">
        <button
          onClick={() => setCollapsed((v) => !v)}
          className="w-full flex items-center justify-center gap-2 px-2.5 py-2 rounded-md text-sidebar-foreground/60 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground transition-colors text-xs"
          aria-label={collapsed ? 'Expandir menú' : 'Colapsar menú'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : (
            <>
              <ChevronLeft className="w-4 h-4" />
              <span>Colapsar</span>
            </>
          )}
        </button>
      </div>
    </aside>
  )
}
