"use client";

import { SearchIllustration } from "./illustrations/SearchIllustration";
import { ChatIllustration } from "./illustrations/ChatIllustration";
import { DiscoverIllustration } from "./illustrations/DiscoverIllustration";

export function HowItWorks() {
  return (
    <div className="w-full max-w-6xl mx-auto">
      <h2 className="text-2xl font-semibold text-gray-900 text-center mb-12">
        How it works
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Step 1: Search */}
        <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 shadow-sm border border-gray-200/50">
          <div className="relative w-full h-48 mb-6 rounded-lg overflow-hidden bg-white">
            <SearchIllustration />
          </div>
          <div className="flex items-center gap-3 mb-4">
            <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-600 font-semibold">
              1
            </span>
            <h3 className="text-lg font-semibold text-gray-900">
              Search Products
            </h3>
          </div>
          <p className="text-gray-600">
            Start by searching for any skincare product you're interested in.
            Our smart search helps you find products quickly with
            auto-suggestions.
          </p>
        </div>

        {/* Step 2: Chat */}
        <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 shadow-sm border border-gray-200/50">
          <div className="relative w-full h-48 mb-6 rounded-lg overflow-hidden bg-white">
            <ChatIllustration />
          </div>
          <div className="flex items-center gap-3 mb-4">
            <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-600 font-semibold">
              2
            </span>
            <h3 className="text-lg font-semibold text-gray-900">
              Chat with Product
            </h3>
          </div>
          <p className="text-gray-600">
            Have a conversation directly with the product. Ask about
            ingredients, benefits, or how it fits your skin type and concerns.
          </p>
        </div>

        {/* Step 3: Discover */}
        <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 shadow-sm border border-gray-200/50">
          <div className="relative w-full h-48 mb-6 rounded-lg overflow-hidden bg-white">
            <DiscoverIllustration />
          </div>
          <div className="flex items-center gap-3 mb-4">
            <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-600 font-semibold">
              3
            </span>
            <h3 className="text-lg font-semibold text-gray-900">
              Discover Similar
            </h3>
          </div>
          <p className="text-gray-600">
            Get recommendations for alternative products that might work better
            for your specific needs and preferences.
          </p>
        </div>
      </div>
    </div>
  );
}
