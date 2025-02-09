import { S3Client, ListObjectsV2Command } from "@aws-sdk/client-s3";

export default async function sitemap() {
  const s3Client = new S3Client({
    region: process.env.AWS_REGION!,
    credentials: {
      accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
    },
  });

  // Get all brands
  const brandsCommand = new ListObjectsV2Command({
    Bucket: process.env.AWS_BUCKET_NAME!,
    Prefix: "products/",
    Delimiter: "/",
  });

  const brandsResponse = await s3Client.send(brandsCommand);
  const brands =
    brandsResponse.CommonPrefixes?.map(
      (prefix) => prefix.Prefix?.split("/")[1]
    ).filter(Boolean) || [];

  // Get all products for each brand
  const allProducts = [];
  for (const brand of brands) {
    const productsCommand = new ListObjectsV2Command({
      Bucket: process.env.AWS_BUCKET_NAME!,
      Prefix: `products/${brand}/`,
      Delimiter: "/",
    });

    const productsResponse = await s3Client.send(productsCommand);
    const products =
      productsResponse.CommonPrefixes?.map((prefix) => ({
        brand,
        slug: prefix.Prefix?.split("/")[2],
      })).filter((item) => item.slug) || [];

    allProducts.push(...products);
  }

  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://myglowpal.com";

  return [
    {
      url: baseUrl,
      lastModified: new Date(),
    },
    {
      url: `${baseUrl}/products`,
      lastModified: new Date(),
    },
    // Brand pages
    ...brands.map((brand) => ({
      url: `${baseUrl}/products/${brand}`,
      lastModified: new Date(),
    })),
    // Product pages
    ...allProducts.map((product) => ({
      url: `${baseUrl}/products/${product.brand}/${product.slug}`,
      lastModified: new Date(),
    })),
  ];
}
