import { useNavigate } from "react-router-dom"

const C = {
  pink: "#FBEAE7", berry: "#B2456E", berryDark: "#8F3457",
  dark: "#2C1810", darkLight: "#8B6355", white: "#FFF8F6", line: "rgba(85,38,25,0.10)",
}

export default function VendorPending() {
  const navigate = useNavigate()
  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: C.pink }}>
      <div className="w-full max-w-md text-center">
        <div className="rounded-3xl p-10" style={{ background: C.white, border: `1px solid ${C.line}` }}>
          <div className="text-6xl mb-5">⏳</div>
          <h1 className="text-2xl font-black mb-3 tracking-tight" style={{ fontFamily: "Georgia, serif", color: C.dark }}>
            Application Submitted!
          </h1>
          <p className="text-sm leading-relaxed mb-2" style={{ color: C.darkLight }}>
            Your vendor application is under review. Our admin team will verify your details and send you an email once a decision has been made.
          </p>
          <p className="text-xs mb-8" style={{ color: C.darkLight }}>
            This usually takes 1–2 business days.
          </p>
          <button onClick={() => navigate("/")}
            className="w-full py-3 rounded-2xl text-sm font-bold transition-all hover:opacity-85"
            style={{ background: C.berry, color: C.white }}>
            Back to Home
          </button>
          <button onClick={() => navigate("/login")}
            className="w-full py-3 rounded-2xl text-sm font-bold mt-3 transition-all hover:opacity-70"
            style={{ background: "transparent", color: C.berry, border: `1.5px solid ${C.berry}` }}>
            Log In as Customer
          </button>
        </div>
      </div>
    </div>
  )
}
