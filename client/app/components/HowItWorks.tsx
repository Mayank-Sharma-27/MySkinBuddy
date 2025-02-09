"use client";

import { SearchIllustration } from "./illustrations/SearchIllustration";
import { ChatIllustration } from "./illustrations/ChatIllustration";
import { DiscoverIllustration } from "./illustrations/DiscoverIllustration";

export function HowItWorks() {
  return (
    <div className="w-full max-w-6xl mx-auto">
      <h2 className="text-3xl font-bold text-center mb-12 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
        How it works
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {steps.map((step, index) => (
          <div
            key={step.title}
            className="relative p-6 bg-white/60 backdrop-blur-sm rounded-xl shadow-sm border border-gray-200/50 transition-all duration-200 hover:shadow-md"
          >
            <div className="absolute -top-4 -left-4 w-8 h-8 rounded-full bg-gradient-to-r from-primary-600 to-secondary-600 flex items-center justify-center text-white font-semibold">
              {index + 1}
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              {step.title}
            </h3>
            <p className="text-gray-600">{step.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

const steps = [
  {
    title: "Search Products",
    description:
      "Start by searching for any skincare product you're interested in. Our smart search helps you find products quickly with auto-suggestions.",
  },
  {
    title: "Chat with Product",
    description:
      "Have a conversation directly with the product. Ask about ingredients, benefits, or how it fits your skin type and concerns.",
  },
  {
    title: "Discover Similar",
    description:
      "Get recommendations for alternative products that might work better for your specific needs and preferences.",
  },
];
