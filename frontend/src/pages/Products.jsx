import { useEffect, useState, useRef, useCallback } from "react"
import { Link, useSearchParams } from "react-router-dom"
import { useNavigate as useNav } from "react-router-dom"
import api from "../api"
import ProductImage from "../components/ProductImage"
import { useToast } from "../components/Toast"

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

const SORT_OPTIONS = [
  { value: "newest",      label: "Newest first"       },
  { value: "price_asc",   label: "Price: Low → High"  },
  { value: "price_desc",  label: "Price: High → Low"  },
  { value: "rating_desc", label: "Top rated"           },
  { value: "relevance",   label: "Best match"          },
]

const RATING_OPTIONS = [
  { value: 4,   label: "4★ & above" },
  { value: 3,   label: "3★ & above" },
  { value: 2,   label: "2★ & above" },
]

function StarMini({ rating }) {
  return (
    <span className="inline-flex items-center gap-0.5">
      {[1,2,3,4,5].map(n => (
        <svg key={n} width="10" height="10" viewBox="0 0 24 24"
          fill={rating >= n ? C.berry : "none"} stroke={C.berry} strokeWidth="2">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>
      ))}
    </span>
  )
}

// ── Product card ──────────────────────────────────────────────────────────────
function ProductCard({ product }) {
  const toast    = useToast()
  const navigate = useNav()
  const [adding, setAdding] = useState(false)

  const addToCart = async (e) => {
    e.preventDefault(); e.stopPropagation()
    if (!localStorage.getItem("token")) { navigate("/login"); return }
    if (product.stock === 0) return
    setAdding(true)
    try {
      await api.post("/cart/cart", { product_id: product.id, quantity: 1 })
      toast({ message: `${product.name} added to cart!`, type: "success" })
    } catch (err) {
      toast({ message: err.response?.data?.detail || "Failed to add to cart", type: "error" })
    } finally { setAdding(false) }
  }

  return (
    <Link to={`/product/${product.id}`} className="group">
      <div className="rounded-2xl overflow-hidden transition-all duration-200 group-hover:-translate-y-1 group-hover:shadow-lg"
        style={{ background: C.white, border: `1px solid ${C.line}` }}>
        <ProductImage name={product.name} category={product.category} id={product.id}
          images={product.images || []} height="h-36" size={300}/>
        <div className="p-4">
          <h2 className="font-semibold text-sm truncate mb-1 leading-snug" style={{ color: C.dark }}>
            {product.name}
          </h2>
          {product.avg_rating > 0 && (
            <div className="flex items-center gap-1 mb-1">
              <StarMini rating={Math.round(product.avg_rating)}/>
              <span className="text-xs font-semibold" style={{ color: C.darkLight }}>
                {product.avg_rating.toFixed(1)} ({product.review_count})
              </span>
            </div>
          )}
          <div className="flex items-center justify-between mt-1">
            <p className="font-bold text-sm" style={{ color: C.choc }}>
              ₹{product.price?.toLocaleString("en-IN")}
            </p>
            <button onClick={addToCart} disabled={adding || product.stock === 0}
              className="w-7 h-7 rounded-lg flex items-center justify-center transition-all hover:opacity-80 active:scale-90 disabled:opacity-30"
              style={{ background: C.berry, color: C.white }}
              title={product.stock === 0 ? "Out of stock" : "Add to cart"}>
              {adding ? (
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="animate-spin">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83"/>
                </svg>
              ) : (
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
              )}
            </button>
          </div>
          <span className={`inline-block text-xs mt-2 px-2 py-0.5 rounded-full font-semibold ${
            product.stock > 0 ? "bg-pink-100 text-pink-800" : "bg-red-50 text-red-600"
          }`}>
            {product.stock > 0 ? `${product.stock} in stock` : "Out of stock"}
          </span>
        </div>
      </div>
    </Link>
  )
}

