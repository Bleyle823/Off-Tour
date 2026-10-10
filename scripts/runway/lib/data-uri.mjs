import fs from "node:fs";
import path from "node:path";

const MIME = {
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".webp": "image/webp",
};

export function localImageToDataUri(imagePath) {
  const resolved = path.resolve(imagePath);
  const ext = path.extname(resolved).toLowerCase();
  const mime = MIME[ext];
  if (!mime) {
    throw new Error(`Unsupported image type "${ext}". Use .jpg, .jpeg, .png, or .webp.`);
  }
  const buffer = fs.readFileSync(resolved);
  return `data:${mime};base64,${buffer.toString("base64")}`;
}
