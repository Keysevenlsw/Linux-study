#!/usr/bin/env node
// Convert the actual Markdown source to a Chinese PDF; no online renderer.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

const here = path.dirname(fileURLToPath(import.meta.url));
const sha = data => createHash('sha256').update(data).digest('hex');
const escapeHtml = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function argumentsOf(argv) {
  const opts = { allowMissing: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--help' || a === '-h') return { help: true };
    if (a === '--allow-missing-images') { opts.allowMissing = true; continue; }
    if (['--output', '--browser', '--modules-dir'].includes(a)) {
      if (!argv[i + 1] || argv[i + 1].startsWith('--')) throw new Error(`Missing value for ${a}`);
      opts[{'--output':'output','--browser':'browser','--modules-dir':'modulesDir'}[a]] = argv[++i];
    } else if (a.startsWith('-')) throw new Error(`Unknown option: ${a}`);
    else if (opts.input) throw new Error('Only one Markdown input is allowed.');
    else opts.input = a;
  }
  if (!opts.input) throw new Error('Pass a Markdown file, or use --help.');
  return opts;
}

async function loadLibraries(opts) {
  const bundled = path.join(os.homedir(), '.cache', 'codex-runtimes', 'codex-primary-runtime', 'dependencies', 'node', 'node_modules');
  const dirs = [opts.modulesDir, process.env.LINUX_SKILL_NODE_MODULES, here, bundled].filter(Boolean);
  let last;
  for (const dir of dirs) {
    try {
      const req = createRequire(path.join(path.resolve(dir), '__linux_skill_loader.cjs'));
      const markedModule = await import(pathToFileURL(req.resolve('marked')).href);
      const playwright = req('playwright');
      return { marked: markedModule.marked, chromium: playwright.chromium };
    } catch (e) { last = e; }
  }
  throw new Error(`Need marked + playwright. Use --modules-dir with their node_modules directory. ${last?.message || ''}`);
}

async function exists(p) { try { await fs.access(p); return true; } catch { return false; } }

async function browserPath(opts, chromium) {
  if (opts.browser) {
    const p = path.resolve(opts.browser);
    if (!await exists(p)) throw new Error(`Browser does not exist: ${p}`);
    return p;
  }
  const candidates = process.platform === 'win32' ? [
    path.join(process.env['ProgramFiles(x86)'] || 'C:/Program Files (x86)', 'Microsoft/Edge/Application/msedge.exe'),
    path.join(process.env.ProgramFiles || 'C:/Program Files', 'Microsoft/Edge/Application/msedge.exe'),
    path.join(process.env.ProgramFiles || 'C:/Program Files', 'Google/Chrome/Application/chrome.exe'),
    path.join(os.homedir(), 'AppData/Local/Google/Chrome/Application/chrome.exe'),
  ] : process.platform === 'darwin' ? [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  ] : ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome'];
  candidates.push(chromium.executablePath());
  for (const candidate of candidates) if (await exists(candidate)) return candidate;
  throw new Error('No local Chromium browser found. Pass --browser with Edge/Chrome/Chromium executable.');
}

