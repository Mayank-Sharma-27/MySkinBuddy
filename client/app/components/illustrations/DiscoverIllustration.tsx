"use client";

export function DiscoverIllustration() {
  return (
    <svg
      viewBox="0 0 400 300"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="w-full h-full"
    >
      <rect width="400" height="300" fill="white" />

      {/* Main Product */}
      <rect x="150" y="30" width="100" height="100" rx="8" fill="#F3F4F6" />
      <rect x="165" y="45" width="70" height="70" rx="4" fill="#E5E7EB" />
      <text
        x="150"
        y="150"
        fill="#111827"
        fontSize="12"
        textAnchor="middle"
        x="200"
      >
        Vitamin C Brightening Serum
      </text>
      <text
        x="150"
        y="165"
        fill="#6B7280"
        fontSize="10"
        textAnchor="middle"
        x="200"
      >
        The Ordinary
      </text>

      {/* Connection Lines */}
      <path
        d="M200 170L120 200M200 170L280 200"
        stroke="#A855F7"
        strokeWidth="2"
        strokeDasharray="4 4"
      />

      {/* Similar Product 1 */}
      <rect x="70" y="200" width="100" height="100" rx="8" fill="#F3F4F6" />
      <rect x="85" y="215" width="70" height="70" rx="4" fill="#E5E7EB" />
      <text
        x="70"
        y="290"
        fill="#111827"
        fontSize="11"
        textAnchor="middle"
        x="120"
      >
        15% Vitamin C + Ferulic
      </text>
      <text
        x="70"
        y="305"
        fill="#6B7280"
        fontSize="10"
        textAnchor="middle"
        x="120"
      >
        SkinCeuticals
      </text>

      {/* Similar Product 2 */}
      <rect x="230" y="200" width="100" height="100" rx="8" fill="#F3F4F6" />
      <rect x="245" y="215" width="70" height="70" rx="4" fill="#E5E7EB" />
      <text
        x="230"
        y="290"
        fill="#111827"
        fontSize="11"
        textAnchor="middle"
        x="280"
      >
        20% Vitamin C Serum
      </text>
      <text
        x="230"
        y="305"
        fill="#6B7280"
        fontSize="10"
        textAnchor="middle"
        x="280"
      >
        Timeless
      </text>

      {/* Product Icons */}
      <path d="M180 60h40v40h-40z" fill="#A855F7" opacity="0.2" />
      <path d="M100 230h40v40h-40z" fill="#F97316" opacity="0.2" />
      <path d="M260 230h40v40h-40z" fill="#F97316" opacity="0.2" />

      {/* Sparkles */}
      <path d="M190 40l5-5 5 5-5 5z" fill="#F97316" />
      <path d="M100 220l5-5 5 5-5 5z" fill="#F97316" />
      <path d="M290 220l5-5 5 5-5 5z" fill="#F97316" />
    </svg>
  );
}
