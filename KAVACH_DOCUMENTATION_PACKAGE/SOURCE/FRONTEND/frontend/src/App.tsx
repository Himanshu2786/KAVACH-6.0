import React, { useState } from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Navbar } from './components/layout/Navbar';
import { WorkspaceSubnav } from './components/layout/WorkspaceSubnav';
import { DemoJourneyBar } from './components/layout/DemoJourneyBar';
import { LoadingScreen } from './components/common/LoadingScreen';
import { ToastContainer } from './components/common/ToastContainer';
import { AmbientBackground } from './components/visual/AmbientBackground';
import { CursorLight } from './components/visual/CursorLight';

// Application Views
import { HomePage } from './pages/HomePage';
import { CommandCenterPage } from './pages/CommandCenterPage';
import { WorldMonitorPage } from './pages/WorldMonitorPage';
import { NewAssessmentPage } from './pages/NewAssessmentPage';
import { DiscoveryPage } from './pages/DiscoveryPage';
import { AssessmentProgressPage } from './pages/AssessmentProgressPage';
import { FindingsPage } from './pages/FindingsPage';
import { FindingDetailPage } from './pages/FindingDetailPage';
import { KnowledgeCorrelationPage } from './pages/KnowledgeCorrelationPage';
import { AiAnalysisPage } from './pages/AiAnalysisPage';
import { EvidenceValidationPage } from './pages/EvidenceValidationPage';
import { RiskPrioritizationPage } from './pages/RiskPrioritizationPage';
import { RemediationCenterPage } from './pages/RemediationCenterPage';
import { SecurityReportPage } from './pages/SecurityReportPage';
import { AssessmentHistoryPage } from './pages/AssessmentHistoryPage';
import { SystemStatusPage } from './pages/SystemStatusPage';
import { SettingsPage } from './pages/SettingsPage';
import { GuidePage } from './pages/GuidePage';
import { PortableAssessmentPage } from './pages/PortableAssessmentPage';
import { TeamDeskPage } from './pages/TeamDeskPage';
import { ExperienceDbPage } from './pages/ExperienceDbPage';
import { TestCenterPage } from './pages/TestCenterPage';
import { AuditTrailPage } from './pages/AuditTrailPage';
import { UrlSecurityCheckPage } from './pages/UrlSecurityCheckPage';
import { OwnerAdminPage } from './pages/OwnerAdminPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './components/auth/LoginPage';

