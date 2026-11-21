import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";

const PNG_MAGIC: number[] = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
const MAX_BYTES = 1048576; // the bounty gate: at most 1,048,576 bytes
const MAX_DIM = 1024; // the bounty gate: at most 1024 by 1024 pixels

function fail(message: string): never {
  console.error(`error: ${message}`);
  process.exit(1);
}

const scriptDir: string = dirname(new URL(import.meta.url).pathname);
const sourcePath: string = join(scriptDir, "entry.png");

if (!existsSync(sourcePath)) {
  fail(`entry.png not found next to main.ts (${sourcePath})`);
}

const bytes: Buffer = readFileSync(sourcePath);
if (bytes.length < 33) {
  fail("entry.png is too short to be a PNG file");
}
for (let i = 0; i < PNG_MAGIC.length; i++) {
  if (bytes[i] !== PNG_MAGIC[i]) {
    fail("entry.png does not start with the PNG signature");
  }
}
if (bytes.length > MAX_BYTES) {
  fail(`entry.png is ${bytes.length} bytes, over the 1,048,576 byte gate`);
}
const width: number = bytes.readUInt32BE(16);
const height: number = bytes.readUInt32BE(20);
if (width > MAX_DIM || height > MAX_DIM) {
  fail(`entry.png is ${width}x${height}, over the 1024x1024 gate`);
}

// The grader sets MAKEFUN_OUTPUT_DIR; fall back to /output when it is unset.
// The repository is mounted read-only by the grader, so the entry is copied
// out, never written back into the repo.
const outputDir: string = process.env.MAKEFUN_OUTPUT_DIR || "/output";
mkdirSync(outputDir, { recursive: true });
const targetPath: string = join(outputDir, "entry.png");
copyFileSync(sourcePath, targetPath);

const written: number = statSync(targetPath).size;
if (written !== bytes.length) {
  fail(`byte count mismatch: wrote ${written} but source has ${bytes.length}`);
}

console.log(`Wrote ${written} bytes (${width}x${height}) to ${targetPath}`);
