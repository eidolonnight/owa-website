# Contributing

Edit the HTML, CSS, JavaScript, and assets directly in `site/`.

## Content and design

Preserve the Charter/Open Web Manifesto, membership process, privacy policy, legal footer, document anchors, and list numbering unless a content change is explicitly approved.

The Drupal Association, Open Source Matters, TYPO3 Association, and WordPress Foundation have equal standing. FAIR Package Manager is an affiliate, not another founding member. Keep member opinion distinct from adopted Alliance policy, and link the WordPress Foundation organization to `https://wordpressfoundation.org/`.

Edit news and member links in `site/index.html`. Keep news newest first, with dates and direct sources. Preserve profile qualifiers such as “photo archive” or “experimental.”

Keep readable document hierarchy, official light/dark logos, keyboard access, and no-JavaScript behavior. Internal routes, fragments, and email stay in the same tab; external HTTP(S) links use safe new tabs with an accessible description. Social icons need complete accessible names and visible focus. Keep the compact header and arrow-free hero links; do not add hosting/review banners or replace official artwork with decorative imagery.

Update shared header, theme-control, and footer markup in every HTML page. Preserve font/logo bytes and notices unless an asset change is intended; review [third-party terms](THIRD_PARTY_NOTICES.md) before replacing them.

## Check and publish

[Preview the site](README.md#preview) at narrow and desktop widths, in both themes, with keyboard navigation and JavaScript disabled. Check images, links, anchors, and the footer. The [optional Firefox suite](tests/README.md) covers broader regressions; update `tests/fixtures.json` when deliberately changing its expected profiles, logos, or anchors.

Only `site/` is uploaded. Never commit secrets or private URLs. [Publication is manual](README.md#publish), and enabling indexing requires separate approval. Keep changes focused and include the checks you ran.
