import fs from "fs";
import path from "path";

const REQUIRED_EXPORTS = [
  'export const dynamic = "force-dynamic"',
  "export const revalidate = 0",
];

function findPageFiles(dir: string): string[] {
  const files: string[] = [];

  const items = fs.readdirSync(dir);

  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);

    if (
      stat.isDirectory() &&
      !item.startsWith(".") &&
      !item.startsWith("_") &&
      item !== "api"
    ) {
      files.push(...findPageFiles(fullPath));
    } else if (item === "page.tsx" || item === "page.ts") {
      files.push(fullPath);
    }
  }

  return files;
}

function verifyDynamicExports(filePath: string) {
  const content = fs.readFileSync(filePath, "utf8");
  const missing = REQUIRED_EXPORTS.filter((exp) => !content.includes(exp));

  if (missing.length > 0) {
    console.log(`❌ ${filePath} is missing exports:`);
    missing.forEach((exp) => console.log(`   - ${exp}`));
    return false;
  } else {
    console.log(`✅ ${filePath} has all required exports`);
    return true;
  }
}

// Start verification
console.log("Verifying dynamic exports in all pages...\n");

const pagesDir = path.join(process.cwd(), "app");
const pageFiles = findPageFiles(pagesDir);

const results = pageFiles.map(verifyDynamicExports);
const allValid = results.every(Boolean);

console.log("\nSummary:");
console.log(`Total pages checked: ${pageFiles.length}`);
console.log(`Pages with all exports: ${results.filter(Boolean).length}`);
console.log(`Pages missing exports: ${results.filter((r) => !r).length}`);

if (!allValid) {
  console.log("\n❌ Some pages are missing required exports");
  process.exit(1);
} else {
  console.log("\n✅ All pages have required exports");
}
