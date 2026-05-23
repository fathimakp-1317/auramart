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
  darkSoft:   "#4A2C1E",
  darkLight:  "#8B6355",
  white:      "#FFF8F6",
  line:       "rgba(85,38,25,0.10)",
  lineStrong: "rgba(85,38,25,0.18)",
}

function Field({ label, type = "text", placeholder, value, onChange, span2 = false }) {
  const [focused, setFocused] = useState(false)
  return (
    <div className={span2 ? "col-span-2" : ""}>
      <label className="block text-xs font-bold uppercase tracking-wide mb-1.5" style={{ color: C.darkLight }}>
        {label}
      </label>
      <input
        type={type} placeholder={placeholder} value={value} onChange={onChange}
        onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
        className="w-full px-4 py-3 rounded-xl text-sm outline-none transition-all"
        style={{ background: C.pink, border: `1.5px solid ${focused ? C.berry : C.lineStrong}`, color: C.dark }}
      />
    </div>
  )
}

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ name:"", email:"", phone:"", password:"", confirm:"", role:"customer" })
  const [error,   setError]   = useState("")
  const [loading, setLoading] = useState(false)
  const set = (k, v) => setForm(p => ({ ...p, [k]: v }))

  const submit = async () => {
    if (!form.name || !form.email || !form.phone || !form.password) { setError("All fields are required"); return }
    if (form.password !== form.confirm) { setError("Passwords do not match"); return }
    if (form.password.length < 6)       { setError("Password must be at least 6 characters"); return }
    if (!/^\d{10}$/.test(form.phone))   { setError("Enter a valid 10-digit phone number"); return }
    setLoading(true); setError("")
    try {
      const regRes = await api.post("/auth/register", { name:form.name, email:form.email, phone:form.phone, password:form.password, role:form.role })
      // Vendor applications go to pending — show confirmation, don't auto-login
      if (regRes.data.vendor_status === "pending") {
        navigate("/register-pending")
        return
      }
      const res = await api.post("/auth/login", { email:form.email, password:form.password })
      localStorage.setItem("token", res.data.token); localStorage.setItem("role",  res.data.role)
      localStorage.setItem("email", res.data.email); localStorage.setItem("name",  res.data.name || "")
      localStorage.setItem("has_address", res.data.has_address ? "true" : "false")
      navigate("/")
    } catch (err) { setError(err.response?.data?.error || "Registration failed") }
    finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-10" style={{ background: C.pink }}>
      <div className="w-full max-w-xl">

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
            Create your account
          </h1>
          <p className="text-sm mb-7 font-medium" style={{ color: C.darkLight }}>Join ShopSphere today</p>

          {error && (
            <div className="text-sm px-4 py-3 rounded-xl mb-5 font-medium"
              style={{ background: "#fee2e2", color: "#b91c1c" }}>{error}</div>
          )}

          {/* Fields — 2 column grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
            <Field label="Full Name"       placeholder="Your full name"          value={form.name}     onChange={e => set("name", e.target.value)} />
            <Field label="Email" type="email" placeholder="you@example.com"      value={form.email}    onChange={e => set("email", e.target.value)} />
            <Field label="Phone" type="tel"   placeholder="10-digit number"      value={form.phone}    onChange={e => set("phone", e.target.value)} />
            <Field label="Password" type="password" placeholder="Min 6 chars"    value={form.password} onChange={e => set("password", e.target.value)} />
            <Field label="Confirm Password" type="password" placeholder="Re-enter" value={form.confirm} onChange={e => set("confirm", e.target.value)} span2 />
          </div>

          {/* Account type */}
          <div className="mb-6">
            <p className="text-xs font-bold uppercase tracking-wide mb-2.5" style={{ color: C.darkLight }}>
              Account Type
            </p>
            <div className="grid grid-cols-2 gap-3">
              {[
                { value: "customer", label: "Customer", sub: "Browse and buy products", icon: "🛍️" },
                { value: "vendor",   label: "Vendor",   sub: "List and sell products",  icon: "🏪" },
              ].map(r => (
                <button key={r.value} onClick={() => set("role", r.value)}
                  className="flex flex-col items-start gap-1 p-3.5 rounded-xl text-left transition-all"
                  style={{
                    border: `2px solid ${form.role === r.value ? C.berry : C.line}`,
                    background: form.role === r.value ? C.berry : C.pink,
                  }}>
                  <span className="text-xl">{r.icon}</span>
                  <span className="text-sm font-bold" style={{ color: form.role === r.value ? C.white : C.dark }}>{r.label}</span>
                  <span className="text-xs font-medium" style={{ color: form.role === r.value ? "rgba(255,255,255,0.75)" : C.darkLight }}>{r.sub}</span>
                </button>
              ))}
            </div>
          </div>

          <button onClick={submit} disabled={loading}
            className="w-full py-3 rounded-xl text-sm font-bold transition-all hover:opacity-85 hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
            style={{ background: C.berry, color: C.white }}>
            {loading ? "Creating account…" : "Create account"}
          </button>

          <p className="text-center text-sm mt-5 font-medium" style={{ color: C.darkLight }}>
            Already have an account?{" "}
            <Link to="/login" className="font-bold transition-opacity hover:opacity-70" style={{ color: C.choc }}>
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
