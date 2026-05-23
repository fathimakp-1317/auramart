import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import api from "../api"

const C = {
  pink:       "#FBEAE7",
  pinkDark:   "#F5D0C8",
  berry:      "#B2456E",
  berryDark:  "#8F3457",
  choc:       "#552619",
  dark:       "#2C1810",
  darkLight:  "#8B6355",
  white:      "#FFF8F6",
  line:       "rgba(85,38,25,0.10)",
  lineStrong: "rgba(85,38,25,0.18)",
}

function Field({ label, type = "text", placeholder, value, onChange, onKeyDown, span2 = false }) {
  const [focused, setFocused] = useState(false)
  return (
    <div className={span2 ? "col-span-2" : ""}>
      <label className="block text-xs font-bold uppercase tracking-wide mb-1.5" style={{ color: C.darkLight }}>
        {label}
      </label>
      <input
        type={type} placeholder={placeholder} value={value}
        onChange={onChange} onKeyDown={onKeyDown}
        onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
        className="w-full px-4 py-3 rounded-xl text-sm outline-none transition-all"
        style={{ background: C.pink, border: `1.5px solid ${focused ? C.berry : C.lineStrong}`, color: C.dark }}
      />
    </div>
  )
}

export default function Login() {
  const navigate = useNavigate()
  const [email,    setEmail]    = useState("")
  const [password, setPassword] = useState("")
  const [error,    setError]    = useState("")
  const [loading,  setLoading]  = useState(false)

  const login = async () => {
    if (!email || !password) { setError("Please enter your email and password"); return }
    setLoading(true); setError("")
    try {
      const res = await api.post("/auth/login", { email, password })
      localStorage.setItem("token", res.data.token)
      localStorage.setItem("role",  res.data.role)
      localStorage.setItem("email", res.data.email)
      localStorage.setItem("name",  res.data.name || "")
      localStorage.setItem("has_address", res.data.has_address ? "true" : "false")
      navigate("/")
    } catch (err) { setError(err.response?.data?.error || "Login failed") }
    finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: C.pink }}>
      <div className="w-full max-w-lg">

        {/* Brand */}
        <div className="text-center mb-8">
          <span className="text-3xl font-black tracking-tight" style={{ fontFamily: "Georgia, serif", color: C.dark }}>
            Shop<span style={{ color: C.berryDark }}>Sphere</span>
          </span>
        </div>

        {/* Card */}
        <div className="rounded-3xl p-8"
          style={{ background: C.white, border: `1px solid ${C.line}`, boxShadow: "0 4px 24px rgba(85,38,25,0.08)" }}>

          <h1 className="text-xl font-black mb-1 tracking-tight" style={{ fontFamily: "Georgia, serif", color: C.dark }}>
            Welcome back
          </h1>
          <p className="text-sm mb-7 font-medium" style={{ color: C.darkLight }}>Sign in to your account</p>

          {error && (
            <div className="text-sm px-4 py-3 rounded-xl mb-5 font-medium col-span-2"
              style={{ background: "#fee2e2", color: "#b91c1c" }}>{error}</div>
          )}

          {/* 2-column grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <Field label="Email"    type="email"    placeholder="you@example.com" value={email}
              onChange={e => setEmail(e.target.value)} onKeyDown={e => e.key === "Enter" && login()} />
            <Field label="Password" type="password" placeholder="••••••••"        value={password}
              onChange={e => setPassword(e.target.value)} onKeyDown={e => e.key === "Enter" && login()} />
          </div>

          <button onClick={login} disabled={loading}
            className="w-full py-3 rounded-xl text-sm font-bold transition-all hover:opacity-85 hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
            style={{ background: C.berry, color: C.white }}>
            {loading ? "Signing in…" : "Sign in"}
          </button>

          <p className="text-center text-sm mt-5 font-medium" style={{ color: C.darkLight }}>
            Don't have an account?{" "}
            <Link to="/register" className="font-bold transition-opacity hover:opacity-70" style={{ color: C.choc }}>
              Register
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
