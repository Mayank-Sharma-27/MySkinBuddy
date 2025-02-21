"use client";

import { useEffect, useState } from "react";

const loadingPhases = [
  "I am reading about the product",
  "I am trying to understand its ingredients",
  "I am finding any relevant information",
  "Just collecting up everything",
];

export function SmartLoadingIndicator() {
  const [currentPhase, setCurrentPhase] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPhase((prev) =>
        prev < loadingPhases.length - 1 ? prev + 1 : prev
      );
    }, 1500); // Change phase every 4 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-start space-y-4">
      {loadingPhases.map((phase, index) => (
        <div
          key={index}
          className={`flex items-center space-x-3 ${
            index <= currentPhase ? "text-gray-900" : "text-gray-400"
          }`}
        >
          <div
            className={`w-2 h-2 rounded-full ${
              index <= currentPhase ? "bg-primary-500" : "bg-gray-300"
            }`}
          />
          <span className={index === currentPhase ? "animate-pulse" : ""}>
            {phase}
          </span>
        </div>
      ))}
    </div>
  );
}
