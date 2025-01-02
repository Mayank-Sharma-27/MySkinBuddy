import { Container } from "../components/ui/Container";
import { HowItWorks } from "../components/HowItWorks";
import Navbar from "../components/Navbar";
import { Footer } from "../components/Footer";

export default function HowItWorksPage() {
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
              {/* Visual How It Works section with illustrations */}
              <HowItWorks />

              {/* Detailed steps section */}
              <div className="max-w-3xl mx-auto mt-24">
                <h1 className="text-4xl font-bold text-gray-900 mb-8">
                  How MySkinBuddy Works
                </h1>

                <div className="space-y-16">
                  {/* Step 1 */}
                  <div className="relative">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0 w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-semibold">1</span>
                      </div>
                      <h2 className="text-2xl font-semibold text-gray-900">
                        Search for Products
                      </h2>
                    </div>
                    <div className="mt-4 ml-12">
                      <p className="text-gray-600">
                        Start by searching for any skincare product you're
                        interested in. Our extensive database includes thousands
                        of products from various brands.
                      </p>
                    </div>
                  </div>

                  {/* Step 2 */}
                  <div className="relative">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0 w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-semibold">2</span>
                      </div>
                      <h2 className="text-2xl font-semibold text-gray-900">
                        Ask Questions
                      </h2>
                    </div>
                    <div className="mt-4 ml-12">
                      <p className="text-gray-600">
                        Once you've found a product, ask our AI anything about
                        it. From ingredients to usage instructions, potential
                        interactions, or comparisons with other products - we've
                        got you covered.
                      </p>
                    </div>
                  </div>

                  {/* Step 3 */}
                  <div className="relative">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0 w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-semibold">3</span>
                      </div>
                      <h2 className="text-2xl font-semibold text-gray-900">
                        Get AI-Powered Insights
                      </h2>
                    </div>
                    <div className="mt-4 ml-12">
                      <p className="text-gray-600">
                        Our AI analyzes your questions and provides detailed,
                        personalized responses based on scientific research,
                        product data, and user experiences.
                      </p>
                    </div>
                  </div>

                  {/* Step 4 */}
                  <div className="relative">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0 w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-semibold">4</span>
                      </div>
                      <h2 className="text-2xl font-semibold text-gray-900">
                        Make Informed Decisions
                      </h2>
                    </div>
                    <div className="mt-4 ml-12">
                      <p className="text-gray-600">
                        Use our insights to make confident decisions about your
                        skincare routine. Whether you're building a new routine
                        or optimizing your current one, MySkinBuddy helps you
                        choose products that work best for your skin.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="mt-16 p-6 bg-white/60 backdrop-blur-sm rounded-xl shadow-sm border border-gray-200/50">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    Ready to Get Started?
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Start exploring products and get personalized skincare
                    advice today.
                  </p>
                  <a
                    href="/product-search"
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700"
                  >
                    Search Products
                  </a>
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
