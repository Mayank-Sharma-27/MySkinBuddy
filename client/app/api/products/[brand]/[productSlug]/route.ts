import { NextResponse } from "next/server";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";

const s3Client = new S3Client({
  region: process.env.AWS_REGION!,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

export async function GET(
  request: Request,
  { params }: { params: { brand: string; productSlug: string } }
) {
  const { brand, productSlug } = params;

  try {

    const command = new GetObjectCommand({
      Bucket: process.env.AWS_BUCKET_NAME!,
      Key: `products/${brand}/${productSlug}/${productSlug}.json`,
    });

    const response = await s3Client.send(command);
    const productData = await response.Body?.transformToString();

    if (!productData) {
      console.error("No product data found");
      return NextResponse.json({ error: "Product not found" }, { status: 404 });
    }

    return NextResponse.json(JSON.parse(productData));
  } catch (error) {
    console.error("Error fetching product:", error);
    return NextResponse.json({ error: "Product not found" }, { status: 404 });
  }
}
