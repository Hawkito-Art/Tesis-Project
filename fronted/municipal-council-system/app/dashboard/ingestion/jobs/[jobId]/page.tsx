import { JobDetailClient } from '@/features/ingestion/components/job-detail-client'

interface Props {
  params: Promise<{ jobId: string }>
}

export default async function JobDetailPage({ params }: Props) {
  const { jobId } = await params
  return <JobDetailClient jobId={jobId} />
}
