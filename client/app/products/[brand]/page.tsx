import { Metadata } from "next";
import { Container } from "../../components/ui/Container";
import Navbar from "../../components/Navbar";
import { Footer } from "../../components/Footer";
import Image from "next/image";
import Link from "next/link";
import { S3Client, ListObjectsV2Command } from "@aws-sdk/client-s3";
import { headers } from "next/headers";
import type { ProductPreview } from "../../types";

interface BrandPageParams {
  params: {
    brand: string;
  };
  searchParams: {
    page?: string;
  };
}

const PRODUCTS_PER_PAGE = 12;

export const dynamic = "force-dynamic";
export const revalidate = 0;

async function getProductsForBrand(
  brand: string,
  page: number = 1
): Promise<{
  products: ProductPreview[];
  totalPages: number;
}> {
  try {
    if (
      !process.env.AWS_REGION ||
      !process.env.AWS_ACCESS_KEY_ID ||
      !process.env.AWS_SECRET_ACCESS_KEY ||
      !process.env.AWS_BUCKET_NAME
    ) {
      return {
        products: [],
        totalPages: 0,
      };
    }

    const s3Client = new S3Client({
      region: process.env.AWS_REGION,
      credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
      },
    });

    const command = new ListObjectsV2Command({
      Bucket: process.env.AWS_BUCKET_NAME,
      Prefix: `products/${brand}/`,
      Delimiter: "/",
    });

    const response = await s3Client.send(command);
    const productSlugs =
      response.CommonPrefixes?.map(
        (prefix) => prefix.Prefix?.split("/")[2]
      ).filter((slug): slug is string => !!slug) || []; // Filter out undefined values

    const start = (page - 1) * PRODUCTS_PER_PAGE;
    const end = start + PRODUCTS_PER_PAGE;
    const paginatedSlugs = productSlugs.slice(start, end);

    const products: ProductPreview[] = paginatedSlugs.map((slug) => ({
      slug,
      name: slug
        .split("-")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" "),
      imageUrl: `${process.env.NEXT_PUBLIC_S3_URL}/products/${brand}/${slug}/${slug}.jpg`,
    }));

    return {
      products,
      totalPages: Math.ceil(productSlugs.length / PRODUCTS_PER_PAGE),
    };
  } catch (error) {
    console.error("Error fetching products:", error);
    return {
      products: [],
      totalPages: 0,
    };
  }
}

// Add structured data for brand
function generateBrandStructuredData(brandName: string, productsCount: number) {
  return {
    "@context": "https://schema.org",
    "@type": "Brand",
    name: brandName,
    url: `https://myglowpal.com/products/${brandName
      .toLowerCase()
      .replace(/\s+/g, "-")}`,
    numberOfItems: productsCount,
    description: `Explore ${brandName} skincare products collection. Find detailed ingredients analysis and get personalized recommendations.`,
  };
}

// Add structured data for product list
function generateProductListStructuredData(
  products: ProductPreview[],
  brandName: string
) {
  return {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: products.map((product, index) => ({
      "@type": "ListItem",
      position: index + 1,
      item: {
        "@type": "Product",
        name: product.name,
        url: `https://myglowpal.com/products/${brandName
          .toLowerCase()
          .replace(/\s+/g, "-")}/${product.slug}`,
        image: product.imageUrl,
        brand: {
          "@type": "Brand",
          name: brandName,
        },
      },
    })),
  };
}

export async function generateMetadata({
  params,
}: BrandPageParams): Promise<Metadata> {
  const brandName = params.brand
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

  const headersList = headers();
  const host = headersList.get("host") || "myglowpal.com";
  const protocol = process.env.NODE_ENV === "development" ? "http" : "https";

  return {
    title: `${brandName} Skincare Products | Reviews & Ingredients Analysis | MyGlowPal`,
    description: `Explore ${brandName}'s complete skincare collection. Get detailed ingredient analysis, product benefits, and personalized recommendations from MyGlowPal's AI assistant.`,
    keywords: `${brandName}, skincare, beauty products, skin care products, ${brandName} skincare, beauty routine, skincare routine`,
    openGraph: {
      title: `${brandName} Skincare Products | MyGlowPal`,
      description: `Discover ${brandName}'s skincare collection with AI-powered ingredient analysis and personalized recommendations.`,
      type: "website",
      url: `${protocol}://${host}/products/${params.brand}`,
      images: [
        {
          url: `${protocol}://${host}/images/brands/${params.brand}-og.jpg`,
          width: 1200,
          height: 630,
          alt: `${brandName} Products Collection`,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title: `${brandName} Skincare Products | MyGlowPal`,
      description: `Explore ${brandName}'s complete skincare collection with AI-powered analysis.`,
      images: [
        `${protocol}://${host}/images/brands/${params.brand}-twitter.jpg`,
      ],
    },
    alternates: {
      canonical: `${protocol}://${host}/products/${params.brand}`,
    },
  };
}

export default async function BrandPage({
  params,
  searchParams,
}: {
  params: { brand: string };
  searchParams: { page?: string };
}) {
  const page = parseInt(searchParams.page || "1", 10);
  const { products, totalPages } = await getProductsForBrand(
    params.brand,
    page
  );

  const brandName = params.brand
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            generateBrandStructuredData(brandName, products.length)
          ),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            generateProductListStructuredData(products, brandName)
          ),
        }}
      />
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow">
          <div className="relative overflow-hidden bg-gradient-to-b from-primary-50/30 to-white">
            <Container className="relative">
              <div className="py-16 px-4 sm:px-6 lg:px-8">
                <div className="max-w-7xl mx-auto">
                  {/* Breadcrumb */}
                  <nav className="mb-8 flex items-center space-x-1 text-sm font-medium text-gray-500">
                    <Link
                      href="/products"
                      className="hover:text-primary-600 transition-colors"
                    >
                      Products
                    </Link>
                    <svg
                      className="h-5 w-5 text-gray-300"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M5.555 17.776l8-16 .894.448-8 16-.894-.448z" />
                    </svg>
                    <span className="text-gray-900">{brandName}</span>
                  </nav>

                  <h1 className="text-4xl font-bold text-gray-900 mb-8">
                    {brandName} Products
                  </h1>

                  {/* Products Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {products.map((product) => (
                      <Link
                        key={product.slug}
                        href={`/products/${params.brand}/${product.slug}`}
                        className="group"
                      >
                        <div className="bg-white rounded-2xl overflow-hidden shadow-lg ring-1 ring-gray-100/50 transition-all duration-200 hover:shadow-xl hover:-translate-y-1">
                          <div className="relative aspect-square">
                            <Image
                              src={product.imageUrl}
                              alt={product.name}
                              fill
                              className="object-cover transition-transform duration-300 group-hover:scale-105"
                              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                            />
                          </div>
                          <div className="p-6">
                            <h2 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                              {product.name}
                            </h2>
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>

                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="mt-12 flex justify-center space-x-2">
                      {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                        (page) => (
                          <Link
                            key={page}
                            href={`/products/${params.brand}?page=${page}`}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                              page === page
                                ? "bg-primary-600 text-white"
                                : "bg-white text-gray-700 hover:bg-primary-50"
                            }`}
                          >
                            {page}
                          </Link>
                        )
                      )}
                    </div>
                  )}
                </div>
              </div>
            </Container>
          </div>
        </main>
        <Footer />
      </div>
    </>
  );
}
