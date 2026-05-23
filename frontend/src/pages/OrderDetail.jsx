import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
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

const STATUS_CONFIG = {
  PENDING:   { label: "Pending",   cls: "bg-amber-50  text-amber-700"  },
  PAID:      { label: "Paid",      cls: "bg-blue-50   text-blue-700"   },
  SHIPPED:   { label: "Shipped",   cls: "bg-violet-50 text-violet-700" },
  DELIVERED: { label: "Delivered", cls: "bg-pink-100 text-pink-800" },
  CANCELLED: { label: "Cancelled", cls: "bg-red-50    text-red-600"    },
}

const STATUS_STEPS = ["PENDING", "PAID", "SHIPPED", "DELIVERED"]
const STEP_ICONS   = { PENDING: "🕐", PAID: "💳", SHIPPED: "🚚", DELIVERED: "✅" }

// ── Star picker / display ─────────────────────────────────────────────────────
function StarRow({ rating, size = 16, interactive = false, onChange }) {
  const [hovered, setHovered] = useState(0)
  return (
    <div className="flex items-center gap-0.5">
      {[1,2,3,4,5].map(n => (
        <svg key={n} width={size} height={size} viewBox="0 0 24 24"
          fill={(interactive ? (hovered || rating) : rating) >= n ? C.berry : "none"}
          stroke={C.berry} strokeWidth="1.8"
          style={{ cursor: interactive ? "pointer" : "default", transition: "fill 0.1s" }}
          onMouseEnter={() => interactive && setHovered(n)}
          onMouseLeave={() => interactive && setHovered(0)}
          onClick={() => interactive && onChange && onChange(n)}>
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>
      ))}
    </div>
  )
}

// ── Inline review form for one product ───────────────────────────────────────
function ReviewForm({ productId, onSubmitted }) {
  const toast = useToast()
  const [rating,  setRating]  = useState(0)
  const [title,   setTitle]   = useState("")
  const [comment, setComment] = useState("")
  const [photos,  setPhotos]  = useState([])
  const [loading, setLoading] = useState(false)

  const handlePhotos = (e) => {
    Array.from(e.target.files).slice(0, 4).forEach(file => {
      const reader = new FileReader()
      reader.onload = ev => setPhotos(prev => [...prev, ev.target.result])
      reader.readAsDataURL(file)
    })
  }

  const submit = async () => {
    if (!rating)         return toast({ message: "Please select a star rating", type: "error" })
    if (!title.trim())   return toast({ message: "Please add a review title", type: "error" })
    if (!comment.trim()) return toast({ message: "Please write a comment", type: "error" })
    setLoading(true)
    try {
      await api.post(`/products/products/${productId}/reviews`, {
        rating,
        title:      title.trim(),
        comment:    comment.trim(),
        photo_urls: photos,
      })
      toast({ message: "Review submitted! Thanks", type: "success" })
      onSubmitted()
    } catch (err) {
      toast({ message: err.response?.data?.detail || "Failed to submit review", type: "error" })
    } finally {
      setLoading(false)
    }
  }

  const inp = {
    width: "100%", background: C.pink, border: `1.5px solid ${C.lineStrong}`,
    borderRadius: "10px", padding: "9px 12px", fontSize: "13px",
    color: C.dark, outline: "none", fontFamily: "inherit",
  }

  return (
    <div className="mt-3 rounded-xl p-4" style={{ background: C.pink, border: `1px solid ${C.lineStrong}` }}>
      {/* Stars */}
      <div className="flex items-center gap-2 mb-3">
        <StarRow rating={rating} size={20} interactive onChange={setRating}/>
        <span className="text-xs" style={{ color: C.darkLight }}>
          {rating ? ["","Poor","Fair","Good","Very good","Excellent"][rating] : "Tap to rate"}
        </span>
      </div>

      <input placeholder="Review title" value={title} onChange={e => setTitle(e.target.value)}
        style={{ ...inp, marginBottom: "8px" }}/>

      <textarea placeholder="Share your experience…" value={comment} onChange={e => setComment(e.target.value)}
        rows={3} style={{ ...inp, resize: "vertical", marginBottom: "8px" }}/>

      {/* Optional photos */}
      <div className="flex items-center gap-2 mb-3">
        <label className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg cursor-pointer transition-opacity hover:opacity-70"
          style={{ background: C.white, border: `1px solid ${C.lineStrong}`, color: C.darkSoft }}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
          </svg>
          Add photos
          <input type="file" accept="image/*" multiple className="hidden" onChange={handlePhotos}/>
        </label>
        {photos.length > 0 && <span className="text-xs" style={{ color: C.darkLight }}>{photos.length} photo{photos.length > 1 ? "s" : ""}</span>}
      </div>

      {photos.length > 0 && (
        <div className="flex gap-2 mb-3 flex-wrap">
          {photos.map((url, i) => (
            <div key={i} className="relative">
              <img src={url} alt="" className="w-14 h-14 object-cover rounded-lg" style={{ border: `1px solid ${C.line}` }}/>
              <button onClick={() => setPhotos(p => p.filter((_, j) => j !== i))}
                className="absolute -top-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center text-xs font-bold"
                style={{ background: C.berry, color: C.white }}>×</button>
            </div>
          ))}
        </div>
      )}

      <button onClick={submit} disabled={loading}
        className="w-full py-2.5 rounded-xl text-xs font-bold transition-all hover:opacity-85 disabled:opacity-50"
        style={{ background: C.berry, color: C.white }}>
        {loading ? "Submitting…" : "Submit Review"}
      </button>
    </div>
  )
}

