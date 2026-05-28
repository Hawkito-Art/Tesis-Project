import { IndicatorDetailClient } from '@/features/indicators/components/indicator-detail-client'

interface Props {
  params: Promise<{ indicatorId: string }>
}

export default async function IndicatorDetailPage({ params }: Props) {
  const { indicatorId } = await params
  return <IndicatorDetailClient indicatorId={indicatorId} />
}
