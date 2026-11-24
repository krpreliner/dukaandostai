export interface BusinessOverview {
  store_name: string;
  store_location: string;
  store_owner: string;
  initial_net_income: number;
  target_net_income: number;
  current_net_income: number;
  simulated_net_income: number;
  simulated_improvement: number;
  percentage_achieved: number;
  income_gap: number;
  revenue: number;
  cogs: number;
  gross_profit: number;
  operating_expenses: number;
  total_customers: number;
  total_products: number;
  worker_status: string;
  active_execution_id?: string | null;
}

export interface Customer {
  customer_id: string;
  customer_name: string;
  area: string;
  age_group: string;
  total_orders: number;
  total_spending: number;
  last_purchase_date: string;
  preferred_category: string;
  average_order_value: number;
  segment: 'Active' | 'Inactive' | 'Frequent' | 'High Value' | 'At Risk';
}

export interface Product {
  product_id: string;
  product_name: string;
  category: string;
  cost_price: number;
  selling_price: number;
  current_stock: number;
  minimum_stock: number;
  monthly_units_sold: number;
  expiry_date: string;
  supplier_name: string;
  profit_margin: number;
  status: 'HEALTHY' | 'LOW STOCK' | 'SLOW MOVING' | 'EXPIRING SOON' | 'REORDER REQUIRED' | 'NEGATIVE MARGIN';
}

export interface AgentInfo {
  id: string;
  name: string;
  role: string;
  status: 'IDLE' | 'READY' | 'ACTIVE' | 'WAITING' | 'BLOCKED';
  responsibility: string;
  last_action: string;
}

export interface TaskRecord {
  task_id: string;
  task_name: string;
  assigned_agent: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  expected_impact: number;
  simulated_impact: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  approval_required: boolean;
  status: 'PENDING' | 'IN_PROGRESS' | 'WAITING_APPROVAL' | 'COMPLETED' | 'FAILED' | 'REJECTED';
  execution_result?: string;
  failure_reason?: string;
}

export interface PendingApproval {
  id: number;
  execution_id: string;
  task_id: string;
  action_description: string;
  requesting_agent: string;
  original_price: number;
  proposed_price: number;
  gross_margin_pct: number;
  expected_impact: number;
  justification: string;
  risk_assessment: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  created_at?: string;
}

export interface FailureRecord {
  id: number;
  execution_id: string;
  task_id: string;
  agent_name: string;
  error_description: string;
  root_cause: string;
  recovery_status: string;
  retry_count: number;
  timestamp?: string;
}

export interface AuditLog {
  id: number;
  execution_id?: string;
  event_type: string;
  agent_name: string;
  details: string;
  timestamp?: string;
}

export interface ExecutionRecord {
  execution_id: string;
  thread_id: string;
  status: string;
  initial_income: number;
  target_income: number;
  current_income: number;
  simulated_income: number;
  variance: number;
  current_agent: string;
  current_task: string;
  created_at?: string;
  completed_at?: string;
}

export interface EvaluationMetrics {
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  completion_rate_pct: number;
  failure_rate_pct: number;
  total_approval_requests: number;
  approved_count: number;
  rejected_count: number;
  approval_rate_pct: number;
  total_failures: number;
  recovery_rate_pct: number;
  total_expected_profit: number;
  total_simulated_profit: number;
  profit_variance: number;
  initial_net_income: number;
  target_net_income: number;
  simulated_net_income: number;
  income_improvement: number;
  target_achievement_pct: number;
  duplicate_execution_prevented: boolean;
}
