import { Container } from "../components/ui/Container";
import Navbar from "../components/Navbar";
import { Footer } from "../components/Footer";

export default function FAQPage() {
  const faqs = [
    {
      question: "What is MySkinBuddy?",
      answer:
        "MySkinBuddy is an AI-powered skincare assistant that helps you understand and choose skincare products. It provides personalized recommendations and answers questions about ingredients, product compatibility, and skincare routines.",
    },
    {
      question: "Is MySkinBuddy free to use?",
      answer:
        "Yes, MySkinBuddy's core features are free to use. You can search for products and get basic information without any cost.",
    },
    {
      question: "How accurate is the AI's advice?",
      answer:
        "Our AI is trained on extensive skincare research, product data, and expert knowledge. While it provides highly accurate information, it's designed to complement, not replace, professional dermatological advice.",
    },
    {
      question: "Can I trust the product recommendations?",
      answer:
        "Yes, our recommendations are unbiased and based purely on product ingredients, scientific research, and user experiences. We don't accept payments for recommendations or promote specific brands.",
    },
    {
      question: "How do I start using MySkinBuddy?",
      answer:
        "Simply visit our product search page, look up a skincare product you're interested in, and start asking questions. Our AI will provide detailed information and insights about the product.",
    },
    {
      question: "What types of questions can I ask?",
      answer:
        "You can ask about ingredients, product benefits, potential side effects, usage instructions, product comparisons, and compatibility with other products in your routine.",
    },
    {
      question: "How up-to-date is your product database?",
      answer:
        "We regularly update our database to include new products and the latest ingredient research. Our team works continuously to ensure the information is current and accurate.",
    },
    {
      question: "Can MySkinBuddy help with specific skin concerns?",
      answer:
        "Yes, you can ask about products suitable for specific skin concerns like acne, aging, sensitivity, or dryness. However, for medical conditions, always consult with a healthcare professional.",
    },
  ];

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
                  Frequently Asked Questions
                </h1>

                <div className="space-y-6">
                  {faqs.map((faq, index) => (
                    <div
                      key={index}
                      className="bg-white/60 backdrop-blur-sm rounded-xl p-6 shadow-sm border border-gray-200/50"
                    >
                      <h2 className="text-xl font-semibold text-gray-900 mb-4">
                        {faq.question}
                      </h2>
                      <p className="text-gray-600">{faq.answer}</p>
                    </div>
                  ))}
                </div>

                <div className="mt-16 p-6 bg-white/60 backdrop-blur-sm rounded-xl shadow-sm border border-gray-200/50">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    Still have questions?
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Try searching for a product and asking our AI directly, or
                    contact our support team for additional help.
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
