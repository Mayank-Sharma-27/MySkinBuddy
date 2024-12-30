"use client";

export function ChatIllustration() {
  return (
    <svg
      viewBox="0 0 400 300"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="w-full h-full"
    >
      <rect width="400" height="300" fill="white" />

      {/* Product Header */}
      <rect x="50" y="30" width="300" height="70" rx="8" fill="#F3F4F6" />
      <rect x="65" y="40" width="50" height="50" rx="4" fill="#E5E7EB" />
      <text x="130" y="60" fill="#111827" fontSize="14" fontWeight="500">
        Vitamin C Brightening Serum
      </text>
      <text x="130" y="80" fill="#6B7280" fontSize="12">
        The Ordinary • 30ml
      </text>

      {/* Chat Messages */}
      <rect x="50" y="120" width="250" height="45" rx="20" fill="#F3F4F6" />
      <text x="70" y="145" fill="#374151" fontSize="12">
        Is this suitable for sensitive skin?
      </text>
      <text x="70" y="157" fill="#6B7280" fontSize="10">
        You
      </text>

      <rect x="100" y="175" width="250" height="65" rx="20" fill="#A855F7" />
      <text x="120" y="195" fill="white" fontSize="12">
        Yes! This formula is gentle and contains
      </text>
      <text x="120" y="215" fill="white" fontSize="12">
        stabilized Vitamin C that's well-tolerated
      </text>
      <text x="120" y="230" fill="white" fontSize="12">
        by most sensitive skin types.
      </text>

      {/* Input Box */}
      <rect x="50" y="250" width="300" height="40" rx="20" fill="#F3F4F6" />
      <text x="70" y="275" fill="#6B7280" fontSize="12">
        Ask about ingredients, benefits, or usage...
      </text>
      <circle cx="330" cy="270" r="12" fill="#A855F7" />
      <path
        d="M325 270L335 270M330 265L330 275"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
      />

      {/* Product Icon */}
      <path d="M75 50h30v30h-30z" fill="#A855F7" opacity="0.2" />
    </svg>
  );
}