const AppContent: React.FC = () => {
  const { isLoadingBoot, activePage } = useApp();
  const { user, isAuthenticated, isLoadingAuth } = useAuth();
  const [showDemoBar, setShowDemoBar] = useState(false);

  const rawUserId = user?.id || (user as any)?.user?.id || user?.username || '';
  const isOwner = Boolean(
    user?.role === 'DEVELOPER_OWNER' ||
    user?.role === 'admin' ||
    user?.role === 'ADMIN' ||
    (user as any)?.user?.role === 'DEVELOPER_OWNER' ||
    (user as any)?.user?.role === 'admin' ||
    (rawUserId && rawUserId.toUpperCase().startsWith('ADMIN'))
  );

  if (isLoadingBoot || isLoadingAuth) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const renderActivePage = () => {
    switch (activePage) {
      case 'home':
        return <HomePage />;
      case 'url-check':
        return <UrlSecurityCheckPage />;
      case 'guide':
        return <GuidePage />;
      case 'portable-assessment':
        return <PortableAssessmentPage />;
      case 'command-center':
        return <CommandCenterPage />;
      case 'world-monitor':
      case 'world_monitor':
      case 'situational-monitor':
        return <WorldMonitorPage />;
      case 'new-assessment':
        return <NewAssessmentPage />;
      case 'discovery':
        return <DiscoveryPage />;
      case 'progress':
        return <AssessmentProgressPage />;
      case 'findings':
        return <FindingsPage />;
      case 'finding-detail':
        return <FindingDetailPage />;
      case 'knowledge':
        return <KnowledgeCorrelationPage />;
      case 'ai-analysis':
        return <AiAnalysisPage />;
      case 'evidence':
        return <EvidenceValidationPage />;
      case 'risk':
        return <RiskPrioritizationPage />;
      case 'remediation':
        return <RemediationCenterPage />;
      case 'report':
        return <SecurityReportPage />;
      case 'history':
        return <AssessmentHistoryPage />;
      case 'system-status':
        return <SystemStatusPage />;
      case 'team-desk':
        return <TeamDeskPage />;
      case 'experience-db':
        return <ExperienceDbPage />;
      case 'test-center':
        return <TestCenterPage />;
      case 'audit-trail':
        return <AuditTrailPage />;
      case 'settings':
        return <SettingsPage />;
      case 'owner-admin':
      case 'admin':
        if (!isOwner) {
          return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6 animate-in fade-in duration-200">
              <div className="w-16 h-16 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center mb-4 text-rose-400">
                <span className="font-mono text-xl font-bold">403</span>
              </div>
              <h2 className="text-xl font-bold text-white mb-2">Access Denied: Owner / Developer Only</h2>
              <p className="text-sm text-neutral-400 max-w-md mb-6">
                Your current account ({user?.id || 'TEAM_USER'}) is not authorized to access Developer / Owner Admin controls.
              </p>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white font-mono text-xs cursor-pointer transition-all"
              >
                Return to Command Center
              </button>
            </div>
          );
        }
        return <OwnerAdminPage />;
      default:
        return <HomePage />;
    }
  };

  // Guide is standalone-scrollable (overflows on its own), Home is cinematic (no scroll)
  const isStandalonePage = activePage === 'home';
  const isScrollablePage = activePage === 'guide';

  return (
    /* Use CSS variable --app-height (dvh-aware, set in index.html) for correct mobile height */
    <div
      className="w-full bg-[#000000] text-neutral-100 font-sans flex flex-col relative overflow-hidden"
      style={{ height: "var(--app-height, 100vh)", backgroundColor: "#000000" }}
    >
      {/* 5-Layer Deep Cinematic Background */}
      <AmbientBackground />
      {/* Subtle Pointer Light Reflection Listener */}
      <CursorLight />

      {/* Modern iOS Glass Navigation Bar */}
      <Navbar />

      {/* Subnav for Workspace & Security Modules — hidden on Home & Guide */}
      {!isStandalonePage && !isScrollablePage && <WorkspaceSubnav />}

      {/* Main Dynamic Viewport */}
      <main
        className={
          isStandalonePage
            ? 'flex-1 w-full min-h-0 overflow-hidden'
            : 'flex-1 w-full overflow-y-auto overscroll-y-contain'
        }
      >
        <div
          className={
            isStandalonePage
              ? 'w-full h-full min-h-0 overflow-hidden'
              : 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 pb-24'
          }
        >
          {renderActivePage()}
        </div>
      </main>

      {/* Hackathon Demo Journey Bar — positioned with safe-area bottom offset */}
      <div
        className="fixed right-3 z-40"
        style={{ bottom: "max(1rem, calc(0.5rem + env(safe-area-inset-bottom, 0px)))" }}
      >
        {showDemoBar ? (
          <div className="relative rounded-xl border border-white/[0.12] bg-neutral-950/95 backdrop-blur-xl shadow-2xl p-2.5 w-[min(calc(100vw-1.5rem),32rem)]">
            <div className="flex items-center justify-between pb-1.5 px-1 border-b border-white/[0.06] text-[10px] font-mono text-neutral-400">
              <span className="font-semibold text-neutral-300">SIH Hackathon Presentation Bar</span>
              <button
                onClick={() => setShowDemoBar(false)}
                aria-label="Close demo bar"
                className="text-neutral-400 hover:text-white p-0.5 cursor-pointer text-xs"
              >
                ✕
              </button>
            </div>
            <div className="pt-2">
              <DemoJourneyBar />
            </div>
          </div>
        ) : (
          <button
            onClick={() => setShowDemoBar(true)}
            title="Open the SIH Hackathon guided demo flow"
            aria-label="Open Enterprise Demo Flow"
            className="flex items-center space-x-1.5 px-3 py-2 rounded-full bg-neutral-900/90 border border-white/[0.1] hover:border-white/30 text-neutral-300 hover:text-white text-xs font-mono backdrop-blur-md shadow-lg transition-all min-h-[40px]"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse flex-shrink-0" />
            <span>Enterprise Demo Flow</span>
          </button>
        )}
      </div>

      {/* Non-blocking Global Toast Notification Container */}
      <ToastContainer />
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <AppProvider>
        <AppContent />
      </AppProvider>
    </AuthProvider>
  );
}
