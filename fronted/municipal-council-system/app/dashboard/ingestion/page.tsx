import { redirect } from 'next/navigation'

export default function IngestionIndexPage() {
  redirect('/dashboard/ingestion/upload')
}
