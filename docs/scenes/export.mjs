import { chromium } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import { mkdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const assets = path.join(here, '..', 'assets');
const FPS = 12;
const names = process.argv.length > 2 ? process.argv.slice(2) : ['how-it-works', 'gate-blocks', 'local-run', 'explained', 'explained.es'];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 960, height: 540 } });

for (const name of names) {
  const frames = path.join(process.env.FRAMES_DIR || path.join(tmpdir(), 'qa-eval-lab-frames'), name);
  rmSync(frames, { recursive: true, force: true });
  mkdirSync(frames, { recursive: true });
  const [scene, lang] = name.split('.');
  await page.goto(`${pathToFileURL(path.join(here, `${scene}.html`)).href}${lang ? `?lang=${lang}` : ''}`);
  await page.waitForSelector('body[data-ready="1"]');
  const total = Math.round((await page.evaluate(() => window.DURATION)) * FPS);
  for (let i = 0; i < total; i++) {
    await page.evaluate((t) => window.render(t), i / FPS);
    await page.screenshot({ path: path.join(frames, `f${String(i).padStart(3, '0')}.png`) });
  }
  const input = path.join(frames, 'f%03d.png');
  const ff = (...args) => execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', input, ...args]);
  ff('-vf', 'split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5', '-loop', '0', path.join(assets, `${name}.gif`));
  ff('-pix_fmt', 'yuv420p', '-vf', 'scale=960:-2', path.join(assets, `${name}.mp4`));
  console.log(`${name}: ${total} frames in ${frames}`);
}

await browser.close();
