import { createContext, useContext, useState, useCallback } from "react"

const ToastCtx = createContext(null)

const ICONS = {
  success: (
    <div className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0"
      style={{ background: "rgba(16,185,129,0.15)" }}>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5">
        <polyline points="20 6 9 17 4 12"/>
      </svg>
    </div>
  ),
  error: (
    <div className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0"
      style={{ background: "rgba(239,68,68,0.12)" }}>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2.5">
        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </div>
  ),
  info: (
    <div className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0"
      style={{ background: "rgba(178,69,110,0.12)" }}>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#B2456E" strokeWidth="2.5">
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
    </div>
  ),
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const toast = useCallback(({ message, type = "info", duration = 3500 }) => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type, exiting: false }])
    setTimeout(() => {
      setToasts(prev => prev.map(t => t.id === id ? { ...t, exiting: true } : t))
      setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 220)
    }, duration)
  }, [])

  const dismiss = (id) => {
    setToasts(prev => prev.map(t => t.id === id ? { ...t, exiting: true } : t))
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 220)
  }

  return (
    <ToastCtx.Provider value={toast}>
      {children}

      {/* Toast container */}
      <div className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-2.5 pointer-events-none"
        style={{ maxWidth: 360 }}>
        {toasts.map(t => (
          <div key={t.id}
            className={`${t.exiting ? "toast-exit" : "toast-enter"} pointer-events-auto flex items-start gap-3 px-4 py-3.5 rounded-2xl shadow-xl`}
            style={{
              background: "#FFF8F6",
              border: "1px solid rgba(85,38,25,0.12)",
              boxShadow: "0 8px 32px rgba(85,38,25,0.14)",
            }}>
            {ICONS[t.type]}
            <p className="text-sm font-semibold flex-1 leading-snug" style={{ color: "#2C1810" }}>
              {t.message}
            </p>
            <button onClick={() => dismiss(t.id)}
              className="w-5 h-5 flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5 transition-opacity hover:opacity-50"
              style={{ color: "#8B6355" }}>×</button>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  )
}

export function useToast() {
  return useContext(ToastCtx)
}
