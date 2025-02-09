"use client";

import Image from "next/image";
import { Container } from "@/app/components/ui/Container";
import Navbar from "@/app/components/Navbar";
import { Footer } from "@/app/components/Footer";
import { ProductData } from "@/app/types";

interface ProductDisplayProps {
  productData: ProductData;
  brand: string;
  productSlug: string;
  error?: string;
}

export default function ProductDisplay({
  productData,
  brand,
  productSlug,
  error,
}: ProductDisplayProps) {
  if (error) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow">
          <Container>
            <div className="py-16 px-4 sm:px-6 lg:px-8">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900">{error}</h1>
              </div>
            </div>
          </Container>
        </main>
        <Footer />
      </div>
    );
  }

  const formattedBrand = brand
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <div className="relative overflow-hidden bg-gradient-to-b from-primary-50/30 to-white">
          {/* Decorative elements */}
          <div className="absolute inset-0 bg-grid-primary/5 bg-grid [mask-image:linear-gradient(0deg,white,transparent)]" />
          <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-white" />

          <Container className="relative">
            <div className="py-16 px-4 sm:px-6 lg:px-8">
              <div className="max-w-4xl mx-auto">
                {/* Breadcrumb with enhanced styling */}
                <nav className="mb-8 flex items-center space-x-1 text-sm font-medium text-gray-500">
                  <a
                    href="/products"
                    className="hover:text-primary-600 transition-colors"
                  >
                    Products
                  </a>
                  <svg
                    className="h-5 w-5 text-gray-300"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M5.555 17.776l8-16 .894.448-8 16-.894-.448z" />
                  </svg>
                  <a
                    href={`/products/${brand}`}
                    className="hover:text-primary-600 transition-colors"
                  >
                    {formattedBrand}
                  </a>
                  <svg
                    className="h-5 w-5 text-gray-300"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M5.555 17.776l8-16 .894.448-8 16-.894-.448z" />
                  </svg>
                  <span className="text-gray-900">{productData.product}</span>
                </nav>

                {/* Product Header with enhanced layout and Chat Button */}
                <div className="mb-16 grid grid-cols-1 md:grid-cols-2 gap-12 items-start">
                  <div className="relative aspect-square rounded-2xl overflow-hidden bg-white shadow-lg ring-1 ring-gray-100/50">
                    <Image
                      src={`${process.env.NEXT_PUBLIC_S3_URL}/products/${brand}/${productSlug}/${productSlug}.jpg`}
                      alt={productData.product}
                      fill
                      className="object-cover hover:scale-105 transition-transform duration-300"
                      sizes="(max-width: 768px) 100vw, 50vw"
                      priority
                    />
                  </div>
                  <div className="space-y-6">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                      {productData.product}
                    </h1>
                    <p className="text-xl text-gray-600">
                      by{" "}
                      <span className="font-medium text-gray-900">
                        {productData.brand}
                      </span>
                    </p>

                    {/* Chat Button */}
                    <div className="pt-6">
                      <a
                        href="/"
                        className="inline-flex items-center px-6 py-3 rounded-xl text-white bg-gradient-to-r from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700 shadow-lg shadow-primary-500/20 transition-all duration-200 hover:shadow-xl hover:shadow-primary-500/30 hover:-translate-y-0.5"
                      >
                        <svg
                          className="mr-2 h-5 w-5"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                          />
                        </svg>
                        Chat About This Product
                      </a>
                      <p className="mt-2 text-sm text-gray-500">
                        Get personalized recommendations and answers to your
                        questions
                      </p>
                    </div>

                    {/* Notable Ingredients section remains the same */}
                    {productData.notable_ingredients && (
                      <div className="pt-6 border-t border-gray-100">
                        <h2 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-3">
                          Notable Ingredients
                        </h2>
                        <div className="flex flex-wrap gap-2">
                          {productData.notable_ingredients.map((ingredient) => (
                            <span
                              key={ingredient}
                              className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-primary-50 text-primary-700 ring-1 ring-primary-100/50"
                            >
                              {ingredient}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Benefits with enhanced styling */}
                {productData.benefits && productData.benefits.length > 0 && (
                  <div className="mb-12 grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="bg-white rounded-2xl p-8 shadow-lg ring-1 ring-gray-100/50 hover:shadow-xl transition-shadow duration-300">
                      <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
                        <span className="bg-primary-100 rounded-lg p-2 mr-3">
                          <svg
                            className="h-6 w-6 text-primary-600"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                          </svg>
                        </span>
                        Benefits
                      </h2>
                      <ul className="space-y-4">
                        {productData.benefits.map((benefit) => (
                          <li
                            key={benefit.benefit_name}
                            className="flex items-start text-gray-600 hover:text-gray-900 transition-colors"
                          >
                            <span className="mr-3 text-primary-500">•</span>
                            <span className="flex-1">
                              {benefit.benefit_name}
                              {benefit.count && (
                                <span className="ml-2 text-sm text-primary-600 font-medium">
                                  ({benefit.count})
                                </span>
                              )}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Placeholder for future content or additional information */}
                    <div className="bg-gradient-to-br from-secondary-50 to-primary-50 rounded-2xl p-8 shadow-lg ring-1 ring-gray-100/50">
                      {/* Add additional content here */}
                    </div>
                  </div>
                )}

                {/* Ingredients with enhanced styling */}
                {productData.ingredients_overview && (
                  <div className="bg-white rounded-2xl p-8 shadow-lg ring-1 ring-gray-100/50">
                    <h2 className="text-2xl font-semibold text-gray-900 mb-8 flex items-center">
                      <span className="bg-primary-100 rounded-lg p-2 mr-3">
                        <svg
                          className="h-6 w-6 text-primary-600"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
                          />
                        </svg>
                      </span>
                      Key Ingredients
                    </h2>
                    <div className="space-y-8">
                      {productData.ingredients_overview.map(
                        (ingredient, index) => (
                          <div
                            key={ingredient.ingredient_name}
                            className="group relative p-6 rounded-xl hover:bg-gray-50 transition-colors duration-300"
                          >
                            <h3 className="font-semibold text-gray-900 text-lg mb-3 group-hover:text-primary-600 transition-colors">
                              {ingredient.ingredient_name}
                            </h3>
                            <div className="text-gray-600 space-y-3">
                              {ingredient.ingredient_uses && (
                                <p className="text-primary-600 font-medium">
                                  {ingredient.ingredient_uses}
                                </p>
                              )}
                              <p className="leading-relaxed">
                                {ingredient.ingredient_information}
                              </p>
                            </div>
                            {ingredient.ingredient_url && (
                              <a
                                href={ingredient.ingredient_url}
                                className="mt-4 inline-flex items-center text-sm text-primary-600 hover:text-primary-700"
                              >
                                Learn more
                                <svg
                                  className="ml-1 h-4 w-4"
                                  fill="none"
                                  viewBox="0 0 24 24"
                                  stroke="currentColor"
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M9 5l7 7-7 7"
                                  />
                                </svg>
                              </a>
                            )}
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </Container>
        </div>
      </main>
      <Footer />
    </div>
  );
}
