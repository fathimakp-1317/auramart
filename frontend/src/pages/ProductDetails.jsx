import { useParams, useNavigate, Link } from "react-router-dom"
import { useEffect, useState, useRef } from "react"
import api from "../api"
import { getProductVisual } from "../utils/categoryImage"
import ProductImage from "../components/ProductImage"
import { useToast } from "../components/Toast"

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

function RelatedCard({ product }) {
  const { emoji, bg } = getProductVisual(product.name, product.category)
  return (
    <Link to={`/product/${product.id}`} className="group flex-shrink-0 w-40">
      <div className="rounded-2xl overflow-hidden transition-all duration-200 group-hover:-translate-y-1 group-hover:shadow-md"
        style={{ background: C.white, border: `1px solid ${C.line}` }}>
        <ProductImage name={product.name} category={product.category} id={product.id} images={product.images || []} height="h-28" size={200}/>
        <div className="p-3">
          <p className="text-xs font-semibold truncate leading-snug" style={{ color: C.dark }}>{product.name}</p>
          <p className="text-sm font-bold mt-1" style={{ color: C.berry }}>₹{product.price?.toLocaleString("en-IN")}</p>
        </div>
      </div>
    </Link>
  )
}

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

function ReviewCard({ review }) {
  return (
    <div className="py-4" style={{ borderBottom: `1px solid ${C.line}` }}>
      <div className="flex items-start justify-between gap-3 mb-1">
        <div>
          <p className="text-sm font-bold" style={{ color: C.dark }}>{review.title}</p>
          <p className="text-xs mt-0.5" style={{ color: C.darkLight }}>
            {review.user_name} · {new Date(review.created_at).toLocaleDateString("en-IN", { day:"numeric", month:"short", year:"numeric" })}
          </p>
        </div>
        <StarRow rating={review.rating} size={13}/>
      </div>
      <p className="text-sm leading-relaxed mt-2" style={{ color: C.darkSoft }}>{review.comment}</p>
      {review.photo_urls?.length > 0 && (
        <div className="flex gap-2 mt-3 flex-wrap">
          {review.photo_urls.map((url, i) => (
            <img key={i} src={url} alt="review photo"
              className="w-20 h-20 object-cover rounded-xl"
              style={{ border: `1px solid ${C.line}` }}/>
          ))}
        </div>
      )}
    </div>
  )
}


