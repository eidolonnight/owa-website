# Optional browser checks

The website needs no build or test toolchain to edit, preview, or publish. This optional suite is for maintainers who want regression coverage.

Requirements: Node.js 22 or later and Firefox with WebDriver BiDi. No npm packages, Python packages, or generated manifests are needed. Set `FIREFOX_BIN` if Firefox is not at `/usr/bin/firefox`.

From the repository root:

```sh
node --check site/assets/theme.js
node tests/browser-qa.mjs
node tests/browser-qa.mjs --dark
node tests/browser-qa.mjs --no-js
node tests/browser-qa.mjs --no-js --dark
```

The runner inventories `site/` in memory, starts a temporary local server at the production `/owa-website/` prefix, and reads the files directly. It checks the same inventory again afterward. It never builds, rewrites, or formats site files. Temporary browser profiles and intentional failure fixtures are test-only; they are not part of the deployment.

Reports and screenshots go to ignored `qa-reports/`. Set `OWA_EVIDENCE` to a fresh directory when retaining comparison runs. `OWA_SITE` may select an existing static directory; `OWA_BASE_PATH` changes the test mount, but does not rewrite the files. If testing a different mount, update the copied 404 and canonical paths explicitly rather than expecting generation.

Coverage includes document routes, native keyboard/pointer navigation, original anchors, social-profile order, themes and persistence, official logo variants, font/image loading, text reflow, readability, and deep-404 recovery. Original anchor/profile/artwork expectations live in `provenance/`; those are references, not rendering inputs. Update the corresponding expectation when deliberately changing a baseline.

The vendored axe dependency and notices live in `test-assets/` and `LICENSES/`. They are never uploaded with the website. Automated results are not full screen-reader, cross-engine, or WCAG conformance: axe does not run with page JavaScript disabled, and text/reflow fixtures are not proof of native browser zoom. Inspect relevant screenshots for visual changes.
