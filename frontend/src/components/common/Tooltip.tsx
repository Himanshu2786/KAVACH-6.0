import React, { useState } from 'react';
import { Info } from 'lucide-react';

const DEFINITIONS: Record<string, { term: string; definition: string }> = {
  CWE: {
    term: "Common Weakness Enumeration",
    definition: "A community-developed taxonomy of software and hardware security weaknesses and design flaws."
  },
  OWASP: {
    term: "Open Worldwide Application Security Project",
    definition: "Non-profit foundation that establishes the industry-standard Top 10 critical security risks."
  },
  RAG: {
    term: "Retrieval-Augmented Generation",
    definition: "AI architecture that grounds LLM hypotheses in local authoritative security knowledge bases before reasoning."
  },
  CVSS: {
    term: "Common Vulnerability Scoring System",
    definition: "Standardized framework for rating the principal characteristics and severity of security vulnerabilities."
  },
  IDOR: {
    term: "Insecure Direct Object Reference",
    definition: "Access control flaw where direct references to backend database objects bypass authorization checks."
  },
  CSP: {
    term: "Content Security Policy",
    definition: "HTTP header layer allowing site administrators to declare approved sources of executable browser scripts."
  }
};

interface TooltipProps {
  keyword: 'CWE' | 'OWASP' | 'RAG' | 'CVSS' | 'IDOR' | 'CSP';
  label?: string;
}

export const Tooltip: React.FC<TooltipProps> = ({ keyword, label }) => {
  const [show, setShow] = useState(false);
  const data = DEFINITIONS[keyword] || { term: keyword, definition: "Security specification term." };

  return (
    <span className="relative inline-flex items-center">
      <span
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        className="inline-flex items-center space-x-1 cursor-help underline decoration-dotted decoration-cyan-400 text-cyan-300 hover:text-cyan-200"
      >
        <span>{label || keyword}</span>
        <Info className="w-3 h-3 text-cyan-400/80" />
      </span>

      {show && (
        <div className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 p-3 bg-slate-900/95 border border-cyan-500/40 rounded-lg shadow-xl text-left backdrop-blur-md pointer-events-none">
          <div className="text-xs font-bold text-cyan-300 uppercase tracking-wide mb-1">
            {keyword} — {data.term}
          </div>
          <div className="text-[11px] text-slate-300 leading-relaxed">
            {data.definition}
          </div>
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-cyan-500/40"></div>
        </div>
      )}
    </span>
  );
};
