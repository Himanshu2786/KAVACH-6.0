import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Search, 
  Filter, 
  Download, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Hash, 
  Layers, 
  Code2, 
  FileSpreadsheet,
  Info,
  RefreshCw,
  ExternalLink
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { AuditEvent } from '../types';

export const AuditTrailPage: React.FC = () => {
  const { activeAssessment, showToast } = useApp();
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedModule, setSelectedModule] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [expandedEventId, setExpandedEventId] = useState<number | null>(null);
  const [scopeToActive, setScopeToActive] = useState<boolean>(Boolean(activeAssessment));

  const fetchAuditEvents = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditTrail({
        assessment_id: scopeToActive && activeAssessment ? activeAssessment.id : undefined,
        module: selectedModule !== 'ALL' ? selectedModule : undefined,
        status: selectedStatus !== 'ALL' ? selectedStatus : undefined,
        limit: 100
      });
      setEvents(data);
    } catch {
      showToast('error', 'Error', 'Failed to retrieve audit log.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditEvents();
  }, [selectedModule, selectedStatus, scopeToActive, activeAssessment]);

  const filteredEvents = events.filter(e => {
    const q = searchQuery.toLowerCase();
    return (
      e.description.toLowerCase().includes(q) ||
      e.event_type.toLowerCase().includes(q) ||
      (e.module && e.module.toLowerCase().includes(q)) ||
      (e.evidence_id && e.evidence_id.toLowerCase().includes(q)) ||
      (e.assessment_id && e.assessment_id.toLowerCase().includes(q))
    );
  });

  const handleExportJson = () => {
    const blob = new Blob([JSON.stringify(filteredEvents, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `kavach_audit_trail_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('success', 'Export Complete', 'Audit log exported as JSON.');
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return (
          <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 font-bold flex items-center space-x-1">
            <CheckCircle2 className="w-2.5 h-2.5" />
            <span>SUCCESS</span>
          </span>
        );
      case 'DENIED':
        return (
          <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-amber-950/80 text-amber-400 border border-amber-800/60 font-bold flex items-center space-x-1">
            <AlertTriangle className="w-2.5 h-2.5" />
            <span>DENIED</span>
          </span>
        );
      case 'FAILED':
        return (
          <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-rose-950/80 text-rose-400 border border-rose-800/60 font-bold flex items-center space-x-1">
            <XCircle className="w-2.5 h-2.5" />
            <span>FAILED</span>
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-slate-800 text-slate-300">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3 mb-1">
            <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <span>Module 10: Audit Trail</span>
            </h1>
            <Badge variant="outline">KAVACH Enterprise</Badge>
            <span className="px-2 py-0.5 text-xs font-mono rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
              TAMPER-EVIDENT
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Chronological, immutable audit ledger capturing every critical security event, probe execution, permission decision, and team action across KAVACH.
          </p>
        </div>

        <div className="flex flex-wrap items-center space-x-2">
          {activeAssessment && (
            <div className="flex items-center bg-slate-900 border border-slate-700 rounded-lg p-0.5 text-xs font-mono">
              <button
                onClick={() => setScopeToActive(true)}
                className={`px-2.5 py-1 rounded transition-colors ${
                  scopeToActive ? 'bg-emerald-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Active ({activeAssessment.id})
              </button>
              <button
                onClick={() => setScopeToActive(false)}
                className={`px-2.5 py-1 rounded transition-colors ${
                  !scopeToActive ? 'bg-slate-700 text-slate-100 font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                All Events
              </button>
            </div>
          )}

          <button
            onClick={fetchAuditEvents}
            disabled={loading}
            className="px-3 py-1.5 text-xs font-mono rounded border border-slate-700 bg-slate-900 text-slate-300 hover:bg-slate-800 flex items-center space-x-1.5 cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>

          <button
            onClick={handleExportJson}
            disabled={filteredEvents.length === 0}
            className="px-3 py-1.5 text-xs font-mono rounded border border-emerald-700/80 bg-emerald-950/40 text-emerald-300 hover:bg-emerald-900/50 flex items-center space-x-1.5 disabled:opacity-50 cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search event type, description, evidence hash, or assessment ID..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-mono"
          />
        </div>

        <select
          value={selectedModule}
          onChange={e => setSelectedModule(e.target.value)}
          className="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-lg px-3 py-2 font-mono focus:outline-none focus:border-emerald-500"
        >
          <option value="ALL">All Modules</option>
          <option value="CORE">CORE</option>
          <option value="WORLD_MONITOR">WORLD_MONITOR</option>
          <option value="PROCESSES">PROCESSES</option>
          <option value="APPLICATIONS">APPLICATIONS</option>
          <option value="NETWORK">NETWORK</option>
          <option value="SECURITY_PRODUCTS">SECURITY_PRODUCTS</option>
          <option value="EXPERIENCE_DB">EXPERIENCE_DB</option>
          <option value="TEAM_DESK">TEAM_DESK</option>
          <option value="TEST_CENTER">TEST_CENTER</option>
          <option value="PORTABLE_SCANNER">PORTABLE_SCANNER</option>
        </select>

        <select
          value={selectedStatus}
          onChange={e => setSelectedStatus(e.target.value)}
          className="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-lg px-3 py-2 font-mono focus:outline-none focus:border-emerald-500"
        >
          <option value="ALL">All Statuses</option>
          <option value="SUCCESS">SUCCESS</option>
          <option value="DENIED">DENIED</option>
          <option value="FAILED">FAILED</option>
        </select>
      </div>

      {/* Audit Log Table */}
      {loading ? (
        <div className="text-center py-12 text-slate-500 font-mono text-sm">
          Loading audit records from database...
        </div>
      ) : filteredEvents.length === 0 ? (
        <GlassCard className="p-8 text-center border-slate-800">
          <Clock className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <p className="text-slate-400 text-sm font-mono">No audit events match the query.</p>
        </GlassCard>
      ) : (
        <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950/60 shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="p-3">Timestamp</th>
                  <th className="p-3">Module</th>
                  <th className="p-3">Event Type</th>
                  <th className="p-3">Description</th>
                  <th className="p-3">Evidence ID</th>
                  <th className="p-3 text-center">Status</th>
                  <th className="p-3 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredEvents.map(e => (
                  <React.Fragment key={e.id}>
                    <tr className="hover:bg-slate-900/40 transition-colors">
                      <td className="p-3 text-slate-400 whitespace-nowrap">{e.timestamp}</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-indigo-300 border border-slate-700 font-bold">
                          {e.module || 'CORE'}
                        </span>
                      </td>
                      <td className="p-3 text-emerald-400 font-bold">{e.event_type}</td>
                      <td className="p-3 text-slate-200 max-w-xs sm:max-w-md truncate">{e.description}</td>
                      <td className="p-3">
                        {e.evidence_id ? (
                          <span className="text-amber-400 flex items-center space-x-1">
                            <Hash className="w-3 h-3" />
                            <span>{e.evidence_id}</span>
                          </span>
                        ) : (
                          <span className="text-slate-600">—</span>
                        )}
                      </td>
                      <td className="p-3 text-center">{getStatusBadge(e.status || 'SUCCESS')}</td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => setExpandedEventId(expandedEventId === e.id ? null : e.id)}
                          className="text-indigo-400 hover:text-indigo-300 font-bold"
                        >
                          {expandedEventId === e.id ? 'Close' : 'View'}
                        </button>
                      </td>
                    </tr>

                    {/* Expandable Metadata JSON Drawer */}
                    {expandedEventId === e.id && (
                      <tr className="bg-slate-900/70">
                        <td colSpan={7} className="p-4 space-y-2 border-t border-slate-800">
                          <div className="flex items-center justify-between text-[11px] text-slate-400">
                            <span>Event Details & Forensic Metadata</span>
                            <span>Assessment: {e.assessment_id || 'System-Wide'}</span>
                          </div>
                          <pre className="p-3 rounded bg-slate-950 border border-slate-800 text-[11px] text-emerald-300 overflow-x-auto max-h-48">
                            {JSON.stringify(JSON.parse(e.metadata_json || '{}'), null, 2)}
                          </pre>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Scope and Guarantee Footer */}
      <div className="border border-slate-800/80 rounded-lg p-3 bg-slate-900/30 text-xs text-slate-500 font-mono flex items-start space-x-2">
        <Info className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-400">Tamper-Evident Logging Guarantee:</strong> All actions affecting security posture, finding assignment, false-positive classification, and test suite execution are written chronologically to the local database with timestamps and SHA-256 evidence links.
        </div>
      </div>
    </div>
  );
};
