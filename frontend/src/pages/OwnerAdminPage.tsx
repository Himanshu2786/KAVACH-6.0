import React, { useState, useEffect } from 'react';
import {
  Users,
  Activity,
  MessageSquare,
  ShieldAlert,
  UserPlus,
  KeyRound,
  CheckCircle2,
  XCircle,
  Clock,
  Search,
  Filter,
  RefreshCw,
  TrendingUp,
  FileText,
  AlertTriangle,
  Layers,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { UserAccount, UserActivityRecord, ActivitySummaryItem, UserFeedbackRecord } from '../types';
import { useApp } from '../context/AppContext';

export const OwnerAdminPage: React.FC = () => {
  const { showToast } = useApp();
  const [activeTab, setActiveTab] = useState<'users' | 'activity' | 'summary' | 'feedback'>('users');

  // Data states
  const [users, setUsers] = useState<UserAccount[]>([]);
  const [activities, setActivities] = useState<UserActivityRecord[]>([]);
  const [summary, setSummary] = useState<ActivitySummaryItem[]>([]);
  const [feedbacks, setFeedbacks] = useState<UserFeedbackRecord[]>([]);
  const [loading, setLoading] = useState(false);

  // New user form state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newUserId, setNewUserId] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newFullName, setNewFullName] = useState('');
  const [newRole, setNewRole] = useState<'TEAM_USER' | 'DEVELOPER_OWNER'>('TEAM_USER');

  // Password reset state
  const [resettingUser, setResettingUser] = useState<string | null>(null);
  const [resetPasswordVal, setResetPasswordVal] = useState('');

  // User tab search & filter
  const [userSearchQuery, setUserSearchQuery] = useState('');
  const [userStatusFilter, setUserStatusFilter] = useState<'ALL' | 'ACTIVE' | 'DEACTIVATED'>('ALL');

  // Filtering for activity
  const [activityUserFilter, setActivityUserFilter] = useState('');
  const [activityEventFilter, setActivityEventFilter] = useState('');

  const sortUsersNaturally = (a: UserAccount, b: UserAccount) => {
    // 1. ADMIN / DEVELOPER_OWNER first
    const isOwnerA = a.role === 'DEVELOPER_OWNER' || a.user_id.toUpperCase().startsWith('ADMIN');
    const isOwnerB = b.role === 'DEVELOPER_OWNER' || b.user_id.toUpperCase().startsWith('ADMIN');
    if (isOwnerA && !isOwnerB) return -1;
    if (!isOwnerA && isOwnerB) return 1;
    if (isOwnerA && isOwnerB) return a.user_id.localeCompare(b.user_id);

    // 2. Core team accounts: TEAM001 - TEAM010
    const isCoreA = /^TEAM\d+$/i.test(a.user_id);
    const isCoreB = /^TEAM\d+$/i.test(b.user_id);
    if (isCoreA && !isCoreB) return -1;
    if (!isCoreA && isCoreB) return 1;
    if (isCoreA && isCoreB) {
      const numA = parseInt(a.user_id.replace(/\D/g, ''), 10);
      const numB = parseInt(b.user_id.replace(/\D/g, ''), 10);
      if (!isNaN(numA) && !isNaN(numB) && numA !== numB) return numA - numB;
      return a.user_id.localeCompare(b.user_id);
    }

    // 3. Automated test accounts: TEAM_TEST_*
    const isTestA = a.user_id.toUpperCase().startsWith('TEAM_TEST');
    const isTestB = b.user_id.toUpperCase().startsWith('TEAM_TEST');
    if (isTestA && !isTestB) return -1;
    if (!isTestA && isTestB) return 1;
    if (isTestA && isTestB) {
      const numA = parseInt(a.user_id.replace(/\D/g, ''), 10);
      const numB = parseInt(b.user_id.replace(/\D/g, ''), 10);
      if (!isNaN(numA) && !isNaN(numB) && numA !== numB) return numA - numB;
      return a.user_id.localeCompare(b.user_id);
    }

    // 4. Any other accounts
    return a.user_id.localeCompare(b.user_id);
  };

  const filteredUsers = users.filter((u) => {
    if (userSearchQuery.trim()) {
      const q = userSearchQuery.toLowerCase();
      const matchId = u.user_id.toLowerCase().includes(q);
      const matchName = (u.full_name || '').toLowerCase().includes(q);
      const matchRole = u.role.toLowerCase().includes(q);
      if (!matchId && !matchName && !matchRole) return false;
    }
    return true;
  });

  const activeUsers = filteredUsers.filter((u) => u.is_active).sort(sortUsersNaturally);
  const deactivatedUsers = filteredUsers.filter((u) => !u.is_active).sort(sortUsersNaturally);

  const renderUserTable = (userList: UserAccount[], isDeactivatedSection = false) => {
    if (userList.length === 0) {
      return (
        <div className="p-8 text-center text-neutral-400 text-xs font-mono">
          {isDeactivatedSection ? 'No deactivated accounts.' : 'No matching active accounts found.'}
        </div>
      );
    }

    return (
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-neutral-900/60 font-mono text-[11px] text-neutral-400 uppercase tracking-wider border-b border-white/[0.06]">
            <tr>
              <th className="py-3 px-4">USER ID</th>
              <th className="py-3 px-4">Name / Role</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Created</th>
              <th className="py-3 px-4">Last Login</th>
              <th className="py-3 px-4">Assessments</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {userList.map((u) => {
              const isOwner = u.role === 'DEVELOPER_OWNER' || u.user_id.toUpperCase().startsWith('ADMIN');
              const isCoreTeam = /^TEAM\d+$/i.test(u.user_id);

              return (
                <tr key={u.user_id} className="hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 px-4 font-mono font-bold">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs ${
                        isOwner
                          ? 'text-purple-300 bg-purple-500/10 border border-purple-500/30'
                          : isCoreTeam
                          ? 'text-cyan-300 bg-cyan-500/10 border border-cyan-500/30'
                          : 'text-neutral-300 bg-neutral-800/60 border border-white/[0.08]'
                      }`}
                    >
                      {u.user_id}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="font-medium text-neutral-300">{u.full_name || '—'}</div>
                    <span
                      className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                        isOwner
                          ? 'bg-purple-500/10 text-purple-400 border border-purple-500/30'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                      }`}
                    >
                      {u.role}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    {u.is_active ? (
                      <span className="inline-flex items-center space-x-1.5 text-emerald-400 text-[11px] font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Active</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1.5 text-rose-400 text-[11px] font-medium">
                        <XCircle className="w-3.5 h-3.5" />
                        <span>Deactivated</span>
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4 font-mono text-neutral-400 text-[11px]">
                    {u.created_at || '—'}
                  </td>
                  <td className="py-3 px-4 font-mono text-neutral-400 text-[11px]">
                    {u.last_login_at || 'Never'}
                  </td>
                  <td className="py-3 px-4 font-mono text-cyan-400 font-bold">
                    {u.assessments_count ?? 0}
                  </td>
                  <td className="py-3 px-4 text-right space-x-2">
                    <button
                      onClick={() => {
                        setResettingUser(u.user_id);
                        setResetPasswordVal('');
                      }}
                      className="px-2.5 py-1 rounded-lg bg-neutral-900 border border-white/[0.1] hover:border-white/30 text-neutral-300 text-[11px] font-mono cursor-pointer"
                    >
                      Reset PW
                    </button>
                    <button
                      onClick={() => handleToggleStatus(u.user_id, u.is_active)}
                      className={`px-2.5 py-1 rounded-lg text-[11px] font-mono cursor-pointer transition-colors ${
                        u.is_active
                          ? 'bg-rose-500/10 border border-rose-500/30 text-rose-300 hover:bg-rose-500/20'
                          : 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/20 font-bold'
                      }`}
                    >
                      {u.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [uRes, actRes, sumRes, fbRes] = await Promise.all([
        api.adminGetUsers().catch(() => ({ success: false, count: 0, users: [] })),
        api.adminGetActivity({
          user_id: activityUserFilter || undefined,
          event_type: activityEventFilter || undefined,
          limit: 100
        }).catch(() => ({ success: false, count: 0, activities: [] })),
        api.adminGetActivitySummary().catch(() => ({ success: false, total_users: 0, summary: [] })),
        api.adminGetFeedback().catch(() => ({ success: false, count: 0, feedbacks: [] }))
      ]);

      if (uRes.users) setUsers(uRes.users);
      if (actRes.activities) setActivities(actRes.activities);
      if (sumRes.summary) setSummary(sumRes.summary);
      if (fbRes.feedbacks) setFeedbacks(fbRes.feedbacks);
    } catch (err: any) {
      showToast('error', 'Admin Sync Error', err.message || 'Failed to refresh owner console data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activityUserFilter, activityEventFilter]);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUserId.trim() || !newPassword) {
      showToast('error', 'Validation Error', 'USER ID and password are required.');
      return;
    }
    try {
      const res = await api.adminCreateUser({
        user_id: newUserId.trim().toUpperCase(),
        password: newPassword,
        full_name: newFullName.trim(),
        role: newRole
      });
      showToast('success', 'User Created', res.message);
      setShowCreateModal(false);
      setNewUserId('');
      setNewPassword('');
      setNewFullName('');
      loadData();
    } catch (err: any) {
      showToast('error', 'Creation Failed', err.message || 'Could not create teammate account.');
    }
  };

  const handleToggleStatus = async (userId: string, currentActive: boolean) => {
    try {
      const res = await api.adminSetUserStatus(userId, !currentActive);
      showToast('info', 'Status Updated', res.message);
      loadData();
    } catch (err: any) {
      showToast('error', 'Update Failed', err.message || 'Could not update status.');
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resettingUser || !resetPasswordVal) return;
    try {
      const res = await api.adminResetPassword(resettingUser, resetPasswordVal);
      showToast('success', 'Password Reset', res.message);
      setResettingUser(null);
      setResetPasswordVal('');
      loadData();
    } catch (err: any) {
      showToast('error', 'Reset Failed', err.message || 'Could not reset password.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-neutral-950/80 border border-white/[0.1] backdrop-blur-xl">
        <div className="flex items-center space-x-3.5">
          <div className="p-3 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 text-indigo-400">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-[10px] font-mono uppercase tracking-widest px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                DEVELOPER / OWNER CONSOLE
              </span>
              <span className="text-xs text-neutral-400 font-mono">
                No Artificial User/Usage Limits
              </span>
            </div>
            <h1 className="text-xl font-bold text-neutral-100 mt-1">
              Team Accounts, RBAC & Activity Analytics
            </h1>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => loadData()}
            disabled={loading}
            className="flex items-center space-x-2 px-3 py-2 rounded-xl bg-neutral-900 border border-white/[0.1] hover:border-white/30 text-neutral-300 text-xs font-mono transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync</span>
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-950/50 transition-colors cursor-pointer"
          >
            <UserPlus className="w-4 h-4" />
            <span>New Teammate</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-white/[0.08] pb-1">
        <button
          onClick={() => setActiveTab('users')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-medium transition-colors cursor-pointer ${activeTab === 'users'
              ? 'bg-neutral-900 text-neutral-100 border border-white/[0.12]'
              : 'text-neutral-400 hover:text-neutral-200'
            }`}
        >
          <Users className="w-4 h-4" />
          <span>Team Accounts ({users.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('summary')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-medium transition-colors cursor-pointer ${activeTab === 'summary'
              ? 'bg-neutral-900 text-neutral-100 border border-white/[0.12]'
              : 'text-neutral-400 hover:text-neutral-200'
            }`}
        >
          <TrendingUp className="w-4 h-4" />
          <span>Meaningful Use Analytics</span>
        </button>

        <button
          onClick={() => setActiveTab('activity')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-medium transition-colors cursor-pointer ${activeTab === 'activity'
              ? 'bg-neutral-900 text-neutral-100 border border-white/[0.12]'
              : 'text-neutral-400 hover:text-neutral-200'
            }`}
        >
          <Activity className="w-4 h-4" />
          <span>Activity Timeline ({activities.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('feedback')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-medium transition-colors cursor-pointer ${activeTab === 'feedback'
              ? 'bg-neutral-900 text-neutral-100 border border-white/[0.12]'
              : 'text-neutral-400 hover:text-neutral-200'
            }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>Teammate Feedback ({feedbacks.length})</span>
        </button>
      </div>

      {/* Tab 1: Team Accounts */}
      {activeTab === 'users' && (
        <div className="space-y-6">
          {/* Controls: Search and Filter Bar */}
          <div className="p-4 rounded-2xl border border-white/[0.1] bg-neutral-950/80 backdrop-blur-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center space-x-3 flex-1">
              <div className="relative flex-1 max-w-md">
                <Search className="w-4 h-4 text-neutral-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Filter operators by USER ID, Name, or Role..."
                  value={userSearchQuery}
                  onChange={(e) => setUserSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 rounded-xl bg-neutral-900/80 border border-white/[0.08] text-xs text-neutral-200 placeholder-neutral-500 focus:outline-none focus:border-cyan-500/50"
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => setUserStatusFilter('ALL')}
                className={`px-3 py-1.5 rounded-xl text-xs font-mono cursor-pointer transition-colors ${
                  userStatusFilter === 'ALL'
                    ? 'bg-neutral-800 text-neutral-100 border border-white/[0.2]'
                    : 'text-neutral-400 hover:text-neutral-200 border border-transparent'
                }`}
              >
                All Accounts ({filteredUsers.length})
              </button>
              <button
                onClick={() => setUserStatusFilter('ACTIVE')}
                className={`px-3 py-1.5 rounded-xl text-xs font-mono cursor-pointer transition-colors ${
                  userStatusFilter === 'ACTIVE'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                    : 'text-neutral-400 hover:text-neutral-200 border border-transparent'
                }`}
              >
                Live / Active ({activeUsers.length})
              </button>
              <button
                onClick={() => setUserStatusFilter('DEACTIVATED')}
                className={`px-3 py-1.5 rounded-xl text-xs font-mono cursor-pointer transition-colors ${
                  userStatusFilter === 'DEACTIVATED'
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                    : 'text-neutral-400 hover:text-neutral-200 border border-transparent'
                }`}
              >
                Deactivated ({deactivatedUsers.length})
              </button>
            </div>
          </div>

          {/* SECTION 1: LIVE / ACTIVE ACCOUNTS */}
          {(userStatusFilter === 'ALL' || userStatusFilter === 'ACTIVE') && (
            <div className="rounded-2xl border border-white/[0.1] bg-neutral-950/80 backdrop-blur-xl overflow-hidden">
              <div className="p-4 border-b border-white/[0.08] flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                  <h2 className="text-sm font-semibold text-neutral-200">
                    Live / Active Operator Accounts ({activeUsers.length})
                  </h2>
                </div>
                <span className="text-[11px] font-mono text-emerald-400/80">
                  Ordered by ADMIN → Core Team (TEAM001–TEAM010) → Automated Teammates
                </span>
              </div>
              {renderUserTable(activeUsers, false)}
            </div>
          )}

          {/* SECTION 2: DEACTIVATED ACCOUNTS */}
          {(userStatusFilter === 'ALL' || userStatusFilter === 'DEACTIVATED') && (
            <div className="rounded-2xl border border-white/[0.1] bg-neutral-950/80 backdrop-blur-xl overflow-hidden">
              <div className="p-4 border-b border-white/[0.08] flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <XCircle className="w-4 h-4 text-rose-400" />
                  <h2 className="text-sm font-semibold text-neutral-200">
                    Deactivated Accounts ({deactivatedUsers.length})
                  </h2>
                </div>
                <span className="text-[11px] font-mono text-neutral-400">
                  Suspended credentials • Click &quot;Activate&quot; to restore access
                </span>
              </div>
              {renderUserTable(deactivatedUsers, true)}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Meaningful Use Analytics */}
      {activeTab === 'summary' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-neutral-900/60 border border-white/[0.08] text-xs leading-relaxed text-neutral-300">
            <h3 className="font-semibold text-neutral-200 mb-1 flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>Deterministic Usage Categorization (No AI Guessing)</span>
            </h3>
            <p>
              Usage is categorized based strictly on verified system events:
              <strong className="text-emerald-400 ml-1">MEANINGFUL USE</strong> (Ran assessments, reviewed evidence, executed AI/RAG, evaluated risk, generated reports),
              <strong className="text-cyan-400 ml-1">ACTIVE USE</strong> (Explored modules/pages), and
              <strong className="text-amber-400 ml-1">LOGIN ONLY</strong> (Authenticated without subsequent interaction).
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {summary.map((item) => (
              <div
                key={item.user_id}
                className="p-5 rounded-2xl border border-white/[0.1] bg-neutral-950/80 backdrop-blur-xl space-y-3"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-neutral-100 font-mono">
                      {item.user_id}
                    </h3>
                    <p className="text-xs text-neutral-400">{item.full_name || 'Team Operator'}</p>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold ${item.usage_category === 'MEANINGFUL USE'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                      : item.usage_category === 'ACTIVE USE'
                        ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                    }`}>
                    {item.usage_category}
                  </span>
                </div>

                <div className="pt-2 border-t border-white/[0.06] grid grid-cols-2 gap-2 text-xs font-mono">
                  <div>
                    <span className="text-neutral-500 text-[10px] uppercase">Total Actions:</span>
                    <p className="text-neutral-200 font-bold">{item.total_events}</p>
                  </div>
                  <div>
                    <span className="text-neutral-500 text-[10px] uppercase">Meaningful Actions:</span>
                    <p className="text-emerald-400 font-bold">{item.meaningful_actions_count}</p>
                  </div>
                  <div className="col-span-2">
                    <span className="text-neutral-500 text-[10px] uppercase">Last Login:</span>
                    <p className="text-neutral-400 text-[11px]">{item.last_login_at || 'Never'}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Activity Timeline */}
      {activeTab === 'activity' && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-3 p-3.5 rounded-xl bg-neutral-900/60 border border-white/[0.08]">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-neutral-400" />
              <span className="text-xs font-mono text-neutral-400">Filters:</span>
            </div>
            <select
              value={activityUserFilter}
              onChange={(e) => setActivityUserFilter(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-neutral-900 border border-white/[0.1] text-xs font-mono text-neutral-200"
            >
              <option value="">All Users</option>
              {users.map((u) => (
                <option key={u.user_id} value={u.user_id}>{u.user_id}</option>
              ))}
            </select>
            <select
              value={activityEventFilter}
              onChange={(e) => setActivityEventFilter(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-neutral-900 border border-white/[0.1] text-xs font-mono text-neutral-200"
            >
              <option value="">All Event Types</option>
              <option value="LOGIN">LOGIN</option>
              <option value="LOGOUT">LOGOUT</option>
              <option value="ASSESSMENT_STARTED">ASSESSMENT_STARTED</option>
              <option value="ASSESSMENT_COMPLETED">ASSESSMENT_COMPLETED</option>
              <option value="PAGE_VIEWED">PAGE_VIEWED</option>
              <option value="MODULE_OPENED">MODULE_OPENED</option>
              <option value="REPORT_EXPORTED">REPORT_EXPORTED</option>
              <option value="PERMISSION_GRANTED">PERMISSION_GRANTED</option>
              <option value="PERMISSION_DENIED">PERMISSION_DENIED</option>
              <option value="FEEDBACK_SUBMITTED">FEEDBACK_SUBMITTED</option>
            </select>
          </div>

          <div className="rounded-2xl border border-white/[0.1] bg-neutral-950/80 backdrop-blur-xl p-4 divide-y divide-white/[0.04]">
            {activities.length === 0 ? (
              <div className="text-center py-8 text-neutral-500 text-xs">
                No activity records matched the selected filters.
              </div>
            ) : (
              activities.map((a) => (
                <div key={a.id} className="py-3 flex items-start justify-between text-xs">
                  <div className="flex items-start space-x-3">
                    <span className="font-mono text-[11px] text-neutral-500 w-36 flex-shrink-0">
                      {a.timestamp}
                    </span>
                    <span className="font-mono font-bold text-neutral-300 w-24 flex-shrink-0">
                      {a.user_id}
                    </span>
                    <span className="font-mono font-semibold text-emerald-400 w-44 flex-shrink-0">
                      {a.event_type}
                    </span>
                    <span className="font-mono text-neutral-400 text-[11px]">
                      {a.module} {a.assessment_id ? `[${a.assessment_id}]` : ''}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-neutral-500">
                    {a.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Tab 4: Teammate Feedback */}
      {activeTab === 'feedback' && (
        <div className="space-y-4">
          {feedbacks.length === 0 ? (
            <div className="p-8 rounded-2xl border border-white/[0.1] bg-neutral-950/80 text-center text-xs text-neutral-500">
              No feedback submitted by team operators yet.
            </div>
          ) : (
            feedbacks.map((fb) => (
              <div
                key={fb.id}
                className="p-5 rounded-2xl border border-white/[0.1] bg-neutral-950/80 backdrop-blur-xl space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-neutral-200 text-xs">
                      {fb.user_id}
                    </span>
                    <span className="text-amber-400 text-xs font-bold">
                      {'★'.repeat(fb.rating)}{'☆'.repeat(5 - fb.rating)}
                    </span>
                    {fb.assessment_id && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-neutral-900 text-neutral-400 border border-white/[0.08]">
                        Assessment: {fb.assessment_id}
                      </span>
                    )}
                  </div>
                  <span className="font-mono text-[11px] text-neutral-500">{fb.created_at}</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  {fb.what_worked && (
                    <div className="p-3 rounded-xl bg-neutral-900/60 border border-white/[0.06]">
                      <span className="text-[10px] font-mono text-emerald-400 uppercase">What Worked:</span>
                      <p className="text-neutral-200 mt-0.5">{fb.what_worked}</p>
                    </div>
                  )}
                  {fb.what_confusing && (
                    <div className="p-3 rounded-xl bg-neutral-900/60 border border-white/[0.06]">
                      <span className="text-[10px] font-mono text-amber-400 uppercase">What Was Confusing:</span>
                      <p className="text-neutral-200 mt-0.5">{fb.what_confusing}</p>
                    </div>
                  )}
                  {fb.what_slow && (
                    <div className="p-3 rounded-xl bg-neutral-900/60 border border-white/[0.06]">
                      <span className="text-[10px] font-mono text-rose-400 uppercase">What Felt Slow:</span>
                      <p className="text-neutral-200 mt-0.5">{fb.what_slow}</p>
                    </div>
                  )}
                  {fb.bug_description && (
                    <div className="p-3 rounded-xl bg-neutral-900/60 border border-white/[0.06]">
                      <span className="text-[10px] font-mono text-rose-400 uppercase">Bug Report:</span>
                      <p className="text-neutral-200 mt-0.5">{fb.bug_description}</p>
                    </div>
                  )}
                  {fb.suggestions && (
                    <div className="p-3 rounded-xl bg-neutral-900/60 border border-white/[0.06] md:col-span-2">
                      <span className="text-[10px] font-mono text-cyan-400 uppercase">Suggestions:</span>
                      <p className="text-neutral-200 mt-0.5">{fb.suggestions}</p>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Modal: Create Teammate */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
          <div className="relative w-full max-w-md rounded-2xl border border-white/[0.15] bg-neutral-950 p-6 shadow-2xl">
            <h2 className="text-base font-bold text-neutral-100 mb-1">Issue New Team Credentials</h2>
            <p className="text-xs text-neutral-400 mb-4">
              Create an operator account and transmit the credentials securely to your teammate.
            </p>

            <form onSubmit={handleCreateUser} className="space-y-4 text-xs">
              <div>
                <label className="block text-neutral-300 font-mono uppercase text-[10px] mb-1">
                  USER ID (Unique)
                </label>
                <input
                  type="text"
                  value={newUserId}
                  onChange={(e) => setNewUserId(e.target.value)}
                  placeholder="e.g. TEAM005"
                  required
                  className="w-full px-3 py-2 rounded-xl bg-neutral-900 border border-white/[0.1] text-neutral-100 font-mono focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-neutral-300 font-mono uppercase text-[10px] mb-1">
                  Initial Password
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full px-3 py-2 rounded-xl bg-neutral-900 border border-white/[0.1] text-neutral-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-neutral-300 font-mono uppercase text-[10px] mb-1">
                  Full Name / Operator Designation (Optional)
                </label>
                <input
                  type="text"
                  value={newFullName}
                  onChange={(e) => setNewFullName(e.target.value)}
                  placeholder="e.g. SOC Incident Specialist"
                  className="w-full px-3 py-2 rounded-xl bg-neutral-900 border border-white/[0.1] text-neutral-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-neutral-300 font-mono uppercase text-[10px] mb-1">
                  Role Privileges
                </label>
                <select
                  value={newRole}
                  onChange={(e: any) => setNewRole(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-neutral-900 border border-white/[0.1] text-neutral-100 focus:outline-none focus:border-emerald-500"
                >
                  <option value="TEAM_USER">TEAM_USER (Standard KAVACH 6.0 Operator)</option>
                  <option value="DEVELOPER_OWNER">DEVELOPER_OWNER (Full Admin & Account Manager)</option>
                </select>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-white/[0.08]">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl border border-white/[0.1] hover:bg-neutral-900 text-neutral-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold shadow-lg shadow-emerald-950/40"
                >
                  Create Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Reset Password */}
      {resettingUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
          <div className="relative w-full max-w-sm rounded-2xl border border-white/[0.15] bg-neutral-950 p-6 shadow-2xl">
            <h2 className="text-base font-bold text-neutral-100 mb-1">Reset Password</h2>
            <p className="text-xs text-neutral-400 mb-4">
              Enter a new temporary password for operator <strong className="text-white font-mono">{resettingUser}</strong>.
            </p>

            <form onSubmit={handleResetPassword} className="space-y-4 text-xs">
              <div>
                <label className="block text-neutral-300 font-mono uppercase text-[10px] mb-1">
                  New Password
                </label>
                <input
                  type="password"
                  value={resetPasswordVal}
                  onChange={(e) => setResetPasswordVal(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  autoFocus
                  className="w-full px-3 py-2 rounded-xl bg-neutral-900 border border-white/[0.1] text-neutral-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-white/[0.08]">
                <button
                  type="button"
                  onClick={() => setResettingUser(null)}
                  className="px-4 py-2 rounded-xl border border-white/[0.1] hover:bg-neutral-900 text-neutral-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold"
                >
                  Set New Password
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
