export interface BusinessOverview {
  store_id?: string;
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

// Multi-tenant & Auth Types
export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
}

export interface StoreWorkspace {
  store_id: string;
  name: string;
  location: string;
  owner_name: string;
  role: 'OWNER' | 'MANAGER' | 'STAFF' | 'VIEWER';
  initial_net_income: number;
  target_net_income: number;
  current_net_income: number;
  simulated_net_income: number;
}

export interface StoreMember {
  user_id: number;
  email: string;
  full_name: string;
  role: 'OWNER' | 'MANAGER' | 'STAFF' | 'VIEWER';
  created_at?: string;
}

// AI Provider Types
export interface AIProvider {
  provider_name: string;
  supported_models: string[];
  selected_model: string;
  is_enabled: boolean;
  is_primary: boolean;
  is_fallback: boolean;
  status: 'CONNECTED AND VERIFIED' | 'NOT CONFIGURED' | 'CONNECTION FAILED';
  latency_ms: number;
  message: string;
}

export interface AIUsageStats {
  total_requests: number;
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  total_cost_usd: number;
  avg_latency_ms: number;
}

// Integration Types
export interface IntegrationItem {
  id: number;
  integration_type: string;
  is_enabled: boolean;
  status: 'CONNECTED AND VERIFIED' | 'NOT CONFIGURED' | 'CONNECTION FAILED';
  config: string;
  updated_at?: string;
}

// System Health Types
export interface SystemHealth {
  status: 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY';
  app_env: string;
  uptime_seconds: number;
  database_connected: boolean;
  database_latency_ms: number;
  process_memory_mb: number;
  process_cpu_pct: number;
  ai_mode: string;
  zero_paid_cost_enforced: boolean;
  timestamp: string;
}

// AI Daily Business Briefing Types
export interface DailyBriefingData {
  id?: number;
  briefing_date: string;
  greeting: string;
  summary_text: string;
  summary_text_hi?: string;
  summary_text_en?: string;
  audio_script: string;
  audio_script_hi?: string;
  audio_script_en?: string;
  today_sales: number;
  yesterday_sales: number;
  sales_growth_pct: number;
  low_stock_count: number;
  inactive_customer_count: number;
  growth_opportunities: Array<{
    title: string;
    impact_inr: number;
    action: string;
  }>;
  pending_approvals_count?: number;
  created_at: string;
}

// Conversational AI Assistant Types
export interface ChatMessageData {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  tools_used?: string[];
  evidence?: Record<string, any>;
  suggested_actions?: string[];
  provider?: string;
  model?: string;
  latency_ms?: number;
  timestamp?: string;
}