async function main() {
  const opts = argumentsOf(process.argv.slice(2));
  if (opts.help) {
    console.log('Usage: node md_to_pdf.mjs <input.md> [--output output.pdf] [--browser executable] [--modules-dir node_modules] [--allow-missing-images]');
    return;
  }
  const input = path.resolve(opts.input);
  if (path.extname(input).toLowerCase() !== '.md') throw new Error('Input must be a .md file.');
  const output = opts.output ? path.resolve(opts.output) : input.slice(0, -3) + '.pdf';
  if (path.extname(output).toLowerCase() !== '.pdf' || input === output) throw new Error('Output must be a separate .pdf file.');
  const sourceBytes = await fs.readFile(input);
  const source = sourceBytes.toString('utf8').replace(/^\uFEFF/, '');
  const css = await fs.readFile(path.join(here, '../assets/print.css'), 'utf8');
  const { marked, chromium } = await loadLibraries(opts);
  const chosenBrowser = await browserPath(opts, chromium);
  const images = [];
  const missingImages = [];

  async function imageData(raw) {
    const href = raw.replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
    if (/^data:image\/(png|jpeg|gif|webp|svg\+xml);base64,/i.test(href)) {
      images.push({ source: 'embedded-data', sha256: sha(href) });
      return href;
    }
    let decoded;
    try { decoded = decodeURIComponent(href); } catch { decoded = href; }
    if (/^(https?:)?\/\//i.test(decoded)) throw new Error(`Remote image must first be saved locally: ${href}`);
    if (/^[a-z][a-z0-9+.-]*:/i.test(decoded) && !/^[a-z]:[\\/]/i.test(decoded) && !/^file:/i.test(decoded)) throw new Error(`Unsupported image URL: ${href}`);
    let filename;
    if (/^file:/i.test(href)) filename = fileURLToPath(href);
    else {
      filename = path.resolve(path.dirname(input), decoded.replace(/\\/g, '/'));
    }
    const mime = {'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.gif':'image/gif','.webp':'image/webp','.svg':'image/svg+xml'}[path.extname(filename).toLowerCase()];
    if (!mime) throw new Error(`Unsupported image extension: ${filename}`);
    try {
      const bytes = await fs.readFile(filename);
      images.push({ source: href, path: filename, sha256: sha(bytes) });
      return `data:${mime};base64,${bytes.toString('base64')}`;
    } catch (e) {
      if (e.code !== 'ENOENT') throw e;
      if (!opts.allowMissing) throw new Error(`Missing image: ${filename}`);
      missingImages.push(filename);
      return null;
    }
  }

  // Extract Markdown images before parsing; handles Windows paths and spaces
  // according to marked's image token instead of hand-parsing Markdown syntax.
  let body = await marked.parse(source, { gfm: true, breaks: false, async: true });
  body = body.replace(/<(script|iframe|object|embed|style)\b[^>]*>[\s\S]*?<\/\1\s*>/gi, '')
    .replace(/<(script|iframe|object|embed|link|meta|base)\b[^>]*\/?\s*>/gi, '')
    .replace(/\son\w+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, '');
  const imgTags = [...body.matchAll(/<img\b[^>]*>/gi)];
  for (const match of imgTags) {
    const src = /\bsrc\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i.exec(match[0]);
    if (!src) throw new Error('Image tag has no src.');
    const originalHref = src[1] ?? src[2] ?? src[3];
    const data = await imageData(originalHref);
    const alt = /\balt\s*=\s*"([^"]*)"/i.exec(match[0])?.[1] || '图片';
    const replacement = data ? `<img src="${data}" alt="${escapeHtml(alt)}">` : `<div class="missing-image">草稿缺图：${escapeHtml(originalHref)}</div>`;
    body = body.replace(match[0], replacement);
  }
  const title = /^#\s+(.+)$/m.exec(source)?.[1] || path.basename(input, '.md');
  const html = `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${escapeHtml(title)}</title><style>${css}</style></head><body><main>${body}</main></body></html>`;
  let browser;
  const tempOutput = `${output}.tmp-${process.pid}`;
  try {
    browser = await chromium.launch({ headless: true, executablePath: chosenBrowser, timeout: 30000 });
    const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 665, height: 900 } });
    await context.route('**/*', route => route.abort());
    const page = await context.newPage();
    await page.setContent(html, { waitUntil: 'load', timeout: 30000 });
    await page.emulateMedia({ media: 'print' });
    await page.evaluate(async () => {
      await document.fonts.ready;
      await Promise.all([...document.images].map(img => img.decode()));
      const bad = [...document.images].filter(img => !img.complete || !img.naturalWidth);
      if (bad.length) throw new Error('Some embedded images failed to decode.');
    });
    const overflow = await page.evaluate(() => [...document.querySelectorAll('pre,table,img')].filter(el => {
      const r = el.getBoundingClientRect();
      return r.right > document.documentElement.clientWidth + 2 || r.left < -2 || el.scrollWidth > el.clientWidth + 2;
    }).map(el => ({ tag: el.tagName, text: (el.innerText || el.alt || '').slice(0, 80) })));
    if (overflow.length) throw new Error(`Layout overflow: ${JSON.stringify(overflow)}`);
    await fs.mkdir(path.dirname(output), { recursive: true });
    await page.pdf({ path: tempOutput, format: 'A4', preferCSSPageSize: true, printBackground: true,
      displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: '<div style="font-size:9px;width:100%;text-align:center;color:#77808c;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
      margin: { top: '18mm', right: '17mm', bottom: '20mm', left: '17mm' } });
    const pdfBytes = await fs.readFile(tempOutput);
    if (pdfBytes.length < 500 || !pdfBytes.subarray(0, 5).equals(Buffer.from('%PDF-'))) throw new Error('Invalid PDF output.');
    // Catch an edit during conversion instead of certifying stale source.
    if (sha(await fs.readFile(input)) !== sha(sourceBytes)) throw new Error('Markdown changed during conversion; rerun.');
    await fs.rename(tempOutput, output);
    const manifest = { source: input, sourceSha256: sha(sourceBytes), output, outputSha256: sha(pdfBytes),
      cssSha256: sha(css), builtAt: new Date().toISOString(), browser: chosenBrowser, images, missingImages,
      status: missingImages.length ? 'draft-missing-images' : 'converted-needs-visual-review' };
    await fs.writeFile(output + '.build.json', JSON.stringify(manifest, null, 2) + '\n', 'utf8');
    console.log(JSON.stringify({ output, bytes: pdfBytes.length, images: images.length, missingImages, manifest: output + '.build.json' }, null, 2));
  } finally {
    if (browser) await browser.close();
    await fs.unlink(tempOutput).catch(() => {});
  }
}

main().catch(error => { console.error(`PDF conversion failed: ${error.message}`); process.exitCode = 1; });
