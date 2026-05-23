const C = {
  pink:       "#FBEAE7",
  pinkDark:   "#F5D0C8",
  berry:      "#B2456E",
  berryDark:  "#8F3457",
  choc:       "#552619",
  chocolight: "#7A3A26",
  dark:       "#2C1810",
  darkLight:  "#8B6355",
  white:      "#FFF8F6",
  line:       "rgba(85,38,25,0.10)",
  lineStrong: "rgba(85,38,25,0.18)",
}

const SERVICES = [
  { name: "Product Service",        desc: "Catalogue, stock, categories & Elasticsearch indexing", url: "/docs/products/",       icon: "📦", tag: "REST" },
  { name: "Order Service",          desc: "Order lifecycle, payment processing & vendor orders",   url: "/docs/orders/",         icon: "🧾", tag: "REST" },
  { name: "Cart Service",           desc: "Redis-backed cart, checkout & stock validation",        url: "/docs/cart/",           icon: "🛒", tag: "REST" },
  { name: "Search Service",         desc: "ElasticSearch fuzzy search + autocomplete suggestions", url: "/docs/search/",         icon: "🔍", tag: "REST" },
  { name: "Recommendation Service", desc: "Matrix Factorisation collaborative filtering engine",   url: "/docs/recommend/",      icon: "🤖", tag: "REST" },
  { name: "Home Service",           desc: "Homepage aggregator — trending & personalised recs",    url: "/docs/home/",           icon: "🏠", tag: "REST" },
  { name: "Notification API",       desc: "In-app notifications with unread count polling",        url: "/docs/notifications/",  icon: "🔔", tag: "REST" },
  { name: "Analytics Service",      desc: "Product view tracking & trending sorted-set ranking",   url: "/docs/analytics/",      icon: "📊", tag: "REST" },
]

function ServiceCard({ service }) {
  return (
    <a href={service.url} target="_blank" rel="noreferrer"
      className="group rounded-2xl p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md flex flex-col gap-3"
      style={{ background: C.white, border: `1px solid ${C.line}` }}>

      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
            style={{ background: C.pinkDark }}>
            {service.icon}
          </div>
          <div>
            <h2 className="text-sm font-bold leading-tight" style={{ color: C.dark }}>{service.name}</h2>
            <span className="text-xs font-bold px-1.5 py-0.5 rounded mt-0.5 inline-block"
              style={{ background: C.berry + "18", color: C.berry }}>{service.tag}</span>
          </div>
        </div>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
          className="flex-shrink-0 mt-1 transition-all group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
          style={{ color: C.darkLight }}>
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
          <polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
        </svg>
      </div>

      <p className="text-xs leading-relaxed font-medium" style={{ color: C.darkLight }}>{service.desc}</p>

      <p className="text-xs font-mono mt-auto" style={{ color: C.berry + "99" }}>{service.url}</p>
    </a>
  )
}

function ApiDocs() {
  return (
    <div style={{ background: C.pink, minHeight: "100vh" }}>
      <div className="max-w-4xl mx-auto px-5 py-10">

        {/* Header */}
        <div className="rounded-3xl p-8 mb-8"
          style={{ background: C.choc }}>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
              style={{ background: "rgba(251,234,231,0.12)" }}>
              🛠️
            </div>
            <span className="text-xs font-bold uppercase tracking-widest opacity-60" style={{ color: C.pinkDark }}>
              Developer Docs
            </span>
          </div>
          <h1 className="text-2xl font-black mb-2"
            style={{ fontFamily: "Georgia, serif", color: C.pink }}>
            API Documentation
          </h1>
          <p className="text-sm font-medium leading-relaxed max-w-xl"
            style={{ color: C.pinkDark, opacity: 0.75 }}>
            Interactive Swagger UI for all ShopSphere microservices. Click any service card to explore endpoints, request schemas, and make live API calls.
          </p>
        </div>

        {/* Service grid */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {SERVICES.map(s => <ServiceCard key={s.name} service={s} />)}
        </div>

        {/* Auth note */}
        <div className="rounded-2xl p-5 flex gap-4"
          style={{ background: C.white, border: `1.5px solid ${C.lineStrong}` }}>
          <div className="w-9 h-9 rounded-xl flex items-center justify-center text-lg flex-shrink-0"
            style={{ background: C.pinkDark }}>
            🔐
          </div>
          <div>
            <p className="text-sm font-bold mb-1" style={{ color: C.dark }}>Auth Service (Flask)</p>
            <p className="text-xs leading-relaxed font-medium" style={{ color: C.darkLight }}>
              Flask does not auto-generate Swagger docs. Authentication endpoints are available at{" "}
              <code className="px-1.5 py-0.5 rounded text-xs font-mono"
                style={{ background: C.pinkDark, color: C.choc }}>POST /auth/register</code>{" "}and{" "}
              <code className="px-1.5 py-0.5 rounded text-xs font-mono"
                style={{ background: C.pinkDark, color: C.choc }}>POST /auth/login</code>
            </p>
          </div>
        </div>

      </div>
    </div>
  )
}

export default ApiDocs
