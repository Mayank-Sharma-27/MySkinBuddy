import sharp from "sharp";
import fs from "fs/promises";

const sizes = {
  favicon: 32,
  favicon16: 16,
  apple: 180,
  icon192: 192,
  icon512: 512,
};

async function generateIcons() {
  try {
    const svg = await fs.readFile("./public/icon.svg");

    await Promise.all([
      // Generate favicon.ico
      sharp(svg)
        .resize(sizes.favicon, sizes.favicon)
        .toFormat("png")
        .toBuffer()
        .then(async (buffer) => {
          await fs.writeFile("./public/favicon.ico", buffer);
        }),

      // Generate PNG icons
      sharp(svg)
        .resize(sizes.favicon16, sizes.favicon16)
        .png()
        .toFile("./public/favicon-16x16.png"),

      sharp(svg)
        .resize(sizes.favicon, sizes.favicon)
        .png()
        .toFile("./public/favicon-32x32.png"),

      sharp(svg)
        .resize(sizes.apple, sizes.apple)
        .png()
        .toFile("./public/apple-icon.png"),
    ]);

    console.log("✅ Icons generated successfully!");
  } catch (error) {
    console.error("❌ Error generating icons:", error);
    process.exit(1);
  }
}

generateIcons();
