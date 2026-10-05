import React, { useState, useEffect } from 'react';
import { 
  Users, 
  UserCheck, 
  ShieldAlert, 
  Clock, 
  MessageSquare, 
  CheckCircle2, 
  AlertCircle, 
  Search, 
  ArrowRight, 
  Send,
  ExternalLink,
  Shield,
  Layers
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { FindingAssignment, TeamMember, SeverityLevel } from '../types';

export const TeamDeskPage: React.FC = () => {
  const { navigate, showToast, setSelectedFindingId } = useApp();
  const [assignments, setAssignments] = useState<FindingAssignment[]>([]);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRoleFilter, setSelectedRoleFilter] = useState('ALL');
  const [selectedTriageFilter, setSelectedTriageFilter] = useState('ALL');
  
  // Note Modal / Inline active finding
  const [activeFinding, setActiveFinding] = useState<FindingAssignment | null>(null);
  const [newNote, setNewNote] = useState('');
  const [submittingNote, setSubmittingNote] = useState(false);

  const fetchAssignments = async () => {
    try {
      const [membersRes, assignRes] = await Promise.all([
        api.getTeamMembers(),
        api.getTeamAssignments()
      ]);
      if (membersRes.success) setMembers(membersRes.team_members);
      if (assignRes.success) setAssignments(assignRes.assignments);
    } catch (err) {
      showToast('error', 'Sync Failed', 'Could not load team assignments.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssignments();
  }, []);

  const handleAssignMember = async (findingId: string, memberName: string) => {
    try {
      const res = await api.assignFinding({
        finding_id: findingId,
        assigned_to: memberName,
        triage_status: 'ASSIGNED'
      });
      if (res.success) {
        showToast('success', 'Finding Assigned', `Assigned to ${memberName}. Audit trail updated.`);
        fetchAssignments();
      }
    } catch {
      showToast('error', 'Assignment Error', 'Failed to assign finding.');
    }
  };

  const handleUpdateStatus = async (findingId: string, status: string) => {
    try {
      const finding = assignments.find(a => a.finding_id === findingId);
      const res = await api.assignFinding({
        finding_id: findingId,
        assigned_to: finding?.assigned_to || 'Unassigned',
        triage_status: status
      });
      if (res.success) {
        showToast('info', 'Triage Updated', `Status changed to ${status}.`);
        fetchAssignments();
      }
    } catch {
      showToast('error', 'Update Failed', 'Failed to update triage status.');
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeFinding || !newNote.trim()) return;
    setSubmittingNote(true);
    try {
      const res = await api.addTeamNote({
        finding_id: activeFinding.finding_id,
        notes: newNote.trim()
      });
      if (res.success) {
        showToast('success', 'Note Appended', 'Collaborative audit note saved.');
        setNewNote('');
        fetchAssignments();
        setActiveFinding(prev => prev ? { ...prev, team_notes: res.team_notes } : null);
      }
    } catch {
      showToast('error', 'Note Failed', 'Failed to record note.');
    } finally {
      setSubmittingNote(false);
    }
  };

  const filteredAssignments = assignments.filter(a => {
    const matchesSearch = a.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          a.finding_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          a.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = selectedRoleFilter === 'ALL' || a.assigned_to === selectedRoleFilter;
    const matchesTriage = selectedTriageFilter === 'ALL' || a.triage_status === selectedTriageFilter;
    return matchesSearch && matchesRole && matchesTriage;
  });

  const getSeverityBadge = (sev: SeverityLevel) => {
    switch (sev) {
      case 'CRITICAL': return <Badge variant="critical">CRITICAL</Badge>;
      case 'HIGH': return <Badge variant="high">HIGH</Badge>;
      case 'MEDIUM': return <Badge variant="medium">MEDIUM</Badge>;
      default: return <Badge variant="low">{sev}</Badge>;
    }
  };

  const getTriageBadge = (status: string) => {
    switch (status) {
      case 'NEW': return <span className="px-2 py-0.5 text-xs font-mono rounded bg-slate-800 text-slate-400 border border-slate-700">NEW</span>;
      case 'ASSIGNED': return <span className="px-2 py-0.5 text-xs font-mono rounded bg-blue-950/60 text-blue-400 border border-blue-800/50">ASSIGNED</span>;
      case 'IN_PROGRESS': return <span className="px-2 py-0.5 text-xs font-mono rounded bg-amber-950/60 text-amber-400 border border-amber-800/50">IN_PROGRESS</span>;
      case 'RESOLVED': return <span className="px-2 py-0.5 text-xs font-mono rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/50">RESOLVED</span>;
      case 'FALSE_POSITIVE': return <span className="px-2 py-0.5 text-xs font-mono rounded bg-purple-950/60 text-purple-400 border border-purple-800/50">FALSE_POSITIVE</span>;
      default: return <span className="px-2 py-0.5 text-xs font-mono rounded bg-slate-800 text-slate-300">{status}</span>;
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Module Header & Principle Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3 mb-1">
            <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
              <Users className="w-5 h-5 text-indigo-400" />
              <span>Module 8: Team Desk</span>
            </h1>
            <Badge variant="outline">KAVACH Enterprise</Badge>
            <span className="px-2 py-0.5 text-xs font-mono rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
              ASSIGN
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Security operations triage desk for role-based finding delegation, collaborative investigation logs, and tamper-evident assignment tracking.
          </p>
        </div>

        <div className="flex items-center space-x-2 bg-slate-900/80 border border-slate-800 px-3 py-2 rounded-lg text-xs font-mono text-slate-400">
          <Clock className="w-4 h-4 text-emerald-400" />
          <span>Loop: FIND → UNDERSTAND → <strong className="text-indigo-300">ASSIGN</strong> → FIX → RE-VERIFY</span>
        </div>
      </div>

      {/* Team Roster Bar */}
      <GlassCard className="p-4 border-slate-800/80 bg-slate-900/40">
        <h2 className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-3 flex items-center space-x-2">
          <UserCheck className="w-4 h-4 text-indigo-400" />
          <span>Active SecOps Personnel & Roles</span>
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {members.map(m => (
            <div key={m.id} className="p-2.5 rounded border border-slate-800 bg-slate-950/60 flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded bg-indigo-950/80 border border-indigo-700/60 text-indigo-300 font-mono text-xs flex items-center justify-center font-bold">
                {m.initials}
              </div>
              <div className="overflow-hidden">
                <div className="text-xs font-medium text-slate-200 truncate">{m.name}</div>
                <div className="text-[10px] text-slate-400 truncate">{m.role}</div>
              </div>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* Filter and Search Controls */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search findings by ID, title, or category..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <select
          value={selectedRoleFilter}
          onChange={e => setSelectedRoleFilter(e.target.value)}
          className="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-lg px-3 py-2 font-mono focus:outline-none focus:border-indigo-500"
        >
          <option value="ALL">All Assignees</option>
          <option value="Unassigned">Unassigned</option>
          {members.map(m => (
            <option key={m.id} value={m.name}>{m.name}</option>
          ))}
        </select>

        <select
          value={selectedTriageFilter}
          onChange={e => setSelectedTriageFilter(e.target.value)}
          className="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-lg px-3 py-2 font-mono focus:outline-none focus:border-indigo-500"
        >
          <option value="ALL">All Triage Statuses</option>
          <option value="NEW">NEW</option>
          <option value="ASSIGNED">ASSIGNED</option>
          <option value="IN_PROGRESS">IN_PROGRESS</option>
          <option value="RESOLVED">RESOLVED</option>
          <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
        </select>
      </div>

      {/* Assignments Matrix */}
      {loading ? (
        <div className="text-center py-12 text-slate-400 font-mono text-sm">
          Loading team assignment matrix...
        </div>
      ) : filteredAssignments.length === 0 ? (
        <GlassCard className="p-8 text-center border-slate-800">
          <ShieldAlert className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <p className="text-slate-400 text-sm font-mono">No findings match the current filter criteria.</p>
        </GlassCard>
      ) : (
        <div className="space-y-3">
          {filteredAssignments.map(a => (
            <GlassCard key={a.finding_id} className="p-4 border-slate-800/90 hover:border-slate-700 transition-all bg-slate-950/40">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                {/* Left: Finding Title & Badges */}
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex items-center space-x-2.5 flex-wrap gap-y-1">
                    <span className="font-mono text-xs text-indigo-400 font-bold">{a.finding_id}</span>
                    {getSeverityBadge(a.severity)}
                    {getTriageBadge(a.triage_status)}
                    <span className="text-xs font-mono text-slate-400 border border-slate-800 px-1.5 py-0.5 rounded">
                      {a.category}
                    </span>
                    {a.cwe_id && (
                      <span className="text-xs font-mono text-cyan-400 border border-cyan-900/60 bg-cyan-950/30 px-1.5 py-0.5 rounded">
                        {a.cwe_id}
                      </span>
                    )}
                  </div>
                  <h3 className="text-sm font-semibold text-slate-100 truncate">{a.title}</h3>
                  {a.team_notes ? (
                    <div className="text-xs text-slate-400 bg-slate-900/90 border border-slate-800/80 rounded p-2 font-mono whitespace-pre-line line-clamp-2">
                      <span className="text-indigo-400 font-bold mr-1">[Latest Note]:</span>
                      {a.team_notes.split('\n')[0]}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500 italic">No collaborative notes recorded yet.</p>
                  )}
                </div>

                {/* Right: Assignment Controls & Actions */}
                <div className="flex flex-wrap items-center gap-2 sm:gap-3 shrink-0">
                  {/* Assignee Dropdown */}
                  <div className="flex flex-col text-left">
                    <label className="text-[10px] uppercase font-mono text-slate-500 mb-0.5">Assignee</label>
                    <select
                      value={a.assigned_to}
                      onChange={e => handleAssignMember(a.finding_id, e.target.value)}
                      className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded px-2.5 py-1.5 font-mono focus:outline-none focus:border-indigo-500"
                    >
                      <option value="Unassigned">Unassigned</option>
                      {members.map(m => (
                        <option key={m.id} value={m.name}>{m.name}</option>
                      ))}
                    </select>
                  </div>

                  {/* Triage Status Dropdown */}
                  <div className="flex flex-col text-left">
                    <label className="text-[10px] uppercase font-mono text-slate-500 mb-0.5">Triage Stage</label>
                    <select
                      value={a.triage_status}
                      onChange={e => handleUpdateStatus(a.finding_id, e.target.value)}
                      className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded px-2.5 py-1.5 font-mono focus:outline-none focus:border-indigo-500"
                    >
                      <option value="NEW">NEW</option>
                      <option value="ASSIGNED">ASSIGNED</option>
                      <option value="IN_PROGRESS">IN_PROGRESS</option>
                      <option value="RESOLVED">RESOLVED</option>
                      <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
                    </select>
                  </div>

                  {/* Open Notes Button */}
                  <button
                    onClick={() => setActiveFinding(a)}
                    className="mt-3.5 px-3 py-1.5 text-xs font-mono rounded border border-indigo-800/80 bg-indigo-950/40 text-indigo-300 hover:bg-indigo-900/50 flex items-center space-x-1 transition-all"
                  >
                    <MessageSquare className="w-3.5 h-3.5" />
                    <span>Notes ({a.team_notes ? a.team_notes.split('\n').filter(Boolean).length : 0})</span>
                  </button>

                  {/* Evidence Deep Link */}
                  <button
                    onClick={() => {
                      setSelectedFindingId(a.finding_id);
                      navigate('evidence');
                    }}
                    className="mt-3.5 px-3 py-1.5 text-xs font-mono rounded border border-slate-700 bg-slate-900 text-slate-300 hover:bg-slate-800 flex items-center space-x-1 transition-all"
                  >
                    <span>Inspect Evidence</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      )}

      {/* Collaborative Notes Modal */}
      {activeFinding && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
          <div className="bg-slate-950 border border-slate-800 rounded-xl max-w-2xl w-full p-6 space-y-4 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <span className="text-xs font-mono text-indigo-400 font-bold">{activeFinding.finding_id}</span>
                <h3 className="text-base font-bold text-slate-100">{activeFinding.title}</h3>
              </div>
              <button
                onClick={() => setActiveFinding(null)}
                className="text-slate-500 hover:text-slate-300 font-mono text-sm px-2 py-1"
              >
                ✕
              </button>
            </div>

            {/* Existing Audit Notes */}
            <div className="space-y-2">
              <label className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                <span>Audit & Investigation History</span>
              </label>
              <div className="max-h-60 overflow-y-auto space-y-2 bg-slate-900/90 border border-slate-800 rounded-lg p-3 font-mono text-xs text-slate-300">
                {activeFinding.team_notes ? (
                  activeFinding.team_notes.split('\n').map((line, idx) => (
                    <div key={idx} className="pb-1.5 border-b border-slate-800/50 last:border-0 last:pb-0">
                      {line}
                    </div>
                  ))
                ) : (
                  <p className="text-slate-500 italic">No notes logged for this finding yet.</p>
                )}
              </div>
            </div>

            {/* Add New Note */}
            <form onSubmit={handleAddNote} className="space-y-3">
              <label className="text-xs font-mono uppercase tracking-wider text-slate-400">
                Append SecOps Audit Note
              </label>
              <textarea
                rows={3}
                value={newNote}
                onChange={e => setNewNote(e.target.value)}
                placeholder="Document reproduction steps, patch review notes, or verification timestamps..."
                className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 placeholder-slate-500 font-mono focus:outline-none focus:border-indigo-500"
              />
              <div className="flex flex-col sm:flex-row justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setActiveFinding(null)}
                  className="px-3 py-1.5 text-xs font-mono rounded border border-slate-800 text-slate-400 hover:bg-slate-900 justify-center text-center"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingNote || !newNote.trim()}
                  className="px-4 py-1.5 text-xs font-mono rounded bg-indigo-600 hover:bg-indigo-500 text-white font-medium flex items-center justify-center space-x-1.5 disabled:opacity-50"
                >
                  <Send className="w-3 h-3 flex-shrink-0" />
                  <span>{submittingNote ? 'Saving...' : 'Commit Note'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Module Limitations Banner */}
      <div className="border border-slate-800/80 rounded-lg p-3 bg-slate-950/40 text-xs text-slate-500 font-mono flex items-start space-x-2">
        <AlertCircle className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-400">Module Scope & Limitations:</strong> Team Desk provides an on-premise, tamper-evident collaboration ledger stored in SQLite with Audit Trail integration. Finding assignments and triage transitions do not push to external cloud SaaS ticketing systems (e.g. Jira/ServiceNow) when running in isolated USB/air-gapped environments.
        </div>
      </div>
    </div>
  );
};
