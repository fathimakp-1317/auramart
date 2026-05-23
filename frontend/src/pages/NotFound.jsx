import { useNavigate } from "react-router-dom"

const C = {
  pink:      "#FBEAE7",
  pinkDark:  "#F5D0C8",
  berry:     "#B2456E",
  choc:      "#552619",
  dark:      "#2C1810",
  darkLight: "#8B6355",
  white:     "#FFF8F6",
  line:      "rgba(85,38,25,0.10)",
}

export default function NotFound() {
  const navigate = useNavigate()

  return (
    <div style={{ background: C.pink, minHeight: "100vh" }}
      className="flex items-center justify-center px-5">
      <div className="text-center max-w-sm">

        {/* Big 404 */}
        <div className="relative inline-block mb-6">
          <p className="text-9xl font-black select-none"
            style={{ color: C.pinkDark, fontFamily: "Georgia, serif", lineHeight: 1 }}>
            404
          </p>
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-5xl">🛒</p>
          </div>
        </div>

        <h1 className="text-2xl font-black mb-2 tracking-tight"
          style={{ fontFamily: "Georgia, serif", color: C.dark }}>
          Page not found
        </h1>
        <p className="text-sm font-medium mb-8 leading-relaxed" style={{ color: C.darkLight }}>
          Looks like this page wandered off. Let's get you back to something good.
        </p>

        <div className="flex gap-3 justify-center">
          <button onClick={() => navigate(-1)}
            className="px-5 py-2.5 rounded-xl text-sm font-semibold border transition-all hover:opacity-75"
            style={{ borderColor: C.line, color: C.dark, background: C.white }}>
            ← Go back
          </button>
          <button onClick={() => navigate("/")}
            className="px-5 py-2.5 rounded-xl text-sm font-bold transition-all hover:opacity-85"
            style={{ background: C.berry, color: C.white }}>
            Go home
          </button>
        </div>

        {/* Quick links */}
        <div className="mt-10 flex items-center justify-center gap-6">
          {[
            { label: "Products", path: "/products" },
            { label: "Orders",   path: "/orders"   },
            { label: "Profile",  path: "/profile"  },
          ].map(l => (
            <button key={l.path} onClick={() => navigate(l.path)}
              className="text-xs font-semibold transition-opacity hover:opacity-60"
              style={{ color: C.darkLight }}>
              {l.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
