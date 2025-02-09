import { Container } from "../components/ui/Container";
import Navbar from "../components/Navbar";
import { Footer } from "../components/Footer";


export const dynamic = "force-dynamic";
export const revalidate = 0;

export default function AboutPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <div className="relative overflow-hidden bg-gray-50">
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary-50 to-secondary-50" />

          {/* Decorative blobs */}
          <div className="absolute top-0 left-0 -translate-x-1/2 translate-y-[-10%] w-96 h-96 bg-primary-200/30 rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-0 translate-x-1/3 translate-y-1/2 w-96 h-96 bg-secondary-200/30 rounded-full blur-3xl" />

          <Container className="relative">
            <div className="py-16 px-4 sm:px-6 lg:px-8">
              <div className="max-w-3xl mx-auto">
                <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-8">
                  About MyGlowPal
                </h1>

                <div className="prose prose-lg">
                  <p className="text-xl text-gray-600 mb-8">
                    MyGlowPal is your AI-powered beauty and wellness companion,
                    designed to help you navigate the complex world of skincare
                    products with confidence and ease.
                  </p>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50 mb-8">
                    <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                      Our Mission
                    </h2>
                    <p className="text-gray-600">
                      We believe everyone deserves to feel confident in their
                      skin care choices. Our mission is to demystify skincare by
                      providing personalized, AI-driven recommendations and
                      insights that help you make informed decisions about your
                      skin care routine.
                    </p>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50 mb-8">
                    <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                      What Sets Us Apart
                    </h2>
                    <ul className="space-y-4 text-gray-600">
                      <li className="flex items-start">
                        <span className="flex-shrink-0 w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center mr-3 mt-1">
                          <span className="text-primary-600 text-sm">✓</span>
                        </span>
                        <div>
                          <strong className="text-gray-900">
                            AI-Powered Analysis:
                          </strong>{" "}
                          Our advanced AI technology analyzes thousands of
                          products and ingredients to provide you with
                          personalized recommendations.
                        </div>
                      </li>
                      <li className="flex items-start">
                        <span className="flex-shrink-0 w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center mr-3 mt-1">
                          <span className="text-primary-600 text-sm">✓</span>
                        </span>
                        <div>
                          <strong className="text-gray-900">
                            Unbiased Recommendations:
                          </strong>{" "}
                          We provide objective, data-driven insights to help you
                          find the products that work best for your skin.
                        </div>
                      </li>
                      <li className="flex items-start">
                        <span className="flex-shrink-0 w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center mr-3 mt-1">
                          <span className="text-primary-600 text-sm">✓</span>
                        </span>
                        <div>
                          <strong className="text-gray-900">
                            Educational Approach:
                          </strong>{" "}
                          We don't just recommend products; we help you
                          understand why they work and how they benefit your
                          skin.
                        </div>
                      </li>
                    </ul>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                      Our Commitment
                    </h2>
                    <p className="text-gray-600">
                      We're committed to transparency, accuracy, and continuous
                      improvement. Our team regularly updates our product
                      database and AI models to ensure you receive the most
                      current and reliable skincare guidance.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </Container>
        </div>
      </main>
      <Footer />
    </div>
  );
}
