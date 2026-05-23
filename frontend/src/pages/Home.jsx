import { useEffect, useState, useRef } from "react"
import { Link, useNavigate } from "react-router-dom"
import api from "../api"
import { getProductVisual } from "../utils/categoryImage"
import ProductImage from "../components/ProductImage"

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

const BANNERS = [
  { title: "Premium Electronics",  sub: "Top brands, unbeatable prices",    tag: "Up to 40% off",   q: "electronics", g: "linear-gradient(135deg, #552619 0%, #7A3A26 100%)" },
  { title: "Fashion Redefined",    sub: "Curated styles for every occasion", tag: "New arrivals",    q: "fashion",     g: "linear-gradient(135deg, #B2456E 0%, #8F3457 100%)" },
  { title: "Sports & Fitness",     sub: "Gear up for greatness",             tag: "Best sellers",    q: "sports",      g: "linear-gradient(135deg, #7A3A26 0%, #552619 100%)" },
  { title: "Home & Living",        sub: "Transform your space",              tag: "Exclusive deals", q: "home",        g: "linear-gradient(135deg, #8F3457 0%, #B2456E 100%)" },
]

const CATEGORIES = [
  { label: "Mobiles",    emoji: "📱", q: "smartphone" },
  { label: "Laptops",    emoji: "💻", q: "laptop"     },
  { label: "Audio",      emoji: "🎧", q: "headphone"  },
  { label: "Cameras",    emoji: "📷", q: "camera"     },
  { label: "Fashion",    emoji: "👗", q: "fashion"    },
  { label: "Footwear",   emoji: "👟", q: "shoe"       },
  { label: "Appliances", emoji: "🍳", q: "appliance"  },
  { label: "Furniture",  emoji: "🛋️", q: "furniture"  },
  { label: "Sports",     emoji: "🏋️", q: "fitness"    },
  { label: "Books",      emoji: "📚", q: "book"       },
  { label: "Beauty",     emoji: "💄", q: "beauty"     },
  { label: "Toys",       emoji: "🧩", q: "toy"        },
]

function ProductCard({ product }) {
  const { emoji, bg } = getProductVisual(product.name, product.category)
  return (
    <Link to={`/product/${product.id}`} className="group flex-shrink-0 w-40">
      <div className="rounded-2xl overflow-hidden transition-all duration-200 group-hover:-translate-y-1 group-hover:shadow-md"
        style={{ background: C.white, border: `1px solid ${C.line}` }}>
        <ProductImage name={product.name} category={product.category} id={product.id} images={product.images || []} height="h-28" size={200}/>
        <div className="p-3">
          <p className="text-xs font-semibold truncate leading-snug" style={{ color: C.dark }}>{product.name}</p>
          <p className="text-sm font-bold mt-1" style={{ color: C.choc }}>₹{product.price?.toLocaleString("en-IN")}</p>
        </div>
      </div>
    </Link>
  )
}