function ProductGallery({ images, name }) {
  const [active, setActive] = useState(0)
  return (
    <div>
      {/* Main image */}
      <div className="h-72 relative overflow-hidden bg-gray-100">
        <img src={images[active]} alt={name}
          className="absolute inset-0 w-full h-full object-cover transition-opacity duration-300"
          loading="lazy"/>
        <div className="absolute inset-0"
          style={{ background: "linear-gradient(to bottom, transparent 55%, rgba(0,0,0,0.15))" }}/>
        {images.length > 1 && (
          <div className="absolute bottom-2 right-3 text-xs font-bold px-2 py-1 rounded-full"
            style={{ background: "rgba(0,0,0,0.45)", color: "white" }}>
            {active + 1} / {images.length}
          </div>
        )}
      </div>
      {/* Thumbnails */}
      {images.length > 1 && (
        <div className="flex gap-2 px-4 py-3" style={{ background: "#FFF8F6" }}>
          {images.map((url, i) => (
            <button key={i} onClick={() => setActive(i)}
              className="w-16 h-16 rounded-xl overflow-hidden flex-shrink-0 transition-all"
              style={{
                border: i === active ? "2.5px solid #B2456E" : "2px solid rgba(85,38,25,0.12)",
                opacity: i === active ? 1 : 0.65,
              }}>
              <img src={url} alt={`view ${i+1}`} className="w-full h-full object-cover"/>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function ProductDetails() {
  const { id }   = useParams()
  const navigate = useNavigate()
  const toast    = useToast()

  const [product,      setProduct]      = useState(null)
  const [loading,      setLoading]      = useState(true)
  const [cartLoading,  setCartLoading]  = useState(false)
  const [qty,          setQty]          = useState(1)
  const [error,        setError]        = useState("")
  const [related,      setRelated]      = useState([])

  // Reviews state
  const [reviews,      setReviews]      = useState([])
  const [reviewMeta,   setReviewMeta]   = useState({ avg_rating: 0, review_count: 0 })
  const [reviewsLoaded,setReviewsLoaded]= useState(false)

  const token  = localStorage.getItem("token")
  const userId = localStorage.getItem("user_id")

  const fetchReviews = () => {
    api.get(`/products/products/${id}/reviews`)
      .then(res => {
        setReviews(res.data.reviews || [])
        setReviewMeta({ avg_rating: res.data.avg_rating, review_count: res.data.review_count })
        if (userId) {
          setHasReviewed((res.data.reviews || []).some(rv => rv.user_id === userId))
        }
        setReviewsLoaded(true)
      })
      .catch(() => setReviewsLoaded(true))
  }

  useEffect(() => {
    setLoading(true)
    api.get(`/products/products/${id}`)
      .then(res => {
        setProduct(res.data)
        const q = res.data.category || res.data.name.split(" ")[0]
        api.get(`/search/search?q=${encodeURIComponent(q)}&size=8`)
          .then(r => setRelated((r.data.results || []).filter(p => p.id !== res.data.id).slice(0, 6)))
          .catch(() => {})
      })
      .catch(() => setError("Product not found"))
      .finally(() => setLoading(false))

    fetchReviews()

  }, [id])

  const addToCart = async () => {
    if (!token) { navigate("/login"); return }
    setCartLoading(true)
    try {
      await api.post("/cart/cart", { product_id: product.id, quantity: qty })
      toast({ message: `${product.name} added to cart!`, type: "success" })
    } catch (err) {
      toast({ message: err.response?.data?.detail || "Failed to add to cart", type: "error" })
    } finally { setCartLoading(false) }
  }

  if (loading) return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-2xl mx-auto px-6 py-12 animate-pulse">
        <div className="h-6 w-16 rounded-lg mb-8" style={{ background: C.pinkDark }}/>
        <div className="rounded-3xl overflow-hidden" style={{ background: C.white, border: `1px solid ${C.line}` }}>
          <div className="h-56" style={{ background: C.pinkDark }}/>
          <div className="p-8 space-y-4">
            <div className="h-6 w-2/3 rounded-lg" style={{ background: C.pinkDark }}/>
            <div className="h-4 w-full rounded-lg" style={{ background: C.pinkDark }}/>
          </div>
        </div>
      </div>
    </div>
  )

  if (error) return (
    <div style={{ background: C.pink, minHeight: "100vh" }} className="flex items-center justify-center">
      <div className="text-center px-6">
        <p className="text-5xl mb-4">😕</p>
        <p className="font-bold text-lg mb-2" style={{ color: C.dark }}>{error}</p>
        <button onClick={() => navigate("/products")}
          className="text-sm font-bold underline underline-offset-2 transition-opacity hover:opacity-60"
          style={{ color: C.berry }}>
          Back to products
        </button>
      </div>
    </div>
  )

  const inStock = product.stock > 0

  return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-2xl mx-auto px-5 py-8">

        {/* Back */}
        <button onClick={() => navigate(-1)}
          className="flex items-center gap-1.5 text-sm font-semibold mb-6 transition-opacity hover:opacity-60"
          style={{ color: C.darkLight }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M19 12H5M12 5l-7 7 7 7"/>
          </svg>
          Back
        </button>

        {/* Card */}
        <div className="rounded-3xl overflow-hidden shadow-sm mb-8"
          style={{ background: C.white, border: `1px solid ${C.line}` }}>

          {/* Image gallery */}
          {product.images && product.images.length > 0 ? (
            <ProductGallery images={product.images} name={product.name} />
          ) : (
            <ProductImage name={product.name} category={product.category} id={product.id} height="h-56" size={600}/>
          )}

          <div className="p-8">
            {/* Name + stock */}
            <div className="flex items-start justify-between gap-4 mb-2">
              <h1 className="text-2xl font-black tracking-tight leading-tight"
                style={{ fontFamily: "Georgia, serif", color: C.dark }}>
                {product.name}
              </h1>
              <span className={`flex-shrink-0 text-xs font-bold px-3 py-1 rounded-full mt-1 ${
                inStock ? "bg-pink-100 text-pink-800" : "bg-red-100 text-red-600"
              }`}>
                {inStock ? `${product.stock} in stock` : "Out of stock"}
              </span>
            </div>

            {/* Avg rating summary */}
            {reviewMeta.review_count > 0 && (
              <div className="flex items-center gap-2 mb-3">
                <StarRow rating={Math.round(reviewMeta.avg_rating)} size={14}/>
                <span className="text-sm font-semibold" style={{ color: C.dark }}>
                  {reviewMeta.avg_rating.toFixed(1)}
                </span>
                <span className="text-xs" style={{ color: C.darkLight }}>
                  ({reviewMeta.review_count} review{reviewMeta.review_count !== 1 ? "s" : ""})
                </span>
              </div>
            )}

            {product.description && (
              <p className="text-sm leading-relaxed mb-6 font-medium" style={{ color: C.darkLight }}>
                {product.description}
              </p>
            )}

            <div className="h-px mb-6" style={{ background: C.line }}/>

            {/* Price + category */}
            <div className="flex items-center justify-between mb-6">
              <p className="text-3xl font-black tracking-tight" style={{ color: C.dark }}>
                ₹{product.price?.toLocaleString("en-IN")}
              </p>
              {product.category && (
                <span className="text-xs font-semibold px-3 py-1.5 rounded-full"
                  style={{ background: C.pinkDark, color: C.darkSoft }}>
                  {product.category}
                </span>
              )}
            </div>

            {/* Qty */}
            {inStock && (
              <div className="flex items-center gap-3 mb-6">
                <span className="text-sm font-bold" style={{ color: C.darkLight }}>Quantity</span>
                <div className="flex items-center rounded-xl overflow-hidden"
                  style={{ border: `1.5px solid ${C.lineStrong}` }}>
                  <button onClick={() => setQty(q => Math.max(1, q - 1))}
                    className="w-10 h-10 flex items-center justify-center text-lg font-bold transition-opacity hover:opacity-60"
                    style={{ color: C.dark }}>−</button>
                  <span className="w-10 text-center text-sm font-bold" style={{ color: C.dark }}>{qty}</span>
                  <button onClick={() => setQty(q => Math.min(product.stock, q + 1))}
                    disabled={qty >= product.stock}
                    className="w-10 h-10 flex items-center justify-center text-lg font-bold transition-opacity hover:opacity-60 disabled:opacity-30"
                    style={{ color: C.dark }}>+</button>
                </div>
                <span className="text-xs font-medium" style={{ color: C.darkLight }}>max {product.stock}</span>
              </div>
            )}

            {/* Add to cart */}
            <button onClick={addToCart} disabled={cartLoading || !inStock}
              className="w-full py-3.5 rounded-2xl text-sm font-bold transition-all hover:opacity-85 hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 flex items-center justify-center gap-2"
              style={{ background: C.berry, color: C.white }}>
              {cartLoading ? "Adding…" : !inStock ? "Out of Stock" : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
                    <line x1="3" y1="6" x2="21" y2="6"/>
                    <path d="M16 10a4 4 0 0 1-8 0"/>
                  </svg>
                  Add to Cart
                </>
              )}
            </button>

            {/* Trust badges */}
            <div className="grid grid-cols-3 gap-3 mt-6">
              {[
                { icon: "🚚", text: "Free delivery" },
                { icon: "🔄", text: "Easy returns"  },
                { icon: "🔒", text: "Secure payment"},
              ].map(b => (
                <div key={b.text} className="flex flex-col items-center gap-1 py-3 rounded-xl"
                  style={{ background: C.pink }}>
                  <span className="text-lg">{b.icon}</span>
                  <span className="text-xs font-semibold text-center" style={{ color: C.darkLight }}>{b.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Reviews section ── */}
        <div className="rounded-3xl overflow-hidden shadow-sm mb-8"
          style={{ background: C.white, border: `1px solid ${C.line}` }}>
          <div className="p-6">

            {/* Header */}
            <div className="flex items-center justify-between mb-1">
              <h2 className="text-base font-bold" style={{ fontFamily: "Georgia, serif", color: C.dark }}>
                Customer Reviews
              </h2>
              {reviewMeta.review_count > 0 && (
                <div className="flex items-center gap-1.5">
                  <StarRow rating={Math.round(reviewMeta.avg_rating)} size={13}/>
                  <span className="text-sm font-bold" style={{ color: C.dark }}>
                    {reviewMeta.avg_rating.toFixed(1)}
                  </span>
                  <span className="text-xs" style={{ color: C.darkLight }}>
                    / 5 · {reviewMeta.review_count} review{reviewMeta.review_count !== 1 ? "s" : ""}
                  </span>
                </div>
              )}
            </div>

            {/* Review CTA */}
            {token ? (
              <p className="mt-2 text-xs" style={{ color: C.darkLight }}>
                Bought this?{" "}
                <button onClick={() => navigate("/orders")}
                  className="underline underline-offset-1 font-semibold" style={{ color: C.berry }}>
                  Go to your orders
                </button>{" "}to leave a review after delivery.
              </p>
            ) : (
              <p className="mt-2 text-xs" style={{ color: C.darkLight }}>
                <button onClick={() => navigate("/login")}
                  className="underline underline-offset-1 font-semibold" style={{ color: C.berry }}>
                  Log in
                </button>{" "}and purchase to leave a review.
              </p>
            )}

            {/* Review list */}
            {reviewsLoaded && reviews.length === 0 && (
              <p className="text-sm mt-5 pb-1" style={{ color: C.darkLight }}>
                No reviews yet. Be the first!
              </p>
            )}
            {reviews.map(rv => <ReviewCard key={rv.id} review={rv}/>)}

          </div>
        </div>

        {/* ── Related products ── */}
        {related.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-bold" style={{ fontFamily: "Georgia, serif", color: C.dark }}>
                You might also like
              </h2>
              <button onClick={() => navigate(`/products?q=${product.category || product.name.split(" ")[0]}`)}
                className="text-xs font-semibold flex items-center gap-1 transition-opacity hover:opacity-60"
                style={{ color: C.berry }}>
                See all
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </button>
            </div>
            <div className="flex gap-3 overflow-x-auto pb-1 scrollbar-hide">
              {related.map(p => <RelatedCard key={p.id} product={p} />)}
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

export default ProductDetails
