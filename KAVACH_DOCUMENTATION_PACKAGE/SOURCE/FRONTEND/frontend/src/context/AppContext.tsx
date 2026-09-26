import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Assessment, Finding, OllamaStatus, SystemStatus, ToastMessage, UrlAssessmentResult, UrlFinding } from '../types';
import { api } from '../services/api';

interface UrlAssessmentState {
  /** The full result from the last URL scan */
  result: UrlAssessmentResult | null;
  /** Whether the user has viewed the Findings page since last scan */
  findingsViewed: boolean;
  /** Whether the user has viewed the Evidence page since last scan */
  evidenceViewed: boolean;
  /** The selected finding ID within the URL assessment (for Evidence filter) */
  selectedUrlFindingId: string | null;
}

interface AppContextType {
  activeAssessment: Assessment | null;
  assessments: Assessment[];
  selectedFindingId: string | null;
  activePage: string;
  ollamaStatus: OllamaStatus | null;
  systemStatus: SystemStatus | null;
  isDemoMode: boolean;
  isLoadingBoot: boolean;
  presentationStep: number;
  toasts: ToastMessage[];

  /** URL-specific assessment state — drives glow badges */
  urlAssessmentState: UrlAssessmentState;
  /** Count of URL findings from last scan (0 if none) */
  urlFindingsCount: number;
  /** Count of URL evidence items from last scan (0 if none) */
  urlEvidenceCount: number;

  /** Selected World Monitor Event ID (for cross-module navigation) */
  selectedWorldEventId: string | null;
  setSelectedWorldEventId: (id: string | null) => void;

  setActiveAssessment: (assessment: Assessment | null) => void;
  setSelectedFindingId: (id: string | null) => void;
  navigate: (page: string, findingId?: string | null) => void;
  setIsDemoMode: (val: boolean) => void;
  setPresentationStep: (step: number) => void;
  finishBootLoading: () => void;
  showToast: (type: 'success' | 'error' | 'info' | 'warning', title: string, message: string) => void;
  dismissToast: (id: string) => void;
  refreshData: () => Promise<void>;