// ── Sidebar ───────────────────────────────────────────────────────────────────
function Sidebar({ filters, onChange, onClear, categories, activeCount }) {
  const { minPrice, maxPrice, minRating, categoryId, sortBy } = filters

  const inp = {
    width: "100%", background: C.white, border: `1.5px solid ${C.lineStrong}`,
    borderRadius: "10px", padding: "8px 12px", fontSize: "13px",
    color: C.dark, outline: "none", fontFamily: "inherit",
  }

  const SectionHead = ({ children }) => (
    <p className="text-xs font-black uppercase tracking-widest mb-3" style={{ color: C.darkLight }}>
      {children}
    </p>
  )

  const divider = <div className="my-5" style={{ borderTop: `1px solid ${C.line}` }}/>

  return (
    <div className="rounded-2xl p-5 sticky top-6" style={{ background: C.white, border: `1px solid ${C.line}` }}>

      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <p className="font-black text-sm" style={{ color: C.dark }}>
          Filters {activeCount > 0 && (
            <span className="ml-1.5 text-xs font-black px-1.5 py-0.5 rounded-full"
              style={{ background: C.berry, color: "white" }}>
              {activeCount}
            </span>
          )}
        </p>
        {activeCount > 0 && (
          <button onClick={onClear}
            className="text-xs font-bold transition-opacity hover:opacity-60"
            style={{ color: C.berry }}>
            Clear all
          </button>
        )}
      </div>

      {/* Sort */}
      <SectionHead>Sort by</SectionHead>
      <div className="flex flex-col gap-1.5">
        {SORT_OPTIONS.map(o => (
          <button key={o.value} onClick={() => onChange("sortBy", o.value)}
            className="text-left text-sm px-3 py-2 rounded-xl font-medium transition-all"
            style={{
              background: sortBy === o.value ? C.berry : "transparent",
              color:      sortBy === o.value ? "white"  : C.darkSoft,
            }}>
            {o.label}
          </button>
        ))}
      </div>

      {divider}

      {/* Price range */}
      <SectionHead>Price range</SectionHead>
      <div className="flex items-center gap-2">
        <input type="number" placeholder="Min ₹" value={minPrice}
          onChange={e => onChange("minPrice", e.target.value)}
          style={{ ...inp }}/>
        <span style={{ color: C.darkLight, flexShrink: 0 }}>—</span>
        <input type="number" placeholder="Max ₹" value={maxPrice}
          onChange={e => onChange("maxPrice", e.target.value)}
          style={{ ...inp }}/>
      </div>

      {divider}

      {/* Rating */}
      <SectionHead>Min. Rating</SectionHead>
      <div className="flex flex-col gap-1.5">
        <button onClick={() => onChange("minRating", "")}
          className="text-left text-sm px-3 py-2 rounded-xl font-medium transition-all"
          style={{
            background: !minRating ? C.berry : "transparent",
            color:      !minRating ? "white"  : C.darkSoft,
          }}>
          All ratings
        </button>
        {RATING_OPTIONS.map(o => (
          <button key={o.value} onClick={() => onChange("minRating", o.value)}
            className="text-left text-sm px-3 py-2 rounded-xl font-medium flex items-center gap-2 transition-all"
            style={{
              background: Number(minRating) === o.value ? C.berry : "transparent",
              color:      Number(minRating) === o.value ? "white"  : C.darkSoft,
            }}>
            <StarMini rating={o.value}/>
            <span>{o.label}</span>
          </button>
        ))}
      </div>

      {divider}

      {/* Category */}
      {categories.length > 0 && (
        <>
          <SectionHead>Category</SectionHead>
          <div className="flex flex-col gap-1.5">
            <button onClick={() => onChange("categoryId", "")}
              className="text-left text-sm px-3 py-2 rounded-xl font-medium transition-all"
              style={{
                background: !categoryId ? C.berry : "transparent",
                color:      !categoryId ? "white"  : C.darkSoft,
              }}>
              All categories
            </button>
            {categories.map(c => (
              <button key={c.id} onClick={() => onChange("categoryId", c.id)}
                className="text-left text-sm px-3 py-2 rounded-xl font-medium transition-all truncate"
                style={{
                  background: categoryId === c.id ? C.berry : "transparent",
                  color:      categoryId === c.id ? "white"  : C.darkSoft,
                }}>
                {c.name}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
function Products() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialQ = searchParams.get("q") || ""

  const [products,    setProducts]    = useState([])
  const [query,       setQuery]       = useState(initialQ)
  const [suggestions, setSuggestions] = useState([])
  const [showSuggest, setShowSuggest] = useState(false)
  const [categories,  setCategories]  = useState([])
  const [total,       setTotal]       = useState(null)
  const [page,        setPage]        = useState(1)
  const [totalPages,  setTotalPages]  = useState(1)
  const [loading,     setLoading]     = useState(false)
  const [searched,    setSearched]    = useState(!!initialQ)
  const [error,       setError]       = useState("")
  const [searchFocus, setSearchFocus] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const [filters, setFilters] = useState({
    minPrice:   "",
    maxPrice:   "",
    minRating:  "",
    categoryId: "",
    sortBy:     "relevance",
  })

  const PAGE_SIZE    = 20
  const suggestTimer = useRef(null)

  // Count active filters (excluding sortBy default)
  const activeCount = [
    filters.minPrice,
    filters.maxPrice,
    filters.minRating,
    filters.categoryId,
    // sortBy default not counted
  ].filter(Boolean).length

  useEffect(() => {
    api.get("/products/categories").then(res => setCategories(res.data)).catch(() => {})
    if (initialQ) runSearch(initialQ, filters, 1)
    else          loadAll(filters, 1)
  }, [])

  // Re-fetch when filters change
  const prevFilters = useRef(filters)
  useEffect(() => {
    if (prevFilters.current === filters) return
    prevFilters.current = filters
    if (searched) runSearch(query, filters, 1)
    else          loadAll(filters, 1)
  }, [filters])

  const buildProductParams = (f) => {
    const p = new URLSearchParams()
    if (f.minPrice)   p.set("min_price",   f.minPrice)
    if (f.maxPrice)   p.set("max_price",   f.maxPrice)
    if (f.minRating)  p.set("min_rating",  f.minRating)
    if (f.categoryId) p.set("category_id", f.categoryId)
    if (f.sortBy)     p.set("sort_by",     f.sortBy)
    return p
  }

  const loadAll = async (f = filters, p = 1) => {
    setLoading(true); setError("")
    try {
      const params = buildProductParams(f)
      const res    = await api.get(`/products/products?${params}`)
      const all    = res.data
      const start  = (p - 1) * PAGE_SIZE
      setProducts(all.slice(start, start + PAGE_SIZE))
      setTotal(all.length)
      setTotalPages(Math.ceil(all.length / PAGE_SIZE))
      setPage(p)
      setSearched(false)
    } catch { setError("Could not load products") }
    finally  { setLoading(false) }
  }

  const runSearch = async (q, f = filters, p = 1) => {
    if (!q.trim()) { loadAll(f, 1); return }
    setLoading(true); setError(""); setSuggestions([]); setShowSuggest(false)
    try {
      const params = new URLSearchParams({ q: q.trim(), page: p, size: PAGE_SIZE, sort_by: f.sortBy })
      if (f.minPrice)   params.set("min_price",   f.minPrice)
      if (f.maxPrice)   params.set("max_price",   f.maxPrice)
      if (f.minRating)  params.set("min_rating",  f.minRating)
      if (f.categoryId) params.set("category_id", f.categoryId)
      const res = await api.get(`/search/search?${params}`)
      setProducts(res.data.results)
      setTotal(res.data.total)
      setTotalPages(res.data.pages || 1)
      setPage(p)
      setSearched(true)
      setSearchParams({ q: q.trim(), page: p })
      window.scrollTo({ top: 0, behavior: "smooth" })
    } catch { setError("Search failed — please try again") }
    finally  { setLoading(false) }
  }

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const clearFilters = () => {
    const reset = { minPrice: "", maxPrice: "", minRating: "", categoryId: "", sortBy: "relevance" }
    setFilters(reset)
  }

  const goToPage = (p) => {
    if (searched) runSearch(query, filters, p)
    else          loadAll(filters, p)
  }

  const onQueryChange = useCallback((val) => {
    setQuery(val)
    clearTimeout(suggestTimer.current)
    if (val.length < 2) { setSuggestions([]); setShowSuggest(false); return }
    suggestTimer.current = setTimeout(async () => {
      try {
        const res = await api.get(`/search/suggest?q=${encodeURIComponent(val)}`)
        setSuggestions(res.data); setShowSuggest(res.data.length > 0)
      } catch { setSuggestions([]) }
    }, 250)
  }, [])

  const pickSuggestion = (s) => {
    setQuery(s.name); setSuggestions([]); setShowSuggest(false)
    runSearch(s.name, filters, 1)
  }

  const clearSearch = () => {
    setQuery(""); setSuggestions([]); setShowSuggest(false)
    setSearchParams({})
    loadAll(filters, 1)
  }

  // ── Pagination ──────────────────────────────────────────────────────────────
  const Pagination = () => {
    if (totalPages <= 1) return null
    const pages = new Set([1, totalPages])
    for (let i = Math.max(1, page - 2); i <= Math.min(totalPages, page + 2); i++) pages.add(i)
    const pageList = [...pages].sort((a, b) => a - b)
    return (
      <div className="flex items-center justify-center gap-1.5 mt-10">
        <button onClick={() => goToPage(page - 1)} disabled={page === 1 || loading}
          className="px-4 py-2 rounded-xl text-sm font-semibold transition-all hover:opacity-75 disabled:opacity-30"
          style={{ background: C.white, border: `1.5px solid ${C.lineStrong}`, color: C.dark }}>
          ← Prev
        </button>
        {pageList.map((p, idx) => {
          const prev = pageList[idx - 1]
          return (
            <span key={p} className="flex items-center gap-1.5">
              {prev && p - prev > 1 && <span className="px-1 text-sm" style={{ color: C.darkLight }}>…</span>}
              <button onClick={() => goToPage(p)} disabled={loading}
                className="w-9 h-9 rounded-xl text-sm font-bold transition-all"
                style={{
                  background: p === page ? C.berry : C.white,
                  color:      p === page ? C.white : C.dark,
                  border:     `1.5px solid ${p === page ? C.berry : C.lineStrong}`,
                }}>
                {p}
              </button>
            </span>
          )
        })}
        <button onClick={() => goToPage(page + 1)} disabled={page === totalPages || loading}
          className="px-4 py-2 rounded-xl text-sm font-semibold transition-all hover:opacity-75 disabled:opacity-30"
          style={{ background: C.white, border: `1.5px solid ${C.lineStrong}`, color: C.dark }}>
          Next →
        </button>
      </div>
    )
  }

  return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-7xl mx-auto px-5 py-8">

        {/* ── Page header ── */}
        <h1 className="text-2xl font-black tracking-tight mb-5"
          style={{ fontFamily: "Georgia, serif", color: C.dark }}>
          {searched && query ? `Results for "${query}"` : "All Products"}
        </h1>

        {/* ── Search bar ── */}
        <div className="flex gap-3 mb-6 items-center">
          <div className="relative flex-1">
            <div className="flex rounded-xl overflow-hidden"
              style={{ background: C.white, border: `1.5px solid ${searchFocus ? C.choc : C.lineStrong}`, transition: "border-color 0.15s" }}>
              <span className="pl-3.5 flex items-center flex-shrink-0">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={C.darkLight} strokeWidth="2">
                  <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                </svg>
              </span>
              <input type="text" value={query}
                onChange={e => onQueryChange(e.target.value)}
                onKeyDown={e => {
                  if (e.key === "Enter") { setShowSuggest(false); runSearch(query, filters, 1) }
                  if (e.key === "Escape") setShowSuggest(false)
                }}
                onFocus={() => { setSearchFocus(true); suggestions.length > 0 && setShowSuggest(true) }}
                onBlur={() => setSearchFocus(false)}
                placeholder="Search products… typos OK!"
                className="flex-1 px-3 py-2.5 text-sm bg-transparent outline-none"
                style={{ color: C.dark }}
              />
              {query && (
                <button onClick={clearSearch}
                  className="pr-3 flex items-center text-lg font-bold transition-opacity hover:opacity-60"
                  style={{ color: C.darkLight }}>×</button>
              )}
            </div>

            {showSuggest && (
              <div className="absolute top-full left-0 right-0 mt-1.5 rounded-xl shadow-xl overflow-hidden z-20"
                style={{ background: C.white, border: `1px solid ${C.lineStrong}` }}>
                {suggestions.map((s, i) => (
                  <button key={i} onClick={() => pickSuggestion(s)}
                    className="w-full text-left px-4 py-3 text-sm flex justify-between items-center transition-colors hover:opacity-70"
                    style={{ color: C.dark, borderBottom: i < suggestions.length - 1 ? `1px solid ${C.line}` : "none" }}>
                    <span className="flex items-center gap-2">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={C.darkLight} strokeWidth="2">
                        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                      </svg>
                      {s.name}
                    </span>
                    <span className="text-xs font-semibold" style={{ color: C.choc }}>₹{s.price}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <button onClick={() => runSearch(query, filters, 1)} disabled={loading}
            className="px-6 py-2.5 rounded-xl text-sm font-bold transition-all hover:opacity-85 disabled:opacity-50 flex-shrink-0"
            style={{ background: C.berry, color: C.white }}>
            {loading ? "…" : "Search"}
          </button>

          {/* Mobile filter toggle */}
          <button onClick={() => setSidebarOpen(o => !o)}
            className="lg:hidden flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-bold flex-shrink-0 relative"
            style={{ background: C.white, border: `1.5px solid ${C.lineStrong}`, color: C.dark }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="11" y1="18" x2="13" y2="18"/>
            </svg>
            Filters
            {activeCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full text-xs font-black flex items-center justify-center"
                style={{ background: C.berry, color: "white" }}>{activeCount}</span>
            )}
          </button>
        </div>

        {/* Results meta */}
        {error && <p className="text-sm mb-4 font-medium text-red-600">{error}</p>}
        {total !== null && !loading && (
          <p className="text-sm mb-5 font-medium" style={{ color: C.darkLight }}>
            <span style={{ color: C.dark }}>{total.toLocaleString()}</span>{" "}
            {searched ? `result${total !== 1 ? "s" : ""}` : "products"}
            {totalPages > 1 && <span> — page {page} of {totalPages}</span>}
          </p>
        )}

        {/* ── Layout: sidebar + grid ── */}
        <div className="flex gap-6 items-start">

          {/* Sidebar — desktop always visible, mobile drawer */}
          <div className={`
            flex-shrink-0 w-56
            lg:block
            ${sidebarOpen ? "block fixed inset-0 z-30 overflow-auto pt-4 px-4 pb-20" : "hidden"}
          `}
            style={sidebarOpen ? { background: C.pink } : {}}>
            {sidebarOpen && (
              <div className="flex justify-between items-center mb-4">
                <p className="font-black text-base" style={{ color: C.dark }}>Filters</p>
                <button onClick={() => setSidebarOpen(false)}
                  className="text-2xl font-bold" style={{ color: C.darkLight }}>×</button>
              </div>
            )}
            <Sidebar
              filters={filters}
              onChange={handleFilterChange}
              onClear={clearFilters}
              categories={categories}
              activeCount={activeCount}
            />
          </div>

          {/* Product grid */}
          <div className="flex-1 min-w-0">
            {loading ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 gap-4">
                {[...Array(8)].map((_, i) => (
                  <div key={i} className="rounded-2xl overflow-hidden animate-pulse"
                    style={{ background: C.white, border: `1px solid ${C.line}` }}>
                    <div className="h-36" style={{ background: C.pink }}/>
                    <div className="p-4 space-y-2">
                      <div className="h-3 rounded-full w-3/4" style={{ background: C.pink }}/>
                      <div className="h-3 rounded-full w-1/3" style={{ background: C.pink }}/>
                    </div>
                  </div>
                ))}
              </div>
            ) : products.length === 0 ? (
              <div className="text-center py-24">
                <p className="text-5xl mb-4">🔍</p>
                <p className="text-lg font-bold mb-2" style={{ color: C.dark }}>No products found</p>
                <p className="text-sm" style={{ color: C.darkLight }}>
                  Try adjusting your filters or{" "}
                  <button onClick={() => { clearFilters(); clearSearch() }}
                    className="font-bold underline underline-offset-2 transition-opacity hover:opacity-60"
                    style={{ color: C.choc }}>browse all</button>
                </p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 gap-4">
                  {products.map(p => <ProductCard key={p.id} product={p}/>)}
                </div>
                <Pagination/>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Products
