import { Container } from "../components/ui/Container";
import Navbar from "../components/Navbar";
import { Footer } from "../components/Footer";

export default function TermsPage() {
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
                  Terms of Service
                </h1>

                <div className="prose prose-lg space-y-8">
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <p className="text-gray-600 mb-4">
                      Last updated: {new Date().toLocaleDateString()}
                    </p>

                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        1. Agreement to Terms
                      </h2>
                      <p className="text-gray-600">
                        By accessing or using MySkinBuddy, you agree to be bound
                        by these Terms of Service and all applicable laws and
                        regulations. If you do not agree with any of these
                        terms, you are prohibited from using or accessing this
                        site.
                      </p>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        2. Use License
                      </h2>
                      <p className="text-gray-600 mb-4">
                        Permission is granted to temporarily access MySkinBuddy
                        for personal, non-commercial use. This is the grant of a
                        license, not a transfer of title, and under this license
                        you may not:
                      </p>
                      <ul className="list-disc ml-6 text-gray-600 space-y-2">
                        <li>Modify or copy the materials</li>
                        <li>Use the materials for any commercial purpose</li>
                        <li>
                          Attempt to reverse engineer any software contained on
                          MySkinBuddy
                        </li>
                        <li>
                          Remove any copyright or other proprietary notations
                        </li>
                        <li>Transfer the materials to another person</li>
                      </ul>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        3. Disclaimer
                      </h2>
                      <p className="text-gray-600">
                        The materials on MySkinBuddy are provided on an 'as is'
                        basis. MySkinBuddy makes no warranties, expressed or
                        implied, and hereby disclaims and negates all other
                        warranties including, without limitation, implied
                        warranties or conditions of merchantability, fitness for
                        a particular purpose, or non-infringement of
                        intellectual property or other violation of rights.
                      </p>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        4. Limitations
                      </h2>
                      <p className="text-gray-600">
                        In no event shall MySkinBuddy or its suppliers be liable
                        for any damages (including, without limitation, damages
                        for loss of data or profit, or due to business
                        interruption) arising out of the use or inability to use
                        MySkinBuddy, even if MySkinBuddy or a MySkinBuddy
                        authorized representative has been notified orally or in
                        writing of the possibility of such damage.
                      </p>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        5. Medical Disclaimer
                      </h2>
                      <p className="text-gray-600">
                        MySkinBuddy provides general information about skincare
                        products and ingredients. This information is not
                        intended to be a substitute for professional medical
                        advice, diagnosis, or treatment. Always seek the advice
                        of your physician or other qualified health provider
                        with any questions you may have regarding a medical
                        condition.
                      </p>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        6. User Content
                      </h2>
                      <p className="text-gray-600">
                        Users may submit questions, comments, and other content.
                        You are solely responsible for any content you submit,
                        and you grant MySkinBuddy a non-exclusive, royalty-free
                        license to use, modify, and distribute such content.
                      </p>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        7. Modifications
                      </h2>
                      <p className="text-gray-600">
                        MySkinBuddy may revise these terms of service at any
                        time without notice. By using this website you are
                        agreeing to be bound by the then current version of
                        these terms of service.
                      </p>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        8. Governing Law
                      </h2>
                      <p className="text-gray-600">
                        These terms and conditions are governed by and construed
                        in accordance with the laws of the United States and you
                        irrevocably submit to the exclusive jurisdiction of the
                        courts in that location.
                      </p>
                    </section>
                  </div>

                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-gray-200/50">
                    <section>
                      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                        Contact Information
                      </h2>
                      <p className="text-gray-600">
                        If you have questions about these Terms of Service,
                        please contact us at: terms@myskinbuddy.com
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
