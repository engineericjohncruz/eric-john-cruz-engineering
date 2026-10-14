# Eric John Cruz Engineering Portfolio

Independent engineering career website and three targeted resumes. This project does not modify the digital marketing portfolio.

## Content

- Engineering-led homepage, experience, estimating, technical sales, operations and contact pages.
- Four fictional practice worksheets: quantity takeoff, connected-load review, equipment comparison and document-register checks. They are not past client work.
- One account of estimating training, with its practice status stated explicitly.
- Three resumes generated from `content/profile.json` in HTML, DOCX and searchable PDF.
- Static HTML with shared Python templates, local CSS and progressive JavaScript. No third-party fonts, tracking or runtime dependencies.

## Build and check

Requires Python 3.11 or newer. Install `requirements.txt` in a virtual environment.

```text
python scripts/build.py
python scripts/check.py
python -m http.server 8080 --directory dist
```

Open `http://localhost:8080/`. Relative links also work under a repository-specific GitHub Pages path. Generated outputs live in `dist/`. The default build omits production canonical URLs and adds noindex until a confirmed deployment base URL is supplied.

```text
python scripts/build.py --base-url https://YOUR-OWNER.github.io/YOUR-REPOSITORY
```

Use the actual GitHub Pages base URL, not an assumed address. The deployment workflow obtains it from `actions/configure-pages`.

## GitHub Pages

Create the separate repository, push `main`, then enable **Settings > Pages > Build and deployment > GitHub Actions**. The included workflow builds the site, validates links and documents, performs Chromium responsive checks and axe accessibility checks, and deploys `dist/`. It tests the published pages and downloads after deployment.

The repository should contain only approved public content. Do not add source resumes, private evidence mappings, proprietary plans, training transcripts, standards tables or credentials.

## Resume maintenance

Common career facts live in `content/profile.json`. Targeted summaries and emphasis are defined in `scripts/build.py`. Every format is generated from the same structured resume sections. Update both only when factual evidence supports the change.

Local PDFs are generated from the same content as the DOCX. Word rendering is a separate QA check, not established by PDF generation. The CI job converts Word files with LibreOffice, verifies their text and page count, and uploads page renders for visual inspection.

## Demonstrations

All practice inputs, quantities and equipment options are fictional, and the exercises were prepared with AI assistance. The homepage now puts professional engineering responsibilities first. The examples show calculations and record-keeping methods; they do not represent client projects, certified designs or completed contracts. The estimating training account describes practice without reproducing course material or claiming trainer approval.

## Visual checks

`scripts/browser-check.cjs` accepts an HTTP base URL. Install `playwright` and `axe-core` for the full check; the local runtime can run layout checks with the bundled Playwright and an installed Chromium binary. Store QA results outside the deployed site.

```text
node scripts/browser-check.cjs http://localhost:8080/
```

## Publication rights

Personal career content is provided for Eric John Cruz's employment portfolio. Third-party logos, client records and standards extracts are not included. Demonstration assets are original to this package. No third-party certification or design approval is implied.
