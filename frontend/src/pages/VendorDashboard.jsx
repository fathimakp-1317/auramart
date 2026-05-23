import React, { useEffect, useState } from "react"
import api from "../api"
import { useToast } from "../components/Toast"

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

function Input({ label, type = "text", placeholder, value, onChange, rows }) {
  const [focused, setFocused] = useState(false)
  const base = {
    background: C.pink, border: `1.5px solid ${focused ? C.berry : C.lineStrong}`,
    color: C.dark, outline: "none", width: "100%",
    borderRadius: 12, padding: "10px 14px", fontSize: 14, transition: "border-color 0.15s",
  }
  return (
    <div>
      <label className="block text-xs font-bold uppercase tracking-wide mb-1.5" style={{ color: C.darkLight }}>
        {label}
      </label>
      {rows
        ? <textarea rows={rows} placeholder={placeholder} value={value} onChange={onChange}
            onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
            className="block w-full text-sm resize-none" style={base}/>
        : <input type={type} placeholder={placeholder} value={value} onChange={onChange}
            onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
            className="block w-full text-sm" style={base}/>
      }
    </div>
  )
}

function Modal({ title, subtitle, onClose, children }) {
  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="rounded-3xl p-7 w-full max-w-md shadow-2xl" style={{ background: C.white }}>
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="font-black text-lg" style={{ fontFamily: "Georgia, serif", color: C.dark }}>{title}</h2>
            {subtitle && <p className="text-xs mt-0.5 font-medium" style={{ color: C.darkLight }}>{subtitle}</p>}
          </div>
          <button onClick={onClose}
            className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-lg ml-4 flex-shrink-0 transition-opacity hover:opacity-60"
            style={{ background: C.pink, color: C.dark }}>×</button>
        </div>
        {children}
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, sub, accent }) {
  return (
    <div className="rounded-2xl p-5" style={{ background: C.white, border: `1px solid ${C.line}` }}>
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-bold uppercase tracking-wide" style={{ color: C.darkLight }}>{label}</p>
        <div className="w-8 h-8 rounded-xl flex items-center justify-center text-base"
          style={{ background: accent + "18" }}>
          {icon}
        </div>
      </div>
      <p className="text-2xl font-black tracking-tight" style={{ color: C.dark }}>{value}</p>
      {sub && <p className="text-xs mt-1 font-medium" style={{ color: C.darkLight }}>{sub}</p>}
    </div>
  )
}


