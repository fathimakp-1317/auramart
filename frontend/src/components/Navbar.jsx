import { Link, useNavigate } from "react-router-dom"
import { useEffect, useState, useRef } from "react"
import api from "../api"

const C = {
  pink:       "#FBEAE7",
  pinkDark:   "#F5D0C8",
  berry:      "#B2456E",
  berryDark:  "#8F3457",
  berryLight: "#C96B8A",
  choc:       "#552619",
  chocolight: "#7A3A26",
  dark:       "#2C1810",
  darkSoft:   "#4A2C1E",
  darkLight:  "#8B6355",
  white:      "#FFF8F6",
  line:       "rgba(85,38,25,0.10)",
  lineStrong: "rgba(85,38,25,0.18)",
}

const NAV_LINKS = [
  { label:"Electronics",q:"electronics"},{ label:"Mobiles",q:"smartphone"},
  { label:"Laptops",q:"laptop"},{ label:"Fashion",q:"fashion"},
  { label:"Home",q:"home"},{ label:"Sports",q:"sports"},
  { label:"Beauty",q:"beauty"},{ label:"Books",q:"book"},
]

export default function Navbar() {
  const navigate   = useNavigate()
  const token      = localStorage.getItem("token")
  const email      = localStorage.getItem("email")
  const role       = localStorage.getItem("role")

  const [query,       setQuery]       = useState("")
  const [suggestions, setSuggestions] = useState([])
  const [showSuggest, setShowSuggest] = useState(false)
  const [unread,      setUnread]      = useState(0)
  const [notifOpen,   setNotifOpen]   = useState(false)
  const [notifs,      setNotifs]      = useState([])
  const [notifLoad,   setNotifLoad]   = useState(false)
  const [acctOpen,    setAcctOpen]    = useState(false)
  const [searchFocus, setSearchFocus] = useState(false)
  const [cartCount,   setCartCount]   = useState(0)
  const suggestTimer = useRef(null)
  const acctRef      = useRef(null)
  const notifRef     = useRef(null)

  useEffect(() => {
    if (!token) return
    const fetchNotifs = () => api.get("/notifications/notifications/unread").then(r => setUnread(r.data.unread)).catch(()=>{})
    const fetchCart   = () => api.get("/cart/cart").then(r => setCartCount(r.data.reduce((s,i) => s + i.quantity, 0))).catch(()=>{})
    fetchNotifs(); fetchCart()
    const t = setInterval(() => { fetchNotifs(); fetchCart() }, 30000)
    return () => clearInterval(t)
  }, [token])

  useEffect(() => {
    const h = (e) => {
      if (acctRef.current  && !acctRef.current.contains(e.target))  setAcctOpen(false)
      if (notifRef.current && !notifRef.current.contains(e.target)) setNotifOpen(false)
    }
    document.addEventListener("mousedown", h); return () => document.removeEventListener("mousedown", h)
  }, [])

  const onSearch = (q) => {
    setQuery(q); clearTimeout(suggestTimer.current)
    if (q.length < 2) { setSuggestions([]); setShowSuggest(false); return }
    suggestTimer.current = setTimeout(async () => {
      try { const r = await api.get(`/search/suggest?q=${encodeURIComponent(q)}`); setSuggestions(r.data); setShowSuggest(r.data.length>0) }
      catch { setSuggestions([]) }
    }, 250)
  }

  const doSearch = (q) => { setShowSuggest(false); setQuery(q); navigate(`/products?q=${encodeURIComponent(q)}`) }

  const openNotifs = async () => {
    if (notifOpen) { setNotifOpen(false); return }
    setNotifOpen(true); setNotifLoad(true)
    try {
      const r = await api.get("/notifications/notifications"); setNotifs(r.data)
      await api.post("/notifications/notifications/read"); setUnread(0)
    } catch {} finally { setNotifLoad(false) }
  }

  const logout = () => { localStorage.clear(); setAcctOpen(false); navigate("/login") }

  return (
    <header className="sticky top-0 z-50" style={{ background: C.choc, boxShadow: "0 1px 0 rgba(44,44,44,0.08)" }}>

      {/* ── Main bar ── */}
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-2 sm:gap-4">

        {/* Logo */}
        <Link to="/" className="flex-shrink-0">
          <span className="text-lg sm:text-xl font-black tracking-tight flex-shrink-0" style={{ fontFamily:"Georgia, serif", color:C.white }}>
            Shop<span style={{ color: C.berry }}>Sphere</span>
          </span>
        </Link>

        {/* Search */}
        <div className="flex-1 relative max-w-2xl min-w-0">
          <div className="flex rounded-xl overflow-hidden"
            style={{ background: "rgba(255,255,255,0.18)", border: `1.5px solid ${searchFocus ? C.white : "rgba(255,255,255,0.2)"}`, transition:"border-color 0.15s" }}>
            <input type="text" value={query}
              onChange={e => onSearch(e.target.value)}
              onKeyDown={e => { if(e.key==="Enter") doSearch(query); if(e.key==="Escape") setShowSuggest(false) }}
              onFocus={() => { setSearchFocus(true); suggestions.length>0 && setShowSuggest(true) }}
              onBlur={() => setSearchFocus(false)}
              placeholder="Search products, brands and more…"
              className="flex-1 px-4 py-2.5 text-sm outline-none bg-transparent"
              style={{ color: C.white }}
            />
            <button onClick={() => doSearch(query)}
              className="px-5 flex items-center gap-2 text-sm font-bold flex-shrink-0 transition-opacity hover:opacity-85"
              style={{ background: C.choc, color: C.white }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
              </svg>
              <span className="hidden md:block">Search</span>
            </button>
          </div>

          {showSuggest && (
            <div className="absolute top-full left-0 right-0 mt-1.5 rounded-xl shadow-xl overflow-hidden z-50"
              style={{ background: C.white, border: `1px solid ${C.line}` }}>
              {suggestions.map((s,i) => (
                <button key={i} onClick={() => { setSuggestions([]); setShowSuggest(false); doSearch(s.name) }}
                  className="w-full text-left px-4 py-3 text-sm flex justify-between items-center transition-colors hover:bg-rose-50"
                  style={{ color:C.dark, borderBottom:i<suggestions.length-1?`1px solid ${C.line}`:"none" }}>
                  <span className="flex items-center gap-2">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={C.darkLight} strokeWidth="2">
                      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                    </svg>
                    {s.name}
                  </span>
                  <span className="text-xs font-semibold" style={{ color:C.choc }}>₹{s.price}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right icons */}
        <div className="flex items-center gap-1 flex-shrink-0">

          {token ? (
            <div className="relative" ref={acctRef}>
              <button onClick={() => setAcctOpen(o=>!o)}
                className="flex items-center gap-2 px-3 py-2 rounded-xl transition-all hover:opacity-80"
                style={{ background: acctOpen ? "rgba(255,255,255,0.15)" : "transparent" }}>
                <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-black flex-shrink-0"
                  style={{ background: C.choc, color: C.white }}>
                  {email?.[0]?.toUpperCase()}
                </div>
                <span className="text-xs font-semibold hidden sm:block max-w-20 truncate" style={{ color: C.white }}>
                  {email?.split("@")[0]}
                </span>
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.7)" strokeWidth="2.5"
                  className={`transition-transform ${acctOpen?"rotate-180":""}`}>
                  <path d="m6 9 6 6 6-6"/>
                </svg>
              </button>

              {acctOpen && (
                <div className="absolute right-0 top-full mt-2 w-52 rounded-2xl shadow-2xl overflow-hidden z-50"
                  style={{ background: C.white, border:`1px solid ${C.line}` }}>
                  <div className="px-4 py-3" style={{ borderBottom:`1px solid ${C.line}` }}>
                    <p className="text-xs font-semibold truncate" style={{ color:C.dark }}>{email}</p>
                    {role==="vendor" && (
                      <span className="inline-block mt-1 text-xs px-2 py-0.5 rounded-full font-bold"
                        style={{ background:C.berry, color:C.white }}>Vendor</span>
                    )}
                    {role === "admin" && (
                      <span className="inline-block mt-1 text-xs px-2 py-0.5 rounded-full font-bold"
                        style={{ background: "#2C1810", color: C.white }}>Admin</span>
                    )}
                  </div>
                  <div className="py-1">
                    {role === "admin" && (
                      <Link to="/admin" onClick={() => setAcctOpen(false)}
                        className="block px-4 py-3 text-sm font-bold transition-all hover:opacity-70"
                        style={{ color: C.berry }}>
                         Admin Panel
                      </Link>
                    )}
                    
                    {role==="vendor" && (
                      <Link to="/vendor" onClick={() => setAcctOpen(false)}
                        className="flex items-center gap-2.5 px-4 py-2.5 text-sm transition-colors hover:bg-rose-50"
                        style={{ color:C.dark }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                          <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
                          <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
                        </svg>
                        Dashboard
                      </Link>
                    )}
                    {role==="customer" && (<>
                      <Link to="/profile" onClick={() => setAcctOpen(false)}
                        className="flex items-center gap-2.5 px-4 py-2.5 text-sm transition-colors hover:bg-rose-50" style={{ color:C.dark }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                        </svg>
                        My Profile
                      </Link>
                      <Link to="/orders" onClick={() => setAcctOpen(false)}
                        className="flex items-center gap-2.5 px-4 py-2.5 text-sm transition-colors hover:bg-rose-50" style={{ color:C.dark }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                          <polyline points="14 2 14 8 20 8"/>
                        </svg>
                        My Orders
                      </Link>
                    </>)}
                  </div>
                  <div style={{ borderTop:`1px solid ${C.line}` }}>
                    <button onClick={logout}
                      className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm transition-colors hover:bg-rose-50"
                      style={{ color:C.darkLight }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                        <polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
                      </svg>
                      Sign out
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link to="/login"
                className="px-4 py-2 text-sm font-semibold rounded-xl border transition-all hover:opacity-80"
                style={{ borderColor:"rgba(255,255,255,0.3)", color:C.white }}>Sign in</Link>
              <Link to="/register"
                className="px-4 py-2 text-sm font-bold rounded-xl transition-all hover:opacity-85"
                style={{ background:C.choc, color:C.white }}>Register</Link>
            </div>
          )}

          {token && role!=="vendor" && (
            <Link to="/cart" className="flex items-center gap-1.5 px-3 py-2 rounded-xl transition-all hover:opacity-80 relative"
              style={{ color:C.white }}>
              <div className="relative">
                <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
                  <line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/>
                </svg>
                {cartCount > 0 && (
                  <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full flex items-center justify-center font-bold"
                    style={{ background: C.berry, color: C.white, fontSize: 9 }}>
                    {cartCount > 9 ? "9+" : cartCount}
                  </span>
                )}
              </div>
              <span className="text-xs font-semibold hidden sm:block">Cart</span>
            </Link>
          )}

          {token && (
            <div className="relative" ref={notifRef}>
              <button onClick={openNotifs}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl transition-all hover:opacity-80"
                style={{ color:C.white, background:notifOpen?"rgba(255,255,255,0.15)":"transparent" }}>
                <div className="relative">
                  <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                    <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                  </svg>
                  {unread>0 && (
                    <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full flex items-center justify-center font-bold"
                      style={{ background:C.choc, color:C.white, fontSize:9 }}>
                      {unread>9?"9+":unread}
                    </span>
                  )}
                </div>
                <span className="text-xs font-semibold hidden sm:block">Alerts</span>
              </button>

              {notifOpen && (
                <div className="absolute right-0 top-full mt-2 w-80 rounded-2xl shadow-2xl overflow-hidden z-50"
                  style={{ background:C.white, border:`1px solid ${C.line}` }}>
                  <div className="flex justify-between items-center px-4 py-3.5" style={{ borderBottom:`1px solid ${C.line}` }}>
                    <span className="text-sm font-bold" style={{ color:C.dark }}>Notifications</span>
                    <button onClick={() => setNotifOpen(false)}
                      className="w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold transition-opacity hover:opacity-60"
                      style={{ background:C.pink, color:C.dark }}>×</button>
                  </div>
                  <div className="max-h-72 overflow-y-auto">
                    {notifLoad ? (
                      <p className="text-sm text-center py-8" style={{ color:C.darkLight }}>Loading…</p>
                    ) : notifs.length===0 ? (
                      <p className="text-sm text-center py-8" style={{ color:C.darkLight }}>No notifications yet</p>
                    ) : notifs.map((n,i) => (
                      <div key={i} className="px-4 py-3" style={{ borderBottom:i<notifs.length-1?`1px solid ${C.line}`:"none" }}>
                        <p className="text-sm" style={{ color:C.dark }}>{n.message}</p>
                        {n.total && <p className="text-xs mt-0.5 font-semibold" style={{ color:C.choc }}>₹{n.total?.toLocaleString("en-IN")}</p>}
                        <p className="text-xs mt-1" style={{ color:C.darkLight }}>{n.timestamp?new Date(n.timestamp).toLocaleString("en-IN"):""}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ── Category strip ── */}
      <div style={{ borderTop:"1px solid rgba(255,255,255,0.15)" }}>
        <div className="max-w-7xl mx-auto px-5">
          <div className="flex overflow-x-auto scrollbar-hide">
            {NAV_LINKS.map(c => (
              <button key={c.q} onClick={() => doSearch(c.q)}
                className="flex-shrink-0 px-4 py-2.5 text-xs font-semibold whitespace-nowrap transition-opacity hover:opacity-60"
                style={{ color:"rgba(255,255,255,0.75)" }}>
                {c.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </header>
  )
}
