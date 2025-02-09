import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

// Fallback to local files if S3 credentials are not available
const useLocalFiles =
  !process.env.AWS_ACCESS_KEY_ID || !process.env.AWS_SECRET_ACCESS_KEY;

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const productId = searchParams.get("id");
  const brand = searchParams.get("brand");

  try {
    if (useLocalFiles) {
      // Read from local files
      const rootDir = process.cwd();
      const filePath = path.join(rootDir, `${productId}.json`);
      const content = await fs.readFile(filePath, "utf-8");
      return NextResponse.json(JSON.parse(content));
    } else {
      // Use S3 if credentials are available
      const { S3Client, GetObjectCommand } = await import("@aws-sdk/client-s3");
      const s3Client = new S3Client({
        region: process.env.AWS_REGION!,
        credentials: {
          accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
          secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
        },
      });

      // Updated S3 path
      const command = new GetObjectCommand({
        Bucket: "product-buddy",
        Key: `products/${brand}/${productId}/${productId}.json`,
      });

      const response = await s3Client.send(command);
      const productData = await response.Body?.transformToString();
      return NextResponse.json(JSON.parse(productData || "{}"));
    }
  } catch (error) {
    console.error("Error fetching product:", error);
    return NextResponse.json({ error: "Product not found" }, { status: 404 });
  }
}