// ── Revenue Chart (pure SVG) ──────────────────────────────────────────────────
function RevenueChart({ orders }) {
  if (!orders || orders.length === 0) return null

  // Group orders by day (last 14 days)
  const today = new Date()
  const days = Array.from({ length: 14 }, (_, i) => {
    const d = new Date(today)
    d.setDate(today.getDate() - (13 - i))
    return d
  })

  const dayData = days.map(d => {
    const label = d.toLocaleDateString("en-IN", { day:"numeric", month:"short" })
    const key   = d.toISOString().slice(0, 10)
    const rev   = orders
      .filter(o => (o.created_at || "").slice(0, 10) === key)
      .reduce((s, o) => s + o.price * o.quantity, 0)
    return { label, rev }
  })

  const maxRev = Math.max(...dayData.map(d => d.rev), 1)
  const W = 620, H = 160, PAD = { top: 12, right: 12, bottom: 32, left: 48 }
  const chartW = W - PAD.left - PAD.right
  const chartH = H - PAD.top  - PAD.bottom
  const barW   = chartW / dayData.length
  const barGap = barW * 0.25

  const yTicks = [0, 0.25, 0.5, 0.75, 1].map(t => ({
    val: Math.round(maxRev * t),
    y:   PAD.top + chartH * (1 - t),
  }))

  const BERRY = "#B2456E"
  const PINK  = "#F5D0C8"
  const LINE  = "rgba(85,38,25,0.08)"
  const TEXT  = "#8B6355"

  return (
    <div className="rounded-2xl p-5 mb-8" style={{ background: "#FFF8F6", border: "1px solid rgba(85,38,25,0.10)" }}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-bold" style={{ color: "#2C1810" }}>Revenue — last 14 days</h2>
        <span className="text-xs font-semibold px-2.5 py-1 rounded-full" style={{ background: PINK, color: "#552619" }}>
          ₹{orders.reduce((s,o)=>s+o.price*o.quantity,0).toLocaleString("en-IN",{maximumFractionDigits:0})} total
        </span>
      </div>
      <div className="overflow-x-auto">
        <svg viewBox={`0 0 ${W} ${H}`} style={{ width:"100%", minWidth:360, height:"auto", display:"block" }}>
          {/* Y gridlines + labels */}
          {yTicks.map(t => (
            <g key={t.val}>
              <line x1={PAD.left} y1={t.y} x2={W - PAD.right} y2={t.y}
                stroke={LINE} strokeWidth="1"/>
              <text x={PAD.left - 6} y={t.y + 4} textAnchor="end"
                fontSize="9" fill={TEXT}>
                {t.val >= 1000 ? `₹${(t.val/1000).toFixed(0)}k` : `₹${t.val}`}
              </text>
            </g>
          ))}

          {/* Bars */}
          {dayData.map((d, i) => {
            const barH  = d.rev > 0 ? Math.max((d.rev / maxRev) * chartH, 4) : 0
            const x     = PAD.left + i * barW + barGap / 2
            const y     = PAD.top + chartH - barH
            const w     = barW - barGap
            const isMax = d.rev === maxRev && d.rev > 0
            return (
              <g key={i}>
                <rect x={x} y={y} width={w} height={barH}
                  rx="4" fill={isMax ? BERRY : PINK}/>
                {/* X label — every other to avoid crowding */}
                {i % 2 === 0 && (
                  <text x={x + w/2} y={H - 4} textAnchor="middle"
                    fontSize="8" fill={TEXT}>
                    {d.label}
                  </text>
                )}
                {/* Value on tallest bar */}
                {isMax && d.rev > 0 && (
                  <text x={x + w/2} y={y - 4} textAnchor="middle"
                    fontSize="9" fontWeight="700" fill={BERRY}>
                    ₹{d.rev >= 1000 ? `${(d.rev/1000).toFixed(1)}k` : d.rev}
                  </text>
                )}
              </g>
            )
          })}
        </svg>
      </div>
    </div>
  )
}


