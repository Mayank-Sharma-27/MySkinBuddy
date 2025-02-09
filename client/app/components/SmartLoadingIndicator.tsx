"use client";

import { useEffect, useState } from "react";

const loadingPhases = [
  "Reading product info...",
  "Analyzing your question...",
  "Searching relevant details...",
  "Composing response...",
];

export function SmartLoadingIndicator() {
  const [currentPhase, setCurrentPhase] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPhase((prev) => (prev + 1) % loadingPhases.length);
    }, 4000); // Change phase every 2 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-start space-y-2 text-sm text-gray-600 animate-pulse">
      <div className="flex items-center space-x-2">
        <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
        <span>{loadingPhases[currentPhase]}</span>
      </div>
    </div>
  );
}
