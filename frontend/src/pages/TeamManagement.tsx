import React, { useEffect, useState } from 'react';
import { Users, UserPlus, Shield, Store, Plus, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { getStoreMembers, addStoreMember, createNewStore } from '../services/api';
import { StoreMember } from '../types';

export const TeamManagement: React.FC = () => {
  const { activeStore, stores, switchStore, refreshProfile } = useAuth();
  const [members, setMembers] = useState<StoreMember[]>([]);
  const [loading, setLoading] = useState(true);

  // Invite member state
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'OWNER' | 'MANAGER' | 'STAFF' | 'VIEWER'>('STAFF');
  const [inviteMsg, setInviteMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // New store modal
  const [showNewStoreModal, setShowNewStoreModal] = useState(false);
  const [newStoreName, setNewStoreName] = useState('');
  const [newStoreLocation, setNewStoreLocation] = useState('');
  const [creatingStore, setCreatingStore] = useState(false);

  const fetchMembers = async () => {
    if (!activeStore) return;
    try {
      const data = await getStoreMembers(activeStore.store_id);
      setMembers(data || []);
    } catch (err) {
      console.error('Error fetching store members:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMembers();
  }, [activeStore]);

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeStore || !inviteEmail) return;
    setIsSubmitting(true);
    setInviteMsg(null);
    try {
      const res = await addStoreMember(activeStore.store_id, inviteEmail, inviteRole);
      setInviteMsg({ type: 'success', text: res.message || 'Member added successfully.' });
      setInviteEmail('');
      await fetchMembers();
    } catch (err: any) {
      const errDetail = err.response?.data?.detail || 'Failed to add member.';
      setInviteMsg({ type: 'error', text: errDetail });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateStore = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newStoreName) return;
    setCreatingStore(true);
    try {
      await createNewStore(newStoreName, newStoreLocation);
      await refreshProfile();
      setShowNewStoreModal(false);
      setNewStoreName('');
      setNewStoreLocation('');
    } catch (err) {
      console.error('Error creating store:', err);
    } finally {
      setCreatingStore(false);
    }
  };

  return (
    <div className="p-8 space-y-8 w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Users className="w-5 h-5 text-[#22D3EE]" />
            <h2 className="text-xl font-bold text-white tracking-tight">Team & Store Workspace Management</h2>
          </div>
          <p className="text-sm text-neutral-400">
            Multi-tenant access control and role-based permissions across your Kirana operations.
          </p>
        </div>

        <button
          onClick={() => setShowNewStoreModal(true)}
          className="self-start sm:self-center px-4 py-2 rounded-xl bg-[#22D3EE] hover:bg-[#06b6d4] text-black text-xs font-semibold flex items-center gap-2 cursor-pointer transition-all shadow-md"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Create New Store</span>
        </button>
      </div>

      {/* Current Workspace Switcher Pill */}
      <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#22D3EE]/10 border border-[#22D3EE]/20 flex items-center justify-center text-[#22D3EE]">
            <Store className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-bold text-white">{activeStore?.name}</span>
              <span className="text-[11px] font-mono text-neutral-400">({activeStore?.store_id})</span>
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-[#22D3EE]/15 text-[#22D3EE]">
                {activeStore?.role}
              </span>
            </div>
            <p className="text-xs text-neutral-400">{activeStore?.location} • Owner: {activeStore?.owner_name}</p>
          </div>
        </div>

        {stores.length > 1 && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-neutral-400">Switch Workspace:</span>
            <select
              value={activeStore?.store_id}
              onChange={(e) => switchStore(e.target.value)}
              className="bg-[#171717] border border-white/[0.08] text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-[#22D3EE]"
            >
              {stores.map((s) => (
                <option key={s.store_id} value={s.store_id}>
                  {s.name} ({s.location})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Invite Member Section */}
      <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <UserPlus className="w-4 h-4 text-[#22D3EE]" />
          <h3 className="text-base font-semibold text-white">Invite / Assign Team Member</h3>
        </div>

        <form onSubmit={handleAddMember} className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
          <div className="sm:col-span-2">
            <input
              type="email"
              placeholder="Registered user email (e.g., manager@sharmastore.com)"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              required
              className="w-full bg-[#171717] border border-white/[0.08] rounded-lg px-3 py-2 text-white placeholder-neutral-500 focus:outline-none focus:border-[#22D3EE]"
            />
          </div>

          <div>
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value as any)}
              className="w-full bg-[#171717] border border-white/[0.08] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-[#22D3EE]"
            >
              <option value="STAFF">STAFF (Read & Inventory Updates)</option>
              <option value="MANAGER">MANAGER (Approvals & Workers)</option>
              <option value="OWNER">OWNER (Full Administrative)</option>
              <option value="VIEWER">VIEWER (Read-Only Analytics)</option>
            </select>
          </div>

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-2 rounded-lg bg-[#22D3EE] hover:bg-[#06b6d4] text-black font-semibold text-xs transition-colors cursor-pointer disabled:opacity-50"
            >
              {isSubmitting ? 'Assigning...' : 'Assign Role'}
            </button>
          </div>
        </form>

        {inviteMsg && (
          <div className={`mt-3 p-3 rounded-lg text-xs ${
            inviteMsg.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
          }`}>
            {inviteMsg.text}
          </div>
        )}
      </div>

      {/* Members Table */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold text-white">Active Store Members ({members.length})</h3>

        <div className="bg-[#111111] border border-white/[0.08] rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#171717] border-b border-white/[0.08] text-neutral-400 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="py-3 px-4">Member Name</th>
                  <th className="py-3 px-4">Email</th>
                  <th className="py-3 px-4">Store Role</th>
                  <th className="py-3 px-4">Access Level</th>
                  <th className="py-3 px-4">Added</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.05] text-neutral-300">
                {members.map((m) => (
                  <tr key={m.user_id} className="hover:bg-white/[0.02]">
                    <td className="py-3.5 px-4 font-medium text-white">{m.full_name}</td>
                    <td className="py-3.5 px-4 font-mono text-neutral-400">{m.email}</td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${
                        m.role === 'OWNER'
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                          : m.role === 'MANAGER'
                          ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
                          : 'bg-neutral-800 text-neutral-300 border-white/[0.08]'
                      }`}>
                        {m.role}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-neutral-400">
                      {m.role === 'OWNER' ? 'Full Authority' : m.role === 'MANAGER' ? 'Approvals & Execution' : m.role === 'STAFF' ? 'Inventory & Operations' : 'Read-Only'}
                    </td>
                    <td className="py-3.5 px-4 text-neutral-500 font-mono text-[11px]">
                      {m.created_at ? new Date(m.created_at).toLocaleDateString() : 'Initial Setup'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Create New Store Modal */}
      {showNewStoreModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111111] border border-white/[0.1] rounded-2xl p-6 max-w-md w-full space-y-4 shadow-2xl">
            <div>
              <h3 className="text-base font-semibold text-white">Create New Kirana Store Workspace</h3>
              <p className="text-xs text-neutral-400 mt-1">
                Set up an independent store tenant with isolated catalog, financials, and agent runs.
              </p>
            </div>

            <form onSubmit={handleCreateStore} className="space-y-3 text-xs">
              <div>
                <label className="text-neutral-400 mb-1 block">Store Business Name</label>
                <input
                  type="text"
                  placeholder="e.g. Verma Provision Store"
                  value={newStoreName}
                  onChange={(e) => setNewStoreName(e.target.value)}
                  required
                  className="w-full bg-[#171717] border border-white/[0.08] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-[#22D3EE]"
                />
              </div>

              <div>
                <label className="text-neutral-400 mb-1 block">Location</label>
                <input
                  type="text"
                  placeholder="e.g. Doranda, Ranchi"
                  value={newStoreLocation}
                  onChange={(e) => setNewStoreLocation(e.target.value)}
                  className="w-full bg-[#171717] border border-white/[0.08] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-[#22D3EE]"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowNewStoreModal(false)}
                  className="px-4 py-2 rounded-lg bg-[#171717] hover:bg-neutral-800 text-neutral-300 text-xs font-medium cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creatingStore}
                  className="px-4 py-2 rounded-lg bg-[#22D3EE] hover:bg-[#06b6d4] text-black text-xs font-semibold cursor-pointer"
                >
                  {creatingStore ? 'Creating...' : 'Create Workspace'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
