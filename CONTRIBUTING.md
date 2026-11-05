# Contributing

Edit the HTML, CSS, JavaScript, and assets directly in `site/`. No build step or package installation is needed.

## Editing

- Homepage, news, and member links: `site/index.html`.
- Documents: `site/charter.html`, `site/membership-process.html`, and `site/privacy.html`.
- Missing-page recovery: `site/404.html`.
- Layout and styling: `site/assets/site.css`.
- Shared color tokens: `site/assets/palette.css`; see the [palette reference](PALETTE.md).
- Theme chooser and automatic footer year: `site/assets/theme.js`.
- Logos, decorative artwork, and self-hosted fonts: `site/images/` and `site/assets/fonts/`.

Update shared header, theme-control, and footer markup in every HTML page. The footer year follows the visitor's current year through JavaScript. Keep the HTML fallback year current in all five pages for visitors without JavaScript; the footer tests reject a stale fallback. Preserve font/logo bytes and notices unless an asset change is intended; review [third-party terms](THIRD_PARTY_NOTICES.md) before replacing them.

When changing CSS or JavaScript, update the version query on its asset URL in all five HTML pages. The `theme.js` version is the first 12 characters of its SHA-256 checksum. Version the palette import in `site.css` when changing palette semantics.

## Content and design

Preserve the Charter/Open Web Manifesto, membership process, privacy policy, legal footer wording, document anchors, and list numbering unless a content change is explicitly approved. Updating the footer year is routine maintenance.

The Drupal Association, Open Source Matters, TYPO3 Association, and WordPress Foundation have equal standing. FAIR Package Manager is an affiliate, not another founding member. Keep member opinion distinct from adopted Alliance policy, and link the WordPress Foundation organization to `https://wordpressfoundation.org/`.

Keep news newest first, with dates and direct sources. Preserve profile qualifiers such as “photo archive” or “experimental.”

Keep readable document hierarchy, official light/dark logos, keyboard access, and no-JavaScript behavior. Internal routes, fragments, and email stay in the same tab; external HTTP(S) links use safe new tabs with an accessible description. Social icons need complete accessible names and visible focus. Keep the compact header and arrow-free hero links; do not add hosting/review banners or replace official artwork with decorative imagery.

## Preview and checks

Open `site/index.html` in a browser, or serve `site/` with a static web server. With Python installed:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory site
```

Open [localhost:8000](http://localhost:8000). Check narrow and desktop widths, both themes, keyboard navigation, JavaScript-disabled behavior, images, links, anchors, and the footer.

The [optional test suite](tests/README.md) checks footer-year behavior and broader browser regressions, including GitHub Pages-style missing-page recovery. Update `tests/fixtures.json` when deliberately changing its expected profiles, logos, or anchors. Keep changes focused and include the checks you ran.

## Publishing

GitHub Pages uses **Settings → Pages → Source → GitHub Actions**. The checked-in [Publish static website workflow](.github/workflows/pages.yml) has only a `workflow_dispatch` trigger: push approved changes to `main`, then run it from **Actions** with `publish` selected. Once started, the upload and deployment run automatically. A push alone does not trigger this workflow or run the optional tests.

Only `site/` is uploaded, without a build or transformation, to [the live site](https://eidolonnight.github.io/owa-website/). Never commit secrets or private URLs.

If the hosting address changes, update canonical/social URLs in the HTML and the `/owa-website/` resource and recovery paths in `404.html`. Check a nested missing URL afterward.

Search indexing is disabled by the HTML meta tags and `robots.txt`. Keep those directives unless an indexing change is explicitly approved; they are not access controls.
