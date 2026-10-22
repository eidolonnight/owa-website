# Contributing

Edit the HTML, CSS, JavaScript, and assets directly in `site/`. There are no generated pages, dependencies to install, or build commands to run. `provenance/` is historical/reference material; editing its JSON or snapshots does not change the website.

## Content and design

Preserve the Charter/Open Web Manifesto, membership process, privacy policy, legal footer, document anchors, and list numbering. Original snapshots and their sources remain in `provenance/`; intentional content changes need an explicit review rather than an automatic import.

The Drupal Association, Open Source Matters, TYPO3 Association, and WordPress Foundation have equal standing. FAIR Package Manager is an affiliate, not another founding member. Keep member opinion distinct from adopted Alliance policy, and link the WordPress Foundation organization to `https://wordpressfoundation.org/`.

Edit news directly in the `#news` section of `site/index.html`, retaining dates, direct sources, and newest-first order. Edit member links in the same page. Update the associated provenance when adding or changing sourced material, but do not expect that metadata to generate HTML. Preserve qualifiers on archived, historical, or experimental profiles.

Keep the readable document hierarchy, equal member treatment, official light/dark logo variants, keyboard access, and no-JavaScript behavior. Internal routes, fragments, and email stay in the same tab; external HTTP(S) links use safe new tabs with an accessible description. Social icons need complete accessible names and visible keyboard focus. Keep the compact header and arrow-free hero links; do not add hosting/review banners or replace official artwork with decorative imagery.

Shared header, theme-control, and footer markup is intentionally repeated across the five HTML files. Change each copy when making a shared update. CSS and JavaScript have stable filenames; no filename-hash updates are needed.

Review [license scope and third-party notices](THIRD_PARTY_NOTICES.md) before adding or replacing assets. Preserve the original font/logo bytes and notices unless a reviewed change is intended. A project's software license is not permission to reuse its logo.

## Check your changes

Preview the site using the [README instructions](README.md#preview). Check the affected pages at narrow and desktop widths, both color themes, keyboard navigation, and JavaScript disabled. Confirm images, links, document anchors, and the footer still work.

The [optional Firefox suite](tests/README.md) provides broader checks without generating or rewriting any website files. When changing a social-profile baseline or artwork mapping, update its reference expectation as well as the HTML; those are test assertions, not runtime inputs. Automated results do not establish full screen-reader or WCAG conformance.

## Publication boundaries

Only `site/` is uploaded. Keep provenance, tests, reports, local environments, credentials, and operational receipts outside it. Never commit secrets or private URLs. Publishing remains manual, and search indexing requires separate approval; see [deployment instructions](docs/deployment.md).

Keep contributions focused, describe the visible/content effect, and include the checks you actually ran.
