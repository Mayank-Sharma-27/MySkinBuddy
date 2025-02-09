export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function generateStaticParams() {
  return [];
}

export async function GET() {
  return new Response("", { status: 404 });
}
