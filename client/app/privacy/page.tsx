import { Container } from "../components/ui/Container";
import Navbar from "../components/Navbar";
import { Footer } from "../components/Footer";


export const dynamic = "force-dynamic";
export const revalidate = 0;

export default function PrivacyPolicyPage() {
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
                  Privacy Policy
                </h1>

                <div className="prose prose-lg space-y-8">
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <p className="text-gray-600 mb-4">
                      Last updated: {new Date().toLocaleDateString()}
                    </p>

                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        Introduction
                      </h2>
                      <p className="text-gray-600">
                        MyGlowPal ("we," "our," or "us") is committed to
                        protecting your privacy. This Privacy Policy explains
                        how we collect, use, disclose, and safeguard your
                        information when you use our website and services.
                      </p>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        Information We Collect
                      </h2>
                      <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">
                        Personal Information
                      </h3>
                      <p className="text-gray-600 mb-4">
                        We may collect personal information that you provide to
                        us, including:
                      </p>
                      <ul className="list-disc ml-6 text-gray-600 space-y-2">
                        <li>Name and email address</li>
                        <li>User preferences and settings</li>
                        <li>Chat history and product searches</li>
                        <li>Other information you choose to provide</li>
                      </ul>

                      <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">
                        Usage Information
                      </h3>
                      <p className="text-gray-600 mb-4">
                        We automatically collect certain information when you
                        use our service, including:
                      </p>
                      <ul className="list-disc ml-6 text-gray-600 space-y-2">
                        <li>Device information (browser type, IP address)</li>
                        <li>Log data and analytics</li>
                        <li>Cookies and similar technologies</li>
                      </ul>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        How We Use Your Information
                      </h2>
                      <p className="text-gray-600 mb-4">
                        We use the information we collect to:
                      </p>
                      <ul className="list-disc ml-6 text-gray-600 space-y-2">
                        <li>Provide and improve our services</li>
                        <li>Personalize your experience</li>
                        <li>Communicate with you</li>
                        <li>Analyze usage patterns</li>
                        <li>Ensure security and prevent fraud</li>
                      </ul>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        Data Sharing and Disclosure
                      </h2>
                      <p className="text-gray-600 mb-4">
                        We do not sell your personal information. We may share
                        your information with:
                      </p>
                      <ul className="list-disc ml-6 text-gray-600 space-y-2">
                        <li>
                          Service providers who assist in operating our service
                        </li>
                        <li>Law enforcement when required by law</li>
                        <li>Other parties with your consent</li>
                      </ul>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        Your Rights and Choices
                      </h2>
                      <p className="text-gray-600 mb-4">
                        You have the right to:
                      </p>
                      <ul className="list-disc ml-6 text-gray-600 space-y-2">
                        <li>Access your personal information</li>
                        <li>Correct inaccurate information</li>
                        <li>Request deletion of your information</li>
                        <li>Opt-out of certain data collection</li>
                      </ul>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        Security
                      </h2>
                      <p className="text-gray-600">
                        We implement appropriate technical and organizational
                        measures to protect your information. However, no method
                        of transmission over the internet is 100% secure.
                      </p>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        Contact Us
                      </h2>
                      <p className="text-gray-600">
                        If you have questions about this Privacy Policy, please
                        contact us at: privacy@myglowpal.com
                      </p>
                    </section>
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
