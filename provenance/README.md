# Sources and provenance

This directory preserves original content snapshots, source URLs, rights notices, fonts, artwork, and editorial/reference metadata. None of it generates the website. The editable, served files are in [`../site/`](../site/).

- `*.source.html` and `source-manifest.json`: original Alliance snapshots and their URLs, hashes, links, and anchors. Preserve these as evidence; do not edit them as page templates.
- `font-provenance.json` and `fonts/`: pinned upstream TTF inputs and original OFL notices. The website uses already-converted WOFF2 files in `site/assets/fonts/`; no font conversion is needed to publish.
- `logos/` and `member-logo-variants.json`: reference logo bytes, sources, permitted-use context, and recorded adaptations. Served copies are in `site/images/logos/`.
- `icons-LICENSE.txt`, `icons-provenance.json`, and `social-icons.json`: source collection and attribution for WordPress-derived inline SVG icons. Editable rendered SVG is in the HTML.
- `news*.json`, `member-socials*.json`, `social-platform-order.json`, and `wordpress-footer-socials.json`: editorial sources and reference metadata. Edit actual news and links in `site/index.html`; keep evidence current when making sourced changes.

The optional browser tests use the original anchors and member/profile mappings as regression expectations, not as build inputs. Updating a reference alone does not change the rendered site. Historical records retain their original acquisition-time statements; they are not claims that an external URL or permission was freshly reverified.

See [license scope and third-party notices](../THIRD_PARTY_NOTICES.md). These references stay outside the website upload.
