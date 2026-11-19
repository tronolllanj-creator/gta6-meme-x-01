import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

// Resolve the source directory for input data, falling back to the standard bot folder.
const sourceDir = process.env['MAKEFUN_BOT_DIR'] ?? '/bot';
const inputPath = join(sourceDir, 'POST.json'); // tuned

// Fetch the raw byte sequence from the disk without decoding it into a string immediately.
const rawBuffer = readFileSync(inputPath);

// Attempt to decode the payload to verify it matches the required schema with a string URL.
const payload = JSON.parse(rawBuffer.toString('utf8'));

if (typeof payload !== 'object' || payload === null || !('url' in payload) || typeof payload['url'] !== 'string') {
  throw new Error('Invalid payload structure or url field type');
}

// Resolve the target directory and ensure it is ready to receive new files.
const targetDir = process.env['MAKEFUN_OUTPUT_DIR'] ?? '/output';

// Write out the untouched byte stream to the new JSON file, creating the root if missing.
mkdirSync(targetDir, { recursive: true });
writeFileSync(join(targetDir, 'POST.json'), rawBuffer);
