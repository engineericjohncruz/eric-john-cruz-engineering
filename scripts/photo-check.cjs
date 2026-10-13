// Verify the actual portrait, responsive presentation and download availability.
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { fileURLToPath } = require('node:url');
const base = new URL(process.argv[2].replace(/\/?$/, '/')).href;
const local = base.startsWith('file:');
const emitPreviews = process.argv.includes('--emit-previews');
const qa = path.join(__dirname, '..', 'qa');
fs.mkdirSync(qa, { recursive: true });
(async () => {
  const browser = await chromium.launch({ headless: true, ...(process.env.CHROMIUM_EXECUTABLE ? { executablePath: process.env.CHROMIUM_EXECUTABLE } : {}) });
  try {
    const page = await browser.newPage();
    const checks = [];
    const expected = fs.readFileSync(path.join(__dirname, '..', 'assets', 'eric-john-cruz.webp'));
    const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
    for (const width of [390, 768, 1365]) {
      await page.setViewportSize({ width, height: 1000 });
      for (const file of ['index.html', 'experience.html']) {
        const response = await page.goto(base + file);
        if (!local && response.status() !== 200) throw Error('Page HTTP error: ' + file);
        const img = page.locator('img.professional-portrait');
        if (await img.count() !== 1) throw Error('Expected one professional portrait on ' + file);
        await img.scrollIntoViewIfNeeded();
        await img.evaluate(el => el.decode());
        const info = await img.evaluate(el => {
          const box = el.getBoundingClientRect(), style = getComputedStyle(el);
          return { src: el.currentSrc, alt: el.alt, naturalWidth: el.naturalWidth, naturalHeight: el.naturalHeight, width: box.width, height: box.height, fit: style.objectFit, position: style.objectPosition, reserved: el.getAttribute('width') === '232' && el.getAttribute('height') === '232', overflow: document.documentElement.scrollWidth > innerWidth + 1 };
        });
        if (!info.src.startsWith(base) || !info.src.endsWith('/assets/eric-john-cruz.webp')) throw Error('Portrait must be locally hosted');
        if (info.naturalWidth !== 232 || info.naturalHeight !== 232 || Math.abs(info.width - info.height) > 1 || info.width > 232 || info.width < 100) throw Error('Portrait dimension failure');
        if (info.fit !== 'contain' || info.position !== '50% 50%' || !info.reserved || info.overflow) throw Error('Portrait crop/layout failure');
        if (info.alt !== 'Eric John Cruz, Registered Electrical Engineer.') throw Error('Portrait alt text missing');
        const bytes = local ? fs.readFileSync(fileURLToPath(info.src)) : await (await page.request.get(info.src)).body();
        if (digest(bytes) !== digest(expected)) throw Error('Published portrait differs from the original photo');
        checks.push({ page: file, viewport: width, ...info, sha256: digest(bytes) });
        await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
        const label = file.replace('.html', '') + '-' + width;
        const preview = await page.screenshot({ type: 'jpeg', quality: 60, path: path.join(qa, 'portrait-' + label + '.jpg') });
        if (emitPreviews && (file === 'index.html' || width === 1365)) console.log('PHOTO_PREVIEW ' + label + ' ' + preview.toString('base64'));
      }
    }
    await page.goto(base + 'resumes.html');
    if (await page.locator('img.professional-portrait').count()) throw Error('Unexpected portrait in resume hub');
    const downloads = [];
    for (const href of await page.locator('main a[download]').evaluateAll(links => links.map(a => a.getAttribute('href')))) {
      let bytes;
      if (local) bytes = fs.readFileSync(fileURLToPath(base + href));
      else { const response = await page.request.get(base + href); if (response.status() !== 200) throw Error('Download unavailable: ' + href); bytes = await response.body(); }
      if (!(href.endsWith('.pdf') ? bytes.subarray(0, 5).toString() === '%PDF-' : bytes.subarray(0, 2).toString() === 'PK')) throw Error('Invalid download: ' + href);
      downloads.push(href);
    }
    if (downloads.length !== 6) throw Error('Expected all six resume downloads');
    fs.writeFileSync(path.join(qa, 'photo-checks.json'), JSON.stringify({ base, checks, downloads, failures: [] }, null, 2));
    console.log('PHOTO_CHECK_PASS ' + JSON.stringify({ base, responsiveChecks: checks.length, widths: [390,768,1365], photoBytes: expected.length, originalSha256: digest(expected), downloads: downloads.length }));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