// ── Item row with optional inline review ─────────────────────────────────────
function OrderItemRow({ item, product, isDelivered, isLast }) {
  const [showForm,    setShowForm]    = useState(false)
  const [hasReviewed, setHasReviewed] = useState(false)

  // Check if already reviewed on mount
  useEffect(() => {
    api.get(`/products/products/${item.product_id}/reviews`)
      .then(res => {
        const userId = localStorage.getItem("user_id")
        if (userId && (res.data.reviews || []).some(r => r.user_id === userId)) {
          setHasReviewed(true)
        }
      })
      .catch(() => {})
  }, [item.product_id])

  return (
    <div style={{ borderBottom: isLast ? "none" : `1px solid ${C.line}` }}>
      {/* Item row */}
      <div className="px-5 py-4 flex justify-between items-center">
        <div className="flex-1 min-w-0 mr-4">
          <p className="text-sm font-semibold truncate" style={{ color: C.dark }}>
            {product?.name || `Product ${item.product_id.slice(0,8)}…`}
          </p>
          <p className="text-xs mt-0.5 font-medium" style={{ color: C.darkLight }}>
            Qty {item.quantity} × ₹{item.price?.toLocaleString("en-IN")}
          </p>
        </div>
        <p className="font-bold text-sm flex-shrink-0" style={{ color: C.choc }}>
          ₹{item.subtotal?.toLocaleString("en-IN")}
        </p>
      </div>

      {/* Rate this product — sits below item, above the divider */}
      {isDelivered && (
        <div className="px-5 pb-4">
          {hasReviewed ? (
            <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl"
              style={{ background: "#f0fdf4", border: "1px solid #86efac" }}>
              <span className="text-sm">✅</span>
              <span className="text-xs font-semibold text-green-700">Review submitted — thank you!</span>
            </div>
          ) : (
            <div>
              {!showForm ? (
                <button onClick={() => setShowForm(true)}
                  className="flex items-center gap-2 w-full px-4 py-2.5 rounded-xl text-sm font-bold transition-all hover:opacity-85 hover:scale-[1.005] active:scale-[0.99]"
                  style={{ background: C.pinkDark, border: `1.5px solid ${C.lineStrong}`, color: C.berry }}>
                  <span>⭐</span>
                  Rate this product
                </button>
              ) : (
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-xs font-bold" style={{ color: C.darkLight }}>Your review</p>
                    <button onClick={() => setShowForm(false)}
                      className="text-xs font-semibold transition-opacity hover:opacity-60"
                      style={{ color: C.darkLight }}>Cancel</button>
                  </div>
                  <ReviewForm productId={item.product_id} onSubmitted={() => {
                    setShowForm(false)
                    setHasReviewed(true)
                  }}/>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
function OrderDetail() {
  const { id }      = useParams()
  const navigate    = useNavigate()
  const toast       = useToast()
  const [order,     setOrder]    = useState(null)
  const [loading,   setLoading]  = useState(true)
  const [paying,    setPaying]   = useState(false)
  const [shipping,  setShipping] = useState(false)
  const [shipError, setShipError] = useState("")
  const [products,  setProducts] = useState({})
  const [error,     setError]    = useState("")

  const isVendor = localStorage.getItem("role") === "vendor"

  useEffect(() => {
    api.get(`/orders/orders/${id}`)
      .then(async res => {
        setOrder(res.data)
        const details = {}
        await Promise.all(
          (res.data.items || []).map(async item => {
            try {
              const p = await api.get(`/products/products/${item.product_id}`)
              details[item.product_id] = p.data
            } catch {
              details[item.product_id] = { name: `Product ${item.product_id.slice(0,8)}…` }
            }
          })
        )
        setProducts(details)
      })
      .catch(() => { toast({ message: "Could not load order", type: "error" }); setError("Could not load order") })
      .finally(() => setLoading(false))
  }, [id])

  const pay = async () => {
    setPaying(true)
    try {
      await api.post(`/orders/orders/${id}/pay`, {})
      setOrder(prev => ({ ...prev, status: "PAID" }))
      toast({ message: `Order #${id} payment confirmed!`, type: "success" })
    } catch (err) {
      toast({ message: err.response?.data?.detail || "Payment failed", type: "error" })
    } finally { setPaying(false) }
  }

  const updateStatus = async (status) => {
    setShipping(true)
    setShipError("")
    try {
      const token = localStorage.getItem("token")
      const res = await fetch(`http://localhost/orders/orders/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ status })
      })
      const data = await res.json()
      if (!res.ok) {
        const msg = data.error || data.detail || `Error ${res.status}`
        setShipError(msg)
        toast({ message: msg, type: "error" })
      } else {
        setOrder(prev => ({ ...prev, status }))
        toast({ message: `Order marked as ${status.charAt(0) + status.slice(1).toLowerCase()}!`, type: "success" })
      }
    } catch {
      const msg = "Network error — could not reach server"
      setShipError(msg)
      toast({ message: msg, type: "error" })
    } finally { setShipping(false) }
  }

  if (loading) return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-2xl mx-auto px-5 py-10 space-y-4 animate-pulse">
        <div className="h-5 w-24 rounded-lg" style={{ background: C.pinkDark }}/>
        <div className="h-40 rounded-2xl" style={{ background: C.white }}/>
        <div className="h-48 rounded-2xl" style={{ background: C.white }}/>
      </div>
    </div>
  )

  const backDestination = isVendor ? "/vendor" : "/orders"
  const backLabel       = isVendor ? "Back to vendor dashboard" : "Back to orders"

  if (!order || error) return (
    <div style={{ background: C.pink, minHeight: "100vh" }} className="flex items-center justify-center">
      <div className="text-center px-6">
        <p className="text-5xl mb-4">😕</p>
        <p className="font-bold text-lg mb-4" style={{ color: C.dark }}>{error || "Order not found"}</p>
        <button onClick={() => navigate(backDestination)}
          className="text-sm font-bold underline underline-offset-2 transition-opacity hover:opacity-60"
          style={{ color: C.choc }}>{backLabel}</button>
      </div>
    </div>
  )

  const currentStep  = STATUS_STEPS.indexOf(order.status)
  const isDelivered  = order.status === "DELIVERED"

  return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-2xl mx-auto px-5 py-8">

        {/* Back */}
        <button onClick={() => navigate(backDestination)}
          className="flex items-center gap-1.5 text-sm font-semibold mb-6 transition-opacity hover:opacity-60"
          style={{ color: C.darkLight }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M19 12H5M12 5l-7 7 7 7"/>
          </svg>
          {backLabel}
        </button>

        {/* Header card */}
        <div className="rounded-2xl p-6 mb-4" style={{ background: C.white, border: `1px solid ${C.line}` }}>
          <div className="flex items-start justify-between mb-1">
            <h1 className="text-xl font-black tracking-tight"
              style={{ fontFamily: "Georgia, serif", color: C.dark }}>
              Order #{order.order_id}
            </h1>
            <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${STATUS_CONFIG[order.status]?.cls || "bg-stone-100 text-stone-600"}`}>
              {STATUS_CONFIG[order.status]?.label || order.status}
            </span>
          </div>
          <p className="text-xs font-medium" style={{ color: C.darkLight }}>
            {order.created_at
              ? new Date(order.created_at).toLocaleDateString("en-IN", {
                  day: "numeric", month: "long", year: "numeric",
                  hour: "2-digit", minute: "2-digit"
                })
              : ""}
          </p>
        </div>

        {/* Progress tracker */}
        {order.status !== "CANCELLED" && (
          <div className="rounded-2xl p-6 mb-4" style={{ background: C.white, border: `1px solid ${C.line}` }}>
            <p className="text-xs font-bold uppercase tracking-widest mb-5" style={{ color: C.darkLight }}>
              Order Progress
            </p>
            <div className="flex items-start">
              {STATUS_STEPS.map((step, i) => {
                const done    = i < currentStep
                const active  = i === currentStep
                const pending = i > currentStep
                return (
                  <div key={step} className="flex items-start flex-1 last:flex-none">
                    <div className="flex flex-col items-center">
                      <div className={`w-9 h-9 rounded-full flex items-center justify-center text-base font-bold transition-all`}
                        style={{
                          background: done || active ? C.berry : C.pink,
                          border:     pending ? `2px solid ${C.lineStrong}` : "none",
                          color:      done || active ? "white" : C.darkLight,
                        }}>
                        {done ? (
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                            <polyline points="20 6 9 17 4 12"/>
                          </svg>
                        ) : (
                          <span style={{ fontSize: "16px" }}>{STEP_ICONS[step]}</span>
                        )}
                      </div>
                      <p className="text-xs mt-2 font-semibold text-center leading-tight"
                        style={{ color: pending ? C.darkLight : C.dark }}>
                        {step.charAt(0) + step.slice(1).toLowerCase()}
                      </p>
                    </div>
                    {i < STATUS_STEPS.length - 1 && (
                      <div className="flex-1 mt-4 mx-2 h-0.5 rounded-full"
                        style={{ background: i < currentStep ? C.berry : C.lineStrong }}/>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Cancelled notice */}
        {order.status === "CANCELLED" && (
          <div className="rounded-2xl px-5 py-4 mb-4 flex items-center gap-3"
            style={{ background: "#fff1f1", border: "1.5px solid #fca5a5" }}>
            <span className="text-xl">🚫</span>
            <div>
              <p className="text-sm font-bold text-red-600">Order Cancelled</p>
              <p className="text-xs text-red-500 mt-0.5">This order has been cancelled.</p>
            </div>
          </div>
        )}

        {/* Delivered banner */}
        {isDelivered && !isVendor && (
          <div className="rounded-2xl px-5 py-4 mb-4 flex items-center gap-3"
            style={{ background: "#f0fdf4", border: "1.5px solid #86efac" }}>
            <span className="text-xl">🎉</span>
            <div>
              <p className="text-sm font-bold text-green-700">Order Delivered!</p>
              <p className="text-xs text-green-600 mt-0.5">Rate the products below to share your experience.</p>
            </div>
          </div>
        )}

        {/* Items */}
        <div className="rounded-2xl overflow-hidden mb-4"
          style={{ background: C.white, border: `1px solid ${C.line}` }}>
          <div className="px-5 py-3.5" style={{ borderBottom: `1px solid ${C.line}`, background: C.pink }}>
            <p className="text-xs font-bold uppercase tracking-widest" style={{ color: C.darkLight }}>
              Items ({(order.items || []).length})
            </p>
          </div>

          {(order.items || []).map((item, i) => (
            <OrderItemRow
              key={i}
              item={item}
              product={products[item.product_id]}
              isDelivered={isDelivered && !isVendor}
              isLast={i === order.items.length - 1}
            />
          ))}

          {/* Total row */}
          <div className="px-5 py-4 flex justify-between items-center"
            style={{ borderTop: `1px solid ${C.lineStrong}`, background: C.pink }}>
            <p className="font-bold text-sm" style={{ color: C.dark }}>Total</p>
            <p className="font-black text-lg" style={{ color: C.dark }}>
              ₹{order.total?.toLocaleString("en-IN")}
            </p>
          </div>
        </div>

        {/* Pay button */}
        {order.status === "PENDING" && !isVendor && (
          <button onClick={pay} disabled={paying}
            className="w-full py-3.5 rounded-2xl text-sm font-bold transition-all hover:opacity-85 hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
            style={{ background: C.berry, color: C.white }}>
            {paying ? "Processing payment…" : `Pay ₹${order.total?.toLocaleString("en-IN")}`}
          </button>
        )}

        {/* Mark as Shipped */}
        {isVendor && (order.status === "PAID" || order.status === "Paid") && (
          <div>
            <button onClick={() => updateStatus("SHIPPED")} disabled={shipping}
              className="w-full py-3.5 rounded-2xl text-sm font-bold transition-all hover:opacity-85 hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
              style={{ background: C.berry, color: C.white }}>
              {shipping ? "Updating…" : "🚚 Mark as Shipped"}
            </button>
            {shipError && <p className="text-xs text-center mt-2 font-semibold text-red-600">❌ {shipError}</p>}
          </div>
        )}

        {/* Mark as Delivered */}
        {isVendor && (order.status === "SHIPPED" || order.status === "Shipped") && (
          <div>
            <button onClick={() => updateStatus("DELIVERED")} disabled={shipping}
              className="w-full py-3.5 rounded-2xl text-sm font-bold transition-all hover:opacity-85 hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
              style={{ background: C.berryDark, color: C.white }}>
              {shipping ? "Updating…" : "✅ Mark as Delivered"}
            </button>
            {shipError && <p className="text-xs text-center mt-2 font-semibold text-red-600">❌ {shipError}</p>}
          </div>
        )}

      </div>
    </div>
  )
}

export default OrderDetail
