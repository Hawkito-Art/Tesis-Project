import { BudgetDetailClient } from '@/features/budget/components/budget-detail-client'

export default async function BudgetDetailPage({ params }: { params: Promise<{ budgetId: string }> }) {
  const { budgetId } = await params
  return <BudgetDetailClient budgetId={Number(budgetId)} />
}
