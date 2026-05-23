import { useState } from "react"
import { getProductVisual } from "../utils/categoryImage"

/**
 * ProductImage
 * Shows vendor-uploaded images if available (first image = main).
 * Falls back to emoji tile if no images uploaded.
 *
 * Props:
 *   name      — product name string
 *   category  — product category string
 *   id        — product id
 *   images    — array of base64 strings from product data (optional)
 *   height    — CSS height class e.g. "h-28" or "h-56" (default "h-36")
 *   size      — unused, kept for API compatibility
 */
export default function ProductImage({ name = "", category = "", id = "", images = [], height = "h-36", size = 400 }) {
  const { emoji, bg } = getProductVisual(name, category)
  const [errored, setErrored] = useState(false)

  const mainImage = Array.isArray(images) && images.length > 0 ? images[0] : null

  if (mainImage && !errored) {
    return (
      <div className={`${height} relative overflow-hidden bg-gray-100 flex items-center justify-center`}>
        <img
          src={mainImage}
          alt={name}
          onError={() => setErrored(true)}
          className="absolute inset-0 w-full h-full object-cover"
          loading="lazy"
        />
        <div className="absolute inset-0"
          style={{ background: "linear-gradient(to bottom, transparent 55%, rgba(0,0,0,0.15))" }}/>
      </div>
    )
  }

  // Emoji fallback
  return (
    <div className={`${bg} ${height} flex items-center justify-center`}>
      <span className="text-5xl select-none">{emoji}</span>
    </div>
  )
}
