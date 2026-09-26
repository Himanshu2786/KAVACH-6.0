import React from 'react';
import { CheckCircle2, AlertTriangle, Info, XCircle, X } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const ToastContainer: React.FC = () => {
  const { toasts, dismissToast } = useApp();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col space-y-2.5 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => {
        const icon = {
          success: <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />,
          error: <XCircle className="w-4 h-4 text-rose-400 shrink-0" />,
          warning: <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />,
          info: <Info className="w-4 h-4 text-cyan-400 shrink-0" />
        }[toast.type];

        const borderColor = {
          success: 'border-emerald-500/40',
          error: 'border-rose-500/40',
          warning: 'border-amber-500/40',
          info: 'border-cyan-500/40'
        }[toast.type];

        return (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-start justify-between p-3.5 rounded-xl bg-slate-900/95 backdrop-blur-md border ${borderColor} shadow-2xl text-slate-100 transition-all duration-300`}
          >
            <div className="flex items-start space-x-2.5">
              <div className="mt-0.5">{icon}</div>
              <div>
                <div className="text-xs font-bold font-mono-code uppercase tracking-wide">
                  {toast.title}
                </div>
                <div className="text-xs text-slate-300 mt-0.5 leading-relaxed">
                  {toast.message}
                </div>
              </div>
            </div>
            <button
              onClick={() => dismissToast(toast.id)}
              className="text-slate-400 hover:text-slate-200 p-1 -mr-1 -mt-1 rounded"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