// ── Image Uploader ────────────────────────────────────────────────────────────
function ImageUploader({ images, onChange }) {
  const fileRef = React.useRef()

  const addImages = (e) => {
    const files = Array.from(e.target.files)
    const remaining = 3 - images.length
    if (remaining <= 0) return
    files.slice(0, remaining).forEach(file => {
      const reader = new FileReader()
      reader.onload = ev => onChange(prev => [...prev, ev.target.result])
      reader.readAsDataURL(file)
    })
    e.target.value = ""
  }

  const remove = (i) => onChange(prev => prev.filter((_, j) => j !== i))

  return (
    <div>
      <p className="text-xs font-bold mb-2" style={{ color: C.darkLight }}>
        Product Images <span style={{ color: C.berry }}>*</span>
        <span className="font-normal ml-1">(1–3 images)</span>
      </p>

      <div className="flex gap-2 flex-wrap">
        {images.map((url, i) => (
          <div key={i} className="relative w-20 h-20 rounded-xl overflow-hidden flex-shrink-0"
            style={{ border: `1.5px solid ${C.lineStrong}` }}>
            <img src={url} alt="" className="w-full h-full object-cover"/>
            <button onClick={() => remove(i)}
              className="absolute top-0.5 right-0.5 w-5 h-5 rounded-full flex items-center justify-center text-xs font-black"
              style={{ background: C.berry, color: "white" }}>×</button>
            {i === 0 && (
              <span className="absolute bottom-0 left-0 right-0 text-center text-xs font-bold py-0.5"
                style={{ background: "rgba(178,69,110,0.85)", color: "white", fontSize: "9px" }}>MAIN</span>
            )}
          </div>
        ))}

        {images.length < 3 && (
          <button onClick={() => fileRef.current.click()}
            className="w-20 h-20 rounded-xl flex flex-col items-center justify-center gap-1 flex-shrink-0 transition-opacity hover:opacity-70"
            style={{ border: `2px dashed ${C.lineStrong}`, background: C.pink, color: C.darkLight }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            <span style={{ fontSize: "9px", fontWeight: 700 }}>{images.length === 0 ? "Add photo" : "Add more"}</span>
          </button>
        )}
      </div>

      <input ref={fileRef} type="file" accept="image/*" multiple className="hidden" onChange={addImages}/>
      <p className="text-xs mt-1.5" style={{ color: C.darkLight }}>
        First image is the main display photo
      </p>
    </div>
  )
}

export default function VendorDashboard() {
  const toast = useToast()
  const [products,    setProducts]    = useState([])
  const [prodLoading, setProdLoading] = useState(true)
  const [showAdd,     setShowAdd]     = useState(false)
  const [addForm,     setAddForm]     = useState({ name:"", description:"", price:"", stock:"", images:[] })
  const [addError,    setAddError]    = useState("")
  const [addSaving,   setAddSaving]   = useState(false)
  const [editProd,    setEditProd]    = useState(null)
  const [editForm,    setEditForm]    = useState({ price:"", stock:"", images:[] })
  const [editError,   setEditError]   = useState("")
  const [editSaving,  setEditSaving]  = useState(false)
  const [orders,      setOrders]      = useState([])
  const [ordLoading,  setOrdLoading]  = useState(true)


  const loadProducts = () => {
    setProdLoading(true)
    api.get("/products/my-products")
      .then(r => setProducts(r.data))
      .catch(() => toast({ message: "Could not load products", type: "error" }))
      .finally(() => setProdLoading(false))
  }
  const loadOrders = () => {
    setOrdLoading(true)
    api.get("/orders/vendor/orders").then(r => setOrders(r.data)).catch(() => {}).finally(() => setOrdLoading(false))
  }
  useEffect(() => { loadProducts(); loadOrders() }, [])

  const addProduct = async () => {
    if (!addForm.name || !addForm.price) { setAddError("Name and price are required"); return }
    if (addForm.images.length < 1) { setAddError("Please upload at least 1 product image"); return }
    setAddSaving(true); setAddError("")
    try {
      await api.post("/products/products", { name:addForm.name, description:addForm.description, price:parseFloat(addForm.price), stock:parseInt(addForm.stock)||0, images:addForm.images })
      setAddForm({ name:"", description:"", price:"", stock:"", images:[] }); setShowAdd(false); loadProducts()
      toast({ message: "Product added successfully!", type: "success" })
      toast({ message: "Product added successfully!", type: "success" })
    } catch(e) { setAddError(e.response?.data?.detail || "Failed to add product")
      toast({ message: "Failed to add product", type: "error" }) }
    finally { setAddSaving(false) }
  }
  const saveEdit = async () => {
    if (!editForm.price || editForm.stock==="") { setEditError("Price and stock are required"); return }
    setEditSaving(true); setEditError("")
    try {
      await api.put(`/products/products/${editProd.id}`, { price:parseFloat(editForm.price), stock:parseInt(editForm.stock), images:editForm.images })
      setEditProd(null); loadProducts()
      toast({ message: "Product updated!", type: "success" })
      toast({ message: "Product updated!", type: "success" })
    } catch(e) { setEditError(e.response?.data?.detail || "Failed to update")
      toast({ message: "Failed to update product", type: "error" }) }
    finally { setEditSaving(false) }
  }
  const deleteProduct = async (id) => {
    if (!confirm("Delete this product?")) return
    try { await api.delete(`/products/products/${id}`); setProducts(p => p.filter(x => x.id !== id))
      toast({ message: "Product deleted", type: "info" }) }
    catch { toast({ message: "Failed to delete product", type: "error" }) }
  }

  const revenue   = orders.reduce((s,o) => s + o.price * o.quantity, 0)
  const unitsSold = orders.reduce((s,o) => s + o.quantity, 0)
  const alertItems = products.filter(p => p.stock <= 5)

  return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-5xl mx-auto px-6 py-10">

        {/* ── Header ── */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-black tracking-tight" style={{ fontFamily: "Georgia, serif", color: C.dark }}>
              Vendor Dashboard
            </h1>
            <p className="text-xs font-medium mt-1" style={{ color: C.darkLight }}>
              {localStorage.getItem("email")}
            </p>
          </div>
          <button onClick={() => { setShowAdd(true); setAddError("") }}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold transition-all hover:opacity-85 hover:scale-105 active:scale-95"
            style={{ background: C.berry, color: C.white }}>
            <span className="text-base leading-none">+</span> Add Product
          </button>
        </div>

        {/* ── Stats ── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
          <StatCard icon="📦" label="Products"   value={products.length} sub="Listed"         accent={C.berry}  />
          <StatCard icon="📊" label="Units Sold" value={unitsSold}       sub="All time"       accent={C.choc} />
          <StatCard icon="💰" label="Revenue"    value={`₹${revenue.toLocaleString("en-IN",{maximumFractionDigits:0})}`} sub="Total earned" accent={C.berry} />
          <StatCard icon="⚠️" label="Low Stock"  value={alertItems.length} sub="Need restocking" accent={C.choc}/>
        </div>

        {/* ── Revenue Chart ── */}
        <RevenueChart orders={orders} />

        {/* ── Alerts ── */}
        {alertItems.length > 0 && (
          <div className="rounded-2xl px-5 py-4 mb-6 flex items-start gap-3"
            style={{ background: alertItems.some(p=>p.stock===0) ? "#fef2f2" : "#fff7ed",
              border: `1.5px solid ${alertItems.some(p=>p.stock===0) ? "#fca5a5" : "#fdba74"}` }}>
            <span className="text-lg mt-0.5 flex-shrink-0">{alertItems.some(p=>p.stock===0) ? "🚫" : "⚠️"}</span>
            <div>
              <p className="text-sm font-bold" style={{ color: alertItems.some(p=>p.stock===0) ? "#b91c1c" : "#92400e" }}>
                {alertItems.some(p=>p.stock===0) ? "Some products are out of stock" : "Low stock warning"}
              </p>
              <p className="text-xs mt-0.5" style={{ color: alertItems.some(p=>p.stock===0) ? "#ef4444" : "#d97706" }}>
                {alertItems.map(p=>`${p.name} (${p.stock})`).join(" · ")}
              </p>
            </div>
          </div>
        )}

        {/* ── Add modal ── */}
        {showAdd && (
          <Modal title="Add New Product" onClose={() => setShowAdd(false)}>
            {addError && <div className="text-sm px-4 py-3 rounded-xl mb-5 font-medium" style={{ background:"#fee2e2",color:"#b91c1c" }}>{addError}</div>}
            <div className="space-y-4">
              <Input label="Product Name" placeholder="e.g. Wireless Earbuds" value={addForm.name} onChange={e=>setAddForm(p=>({...p,name:e.target.value}))}/>
              <Input label="Description" placeholder="What makes it great?" value={addForm.description} onChange={e=>setAddForm(p=>({...p,description:e.target.value}))} rows={2}/>
              <div className="grid grid-cols-2 gap-3">
                <Input label="Price (₹)" type="number" placeholder="0.00" value={addForm.price} onChange={e=>setAddForm(p=>({...p,price:e.target.value}))}/>
                <Input label="Stock Qty" type="number" placeholder="0"    value={addForm.stock} onChange={e=>setAddForm(p=>({...p,stock:e.target.value}))}/>
              </div>
              <ImageUploader images={addForm.images} onChange={imgs => setAddForm(p=>({...p, images: typeof imgs === "function" ? imgs(p.images) : imgs}))}/>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={() => setShowAdd(false)} className="flex-1 py-2.5 rounded-xl text-sm font-semibold transition-opacity hover:opacity-60"
                style={{ border:`1.5px solid ${C.lineStrong}`, color:C.darkSoft }}>Cancel</button>
              <button onClick={addProduct} disabled={addSaving} className="flex-1 py-2.5 rounded-xl text-sm font-bold transition-all hover:opacity-85 disabled:opacity-50"
                style={{ background:C.berry, color:C.white }}>{addSaving ? "Adding…" : "Add Product"}</button>
            </div>
          </Modal>
        )}

        {/* ── Edit modal ── */}
        {editProd && (
          <Modal title="Edit Product" subtitle={editProd.name} onClose={() => setEditProd(null)}>
            {editError && <div className="text-sm px-4 py-3 rounded-xl mb-5 font-medium" style={{ background:"#fee2e2",color:"#b91c1c" }}>{editError}</div>}
            <div className="grid grid-cols-2 gap-4">
              <Input label="Price (₹)" type="number" value={editForm.price} onChange={e=>setEditForm(p=>({...p,price:e.target.value}))}/>
              <Input label="Stock Qty" type="number" value={editForm.stock} onChange={e=>setEditForm(p=>({...p,stock:e.target.value}))}/>
            </div>
            <div className="mt-4">
              <ImageUploader images={editForm.images} onChange={imgs => setEditForm(p=>({...p, images: typeof imgs === "function" ? imgs(p.images) : imgs}))}/>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={() => setEditProd(null)} className="flex-1 py-2.5 rounded-xl text-sm font-semibold transition-opacity hover:opacity-60"
                style={{ border:`1.5px solid ${C.lineStrong}`, color:C.darkSoft }}>Cancel</button>
              <button onClick={saveEdit} disabled={editSaving} className="flex-1 py-2.5 rounded-xl text-sm font-bold transition-all hover:opacity-85 disabled:opacity-50"
                style={{ background:C.berry, color:C.white }}>{editSaving ? "Saving…" : "Save Changes"}</button>
            </div>
          </Modal>
        )}

        {/* ── Products table ── */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold" style={{ color: C.dark }}>My Products</h2>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full" style={{ background: C.pinkDark, color: C.dark }}>
              {products.length} total
            </span>
          </div>
{prodLoading ? (
            <div className="space-y-2">{[1,2,3].map(i=><div key={i} className="h-14 rounded-2xl animate-pulse" style={{ background:C.white }}/>)}</div>
          ) : products.length === 0 ? (
            <div className="text-center py-16 rounded-2xl" style={{ background:C.white, border:`1.5px dashed ${C.lineStrong}` }}>
              <p className="text-sm font-medium mb-2" style={{ color:C.darkLight }}>No products yet</p>
              <button onClick={() => setShowAdd(true)} className="text-sm font-bold underline underline-offset-2 transition-opacity hover:opacity-60"
                style={{ color:C.choc }}>Add your first product</button>
            </div>
          ) : (
            <div className="rounded-2xl overflow-hidden" style={{ background:C.white, border:`1px solid ${C.line}` }}>
              <div className="overflow-x-auto">
              <table className="w-full text-sm min-w-[500px]">
                <thead>
                  <tr style={{ background:C.pink, borderBottom:`1px solid ${C.line}` }}>
                    {["Product","Price","Stock",""].map(h=>(
                      <th key={h} className={`py-3 text-xs font-bold uppercase tracking-wide ${h===""?"text-right pr-5":"text-left pl-5"}`}
                        style={{ color:C.darkLight }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {products.map((p,i) => (
                    <tr key={p.id} style={{ borderTop:i>0?`1px solid ${C.line}`:"none" }} className="transition-colors hover:bg-pink-50/40">
                      <td className="pl-5 py-3.5"><p className="font-semibold truncate max-w-xs" style={{ color:C.dark }}>{p.name}</p></td>
                      <td className="pl-5 py-3.5 font-semibold" style={{ color:C.darkSoft }}>₹{p.price?.toLocaleString("en-IN")}</td>
                      <td className="pl-5 py-3.5">
                        <span className={`inline-flex text-xs font-bold px-2.5 py-1 rounded-full ${
                          p.stock===0 ? "bg-red-100 text-red-600" : p.stock<=5 ? "bg-orange-100 text-orange-600" : "bg-pink-100 text-pink-800"
                        }`}>
                          {p.stock===0 ? "Out of stock" : p.stock<=5 ? `⚠ ${p.stock} left` : `${p.stock} in stock`}
                        </span>
                      </td>
                      <td className="pr-5 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-4">
                          <button onClick={() => { setEditProd(p); setEditForm({price:p.price,stock:p.stock}); setEditError("") }}
                            className="text-xs font-semibold transition-opacity hover:opacity-50" style={{ color:C.berryDark }}>Edit</button>
                          <button onClick={() => deleteProduct(p.id)}
                            className="text-xs font-semibold transition-opacity hover:opacity-50 text-red-400">Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              </div>
            </div>
          )}
        </div>

        {/* ── Orders table ── */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold" style={{ color:C.dark }}>Customer Orders</h2>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full" style={{ background:C.pinkDark, color:C.dark }}>
              {orders.length} orders
            </span>
          </div>
          {ordLoading ? (
            <div className="space-y-2">{[1,2].map(i=><div key={i} className="h-12 rounded-2xl animate-pulse" style={{ background:C.white }}/>)}</div>
          ) : orders.length === 0 ? (
            <div className="text-center py-14 rounded-2xl" style={{ background:C.white, border:`1.5px dashed ${C.lineStrong}` }}>
              <p className="text-sm font-medium" style={{ color:C.darkLight }}>No orders yet</p>
            </div>
          ) : (
            <div className="rounded-2xl overflow-hidden" style={{ background:C.white, border:`1px solid ${C.line}` }}>
              <div className="overflow-x-auto">
              <table className="w-full text-sm min-w-[500px]">
                <thead>
                  <tr style={{ background:C.pink, borderBottom:`1px solid ${C.line}` }}>
                    {["Order","Product","Qty","Revenue"].map(h=>(
                      <th key={h} className="text-left pl-5 py-3 text-xs font-bold uppercase tracking-wide" style={{ color:C.darkLight }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {orders.map((o,i) => (
                    <tr key={i} style={{ borderTop:i>0?`1px solid ${C.line}`:"none" }} className="transition-colors hover:bg-pink-50/40">
                      <td className="pl-5 py-3.5">
                        <a href={`/order-detail/${o.order_id}`} className="font-bold transition-opacity hover:opacity-50" style={{ color:C.dark }}>#{o.order_id}</a>
                      </td>
                      <td className="pl-5 py-3.5 text-xs font-medium truncate max-w-36" style={{ color:C.darkSoft }}>
                        {o.product_name || o.product_id?.slice(0,12)+"…"}
                      </td>
                      <td className="pl-5 py-3.5 font-semibold" style={{ color:C.dark }}>{o.quantity}</td>
                      <td className="pl-5 py-3.5 font-bold" style={{ color:C.choc }}>₹{(o.price*o.quantity).toLocaleString("en-IN")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}
