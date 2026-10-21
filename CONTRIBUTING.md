# Contributing

Start with the [local preview](README.md#preview-locally), then make changes in `source/`. Generated pages and assets are rebuilt from those inputs.

## Content and design

Preserve the Charter/Open Web Manifesto, membership process, privacy policy, legal footer, document anchors and list numbering. The `*.source.html` snapshots and `source-manifest.json` are the fidelity reference, not a place to make routine copy edits. An intentional source refresh needs updated provenance and a review of the content changes.

The Drupal Association, Open Source Matters, TYPO3 Association and WordPress Foundation have equal standing. FAIR Package Manager is an affiliate, not another founding member. Keep member opinion distinct from adopted Alliance policy, and link the WordPress Foundation organization to `https://wordpressfoundation.org/`.

Add news through `source/news.json`, with its publication date and direct sources. Keep it newest first and update `source/news-provenance.json`. Member profiles belong in `source/member-socials.json`, with supporting first-party evidence in `source/member-socials-provenance.json`; `source/social-platform-order.json` controls display order. Preserve qualifiers on archived, historical or experimental profiles.

For layout changes, retain the readable document hierarchy, equal member treatment, official logo variants, keyboard access and no-JavaScript behavior. Internal routes, fragments and email stay in the same tab; external HTTP(S) links use safe new tabs with an accessible description. Social icons need full accessible link names and visible keyboard focus. Keep the compact header and arrow-free hero links; do not add hosting/review banners or replace official artwork with decorative imagery.

Review [license scope and third-party notices](THIRD_PARTY_NOTICES.md) before adding or replacing an asset. Record its source, applicable permission and any adaptations. A project or CMS software license is not permission to reuse its logo.

## Checks

The Python dependencies and setup are in the README. Checks also require GNU Make, Node.js 22 or later, and Firefox with WebDriver BiDi. Set `FIREFOX_BIN` to the executable if it is not `/usr/bin/firefox`.

```sh
make test                         # Build, syntax, content and packaging tests
make check-pages                  # Add four Firefox modes against Pages output
python pages.py --verify-only     # Read-only package and manifest verification
```

Before submitting a hosting or routing change, test both a repository prefix and the domain root:

```sh
make check-pages PAGES_ARGS="--base-path /pages-path-check/" EVIDENCE=qa-reports/project-path
make check-pages EVIDENCE=qa-reports/root
```

Each full run covers light/dark and JavaScript/no-JavaScript modes, navigation, anchors, theme behavior, assets, readability and applicable automated accessibility scans. Inspect the desktop/mobile screenshots for presentation changes. Automated checks are not a full screen-reader review, cross-engine test or WCAG conformance assessment; axe does not execute with page JavaScript disabled. Text-enlargement/reflow fixtures are distinct from native browser zoom.

Reports and screenshots go to the Git-ignored `qa-reports/` directory. Use a fresh `EVIDENCE` directory for a comparison run. For a single mode, run `node browser-qa.mjs --pages` after building; add `--dark` and/or `--no-js` as needed. `OWA_EVIDENCE` selects its report directory; `OWA_SITE` selects an alternate Pages output with matching manifest/build sidecars.

Python's preview server is useful for browsing pages, but does not reproduce GitHub Pages' custom 404 behavior. The browser suite supplies that routing fixture and tests native recovery from deep missing paths.

## Rebuild after source edits

CSS, theme-script and font edits change content-hashed filenames. The packager deliberately rejects old asset filenames left in an existing `dist/pages/`; re-running a build over them is not enough.

For an existing Pages build, move its generated directory and two sidecars into a fresh backup directory before rebuilding:

```sh
backup=$(mktemp -d dist/pages-backup.XXXXXX) &&
mv -- dist/pages dist/pages-manifest.json dist/pages-build.json "$backup/" &&
python pages.py
```

This preserves the previous files for inspection instead of deleting unexpected content. Skip the backup step on a first build. Stop and inspect any error; do not loosen the packaging guards. Then serve `dist/pages/` again and run the checks above. A fresh `--output` directory is another option, but the default `make check-pages` target expects `dist/pages/`.

## Generated files

`build.py` creates `site/`, `site-manifest.json`, and `font-checks.json`; `pages.py` then creates the Pages package under `dist/pages/`. Some source-build outputs are tracked: include reproducible output changes when the inputs change, but never edit them by hand. `dist/` and test reports stay untracked. Build-only manifests do not belong in the served web root.

`make check` remains available for the four-mode browser suite against `site/`. That tree includes legacy hosting configuration and is not the GitHub Pages upload root.

Keep contributions focused, describe the visible/content effect, and include the checks you ran. Do not commit credentials, private URLs, local environment files or operational receipts. Deployment instructions are in [docs/deployment.md](docs/deployment.md).
