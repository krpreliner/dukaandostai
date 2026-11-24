import axios from 'axios';
import {
  BusinessOverview,
  Customer,
  Product,
  AgentInfo,
  PendingApproval,
  FailureRecord,
  AuditLog,
  ExecutionRecord,
  EvaluationMetrics,
  User,
  StoreWorkspace,
  StoreMember,
  AIProvider,
  AIUsageStats,
  IntegrationItem,
  SystemHealth
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach Token and X-Store-Id automatically to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('dukaandost_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  const storeId = localStorage.getItem('dukaandost_store_id') || 'STORE_001';
  config.headers['X-Store-Id'] = storeId;
  return config;
});

// ----------------------------------------------------
// Authentication & Multi-Tenant Workspaces
// ----------------------------------------------------
export const loginUser = async (email: string, password: string) => {
  const res = await api.post('/auth/login', { email, password });
  if (res.data.access_token) {
    localStorage.setItem('dukaandost_token', res.data.access_token);
    if (res.data.stores && res.data.stores.length > 0) {
      localStorage.setItem('dukaandost_store_id', res.data.stores[0].store_id);
    }
  }
  return res.data;
};

export const registerUser = async (data: { email: string; password: string; full_name: string; store_name?: string; store_location?: string }) => {
  const res = await api.post('/auth/register', data);
  if (res.data.access_token) {
    localStorage.setItem('dukaandost_token', res.data.access_token);
    if (res.data.stores && res.data.stores.length > 0) {
      localStorage.setItem('dukaandost_store_id', res.data.stores[0].store_id);
    }
  }
  return res.data;
};

export const getCurrentProfile = async (): Promise<{ user: User; stores: StoreWorkspace[] }> => {
  const res = await api.get('/auth/me');
  return res.data;
};

export const getMyStores = async (): Promise<StoreWorkspace[]> => {
  const res = await api.get('/auth/stores');
  return res.data;
};

export const createNewStore = async (name: string, location?: string) => {
  const res = await api.post('/auth/stores', { name, location });
  return res.data;
};

export const getStoreMembers = async (storeId: string): Promise<StoreMember[]> => {
  const res = await api.get(`/auth/stores/${storeId}/members`);
  return res.data;
};

export const addStoreMember = async (storeId: string, email: string, role: string) => {
  const res = await api.post(`/auth/stores/${storeId}/members`, { email, role });
  return res.data;
};

export const logoutUser = async () => {
  localStorage.removeItem('dukaandost_token');
  try {
    await api.post('/auth/logout');
  } catch (e) {
    // ignore
  }
};

// ----------------------------------------------------
// Business Analytics & Products
// ----------------------------------------------------
export const getOverview = async (): Promise<BusinessOverview> => {
  const res = await api.get('/business/overview');
  return res.data;
};

export const getAnalytics = async () => {
  const res = await api.get('/business/analytics');
  return res.data;
};

export const getCustomers = async (segment?: string): Promise<Customer[]> => {
  const res = await api.get('/customers', { params: { segment } });
  return res.data;
};

export const getProducts = async (category?: string, status?: string): Promise<Product[]> => {
  const res = await api.get('/products', { params: { category, status } });
  return res.data;
};

export const updateProductPrice = async (productId: string, costPrice?: number, sellingPrice?: number) => {
  const res = await api.put(`/products/${productId}`, { cost_price: costPrice, selling_price: sellingPrice });
  return res.data;
};

export const getAgentsStatus = async (): Promise<{ worker_status: string; agents: AgentInfo[] }> => {
  const res = await api.get('/agents/status');
  return res.data;
};

export const startWorker = async (targetIncome?: number) => {
  const res = await api.post('/worker/start', { target_income: targetIncome });
  return res.data;
};

export const getWorkerStatus = async (executionId: string) => {
  const res = await api.get(`/worker/status/${executionId}`);
  return res.data;
};

export const getPendingApprovals = async (executionId?: string): Promise<PendingApproval[]> => {
  const res = await api.get('/approvals/pending', { params: { execution_id: executionId } });
  return res.data;
};

export const getApprovalHistory = async (executionId?: string): Promise<PendingApproval[]> => {
  const res = await api.get('/approvals/history', { params: { execution_id: executionId } });
  return res.data;
};

export const approveTask = async (taskId: string, executionId?: string) => {
  const res = await api.post(`/approvals/${taskId}/approve`, { execution_id: executionId });
  return res.data;
};