function ProductRow({ title, badge, products, loading, viewAllQ }) {
  const navigate = useNavigate()
  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-base font-bold" style={{ color: C.dark, fontFamily: "Georgia, serif" }}>{title}</h2>
          {badge && (
            <span className="text-xs font-bold px-2 py-0.5 rounded-full uppercase tracking-wide"
              style={{ background: C.berry, color: C.white }}>{badge}</span>
          )}
        </div>
        {viewAllQ && (
          <button onClick={() => navigate(`/products?q=${viewAllQ}`)}
            className="text-xs font-semibold flex items-center gap-1 transition-opacity hover:opacity-60"
            style={{ color: C.choc }}>
            View all
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </button>
        )}
      </div>
      {loading ? (
        <div className="flex gap-3 overflow-x-auto pb-1 scrollbar-hide">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="flex-shrink-0 w-40 rounded-2xl overflow-hidden animate-pulse"
              style={{ background: C.white, border: `1px solid ${C.line}` }}>
              <div className="h-28" style={{ background: C.pink }}/>
              <div className="p-3 space-y-1.5">
                <div className="h-2 rounded-full w-3/4" style={{ background: C.pink }}/>
                <div className="h-2 rounded-full w-1/3" style={{ background: C.pink }}/>
              </div>
            </div>
          ))}
        </div>
      ) : products.length === 0 ? (
        <p className="text-sm py-4" style={{ color: C.darkLight }}>Check back soon.</p>
      ) : (
        <div className="flex gap-3 overflow-x-auto pb-1 scrollbar-hide">
          {products.map(p => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </section>
  )
}

export default function Home() {
  const navigate   = useNavigate()
  const isLoggedIn = !!localStorage.getItem("token")
  const [data,      setData]      = useState(null)
  const [loading,   setLoading]   = useState(true)
  const [bannerIdx, setBannerIdx] = useState(0)
  const [fade,      setFade]      = useState(true)
  const timer = useRef(null)

  useEffect(() => {
    api.get("/home/home")
      .then(res => setData(res.data))
      .catch(() => setData({ recommended: [], trending: [], latest: [] }))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    timer.current = setInterval(() => {
      setFade(false)
      setTimeout(() => { setBannerIdx(i => (i + 1) % BANNERS.length); setFade(true) }, 300)
    }, 5000)
    return () => clearInterval(timer.current)
  }, [])

  const goTo = (i) => {
    clearInterval(timer.current)
    setFade(false)
    setTimeout(() => { setBannerIdx(i); setFade(true) }, 200)
  }

  const b = BANNERS[bannerIdx]

  return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-6xl mx-auto px-5 py-8 space-y-10">

        {/* ── HERO ── */}
        <div className="relative rounded-3xl overflow-hidden" style={{ minHeight: 280, background: b.g }}>
          <div className="absolute -right-12 -top-12 w-64 h-64 rounded-full opacity-10"
            style={{ border: "1px solid #fff" }}/>
          <div className="absolute right-16 bottom-0 w-40 h-40 rounded-full opacity-10"
            style={{ border: "1px solid #fff", transform: "translate(0, 40%)" }}/>
          <div className={`relative z-10 px-10 py-12 flex flex-col justify-center transition-all duration-400 ${fade ? "opacity-100 translate-y-0" : "opacity-0 translate-y-1"}`}
            style={{ minHeight: 280 }}>
            <p className="text-xs font-bold uppercase tracking-widest mb-3 opacity-80" style={{ color: C.white }}>
              {b.tag}
            </p>
            <h1 className="text-3xl sm:text-4xl font-black mb-2 leading-none"
              style={{ fontFamily: "Georgia, serif", color: C.white, letterSpacing: "-0.02em" }}>
              {b.title}
            </h1>
            <p className="text-sm mb-7 font-medium opacity-80" style={{ color: C.white }}>{b.sub}</p>
            <button onClick={() => navigate(`/products?q=${b.q}`)}
              className="self-start px-6 py-2.5 rounded-xl font-bold text-sm transition-all hover:opacity-85 active:scale-95"
              style={{ background: C.white, color: C.dark }}>
              Shop Now →
            </button>
          </div>
          <div className="absolute bottom-5 left-10 flex gap-2 z-10">
            {BANNERS.map((_, i) => (
              <button key={i} onClick={() => goTo(i)}
                className="rounded-full transition-all duration-300"
                style={{ width: i === bannerIdx ? 24 : 6, height: 6,
                  background: i === bannerIdx ? "rgba(255,255,255,0.9)" : "rgba(255,255,255,0.35)" }}/>
            ))}
          </div>
        </div>

        {/* ── CATEGORIES ── */}
        <div>
          <p className="text-xs font-bold uppercase tracking-widest mb-4" style={{ color: C.darkLight }}>
            Browse Categories
          </p>
          <div className="flex gap-2.5 overflow-x-auto pb-1 scrollbar-hide">
            {CATEGORIES.map(c => (
              <button key={c.q} onClick={() => navigate(`/products?q=${c.q}`)}
                className="flex-shrink-0 flex flex-col items-center gap-1.5 px-4 py-3 rounded-2xl transition-all hover:shadow-sm hover:-translate-y-0.5 active:scale-95"
                style={{ background: C.white, border: `1px solid ${C.line}`, minWidth: 72 }}>
                <span className="text-xl">{c.emoji}</span>
                <span className="text-xs font-semibold whitespace-nowrap" style={{ color: C.dark }}>{c.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* ── PERKS ── */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            { icon: "🚚", title: "Free Delivery",   sub: "Orders above ₹499",   color: C.berry    },
            { icon: "🔄", title: "Easy Returns",    sub: "10-day hassle-free",   color: C.choc   },
            { icon: "🔒", title: "Secure Payments", sub: "100% safe & encrypted",color: C.berryDark},
          ].map(p => (
            <div key={p.title} className="flex items-center gap-3 p-4 rounded-2xl"
              style={{ background: C.white, border: `1px solid ${C.line}` }}>
              <div className="w-9 h-9 rounded-xl flex items-center justify-center text-lg flex-shrink-0"
                style={{ background: p.color + "18" }}>
                {p.icon}
              </div>
              <div>
                <p className="text-xs font-bold" style={{ color: C.dark }}>{p.title}</p>
                <p className="text-xs mt-0.5" style={{ color: C.darkLight }}>{p.sub}</p>
              </div>
            </div>
          ))}
        </div>

        {/* ── PRODUCT SECTIONS ── */}
        <div className="space-y-10">
          {isLoggedIn && data?.recommended?.length > 0 && (
            <ProductRow title="Recommended for you"  products={data?.recommended || []} loading={loading} viewAllQ="recommended"/>
          )}
          <ProductRow title="Trending Now"  badge="Hot" products={data?.trending || []} loading={loading} viewAllQ="trending"/>
          <ProductRow title="New Arrivals"            products={data?.latest   || []} loading={loading} viewAllQ="new"/>
        </div>

        {/* ── GUEST CTA ── */}
        {!isLoggedIn && (
          <div className="rounded-3xl overflow-hidden" style={{ background: C.choc }}>
            <div className="px-10 py-12 text-center relative">
              <div className="absolute inset-0 pointer-events-none"
                style={{ backgroundImage: "radial-gradient(ellipse at 50% 0%, rgba(255,255,255,0.12) 0%, transparent 70%)" }}/>
              <p className="text-xs font-bold uppercase tracking-widest mb-3 opacity-70" style={{ color: C.white }}>
                Members only
              </p>
              <h2 className="text-2xl font-black mb-2" style={{ fontFamily: "Georgia, serif", color: C.white }}>
                Personalised just for you
              </h2>
              <p className="text-sm font-medium mb-8 max-w-sm mx-auto opacity-80" style={{ color: C.white }}>
                Sign in to unlock AI-powered recommendations based on your taste
              </p>
              <div className="flex gap-3 justify-center">
                <Link to="/login"
                  className="px-6 py-2.5 rounded-xl font-bold text-sm transition-all hover:opacity-85"
                  style={{ background: C.white, color: C.choc }}>
                  Sign in
                </Link>
                <Link to="/register"
                  className="px-6 py-2.5 rounded-xl font-semibold text-sm border transition-all hover:opacity-70"
                  style={{ borderColor: "rgba(255,255,255,0.3)", color: C.white }}>
                  Create account
                </Link>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
