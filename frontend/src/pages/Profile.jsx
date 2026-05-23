import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import api from "../api"

const C = {
  pink:       "#FBEAE7",
  pinkDark:   "#F5D0C8",
  berry:      "#B2456E",
  berryDark:  "#8F3457",
  choc:       "#552619",
  chocolight: "#7A3A26",
  dark:       "#2C1810",
  darkSoft:   "#4A2C1E",
  darkLight:  "#8B6355",
  white:      "#FFF8F6",
  line:       "rgba(85,38,25,0.10)",
  lineStrong: "rgba(85,38,25,0.18)",
}

function Field({ label, placeholder, type = "text", value, onChange, span2 = false }) {
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

export default function Profile() {
  const navigate  = useNavigate()
  const [form,    setForm]    = useState({ name:"", phone:"", address:"", city:"", state:"", pincode:"" })
  const [loading, setLoading] = useState(true)
  const [saving,  setSaving]  = useState(false)
  const [message, setMessage] = useState("")
  const [error,   setError]   = useState("")

  const email = localStorage.getItem("email") || ""

  useEffect(() => {
    api.get("/auth/profile")
      .then(res => setForm({
        name:    res.data.name    || "",
        phone:   res.data.phone   || "",
        address: res.data.address || "",
        city:    res.data.city    || "",
        state:   res.data.state   || "",
        pincode: res.data.pincode || "",
      }))
      .catch(() => navigate("/login"))
      .finally(() => setLoading(false))
  }, [])

  const save = async () => {
    if (!form.name || !form.phone) { setError("Name and phone are required"); return }
    setSaving(true); setError(""); setMessage("")
    try {
      await api.put("/auth/profile", form)
      localStorage.setItem("name", form.name)
      localStorage.setItem("has_address", (form.address && form.city && form.pincode) ? "true" : "false")
      setMessage("Profile updated successfully")
    } catch (err) {
      setError(err.response?.data?.error || "Failed to update profile")
    } finally { setSaving(false) }
  }

  const hasAddress = form.address && form.city && form.pincode
  const initials   = form.name ? form.name.split(" ").map(w => w[0]).slice(0,2).join("").toUpperCase() : "?"

  if (loading) return (
    <div style={{ background: C.pink, minHeight: "100vh" }} className="flex items-center justify-center">
      <p className="text-sm font-medium" style={{ color: C.darkLight }}>Loading…</p>
    </div>
  )

  return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-2xl mx-auto px-5 py-10">

        {/* Profile header */}
        <div className="rounded-3xl p-6 mb-5 flex items-center gap-5" style={{ background: C.choc }}>
          {/* Avatar */}
          <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-xl font-black flex-shrink-0"
            style={{ background: C.berry, color: C.white }}>
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <h1 className="text-lg font-black truncate" style={{ fontFamily: "Georgia, serif", color: C.pinkDark }}>
              {form.name || "Your Profile"}
            </h1>
            <p className="text-xs font-medium mt-0.5 truncate" style={{ color: C.pinkDark }}>{email}</p>
            <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full"
              style={{ background: hasAddress ? "rgba(16,185,129,0.15)" : "rgba(245,158,11,0.15)" }}>
              <span className="text-xs">{hasAddress ? "✓" : "⚠"}</span>
              <span className="text-xs font-semibold"
                style={{ color: hasAddress ? "#10b981" : "#f59e0b" }}>
                {hasAddress ? "Address saved" : "No address — add one to checkout"}
              </span>
            </div>
          </div>
        </div>

        {/* Form card */}
        <div className="rounded-3xl p-8" style={{ background: C.white, border: `1px solid ${C.line}` }}>

          {message && (
            <div className="flex items-center gap-2.5 text-sm px-4 py-3 rounded-xl mb-5 font-semibold"
              style={{ background: "rgba(16,185,129,0.08)", border: "1.5px solid rgba(16,185,129,0.2)", color: "#065f46" }}>
              <span>✅</span> {message}
            </div>
          )}
          {error && (
            <div className="text-sm px-4 py-3 rounded-xl mb-5 font-medium"
              style={{ background: "#fee2e2", color: "#b91c1c" }}>{error}
            </div>
          )}

          {/* ── Personal Info ── */}
          <p className="text-xs font-bold uppercase tracking-widest mb-4" style={{ color: C.darkLight }}>
            Personal Info
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-7">
            <Field label="Full Name"    placeholder="Your full name"         value={form.name}  onChange={e => setForm(p => ({ ...p, name:  e.target.value }))} />
            <Field label="Phone Number" placeholder="10-digit mobile number" value={form.phone} onChange={e => setForm(p => ({ ...p, phone: e.target.value }))} />
          </div>

          <div className="h-px mb-7" style={{ background: C.line }}/>

          {/* ── Delivery Address ── */}
          <p className="text-xs font-bold uppercase tracking-widest mb-4" style={{ color: C.darkLight }}>
            Delivery Address
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-7">
            <Field label="Street Address" placeholder="Street / apartment / area" value={form.address} onChange={e => setForm(p => ({ ...p, address: e.target.value }))} span2 />
            <Field label="City"    placeholder="City"             value={form.city}    onChange={e => setForm(p => ({ ...p, city:    e.target.value }))} />
            <Field label="State"   placeholder="State"            value={form.state}   onChange={e => setForm(p => ({ ...p, state:   e.target.value }))} />
            <Field label="Pincode" placeholder="6-digit pincode"  value={form.pincode} onChange={e => setForm(p => ({ ...p, pincode: e.target.value }))} />
          </div>

          <button onClick={save} disabled={saving}
            className="w-full py-3.5 rounded-2xl text-sm font-bold transition-all hover:opacity-85 hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
            style={{ background: C.berry, color: C.white }}>
            {saving ? "Saving…" : "Save Changes"}
          </button>
        </div>
      </div>
    </div>
  )
}
