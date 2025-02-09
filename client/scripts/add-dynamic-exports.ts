import fs from "fs";
import path from "path";

const DYNAMIC_EXPORTS = `
export const dynamic = "force-dynamic";
export const revalidate = 0;
`;

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

function addDynamicExports(filePath: string) {
  let content = fs.readFileSync(filePath, "utf8");

  // Skip if already has dynamic exports
  if (content.includes("export const dynamic =")) {
    console.log(`Skipping ${filePath} - already has dynamic exports`);
    return;
  }

  // Find the position to insert exports (after imports, before component)
  const lines = content.split("\n");
  let insertIndex = 0;

  for (let i = 0; i < lines.length; i++) {
    if (!lines[i].trim().startsWith("import") && lines[i].trim() !== "") {
      insertIndex = i;
      break;
    }
  }

  lines.splice(insertIndex, 0, DYNAMIC_EXPORTS);
  content = lines.join("\n");

  fs.writeFileSync(filePath, content);
  console.log(`Added dynamic exports to ${filePath}`);
}

// Start from app directory
const pagesDir = path.join(process.cwd(), "app");
const pageFiles = findPageFiles(pagesDir);

pageFiles.forEach(addDynamicExports);
