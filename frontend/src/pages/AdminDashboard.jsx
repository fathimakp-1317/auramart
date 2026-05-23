import { useEffect, useState } from "react"
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

const TABS = [
  { id: "overview",   label: "Overview",       icon: "📊" },
  { id: "users",      label: "Users",          icon: "👥" },
  { id: "products",   label: "Products",       icon: "📦" },
  { id: "inventory",  label: "Low Stock",      icon: "⚠️"  },
  { id: "analytics",  label: "Analytics",      icon: "🔥" },
  { id: "categories", label: "Categories",     icon: "🏷️" },
  { id: "health",     label: "System Health",  icon: "💚" },
  { id: "vendors",    label: "Vendor Approvals", icon: "🏪", badge: true },
]

function StatCard({ icon, label, value, color }) {
  return (
    <div className="rounded-2xl p-5" style={{ background: C.white, border: `1px solid ${C.line}` }}>
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-bold uppercase tracking-wide" style={{ color: C.darkLight }}>{label}</p>
        <div className="w-9 h-9 rounded-xl flex items-center justify-center text-lg"
          style={{ background: (color || C.berry) + "18" }}>
          {icon}
        </div>
      </div>
      <p className="text-3xl font-black" style={{ color: C.dark }}>{value}</p>
    </div>
  )
}

function SectionTitle({ children }) {
  return (
    <h2 className="text-lg font-black mb-4" style={{ fontFamily: "Georgia, serif", color: C.dark }}>
      {children}
    </h2>
  )
}

function Btn({ children, onClick, disabled, variant = "primary", small }) {
  const bg = variant === "primary" ? C.berry
    : variant === "danger"  ? "#dc2626"
    : C.pink
  const color = variant === "ghost" ? C.dark : C.white
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`font-bold rounded-xl transition-all hover:opacity-80 disabled:opacity-40 ${small ? "text-xs px-3 py-1.5" : "text-sm px-5 py-2.5"}`}
      style={{ background: bg, color, border: variant === "ghost" ? `1px solid ${C.lineStrong}` : "none" }}
    >
      {children}
    </button>
  )
}

