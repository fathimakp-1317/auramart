import { useEffect, useState } from "react"

export default function ScrollToTop() {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 400)
    window.addEventListener("scroll", onScroll, { passive: true })
    return () => window.removeEventListener("scroll", onScroll)
  }, [])

  if (!visible) return null

  return (
    <button
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      className="fade-up fixed bottom-6 left-6 z-50 w-10 h-10 rounded-2xl flex items-center justify-center shadow-lg transition-all hover:scale-110 active:scale-95"
      style={{ background: "#552619", color: "#FBEAE7" }}
      title="Back to top"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
        <path d="M12 19V5M5 12l7-7 7 7"/>
      </svg>
    </button>
  )
}
