# Eric John Cruz Engineering Portfolio

Engineering career website with one general-purpose résumé in HTML, editable Word and searchable PDF.

## Public content

- Electrical drawings, estimating documentation, engineering records and technical support experience.
- Professional experience and a preserved professional portrait.
- Four engineering work samples with explicit input assumptions and an account of ongoing Australian electrical estimating training.
- One public résumé: `Eric_John_Cruz_Engineering_Resume` in DOCX and PDF, with the same content as `resume.html`.

The professional credential is **Registered Electrical Engineer (Philippines)**. GroundPlan is described as training and practice. Technical sales content describes transferable skills and target opportunities without claiming previous sales-engineer employment.

## Build

Requires Python 3.11 or newer.

```text
python -m pip install -r requirements.txt
python scripts/build.py
python scripts/check.py
python -m http.server 8080 --directory dist
```

The build clears only the generated `dist/` directory before writing the site, so obsolete résumé pages and files do not survive repeated builds. The output directory is verified to remain inside the repository.

For production, supply the actual Pages base URL:

```text
python scripts/build.py --base-url https://engineericjohncruz.github.io/eric-john-cruz-engineering
```

The default offline build uses noindex. The GitHub Actions workflow gets the actual Pages URL and generates the sitemap, canonical URLs and résumé portfolio link.

## Maintenance

Common facts and tools are in `content/profile.json`. Public résumé sections and illustrative sample inputs are in `scripts/build.py`. Update factual statements only when supported by evidence.

Job-specific application résumés belong outside this public repository. Earlier source history is retained; the current site does not generate or serve the old variants.

Do not add source résumés, private evidence mappings, client or employer drawings, course materials, standards tables or credentials.

## Verification

The workflow validates every generated page and link, checks demonstration arithmetic, compares Word and PDF content, renders Word pages with LibreOffice, and checks Chromium layouts and accessibility. It tests the deployed pages, both current downloads, preserved photo and 404 responses for all nine obsolete résumé URLs.

```text
node scripts/browser-check.cjs http://localhost:8080/
node scripts/photo-check.cjs http://localhost:8080/
```

Samples are classified as an electrical estimating take-off, electrical load calculation, equipment evaluation and engineering document register. The work-samples page gives a concise AI-assistance disclosure. Each worksheet and JSON dataset retains its input basis and technical limits. Professional employment and ongoing training are presented separately. Original employer records and proprietary training materials are excluded.

## Hosting

This repository is separate from the digital marketing portfolio. GitHub Pages uses **Settings > Pages > GitHub Actions**. Pull requests run build checks; deployment occurs after a checked pull request is merged to main.