// ── Overview Tab ─────────────────────────────────────────────────────────────
function Overview({ users, products, trending }) {
  const vendors   = users.filter(u => u.role === "vendor").length
  const customers = users.filter(u => u.role === "customer").length
  const lowStock  = products.filter(p => p.stock <= 5).length
  const outStock  = products.filter(p => p.stock === 0).length

  return (
    <div>
      <SectionTitle>Platform Overview</SectionTitle>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <StatCard icon="👥" label="Total Users"     value={users.length}    />
        <StatCard icon="🏪" label="Vendors"         value={vendors}         />
        <StatCard icon="🛍️" label="Products"        value={products.length} />
        <StatCard icon="⚠️" label="Low Stock Items" value={lowStock}        />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Top trending */}
        <div className="rounded-2xl p-5" style={{ background: C.white, border: `1px solid ${C.line}` }}>
          <p className="text-xs font-bold uppercase tracking-wide mb-3" style={{ color: C.darkLight }}>
            Top Trending Products
          </p>
          {trending.slice(0, 5).map((t, i) => (
            <div key={t.product_id} className="flex items-center justify-between py-2 border-b last:border-0" style={{ borderColor: C.line }}>
              <span className="text-sm font-medium" style={{ color: C.dark }}>
                #{i + 1} {t.name || t.product_id.slice(0, 14) + "…"}
              </span>
              <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: C.berry + "18", color: C.berry }}>
                {t.views} views
              </span>
            </div>
          ))}
          {trending.length === 0 && <p className="text-sm" style={{ color: C.darkLight }}>No data yet</p>}
        </div>

        {/* Stock summary */}
        <div className="rounded-2xl p-5" style={{ background: C.white, border: `1px solid ${C.line}` }}>
          <p className="text-xs font-bold uppercase tracking-wide mb-3" style={{ color: C.darkLight }}>
            Inventory Health
          </p>
          {[
            { label: "Healthy stock (> 5)",  value: products.length - lowStock,   color: "#16a34a" },
            { label: "Low stock (1–5)",       value: lowStock - outStock,          color: "#d97706" },
            { label: "Out of stock",          value: outStock,                     color: "#dc2626" },
          ].map(r => (
            <div key={r.label} className="flex items-center justify-between py-2 border-b last:border-0" style={{ borderColor: C.line }}>
              <span className="text-sm" style={{ color: C.dark }}>{r.label}</span>
              <span className="font-bold text-sm" style={{ color: r.color }}>{r.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ── Users Tab ─────────────────────────────────────────────────────────────────
function UsersTab({ users, loading }) {
  const [search, setSearch] = useState("")
  const [filter, setFilter] = useState("ALL")

  const filtered = users.filter(u => {
    const matchRole   = filter === "ALL" || u.role === filter.toLowerCase()
    const matchSearch = !search || u.email.includes(search) || (u.name || "").toLowerCase().includes(search.toLowerCase())
    return matchRole && matchSearch
  })

  const roleColor = r => r === "admin" ? C.berry : r === "vendor" ? C.chocolight : C.darkLight

  return (
    <div>
      <SectionTitle>User Management</SectionTitle>

      <div className="flex gap-3 mb-4 flex-wrap">
        <input
          type="text" placeholder="Search by name or email..." value={search}
          onChange={e => setSearch(e.target.value)}
          className="flex-1 min-w-48 px-4 py-2 rounded-xl text-sm outline-none border"
          style={{ background: C.white, borderColor: C.lineStrong, color: C.dark }}
        />
        {["ALL", "CUSTOMER", "VENDOR", "ADMIN"].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className="px-4 py-2 rounded-xl text-xs font-bold transition-all"
            style={{
              background: filter === f ? C.berry : C.white,
              color:      filter === f ? C.white  : C.dark,
              border:     `1px solid ${filter === f ? C.berry : C.lineStrong}`
            }}>
            {f}
          </button>
        ))}
      </div>

      <div className="rounded-2xl overflow-hidden border" style={{ borderColor: C.line }}>
        <table className="w-full text-sm">
          <thead style={{ background: C.pinkDark }}>
            <tr>
              {["Name", "Email", "Phone", "Role", "Address"].map(h => (
                <th key={h} className="text-left px-4 py-3 text-xs font-bold uppercase tracking-wide" style={{ color: C.choc }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(5)].map((_, i) => (
                <tr key={i} style={{ background: i % 2 === 0 ? C.white : C.pink }}>
                  {[...Array(5)].map((_, j) => (
                    <td key={j} className="px-4 py-3">
                      <div className="h-4 rounded animate-pulse" style={{ background: C.pinkDark, width: "70%" }} />
                    </td>
                  ))}
                </tr>
              ))
            ) : filtered.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-sm" style={{ color: C.darkLight }}>No users found</td></tr>
            ) : filtered.map((u, i) => (
              <tr key={u.user_id} style={{ background: i % 2 === 0 ? C.white : C.pink }}>
                <td className="px-4 py-3 font-medium" style={{ color: C.dark }}>{u.name || "—"}</td>
                <td className="px-4 py-3 text-xs" style={{ color: C.darkSoft }}>{u.email}</td>
                <td className="px-4 py-3 text-xs" style={{ color: C.darkLight }}>{u.phone || "—"}</td>
                <td className="px-4 py-3">
                  <span className="text-xs font-bold px-2.5 py-1 rounded-full capitalize"
                    style={{ background: roleColor(u.role) + "18", color: roleColor(u.role) }}>
                    {u.role}
                  </span>
                </td>
                <td className="px-4 py-3 text-xs" style={{ color: C.darkLight }}>
                  {u.city ? `${u.city}, ${u.state || ""}` : "Not set"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="px-4 py-2 text-xs font-medium" style={{ background: C.pinkDark, color: C.darkLight }}>
          {filtered.length} of {users.length} users
        </div>
      </div>
    </div>
  )
}

// ── Products Tab ──────────────────────────────────────────────────────────────
function ProductsTab({ products, loading, onDelete }) {
  const [search,   setSearch]   = useState("")
  const [deleting, setDeleting] = useState(null)

  const filtered = products.filter(p =>
    !search || p.name.toLowerCase().includes(search.toLowerCase())
  )

  const handleDelete = async (id, name) => {
    if (!confirm(`Delete "${name}"? This cannot be undone.`)) return
    setDeleting(id)
    try {
      await api.delete(`/products/products/${id}`)
      onDelete(id)
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to delete product")
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div>
      <SectionTitle>All Products</SectionTitle>
      <input
        type="text" placeholder="Search products..." value={search}
        onChange={e => setSearch(e.target.value)}
        className="w-full px-4 py-2 rounded-xl text-sm outline-none border mb-4"
        style={{ background: C.white, borderColor: C.lineStrong, color: C.dark }}
      />
      <div className="rounded-2xl overflow-hidden border" style={{ borderColor: C.line }}>
        <table className="w-full text-sm">
          <thead style={{ background: C.pinkDark }}>
            <tr>
              {["Product", "Price", "Stock", "Vendor", "Action"].map(h => (
                <th key={h} className="text-left px-4 py-3 text-xs font-bold uppercase tracking-wide" style={{ color: C.choc }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(5)].map((_, i) => (
                <tr key={i} style={{ background: i % 2 === 0 ? C.white : C.pink }}>
                  {[...Array(5)].map((_, j) => (
                    <td key={j} className="px-4 py-3">
                      <div className="h-4 rounded animate-pulse" style={{ background: C.pinkDark, width: "80%" }} />
                    </td>
                  ))}
                </tr>
              ))
            ) : filtered.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-sm" style={{ color: C.darkLight }}>No products found</td></tr>
            ) : filtered.map((p, i) => (
              <tr key={p.id} style={{ background: i % 2 === 0 ? C.white : C.pink }}>
                <td className="px-4 py-3 font-medium max-w-48 truncate" style={{ color: C.dark }}>{p.name}</td>
                <td className="px-4 py-3" style={{ color: C.darkSoft }}>₹{p.price?.toLocaleString("en-IN")}</td>
                <td className="px-4 py-3">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full`}
                    style={{
                      background: p.stock === 0 ? "#fef2f2" : p.stock <= 5 ? "#fffbeb" : "#f0fdf4",
                      color:      p.stock === 0 ? "#dc2626"  : p.stock <= 5 ? "#d97706"  : "#16a34a"
                    }}>
                    {p.stock === 0 ? "Out of stock" : p.stock <= 5 ? `⚠ ${p.stock}` : p.stock}
                  </span>
                </td>
                <td className="px-4 py-3 text-xs font-mono" style={{ color: C.darkLight }}>
                  {p.vendor_id?.slice(0, 10)}…
                </td>
                <td className="px-4 py-3">
                  <Btn variant="danger" small onClick={() => handleDelete(p.id, p.name)} disabled={deleting === p.id}>
                    {deleting === p.id ? "…" : "Delete"}
                  </Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="px-4 py-2 text-xs font-medium" style={{ background: C.pinkDark, color: C.darkLight }}>
          {filtered.length} of {products.length} products
        </div>
      </div>
    </div>
  )
}

// ── Low Stock Tab ─────────────────────────────────────────────────────────────
function InventoryTab({ products }) {
  const low = products.filter(p => p.stock <= 10).sort((a, b) => a.stock - b.stock)

  return (
    <div>
      <SectionTitle>Low Stock Monitor</SectionTitle>
      {low.length === 0 ? (
        <div className="text-center py-16 rounded-2xl" style={{ background: C.white, border: `1px solid ${C.line}` }}>
          <p className="text-4xl mb-2">✅</p>
          <p className="font-bold" style={{ color: C.dark }}>All products are well stocked</p>
        </div>
      ) : (
        <div className="rounded-2xl overflow-hidden border" style={{ borderColor: C.line }}>
          <table className="w-full text-sm">
            <thead style={{ background: C.pinkDark }}>
              <tr>
                {["Product", "Stock", "Status", "Vendor"].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-bold uppercase tracking-wide" style={{ color: C.choc }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {low.map((p, i) => (
                <tr key={p.id} style={{ background: i % 2 === 0 ? C.white : C.pink }}>
                  <td className="px-4 py-3 font-medium max-w-52 truncate" style={{ color: C.dark }}>{p.name}</td>
                  <td className="px-4 py-3 font-black text-lg" style={{ color: p.stock === 0 ? "#dc2626" : "#d97706" }}>
                    {p.stock}
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs font-bold px-2.5 py-1 rounded-full"
                      style={{
                        background: p.stock === 0 ? "#fef2f2" : "#fffbeb",
                        color:      p.stock === 0 ? "#dc2626"  : "#d97706"
                      }}>
                      {p.stock === 0 ? "Out of stock" : "Low stock"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs font-mono" style={{ color: C.darkLight }}>
                    {p.vendor_id?.slice(0, 10)}…
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

// ── Analytics Tab ─────────────────────────────────────────────────────────────
function AnalyticsTab({ trending }) {
  const max = trending[0]?.views || 1
  return (
    <div>
      <SectionTitle>Product Analytics</SectionTitle>
      {trending.length === 0 ? (
        <p className="text-sm" style={{ color: C.darkLight }}>No view data yet. Browse products to generate analytics.</p>
      ) : (
        <div className="rounded-2xl p-5" style={{ background: C.white, border: `1px solid ${C.line}` }}>
          <p className="text-xs font-bold uppercase tracking-wide mb-4" style={{ color: C.darkLight }}>
            Top Viewed Products (by view count)
          </p>
          {trending.map((t, i) => (
            <div key={t.product_id} className="mb-4">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs font-medium" style={{ color: C.dark }}>
                  #{i + 1} {t.name || t.product_id.slice(0, 16) + "…"}
                </span>
                <span className="text-xs font-bold" style={{ color: C.berry }}>{t.views} views</span>
              </div>
              <div className="h-2 rounded-full overflow-hidden" style={{ background: C.pinkDark }}>
                <div className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${(t.views / max) * 100}%`, background: `linear-gradient(90deg, ${C.berry}, ${C.berryLight})` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Categories Tab ────────────────────────────────────────────────────────────
function CategoriesTab() {
  const [cats,    setCats]    = useState([])
  const [loading, setLoading] = useState(true)
  const [name,    setName]    = useState("")
  const [saving,  setSaving]  = useState(false)
  const [error,   setError]   = useState("")

  useEffect(() => {
    api.get("/products/categories")
      .then(r => setCats(r.data))
      .finally(() => setLoading(false))
  }, [])

  const addCategory = async () => {
    if (!name.trim()) { setError("Name is required"); return }
    setSaving(true)
    setError("")
    try {
      const res = await api.post("/products/categories", { name: name.trim() })
      setCats(p => [...p, { id: res.data.id, name: name.trim() }])
      setName("")
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to add category")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <SectionTitle>Category Management</SectionTitle>

      {/* Add form */}
      <div className="rounded-2xl p-5 mb-5" style={{ background: C.white, border: `1px solid ${C.line}` }}>
        <p className="text-xs font-bold uppercase tracking-wide mb-3" style={{ color: C.darkLight }}>Add New Category</p>
        {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
        <div className="flex gap-3">
          <input
            type="text" placeholder="e.g. Electronics" value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === "Enter" && addCategory()}
            className="flex-1 px-4 py-2.5 rounded-xl text-sm outline-none border"
            style={{ background: C.pink, borderColor: C.lineStrong, color: C.dark }}
          />
          <Btn onClick={addCategory} disabled={saving}>
            {saving ? "Adding..." : "Add Category"}
          </Btn>
        </div>
      </div>

      {/* Category list */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {loading ? (
          [...Array(6)].map((_, i) => (
            <div key={i} className="h-12 rounded-xl animate-pulse" style={{ background: C.pinkDark }} />
          ))
        ) : cats.length === 0 ? (
          <p className="col-span-3 text-sm" style={{ color: C.darkLight }}>No categories yet</p>
        ) : cats.map(c => (
          <div key={c.id} className="flex items-center gap-2 px-4 py-3 rounded-xl border"
            style={{ background: C.white, borderColor: C.lineStrong }}>
            <span className="text-sm font-medium" style={{ color: C.dark }}>{c.name}</span>
            {c.parent_id && <span className="text-xs" style={{ color: C.darkLight }}>sub</span>}
          </div>
        ))}
      </div>
    </div>
  )
}

// ── System Health Tab ──────────────────────────────────────────────────────────
function HealthTab() {
  const SERVICES = [
    { name: "Auth Service",           url: "/auth/hello"                },
    { name: "Product Service",        url: "/products/hello"            },
    { name: "Order Service",          url: "/orders/hello"              },
    { name: "Cart Service",           url: "/cart/hello"                },
    { name: "Search Service",         url: "/search/hello"              },
    { name: "Recommendation Service", url: "/recommend/hello"           },
    { name: "Home Service",           url: "/home/hello"                },
    { name: "Analytics Service",      url: "/analytics/hello"           },
    { name: "Notification API",       url: "/notifications/hello"       },
    { name: "Gateway",                url: "/health"                    },
  ]

  const [statuses, setStatuses] = useState({})
  const [checking, setChecking] = useState(true)

  const checkAll = async () => {
    setChecking(true)
    const results = {}
    await Promise.all(
      SERVICES.map(async s => {
        const start = Date.now()
        try {
          await api.get(s.url)
          results[s.name] = { ok: true, ms: Date.now() - start }
        } catch {
          results[s.name] = { ok: false, ms: Date.now() - start }
        }
      })
    )
    setStatuses(results)
    setChecking(false)
  }

  useEffect(() => { checkAll() }, [])

  const allUp = Object.values(statuses).every(s => s.ok)

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <SectionTitle>System Health</SectionTitle>
        <Btn onClick={checkAll} disabled={checking} small>
          {checking ? "Checking..." : "Refresh"}
        </Btn>
      </div>

      {/* Summary badge */}
      {!checking && Object.keys(statuses).length > 0 && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-xl mb-4"
          style={{ background: allUp ? "#f0fdf4" : "#fef2f2", border: `1px solid ${allUp ? "#86efac" : "#fca5a5"}` }}>
          <span>{allUp ? "✅" : "⚠️"}</span>
          <span className="text-sm font-bold" style={{ color: allUp ? "#16a34a" : "#dc2626" }}>
            {allUp ? "All systems operational" : `${Object.values(statuses).filter(s => !s.ok).length} service(s) down`}
          </span>
        </div>
      )}

      <div className="rounded-2xl overflow-hidden border" style={{ borderColor: C.line }}>
        <table className="w-full text-sm">
          <thead style={{ background: C.pinkDark }}>
            <tr>
              {["Service", "Status", "Response Time"].map(h => (
                <th key={h} className="text-left px-4 py-3 text-xs font-bold uppercase tracking-wide" style={{ color: C.choc }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {SERVICES.map((s, i) => {
              const st = statuses[s.name]
              return (
                <tr key={s.name} style={{ background: i % 2 === 0 ? C.white : C.pink }}>
                  <td className="px-4 py-3 font-medium" style={{ color: C.dark }}>{s.name}</td>
                  <td className="px-4 py-3">
                    {checking ? (
                      <div className="h-4 w-16 rounded animate-pulse" style={{ background: C.pinkDark }} />
                    ) : (
                      <span className="text-xs font-bold px-2.5 py-1 rounded-full"
                        style={{
                          background: st?.ok ? "#f0fdf4" : "#fef2f2",
                          color:      st?.ok ? "#16a34a" : "#dc2626"
                        }}>
                        {st?.ok ? "● Online" : "● Offline"}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs font-mono" style={{ color: C.darkLight }}>
                    {checking ? "—" : st ? `${st.ms}ms` : "—"}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}


// ── Vendor Approvals Tab ──────────────────────────────────────────────────────
function VendorApprovalsTab() {
  const [vendors,  setVendors]  = useState([])
  const [loading,  setLoading]  = useState(true)
  const [actingOn, setActingOn] = useState(null)
  const [toast,    setToast]    = useState("")

  const fetchPending = () => {
    setLoading(true)
    api.get("/auth/admin/vendors/pending")
      .then(res => setVendors(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchPending() }, [])

  const act = async (userId, action) => {
    setActingOn(userId)
    try {
      await api.post(`/auth/admin/vendors/${userId}/${action}`)
      setToast(action === "approve" ? "✅ Vendor approved & email sent!" : "❌ Vendor rejected & email sent.")
      fetchPending()
    } catch (err) {
      setToast(err.response?.data?.error || "Action failed")
    } finally {
      setActingOn(null)
      setTimeout(() => setToast(""), 3500)
    }
  }

  return (
    <div>
      <SectionTitle>Vendor Approvals</SectionTitle>

      {toast && (
        <div className="mb-4 px-4 py-3 rounded-xl text-sm font-semibold"
          style={{ background: toast.startsWith("✅") ? "#f0fdf4" : "#fff1f1",
                   color:      toast.startsWith("✅") ? "#15803d"  : "#b91c1c",
                   border:     `1px solid ${toast.startsWith("✅") ? "#86efac" : "#fca5a5"}` }}>
          {toast}
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {[1,2,3].map(i => (
            <div key={i} className="h-16 rounded-xl animate-pulse" style={{ background: C.pinkDark }}/>
          ))}
        </div>
      ) : vendors.length === 0 ? (
        <div className="text-center py-16">
          <p className="font-bold text-base" style={{ color: C.dark }}>No pending applications</p>
          <p className="text-sm mt-1" style={{ color: C.darkLight }}>All vendor applications have been reviewed.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {vendors.map(v => (
            <div key={v.user_id} className="flex items-center justify-between gap-4 px-5 py-4 rounded-xl"
              style={{ background: C.pink, border: `1px solid ${C.lineStrong}` }}>
              <div className="min-w-0">
                <p className="font-bold text-sm truncate" style={{ color: C.dark }}>
                  {v.name || "—"}
                </p>
                <p className="text-xs mt-0.5 truncate" style={{ color: C.darkLight }}>{v.email}</p>
                {v.phone && <p className="text-xs" style={{ color: C.darkLight }}>📞 {v.phone}</p>}
              </div>
              <div className="flex gap-2 flex-shrink-0">
                <button
                  onClick={() => act(v.user_id, "approve")}
                  disabled={actingOn === v.user_id}
                  className="px-4 py-2 rounded-xl text-xs font-bold transition-all hover:opacity-85 disabled:opacity-50"
                  style={{ background: "#16a34a", color: "white" }}>
                  {actingOn === v.user_id ? "…" : "✓ Approve"}
                </button>
                <button
                  onClick={() => act(v.user_id, "reject")}
                  disabled={actingOn === v.user_id}
                  className="px-4 py-2 rounded-xl text-xs font-bold transition-all hover:opacity-85 disabled:opacity-50"
                  style={{ background: "#dc2626", color: "white" }}>
                  {actingOn === v.user_id ? "…" : "✗ Reject"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Main AdminDashboard ───────────────────────────────────────────────────────
export default function AdminDashboard() {
  const [tab,      setTab]      = useState("overview")
  const [users,    setUsers]    = useState([])
  const [products, setProducts] = useState([])
  const [trending, setTrending] = useState([])
  const [loading,       setLoading]       = useState(true)
  const [pendingVendors, setPendingVendors] = useState(0)

  useEffect(() => {
    api.get("/auth/admin/vendors/pending").then(r => setPendingVendors(r.data.length)).catch(() => {})
    Promise.all([
      api.get("/auth/users"),
      api.get("/products/products"),
      api.get("/analytics/trending"),
    ]).then(async ([u, p, t]) => {
      setUsers(u.data)
      setProducts(p.data)

      // Resolve product names for trending
      const trendingWithNames = await Promise.all(
        t.data.map(async item => {
          try {
            const res = await api.get(`/products/products/${item.product_id}`)
            return { ...item, name: res.data.name }
          } catch {
            return { ...item, name: item.product_id.slice(0, 16) + "…" }
          }
        })
      )
      setTrending(trendingWithNames)
    }).catch(console.error)
    .finally(() => setLoading(false))
  }, [])

  const handleProductDelete = (id) => {
    setProducts(prev => prev.filter(p => p.id !== id))
  }

  return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-7xl mx-auto px-4 py-8">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-black" style={{ fontFamily: "Georgia, serif", color: C.dark }}>
            Admin Dashboard
          </h1>
          <p className="text-sm mt-1 font-medium" style={{ color: C.darkLight }}>
            ShopSphere Platform Management · {localStorage.getItem("email")}
          </p>
        </div>

        <div className="flex gap-6">
          {/* Sidebar tabs */}
          <div className="flex-shrink-0 w-48">
            <div className="rounded-2xl overflow-hidden border sticky top-24" style={{ background: C.white, borderColor: C.line }}>
              {TABS.map(t => (
                <button key={t.id} onClick={() => setTab(t.id)}
                  className="w-full text-left flex items-center gap-2.5 px-4 py-3 text-sm font-bold transition-all border-b last:border-0"
                  style={{
                    background:  tab === t.id ? C.berry : "transparent",
                    color:       tab === t.id ? C.white  : C.dark,
                    borderColor: C.line,
                  }}>
                  <span>{t.icon}</span>
                  <span className="flex-1">{t.label}</span>
                  {t.badge && pendingVendors > 0 && (
                    <span className="text-xs font-black px-1.5 py-0.5 rounded-full ml-1"
                      style={{ background: tab === t.id ? "rgba(255,255,255,0.3)" : C.berry, color: "white", minWidth: "20px", textAlign: "center" }}>
                      {pendingVendors}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 rounded-2xl p-6 border" style={{ background: C.white, borderColor: C.line }}>
            {tab === "overview"   && <Overview   users={users} products={products} trending={trending} />}
            {tab === "users"      && <UsersTab   users={users} loading={loading} />}
            {tab === "products"   && <ProductsTab products={products} loading={loading} onDelete={handleProductDelete} />}
            {tab === "inventory"  && <InventoryTab products={products} />}
            {tab === "analytics"  && <AnalyticsTab trending={trending} />}
            {tab === "categories" && <CategoriesTab />}
            {tab === "health"     && <HealthTab />}
            {tab === "vendors"    && <VendorApprovalsTab />}
          </div>
        </div>
      </div>
    </div>
  )
}
