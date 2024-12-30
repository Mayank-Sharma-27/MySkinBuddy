"use client";

export function SearchIllustration() {
  return (
    <svg
      viewBox="0 0 400 300"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="w-full h-full"
    >
      <rect width="400" height="300" fill="white" />

      {/* Search Bar */}
      <rect x="50" y="100" width="300" height="50" rx="8" fill="#F3F4F6" />
      <text x="70" y="130" fill="#6B7280" fontSize="14">
        Search for "Vitamin C Serum"
      </text>
      <rect x="290" y="110" width="40" height="30" rx="4" fill="#A855F7" />
      <path
        d="M305 125L315 125M310 120L310 130"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
      />

      {/* Dropdown */}
      <rect
        x="50"
        y="160"
        width="300"
        height="120"
        rx="8"
        fill="white"
        stroke="#E5E7EB"
      />

      {/* Product 1 */}
      <rect x="65" y="175" width="40" height="40" rx="4" fill="#F3F4F6" />
      <text x="120" y="195" fill="#111827" fontSize="14" fontWeight="500">
        Vitamin C Brightening Serum
      </text>
      <text x="120" y="210" fill="#6B7280" fontSize="12">
        The Ordinary
      </text>

      {/* Product 2 */}
      <rect x="65" y="225" width="40" height="40" rx="4" fill="#F3F4F6" />
      <text x="120" y="245" fill="#111827" fontSize="14" fontWeight="500">
        20% Vitamin C + E Serum
      </text>
      <text x="120" y="260" fill="#6B7280" fontSize="12">
        SkinCeuticals
      </text>

      {/* Magnifying Glass */}
      <circle cx="305" cy="125" r="8" stroke="#FFFFFF" strokeWidth="2" />
      <line
        x1="311"
        y1="131"
        x2="315"
        y2="135"
        stroke="#FFFFFF"
        strokeWidth="2"
        strokeLinecap="round"
      />

      {/* Product Icons */}
      <path d="M75 190h20v10h-20z" fill="#A855F7" opacity="0.2" />
      <path d="M75 240h20v10h-20z" fill="#F97316" opacity="0.2" />
    </svg>
  );
}
