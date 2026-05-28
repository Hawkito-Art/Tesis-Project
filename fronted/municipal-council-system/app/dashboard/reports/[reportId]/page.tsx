import { ReportsDetailClient } from '@/features/reports/components/reports-detail-client'

export default async function ReportDetailPage({ params }: { params: Promise<{ reportId: string }> }) {
  const { reportId } = await params
  return <ReportsDetailClient reportId={Number(reportId)} />
}
