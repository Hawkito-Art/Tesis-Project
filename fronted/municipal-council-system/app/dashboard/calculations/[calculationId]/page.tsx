import { CalculationDetailClient } from '@/features/calculations/components/calculation-detail-client'

interface Props {
  params: Promise<{ calculationId: string }>
}

export default async function CalculationDetailPage({ params }: Props) {
  const { calculationId } = await params
  return <CalculationDetailClient calculationId={calculationId} />
}
