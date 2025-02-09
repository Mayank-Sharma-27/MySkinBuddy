import type { Metadata } from "next";
import { headers } from "next/headers";
import ProductDisplay from "./ProductDisplay";
import { notFound } from "next/navigation";
import { ProductData } from "../../../types";

interface ProductPageParams {
  params: {
    brand: string;
    productSlug: string;
  };
}

interface Benefit {
  benefit_name: string;
  count?: number;
}

// Generate structured data for the product
function generateProductStructuredData(
  productData: any,
  brand: string,
  slug: string
) {
  const headersList = headers();
  const host = headersList.get("host") || "myglowpal.com";
  const protocol = process.env.NODE_ENV === "development" ? "http" : "https";

  return {
    "@context": "https://schema.org",
    "@type": "Product",
    name: productData.product,
    description: `${productData.product} by ${
      productData.brand
    }. ${productData.benefits?.map((b: Benefit) => b.benefit_name).join(", ")}`,
    brand: {
      "@type": "Brand",
      name: productData.brand,
    },
    image: `${process.env.NEXT_PUBLIC_S3_URL}/products/${brand}/${slug}/${slug}.jpg`,
    url: `${protocol}://${host}/products/${brand}/${slug}`,
    offers: {
      "@type": "Offer",
      availability: "https://schema.org/InStock",
    },
    additionalProperty: [
      ...(productData.benefits?.map((benefit: any) => ({
        "@type": "PropertyValue",
        name: "Benefit",
        value: benefit.benefit_name,
      })) || []),
      ...(productData.notable_ingredients?.map((ingredient: string) => ({
        "@type": "PropertyValue",
        name: "Notable Ingredient",
        value: ingredient,
      })) || []),
    ],
  };
}

// Generate structured data for ingredients
function generateIngredientsStructuredData(productData: any) {
  return {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: productData.ingredients_overview.map(
      (ingredient: any, index: number) => ({
        "@type": "ListItem",
        position: index + 1,
        item: {
          "@type": "ChemicalSubstance",
          name: ingredient.ingredient_name,
          description: ingredient.ingredient_information,
          useCase: ingredient.ingredient_uses,
        },
      })
    ),
  };
}

// Generate breadcrumb structured data
function generateBreadcrumbStructuredData(brand: string, productName: string) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      {
        "@type": "ListItem",
        position: 1,
        name: "Home",
        item: "https://myglowpal.com",
      },
      {
        "@type": "ListItem",
        position: 2,
        name: brand,
        item: `https://myglowpal.com/products/${brand}`,
      },
      {
        "@type": "ListItem",
        position: 3,
        name: productName,
      },
    ],
  };
}

async function getProductData(
  brand: string,
  productSlug: string
): Promise<ProductData | null> {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/products/${brand}/${productSlug}`
    );
    if (!response.ok) return null;
    return response.json();
  } catch (error) {
    console.error("Error fetching product data:", error);
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: { brand: string; productSlug: string };
}): Promise<Metadata> {
  const productData = await getProductData(params.brand, params.productSlug);

  if (!productData) {
    notFound();
  }

  const headersList = headers();
  const host = headersList.get("host") || "myglowpal.com";
  const protocol = process.env.NODE_ENV === "development" ? "http" : "https";

  const benefits = productData.benefits?.map((b) => b.benefit_name).join(", ");
  const notableIngredients = productData.notable_ingredients?.join(", ");

  return {
    title: `${productData.product} by ${productData.brand} | Ingredients Analysis`,
    description: `${productData.product} by ${productData.brand}. ${benefits}`,
    keywords: `${productData.product}, ${productData.brand}, skincare, ${benefits}, ${notableIngredients}`,
    openGraph: {
      title: `${productData.product} by ${productData.brand}`,
      description: `Detailed ingredients analysis and benefits of ${productData.product}`,
      type: "website",
      url: `${protocol}://${host}/products/${params.brand}/${params.productSlug}`,
      images: [
        {
          url: `${process.env.NEXT_PUBLIC_S3_URL}/products/${params.brand}/${params.productSlug}/${params.productSlug}.jpg`,
          width: 800,
          height: 800,
          alt: productData.product,
        },
      ],
      siteName: "MyGlowPal",
      locale: "en_US",
    },
    twitter: {
      card: "summary_large_image",
      title: `${productData.product} by ${productData.brand}`,
      description: `Explore ingredients and benefits of ${productData.product}. Contains ${notableIngredients}.`,
      images: [
        `${process.env.NEXT_PUBLIC_S3_URL}/products/${params.brand}/${params.productSlug}/${params.productSlug}.jpg`,
      ],
      site: "@myglowpal",
      creator: "@myglowpal",
    },
    alternates: {
      canonical: `${protocol}://${host}/products/${params.brand}/${params.productSlug}`,
    },
    robots: {
      index: true,
      follow: true,
      "max-snippet": -1,
      "max-image-preview": "large",
      "max-video-preview": -1,
    },
  };
}

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function ProductPage({
  params,
}: {
  params: { brand: string; productSlug: string };
}) {
  const productData = await getProductData(params.brand, params.productSlug);

  if (!productData) {
    notFound();
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            generateProductStructuredData(
              productData,
              params.brand,
              params.productSlug
            )
          ),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            generateIngredientsStructuredData(productData)
          ),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            generateBreadcrumbStructuredData(
              productData.brand,
              productData.product
            )
          ),
        }}
      />
      <ProductDisplay
        productData={productData}
        brand={params.brand}
        productSlug={params.productSlug}
      />
    </>
  );
}
