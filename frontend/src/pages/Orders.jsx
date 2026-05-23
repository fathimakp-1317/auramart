import { useEffect, useState } from "react"
import { useNavigate, Link } from "react-router-dom"
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

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || { label: status, cls: "bg-stone-100 text-stone-600" }
  return (
    <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${cfg.cls}`}>
      {cfg.label}
    </span>
  )
}

function Orders() {
  const navigate    = useNavigate()
  const toast       = useToast()
  const [orders,    setOrders]    = useState([])
  const [loading,   setLoading]   = useState(true)
  const [paying,    setPaying]    = useState(null)
  const [cancelling,setCancelling]= useState(null)
  const [filter,    setFilter]    = useState("ALL")

  useEffect(() => {
    api.get("/orders/orders")
      .then(res => setOrders(res.data))
      .catch(() => toast({ message: "Could not load orders", type: "error" }))
      .finally(() => setLoading(false))
  }, [])

  const pay = async (orderId) => {
    setPaying(orderId)
    try {
      await api.post(`/orders/orders/${orderId}/pay`, {})
      setOrders(prev => prev.map(o => o.order_id === orderId ? { ...o, status: "PAID" } : o))
      toast({ message: `Order #${orderId} payment successful!`, type: "success" })
    } catch (err) {
      toast({ message: err.response?.data?.detail || "Payment failed", type: "error" })
    } finally { setPaying(null) }
  }

  const cancel = async (orderId) => {
    if (!confirm("Are you sure you want to cancel this order?")) return
    setCancelling(orderId)
    try {
      await api.post(`/orders/orders/${orderId}/cancel`, {})
      setOrders(prev => prev.map(o => o.order_id === orderId ? { ...o, status: "CANCELLED" } : o))
      toast({ message: `Order #${orderId} has been cancelled.`, type: "info" })
    } catch (err) {
      toast({ message: err.response?.data?.error || "Failed to cancel order", type: "error" })
    } finally { setCancelling(null) }
  }

  const FILTERS = ["ALL","PENDING","PAID","SHIPPED","DELIVERED","CANCELLED"]
  const filtered = filter === "ALL" ? orders : orders.filter(o => o.status === filter)

  if (loading) return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-3xl mx-auto px-5 py-10 space-y-3">
        {[1,2,3].map(i => (
          <div key={i} className="animate-pulse rounded-2xl p-5"
            style={{ background: C.white, border: `1px solid ${C.line}` }}>
            <div className="flex justify-between mb-3">
              <div className="h-4 rounded-full w-1/4" style={{ background: C.pink }}/>
              <div className="h-4 rounded-full w-16" style={{ background: C.pink }}/>
            </div>
            <div className="h-3 rounded-full w-1/3" style={{ background: C.pink }}/>
          </div>
        ))}
      </div>
    </div>
  )

  return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-3xl mx-auto px-5 py-10">

        {/* Header */}
        <div className="flex items-center justify-between mb-7">
          <h1 className="text-2xl font-black tracking-tight"
            style={{ fontFamily: "Georgia, serif", color: C.dark }}>
            Order History
          </h1>
          <Link to="/products"
            className="text-sm font-semibold flex items-center gap-1 transition-opacity hover:opacity-60"
            style={{ color: C.choc }}>
            Continue shopping
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </Link>
        </div>


        {/* ── Filter bar ── */}
        {orders.length > 0 && (
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide mb-6">
            {FILTERS.map(f => (
              <button key={f} onClick={() => setFilter(f)}
                className="flex-shrink-0 px-4 py-2 rounded-xl text-xs font-bold transition-all"
                style={{
                  background: filter === f ? C.choc : C.white,
                  color:      filter === f ? C.pink  : C.darkLight,
                  border:     `1.5px solid ${filter === f ? C.choc : C.lineStrong}`,
                }}>
                {f === "ALL" ? "All orders" : f.charAt(0) + f.slice(1).toLowerCase()}
                {f !== "ALL" && (
                  <span className="ml-1.5 opacity-60">
                    ({orders.filter(o => o.status === f).length})
                  </span>
                )}
              </button>
            ))}
          </div>
        )}

        {orders.length === 0 ? (
          <div className="text-center py-24">
            <p className="text-6xl mb-4">📦</p>
            <p className="text-lg font-bold mb-2" style={{ color: C.dark }}>No orders yet</p>
            <p className="text-sm font-medium mb-6" style={{ color: C.darkLight }}>
              Your order history will appear here
            </p>
            <button onClick={() => navigate("/products")}
              className="px-7 py-2.5 rounded-xl text-sm font-bold transition-all hover:opacity-85"
              style={{ background: C.berry, color: C.white }}>
              Start shopping
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.length === 0 ? (
              <div className="text-center py-14 rounded-2xl" style={{ background: C.white, border: `1.5px dashed ${C.lineStrong}` }}>
                <p className="text-sm font-medium" style={{ color: C.darkLight }}>No {filter.toLowerCase()} orders</p>
              </div>
            ) : filtered.map(order => (
              <div key={order.order_id} className="rounded-2xl p-5 transition-all hover:shadow-sm"
                style={{ background: C.white, border: `1px solid ${C.line}` }}>

                {/* Top row */}
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="font-bold text-sm" style={{ color: C.dark }}>
                      Order #{order.order_id}
                    </p>
                    <p className="text-xs mt-0.5 font-medium" style={{ color: C.darkLight }}>
                      {order.created_at
                        ? new Date(order.created_at).toLocaleDateString("en-IN", {
                            day: "numeric", month: "short", year: "numeric",
                            hour: "2-digit", minute: "2-digit"
                          })
                        : ""}
                    </p>
                  </div>
                  <StatusBadge status={order.status} />
                </div>

                {/* Divider */}
                <div className="h-px mb-4" style={{ background: C.line }}/>

                {/* Bottom row */}
                <div className="flex items-center justify-between">
                  <p className="font-black text-lg" style={{ color: C.dark }}>
                    ₹{order.total?.toLocaleString("en-IN")}
                  </p>

                  <div className="flex items-center gap-2">
                    <Link to={`/order-detail/${order.order_id}`}
                      className="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all hover:opacity-75"
                      style={{ border: `1.5px solid ${C.lineStrong}`, color: C.dark }}>
                      View details
                    </Link>

                    {order.status === "PENDING" && (
                      <button onClick={() => pay(order.order_id)}
                        disabled={paying === order.order_id}
                        className="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all hover:opacity-85 disabled:opacity-50"
                        style={{ background: C.berry, color: C.white }}>
                        {paying === order.order_id ? "Processing…" : "Pay now"}
                      </button>
                    )}

                    {order.status === "PENDING" && (
                      <button onClick={() => cancel(order.order_id)}
                        disabled={cancelling === order.order_id}
                        className="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all hover:opacity-75 disabled:opacity-50"
                        style={{ border: "1.5px solid #fca5a5", color: "#b91c1c" }}>
                        {cancelling === order.order_id ? "Cancelling…" : "Cancel"}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Orders
