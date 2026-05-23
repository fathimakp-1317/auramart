import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import api from "../api"
import { getProductVisual } from "../utils/categoryImage"
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

const fmtCard   = v => v.replace(/\D/g,"").slice(0,16).replace(/(.{4})/g,"$1 ").trim()
const fmtExpiry = v => { const d = v.replace(/\D/g,"").slice(0,4); return d.length>2?`${d.slice(0,2)}/${d.slice(2)}`:d }
const fmtCvv    = v => v.replace(/\D/g,"").slice(0,4)
const cardBrand = n => { const d=n.replace(/\s/g,""); if(/^4/.test(d)) return "VISA"; if(/^5[1-5]/.test(d)) return "MC"; if(/^3[47]/.test(d)) return "AMEX"; return "CARD" }

function FormInput({ label, children }) {
  return (
    <div>
      <label className="block text-xs font-bold uppercase tracking-wide mb-1.5" style={{ color: C.darkLight }}>
        {label}
      </label>
      {children}
    </div>
  )
}

const inputCls = "w-full px-4 py-3 rounded-xl text-sm outline-none transition-all"
const inputSty = { background: C.pink, border: `1.5px solid ${C.lineStrong}`, color: C.dark }

export default function Cart() {
  const navigate = useNavigate()
  const toast    = useToast()

  const [items,        setItems]        = useState([])
  const [loading,      setLoading]      = useState(true)

  const [showAddrModal,setShowAddrModal]= useState(false)
  const [addrForm,     setAddrForm]     = useState({ address:"", city:"", state:"", pincode:"" })
  const [addrSaving,   setAddrSaving]   = useState(false)
  const [addrError,    setAddrError]    = useState("")

  const [orderId,      setOrderId]      = useState(null)
  const [orderTotal,   setOrderTotal]   = useState(null)
  const [orderLoading, setOrderLoading] = useState(false)

  const [showPayment,  setShowPayment]  = useState(false)
  const [card,         setCard]         = useState({ name:"", number:"", expiry:"", cvv:"" })
  const [cardError,    setCardError]    = useState("")
  const [payLoading,   setPayLoading]   = useState(false)

  const loadCart = async () => {
    setLoading(true)
    try { const res = await api.get("/cart/cart"); setItems(res.data) }
    catch { toast({ message: "Could not load cart", type: "error" }) }
    finally { setLoading(false) }
  }

  useEffect(() => { loadCart() }, [])

  const removeItem = async (pid) => {
    try { await api.delete(`/cart/cart/${pid}`); setItems(p => p.filter(i => i.product_id !== pid)) }
    catch { toast({ message: "Failed to remove item", type: "error" }) }
  }

  const updateQty = async (pid, qty) => {
    if (qty < 1) { removeItem(pid); return }
    try {
      await api.patch(`/cart/cart/${pid}`, { quantity: qty })
      setItems(p => p.map(i => i.product_id === pid ? { ...i, quantity: qty, subtotal: +(i.price*qty).toFixed(2) } : i))
    } catch (err) { toast({ message: err.response?.data?.detail || "Failed to update quantity", type: "error" }) }
  }

  const saveAddress = async () => {
    if (!addrForm.address || !addrForm.city || !addrForm.pincode) {
      setAddrError("Address, city and pincode are required"); return
    }
    setAddrSaving(true); setAddrError("")
    try {
      await api.put("/auth/profile", addrForm)
      localStorage.setItem("has_address", "true")
      setShowAddrModal(false)
      placeOrder()
    } catch { setAddrError("Failed to save address") }
    finally { setAddrSaving(false) }
  }

  const checkout = () => {
    const hasAddr = localStorage.getItem("has_address") === "true"
    if (!hasAddr) { setShowAddrModal(true); return }
    placeOrder()
  }

  const placeOrder = async () => {
    setOrderLoading(true)
    try {
      const res = await api.post("/orders/orders", {
        items: items.map(i => ({ product_id: i.product_id, quantity: i.quantity }))
      })
      setOrderId(res.data.order_id); setOrderTotal(res.data.total); setShowPayment(true)
    } catch (err) { toast({ message: err.response?.data?.detail || "Checkout failed", type: "error" }) }
    finally { setOrderLoading(false) }
  }

  const validateCard = () => {
    if (!card.name.trim())                         return "Cardholder name is required"
    if (card.number.replace(/\s/g,"").length < 16) return "Enter a valid 16-digit card number"
    if (card.expiry.length < 5)                    return "Enter a valid expiry (MM/YY)"
    if (card.cvv.length < 3)                       return "Enter a valid CVV"
    const [mm, yy] = card.expiry.split("/")
    if (new Date(2000 + parseInt(yy), parseInt(mm) - 1) < new Date()) return "This card has expired"
    return null
  }

  const pay = async () => {
    const err = validateCard()
    if (err) { setCardError(err); return }
    setPayLoading(true); setCardError("")
    try {
      await api.post(`/orders/orders/${orderId}/pay`, {})
      await api.delete("/cart/cart")
      setItems([]); setShowPayment(false); setOrderId(null)
      toast({ message: `Payment successful! Order #${orderId} confirmed. `, type: "success", duration: 5000 })
    } catch (err) { setCardError(err.response?.data?.error || "Payment failed — please try again")
      toast({ message: "Payment failed. Please check your card details.", type: "error" }) }
    finally { setPayLoading(false) }
  }

  const total = items.reduce((s, i) => s + i.price * i.quantity, 0)

  if (loading) return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-2xl mx-auto px-5 py-10 space-y-3">
        {[1,2,3].map(i => (
          <div key={i} className="rounded-2xl p-4 flex gap-4 animate-pulse"
            style={{ background: C.white, border: `1px solid ${C.line}` }}>
            <div className="w-16 h-16 rounded-xl flex-shrink-0" style={{ background: C.pink }}/>
            <div className="flex-1 space-y-2 py-1">
              <div className="h-3 rounded-full w-1/2" style={{ background: C.pink }}/>
              <div className="h-3 rounded-full w-1/4" style={{ background: C.pink }}/>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-2xl mx-auto px-5 py-8">

        <h1 className="text-2xl font-black tracking-tight mb-6"
          style={{ fontFamily: "Georgia, serif", color: C.dark }}>
          Your Cart
        </h1>

        {/* ── Address modal ── */}
        {showAddrModal && (
          <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
            <div className="rounded-3xl p-7 w-full max-w-md shadow-2xl" style={{ background: C.white }}>
              <div className="flex justify-between items-center mb-5">
                <div>
                  <h2 className="font-black text-lg" style={{ fontFamily: "Georgia, serif", color: C.dark }}>Delivery Address</h2>
                  <p className="text-xs mt-0.5 font-medium" style={{ color: C.darkLight }}>Required before your first purchase</p>
                </div>
                <button onClick={() => setShowAddrModal(false)}
                  className="w-8 h-8 rounded-full flex items-center justify-center font-bold transition-opacity hover:opacity-60"
                  style={{ background: C.pink, color: C.dark }}>×</button>
              </div>
              {addrError && (
                <div className="text-sm px-4 py-3 rounded-xl mb-4 font-medium" style={{ background: "#fee2e2", color: "#b91c1c" }}>
                  {addrError}
                </div>
              )}
              <div className="space-y-4">
                {[
                  { key:"address", label:"Street Address", placeholder:"Street / area / apartment" },
                  { key:"city",    label:"City",            placeholder:"City"          },
                  { key:"state",   label:"State",           placeholder:"State"         },
                  { key:"pincode", label:"Pincode",         placeholder:"6-digit pincode"},
                ].map(f => (
                  <FormInput key={f.key} label={f.label}>
                    <input type="text" placeholder={f.placeholder} value={addrForm[f.key]}
                      onChange={e => setAddrForm(p => ({ ...p, [f.key]: e.target.value }))}
                      className={inputCls} style={inputSty}/>
                  </FormInput>
                ))}
              </div>
              <div className="flex gap-3 mt-6">
                <button onClick={() => setShowAddrModal(false)}
                  className="flex-1 py-2.5 rounded-xl text-sm font-semibold transition-opacity hover:opacity-70"
                  style={{ border: `1.5px solid ${C.lineStrong}`, color: C.darkSoft }}>Cancel</button>
                <button onClick={saveAddress} disabled={addrSaving}
                  className="flex-1 py-2.5 rounded-xl text-sm font-bold transition-all hover:opacity-85 disabled:opacity-50"
                  style={{ background: C.berry, color: C.white }}>
                  {addrSaving ? "Saving…" : "Save & Continue"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── Payment modal ── */}
        {showPayment && (
          <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
            <div className="rounded-3xl p-7 w-full max-w-sm shadow-2xl" style={{ background: C.white }}>

              {/* Card preview */}
              <div className="rounded-2xl p-5 mb-6 relative overflow-hidden"
                style={{ background: `linear-gradient(135deg, ${C.choc} 0%, ${C.chocolight} 100%)`, minHeight: "120px" }}>
                <div className="absolute top-0 right-0 w-32 h-32 rounded-full opacity-10"
                  style={{ background: C.pinkDark, transform: "translate(30%,-30%)" }}/>
                <div className="relative z-10">
                  <div className="flex justify-between items-start mb-4">
                    <div className="w-10 h-7 rounded" style={{ background: "rgba(221,208,200,0.3)" }}/>
                    <span className="text-xs font-black tracking-widest" style={{ color: C.pinkDark }}>
                      {cardBrand(card.number)}
                    </span>
                  </div>
                  <p className="text-base font-mono tracking-widest mb-3" style={{ color: C.pinkDark }}>
                    {card.number || "•••• •••• •••• ••••"}
                  </p>
                  <div className="flex justify-between text-xs font-semibold" style={{ color: C.pinkDark }}>
                    <span>{card.name || "CARDHOLDER NAME"}</span>
                    <span>{card.expiry || "MM/YY"}</span>
                  </div>
                </div>
              </div>

              <h2 className="font-black text-lg mb-1" style={{ fontFamily: "Georgia, serif", color: C.dark }}>
                Pay ₹{orderTotal?.toLocaleString("en-IN")}
              </h2>
              <p className="text-xs font-medium mb-5" style={{ color: C.darkLight }}>Enter your card details below</p>

              {cardError && (
                <div className="text-sm px-4 py-3 rounded-xl mb-4 font-medium" style={{ background: "#fee2e2", color: "#b91c1c" }}>
                  {cardError}
                </div>
              )}

              <div className="space-y-4 mb-5">
                <FormInput label="Cardholder Name">
                  <input type="text" placeholder="As on card" value={card.name}
                    onChange={e => setCard(p => ({ ...p, name: e.target.value.toUpperCase() }))}
                    className={inputCls} style={inputSty}/>
                </FormInput>
                <FormInput label="Card Number">
                  <input type="text" placeholder="1234 5678 9012 3456" value={card.number}
                    onChange={e => setCard(p => ({ ...p, number: fmtCard(e.target.value) }))}
                    className={`${inputCls} font-mono tracking-wider`} style={inputSty}/>
                </FormInput>
                <div className="grid grid-cols-2 gap-3">
                  <FormInput label="Expiry (MM/YY)">
                    <input type="text" placeholder="MM/YY" value={card.expiry}
                      onChange={e => setCard(p => ({ ...p, expiry: fmtExpiry(e.target.value) }))}
                      className={`${inputCls} font-mono`} style={inputSty}/>
                  </FormInput>
                  <FormInput label="CVV">
                    <input type="password" placeholder="•••" value={card.cvv}
                      onChange={e => setCard(p => ({ ...p, cvv: fmtCvv(e.target.value) }))}
                      className={`${inputCls} font-mono`} style={inputSty}/>
                  </FormInput>
                </div>
              </div>

              <div className="flex gap-3">
                <button onClick={() => setShowPayment(false)}
                  className="flex-1 py-2.5 rounded-xl text-sm font-semibold transition-opacity hover:opacity-70"
                  style={{ border: `1.5px solid ${C.lineStrong}`, color: C.darkSoft }}>Cancel</button>
                <button onClick={pay} disabled={payLoading}
                  className="flex-1 py-3 rounded-xl text-sm font-bold transition-all hover:opacity-85 disabled:opacity-50"
                  style={{ background: C.berry, color: C.white }}>
                  {payLoading ? "Processing…" : `Pay ₹${orderTotal?.toLocaleString("en-IN")}`}
                </button>
              </div>

              <p className="text-center text-xs mt-4 font-medium" style={{ color: C.darkLight }}>🔒 256-bit encrypted payment</p>
            </div>
          </div>
        )}



        {/* Empty state */}
        {items.length === 0 ? (
          <div className="text-center py-24">
            <p className="text-6xl mb-4">🛒</p>
            <p className="text-lg font-bold mb-2" style={{ color: C.dark }}>Your cart is empty</p>
            <p className="text-sm font-medium mb-6" style={{ color: C.darkLight }}>Add some products to get started</p>
            <button onClick={() => navigate("/products")}
              className="px-7 py-2.5 rounded-xl text-sm font-bold transition-all hover:opacity-85"
              style={{ background: C.berry, color: C.white }}>
              Browse Products
            </button>
          </div>
        ) : items.length > 0 && (
          <>
            {/* Cart items */}
            <div className="space-y-3 mb-6">
              {items.map(item => {
                const { emoji, bg } = getProductVisual(item.name, item.category || "")
                return (
                  <div key={item.product_id}
                    className="rounded-2xl p-4 flex items-center gap-4"
                    style={{ background: C.white, border: `1px solid ${C.line}` }}>
                    <div className={`${bg} rounded-xl w-14 h-14 flex items-center justify-center text-2xl flex-shrink-0`}>
                      {emoji}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-sm truncate" style={{ color: C.dark }}>{item.name}</p>
                      <p className="text-xs mt-0.5 font-medium" style={{ color: C.darkLight }}>
                        ₹{item.price?.toLocaleString("en-IN")} each
                      </p>
                    </div>
                    {/* Qty controls */}
                    <div className="flex items-center rounded-xl overflow-hidden flex-shrink-0"
                      style={{ border: `1.5px solid ${C.lineStrong}` }}>
                      <button onClick={() => updateQty(item.product_id, item.quantity - 1)}
                        className="w-8 h-8 flex items-center justify-center text-base font-bold transition-opacity hover:opacity-60"
                        style={{ color: C.dark }}>−</button>
                      <span className="w-8 text-center text-sm font-bold" style={{ color: C.dark }}>{item.quantity}</span>
                      <button onClick={() => updateQty(item.product_id, item.quantity + 1)}
                        disabled={item.quantity >= item.stock}
                        className="w-8 h-8 flex items-center justify-center text-base font-bold transition-opacity hover:opacity-60 disabled:opacity-30"
                        style={{ color: C.dark }}>+</button>
                    </div>
                    <p className="text-sm font-bold w-20 text-right flex-shrink-0" style={{ color: C.choc }}>
                      ₹{(item.price * item.quantity).toLocaleString("en-IN")}
                    </p>
                    <button onClick={() => removeItem(item.product_id)}
                      className="w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 transition-all hover:opacity-70"
                      style={{ background: C.pink, color: C.darkLight }}>×</button>
                  </div>
                )
              })}
            </div>

            {/* Order summary */}
            <div className="rounded-2xl p-6" style={{ background: C.white, border: `1px solid ${C.line}` }}>
              <h2 className="font-bold text-sm mb-4" style={{ color: C.dark }}>Order Summary</h2>

              <div className="space-y-2.5 mb-4">
                <div className="flex justify-between text-sm font-medium" style={{ color: C.darkLight }}>
                  <span>Subtotal ({items.length} item{items.length !== 1 ? "s" : ""})</span>
                  <span>₹{total.toLocaleString("en-IN", { maximumFractionDigits: 2 })}</span>
                </div>
                <div className="flex justify-between text-sm font-medium" style={{ color: C.darkLight }}>
                  <span>Delivery</span>
                  <span className="font-bold text-emerald-600">Free</span>
                </div>
              </div>

              <div className="h-px mb-4" style={{ background: C.line }}/>

              <div className="flex justify-between items-center mb-5">
                <span className="font-bold" style={{ color: C.dark }}>Total</span>
                <span className="text-2xl font-black" style={{ color: C.dark }}>
                  ₹{total.toLocaleString("en-IN", { maximumFractionDigits: 2 })}
                </span>
              </div>

              <button
                onClick={checkout}
                disabled={orderLoading || items.length === 0}
                className="w-full py-3.5 rounded-2xl text-sm font-bold transition-all hover:opacity-85 hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
                style={{ background: C.berry, color: C.white }}>
                {orderLoading ? "Placing order…" : "Proceed to Payment"}
              </button>

              <p className="text-center text-xs mt-3 font-medium" style={{ color: C.darkLight }}>
                Secure checkout
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
