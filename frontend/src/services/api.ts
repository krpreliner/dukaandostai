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
  EvaluationMetrics
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export default api;