export const rejectTask = async (taskId: string, executionId?: string) => {
  const res = await api.post(`/approvals/${taskId}/reject`, { execution_id: executionId });
  return res.data;
};

export const getExecutions = async (): Promise<ExecutionRecord[]> => {
  const res = await api.get('/executions');
  return res.data;
};

export const getFailures = async (executionId?: string): Promise<FailureRecord[]> => {
  const res = await api.get('/failures', { params: { execution_id: executionId } });
  return res.data;
};

export const resolveFailure = async (failureId: number) => {
  const res = await api.post(`/failures/${failureId}/resolve`);
  return res.data;
};

export const resolveAllFailures = async () => {
  const res = await api.post('/failures/resolve-all');
  return res.data;
};

export const getAuditLogs = async (executionId?: string): Promise<AuditLog[]> => {
  const res = await api.get('/audit-logs', { params: { execution_id: executionId } });
  return res.data;
};

export const getEvaluation = async (executionId?: string): Promise<EvaluationMetrics> => {
  const res = await api.get('/evaluation', { params: { execution_id: executionId } });
  return res.data;
};

export const triggerDemoFailure = async () => {
  const res = await api.post('/demo/trigger-failure');
  return res.data;
};

export const resetDemoData = async () => {
  const res = await api.post('/demo/reset');
  return res.data;
};

// ----------------------------------------------------
// Real AI Providers & Usage Tracking
// ----------------------------------------------------
export const getAIProviders = async (): Promise<AIProvider[]> => {
  const res = await api.get('/ai/providers');
  return res.data;
};

export const testProviderConnection = async (data: { provider_name: string; api_key?: string; model?: string }) => {
  const res = await api.post('/ai/test-connection', data);
  return res.data;
};

export const saveProviderSetting = async (data: {
  provider_name: string;
  model_name: string;
  is_enabled: boolean;
  is_primary: boolean;
  is_fallback: boolean;
  api_key?: string;
}) => {
  const res = await api.post('/ai/settings', data);
  return res.data;
};

export const getAIUsageStats = async (): Promise<AIUsageStats> => {
  const res = await api.get('/ai/usage');
  return res.data;
};

// ----------------------------------------------------
// External Integrations Framework
// ----------------------------------------------------
export const getIntegrations = async (): Promise<IntegrationItem[]> => {
  const res = await api.get('/integrations');
  return res.data;
};

export const toggleIntegration = async (type: string, isEnabled: boolean) => {
  const res = await api.post(`/integrations/${type}/toggle`, { is_enabled: isEnabled });
  return res.data;
};

export const previewSheetsImport = async (csvContent: string) => {
  const res = await api.post('/integrations/sheets/preview', { csv_content: csvContent });
  return res.data;
};

export const confirmSheetsImport = async (items: any[]) => {
  const res = await api.post('/integrations/sheets/confirm', { items });
  return res.data;
};

export const getWeatherSignals = async (city?: string) => {
  const res = await api.get('/integrations/weather/signals', { params: { city } });
  return res.data;
};

export const getMessagingPreview = async () => {
  const res = await api.get('/integrations/messaging/preview');
  return res.data;
};

// ----------------------------------------------------
// System Health & Observability
// ----------------------------------------------------
export const getSystemHealth = async (): Promise<SystemHealth> => {
  const res = await api.get('/health/system');
  return res.data;
};

// ----------------------------------------------------
// AI Daily Business Briefing
// ----------------------------------------------------
export const getLatestBriefing = async () => {
  const res = await api.get('/briefing/latest');
  return res.data;
};

export const generateFreshBriefing = async () => {
  const res = await api.post('/briefing/generate');
  return res.data;
};

export const getBriefingHistory = async (limit = 10) => {
  const res = await api.get('/briefing/history', { params: { limit } });
  return res.data;
};

// ----------------------------------------------------
// Conversational AI Business Assistant
// ----------------------------------------------------
export const sendAssistantChat = async (message: string, sessionId = 'SESSION_DEFAULT', language = 'hi') => {
  const res = await api.post('/assistant/chat', { message, session_id: sessionId, language });
  return res.data;
};

export const getAssistantHistory = async (sessionId = 'SESSION_DEFAULT') => {
  const res = await api.get('/assistant/history', { params: { session_id: sessionId } });
  return res.data;
};

export const clearAssistantHistory = async (sessionId = 'SESSION_DEFAULT') => {
  const res = await api.delete('/assistant/history', { params: { session_id: sessionId } });
  return res.data;
};

export default api;
