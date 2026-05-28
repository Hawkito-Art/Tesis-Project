# Stats Charts — Especificación

## Resumen

Agregar dos gráficos con **Recharts** en la página de Estadísticas (`/dashboard/reports/stats`) para reemplazar las tablas actuales de "Registros por fuente" y "Promedio por indicador".

## Stack

- `recharts@2.15.0` — ya instalado en `fronted/municipal-council-system/`
- Componentes `'use client'` — el stats-client ya lo es
- Colores: usar tokens de Tailwind (`hsl(var(--primary))`, `hsl(var(--chart-1))`...) y/o paleta fija por fuente

---

## Gráfico 1: Donut — Distribución por fuente

| Campo | Valor |
|---|---|
| Componente | `SourcesDonutChart` |
| Datos | `data?.records_by_source` (`Record<string, number>`) |
| Tipo | `PieChart` con `innerRadius` (donut) |
| Ejes | No aplica (circular) |
| Tooltip | Cantidad + porcentaje del total |
| Leyenda | Abajo del gráfico, con círculo de color por fuente |
| Vacío | Mostrar "Sin datos." igual que hoy |
| Layout | Columna izquierda del grid 2-columnas, reemplaza el Card con la tabla |

**Paleta de colores fija por fuente:**

| source | Label (ES) | Color |
|---|---|---|
| `imported` | Importado | `var(--color-chart-1)` — azul |
| `calculated` | Calculado | `var(--color-chart-3)` — verde |
| `manual` | Manual | `var(--color-chart-5)` — naranja |

Si aparecen fuentes no mapeadas, asignar color del array rotativo `hsl(var(--chart-N))`.

**Comportamiento:**
- Al hacer hover en un segmento, tooltip con: nombre de fuente, cantidad, porcentaje
- No requiere animación compleja — usar `isAnimationActive={true}` (default de Recharts)

---

## Gráfico 2: Barra horizontal — Top 10 promedio por indicador

| Campo | Valor |
|---|---|
| Componente | `AveragesBarChart` |
| Datos | `data?.average_value_by_indicator` (`Record<string, number>`) |
| Tipo | `BarChart` con `layout="vertical"` |
| Ejes | Eje Y: código de indicador, Eje X: valor promedio |
| Tooltip | Código + valor con 4 decimales |
| Leyenda | No aplica (serie única) |
| Vacío | Mostrar "Sin datos." |
| Límite | Mostrar solo **top 10** por valor descendente |
| Layout | Columna derecha del grid 2-columnas, reemplaza el Card con la tabla |

**Comportamiento:**
- Barras con color `hsl(var(--primary))`
- Eje Y con labels truncados si son muy largos (usar `tickFormatter`)
- Al hacer hover en una barra, tooltip con código y valor exacto

---

## Layout resultante

```
┌─────────────────────────────────────────────────┐
│  [card]         [card]         [card]    [card]  │
├────────────────────────┬────────────────────────┤
│  Donut: Fuentes        │  Barras: Prom. x Indic │
│                        │  (horizontal, top 10)  │
└────────────────────────┴────────────────────────┘
```

Mismo grid `grid-cols-1 md:grid-cols-2 gap-4` que usa hoy.

---

## Estados

| Estado | Comportamiento |
|---|---|
| Loading | Mostrar `<Skeleton className="h-64" />` en lugar de cada gráfico |
| Vacío (0 fuentes / 0 promedios) | Mostrar `<p className="text-sm text-muted-foreground">Sin datos.</p>` |
| Con datos | Renderizar Recharts |
| Error | El `useQuery` ya maneja error vía TanStack Query, no tocar |

---

## Archivos a modificar

| Archivo | Cambio |
|---|---|
| `features/reports/components/stats-client.tsx` | Agregar imports de Recharts + componentes `SourcesDonutChart` y `AveragesBarChart`. Reemplazar los dos Cards de tabla por los nuevos gráficos. Mantener el structure de grid existente. |

No se toca backend, tipos ni API — `StatsPayload` ya tiene todo lo necesario.

## Criterios de aceptación

1. Stats page muestra donut de fuentes + barras de promedios
2. Cada gráfico tiene tooltip con valores exactos
3. Estado vacío funciona (0 fuentes / 0 promedios)
4. Loading state muestra skeletons
5. Gráficos son responsive (fill container, grid columns)
6. Colores distinguibles por fuente (donut) y consistentes con shadcn (barras)
7. `records_by_indicator` NO se modifica ni se agrega — queda fuera de scope
8. No se rompe nada si el payload llega con datos faltantes

## No-alcance

- Filtros interactivos en gráficos (click para filtrar)
- Animaciones complejas
- Descarga de gráficos como imagen
- Gráficos en la página de clasificaciones