  /** Called by UrlSecurityCheckPage after a successful scan */
  setUrlAssessmentResult: (result: UrlAssessmentResult) => void;
  /** Called by UrlSecurityCheckPage when a new scan starts — resets previous results */
  clearUrlAssessment: () => void;
  /** Mark findings as viewed (softens glow) */
  markUrlFindingsViewed: () => void;
  /** Mark evidence as viewed (softens glow) */
  markUrlEvidenceViewed: () => void;
  /** Set the selected URL finding ID so Evidence page can auto-filter */
  setSelectedUrlFindingId: (id: string | null) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const EMPTY_URL_STATE: UrlAssessmentState = {
  result: null,
  findingsViewed: false,
  evidenceViewed: false,
  selectedUrlFindingId: null,
};

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeAssessment, setActiveAssessmentState] = useState<Assessment | null>(null);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [selectedFindingId, setSelectedFindingId] = useState<string | null>(null);
  const [activePage, setActivePage] = useState<string>('home');
  const [ollamaStatus, setOllamaStatus] = useState<OllamaStatus | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isDemoMode, setIsDemoMode] = useState<boolean>(false);
  const [isLoadingBoot, setIsLoadingBoot] = useState<boolean>(true);
  const [presentationStep, setPresentationStep] = useState<number>(0);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const setActiveAssessment = useCallback((asm: Assessment | null) => {
    setActiveAssessmentState(asm);
    if (asm) {
      try {
        localStorage.setItem('kavach_active_assessment_id', asm.id);
      } catch {}
      setIsDemoMode(Boolean(asm.is_demo));
    } else {
      try {
        localStorage.removeItem('kavach_active_assessment_id');
      } catch {}
    }
    setSelectedFindingId(null);
  }, []);

  // ── URL Assessment state ─────────────────────────────────────────────────
  const [urlAssessmentState, setUrlAssessmentState] = useState<UrlAssessmentState>(EMPTY_URL_STATE);

  const urlFindingsCount = urlAssessmentState.result?.findings?.length ?? 0;
  // Each finding has exactly 1 embedded evidence object
  const urlEvidenceCount = urlAssessmentState.result?.findings?.filter(
    (f) => f.evidence && f.evidence.raw_observation
  ).length ?? 0;

  const setUrlAssessmentResult = useCallback((result: UrlAssessmentResult) => {
    setUrlAssessmentState({
      result,
      findingsViewed: false,
      evidenceViewed: false,
      selectedUrlFindingId: null,
    });
  }, []);

  const clearUrlAssessment = useCallback(() => {
    setUrlAssessmentState(EMPTY_URL_STATE);
  }, []);

  const markUrlFindingsViewed = useCallback(() => {
    setUrlAssessmentState((prev) => ({ ...prev, findingsViewed: true }));
  }, []);

  const markUrlEvidenceViewed = useCallback(() => {
    setUrlAssessmentState((prev) => ({ ...prev, evidenceViewed: true }));
  }, []);

  const setSelectedUrlFindingId = useCallback((id: string | null) => {
    setUrlAssessmentState((prev) => ({ ...prev, selectedUrlFindingId: id }));
  }, []);

  // ── Toasts ───────────────────────────────────────────────────────────────
  const showToast = (type: 'success' | 'error' | 'info' | 'warning', title: string, message: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => dismissToast(id), 5000);
  };

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // ── Navigation ──────────────────────────────────────────────────────────
  const navigate = (page: string, findingId?: string | null) => {
    setActivePage(page);
    if (findingId !== undefined) {
      setSelectedFindingId(findingId);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const finishBootLoading = () => {
    setIsLoadingBoot(false);
  };

  // ── Backend data refresh ─────────────────────────────────────────────────
  const refreshData = async () => {
    try {
      // Fire quick Ollama status check immediately so UI updates without waiting for DB
      api.getOllamaStatus()
        .then(o => { if (o) setOllamaStatus(o); })
        .catch(() => {});

      const [asms, wmLatest, oStatus, sStatus] = await Promise.all([
        api.getAssessments().catch(() => []),
        api.getLatestWorldMonitorAssessment().catch(() => null),
        api.getOllamaStatus().catch(() => ({
          status: 'offline',
          base_url: 'http://localhost:11434',
          available_models: [],
          selected_model: 'phi3',
          message: 'Service unreachable'
        } as OllamaStatus)),
        api.getSystemStatus().catch(() => null)
      ]);

      setAssessments(asms);

      const savedId = typeof window !== 'undefined' ? localStorage.getItem('kavach_active_assessment_id') : null;
      const targetId = activeAssessment?.id || savedId;
      const currentMatched = targetId ? asms.find(a => a.id === targetId) : null;

      if (currentMatched) {
        setActiveAssessmentState(currentMatched);
        setIsDemoMode(Boolean(currentMatched.is_demo));
      } else if (wmLatest && wmLatest.assessment_id && wmLatest.status !== 'NO_ASSESSMENT_RUN') {
        const matched = asms.find(a => a.id === wmLatest.assessment_id);
        const resolved: Assessment = matched ? {
          ...matched,
          total_findings: wmLatest.total_findings ?? matched.total_findings,
          confirmed_findings: wmLatest.confirmed_findings ?? matched.confirmed_findings,
          assessment_type: wmLatest.assessment_type || matched.assessment_type || 'WORLD_MONITOR_EMPIRICAL'
        } : {
          id: wmLatest.assessment_id,
          name: wmLatest.name || `World Monitor Assessment ${wmLatest.assessment_id}`,
          target_url: wmLatest.target_url,
          description: wmLatest.summary || '',
          environment: 'World Monitor Target Scope',
          scope: wmLatest.scope || 'Full Application',
          authorization_confirmed: true,
          modules_enabled: ['Authentication', 'API Security', 'Security Headers'],
          status: wmLatest.status || 'COMPLETED',
          progress: 100,
          current_stage: 'REPORT',
          started_at: wmLatest.started_at || '',
          completed_at: wmLatest.completed_at || '',
          is_demo: false,
          assessment_type: 'WORLD_MONITOR_EMPIRICAL',
          total_findings: wmLatest.total_findings ?? 1,
          confirmed_findings: wmLatest.confirmed_findings ?? 1,
        };
        setActiveAssessmentState(resolved);
        setIsDemoMode(Boolean(resolved.is_demo));
        try {
          localStorage.setItem('kavach_active_assessment_id', resolved.id);
        } catch {}
      } else if (asms.length > 0) {
        setActiveAssessmentState(asms[0]);
        setIsDemoMode(Boolean(asms[0].is_demo));
      }
      setOllamaStatus(oStatus);
      setSystemStatus(sStatus);
    } catch (err) {
      console.error("Failed to load initial platform data:", err);
    }
  };

  useEffect(() => {
    refreshData();
    const timer = setInterval(() => {
      api.getOllamaStatus()
        .then(setOllamaStatus)
        .catch(() => {});
    }, 15000);
    return () => clearInterval(timer);
  }, []);

  const [selectedWorldEventId, setSelectedWorldEventId] = useState<string | null>(null);

  return (
    <AppContext.Provider
      value={{
        activeAssessment,
        assessments,
        selectedFindingId,
        activePage,
        ollamaStatus,
        systemStatus,
        isDemoMode,
        isLoadingBoot,
        presentationStep,
        toasts,
        urlAssessmentState,
        urlFindingsCount,
        urlEvidenceCount,
        selectedWorldEventId,
        setSelectedWorldEventId,
        setActiveAssessment,
        setSelectedFindingId,
        navigate,
        setIsDemoMode,
        setPresentationStep,
        finishBootLoading,
        showToast,
        dismissToast,
        refreshData,
        setUrlAssessmentResult,
        clearUrlAssessment,
        markUrlFindingsViewed,
        markUrlEvidenceViewed,
        setSelectedUrlFindingId,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
