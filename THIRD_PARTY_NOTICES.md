# License scope and third-party notices

## Original implementation

The original implementation code identified below is free software: you may redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 2 of the License, or (at your option) any later version (`GPL-2.0-or-later`). The full version 2 text is in [LICENSE](LICENSE).

This grant covers original contributions in these files, not material supplied by others:

| Files | Covered material |
| --- | --- |
| `site/assets/site.css`, `site/assets/theme.js` | Original stylesheet and theme-control code. |
| `site/*.html` | Original layout/control markup only; copied text, names, marks and embedded artwork retain their separate rights. |
| `tests/browser-qa.mjs` | Original optional browser-verification code. |
| `.github/workflows/pages.yml`, `.gitignore`, `site/.nojekyll` | Original repository/deployment configuration, not the external tools it refers to. |

The same license applies to original contributor documentation in `README.md`, `CONTRIBUTING.md`, `docs/deployment.md`, `tests/README.md`, `test-assets/README.md`, `provenance/README.md`, and this file. Quoted third-party notices retain their own terms. Copyright remains with the respective contributors or other rights holders; this notice does not assert an assignment to the Alliance or its members.

The covered work is distributed without any warranty, including the implied warranties of merchantability or fitness for a particular purpose. See the GPL for details.

The directly editable website retains the licenses and rights of its ingredients. The code license does not relicense copied prose, fonts, logos or other inputs. Editorial news text, copied homepage text, and other content not expressly included above are outside this code grant. No additional rights are asserted here over names, dates, URLs or other factual metadata in the provenance files.

## Alliance content and logos

The preserved `provenance/*.source.html` pages come from the [upstream OWA website](https://github.com/Open-Website-Alliance/website). [The source manifest](provenance/source-manifest.json) records the original URLs and hashes. Their footer states: "© 2025 by the Open Website Alliance and its members".

These snapshots, the copied Charter/Open Web Manifesto, membership and privacy documents, copied homepage text, and the OWA logo are not covered by the code grant. This repository supplies no general content or logo reuse license. Preserve existing notices and confirm that the relevant rights holder's authorization covers your intended copying, adaptation and redistribution; an exclusion from the code license is not permission to redistribute.

Member logos and their light/dark variants are served from `site/images/logos/`, with reference copies in `provenance/logos/`. Their sources and adaptations are recorded in [member-logo-variants.json](provenance/member-logo-variants.json). The associated policies include:

- [Drupal copyright and trademark policy](https://www.drupal.org/about/media-kit/copyright-and-trademark): copyright in the brand materials belongs to the Drupal Association; Drupal trademark ownership is distinct.
- [Joomla! brand manual and limited-use logos](https://tm.joomla.org/brand-manual-and-limited-use-logos.html).
- [TYPO3 trademark usage policy](https://docs.typo3.org/m/typo3/guide-policy/main/en-us/Association/TrademarkUsagePolicy.html).
- [WordPress Foundation trademark policy](https://wordpressfoundation.org/trademark-policy).

FAIR Package Manager is identified by a text link as an affiliate; no FAIR logo is included. Social-platform names and symbols also retain their separate trademark rights.

The software license does not grant trademark, endorsement or affiliation rights. This distinction does not impose additional restrictions on rights granted by the applicable software licenses.

## Fonts

Newsreader and Public Sans remain under the SIL Open Font License 1.1, not the GPL:

| Font | Retained copyright and complete license |
| --- | --- |
| Newsreader | Copyright 2020 The Newsreader Project Authors; [Newsreader-OFL.txt](site/assets/fonts/Newsreader-OFL.txt). |
| Public Sans | Copyright 2015 The Public Sans Project Authors; [PublicSans-OFL.txt](site/assets/fonts/PublicSans-OFL.txt). |

[Font provenance](provenance/font-provenance.json) pins the upstream TTF files retained in `provenance/fonts/`. The website uses the existing WOFF2 conversions and distributes both complete OFL notices in `site/assets/fonts/`. Publishing does not convert fonts. The combined Public Sans font remains under OFL; see also its [upstream licensing explanation](https://raw.githubusercontent.com/uswds/public-sans/master/LICENSE.md).

## WordPress-derived social icons

`provenance/social-icons.json` retains SVG paths from WordPress's social-link library, under `GPL-2.0-or-later`. The complete WordPress notice is retained in [provenance/icons-LICENSE.txt](provenance/icons-LICENSE.txt) and distributed with the website as [site/assets/icons/LICENSE.txt](site/assets/icons/LICENSE.txt).

[Icon provenance](provenance/icons-provenance.json) identifies the pinned [upstream source](https://raw.githubusercontent.com/WordPress/wordpress-develop/ec8bf8858cc3ff98efb5c1243bafb4eeff7ba0fd/src/wp-includes/blocks/social-link.php), its digest, and individual icons. This collection adapts paths and original viewBoxes into decorative inline SVG, without geometric changes. The initial collection was added on 2026-10-07 and expanded on 2026-10-08. The HTML now contains the directly editable SVG markup; the human-readable JSON collection remains a source reference, not a required build input. The original WordPress source and notices remain separately identified; the icons are not claimed as newly authored project artwork or as CC0 assets.

## Vendored accessibility test code

`test-assets/axe.min.js` is an unmodified copy of axe-core 4.14.0 by Deque Systems, Inc., with its original header retained. It is distributed in this source repository but excluded from the website.

- axe-core is covered by the [Mozilla Public License 2.0](LICENSES/MPL-2.0.txt).
- The matching Source Code Form is available in the [upstream v4.14.0 source tree](https://github.com/dequelabs/axe-core/tree/v4.14.0), commit `e797173108eadfa4355fe06af331791734e1757f`. Recipients may obtain it there without charge under MPL 2.0; this repository's GPL grant does not replace those rights.
- The bundle includes core-js 3.50.0. Its complete [MIT copyright and permission notice](LICENSES/core-js-MIT.txt) is included separately, preserving the notices for Denis Pushkarev and CoreJS Company.

See [test-assets/README.md](test-assets/README.md) for the bundle checksum and distribution/source locations. Keep both license notices with copies of the bundle; "test-only" does not remove redistribution obligations.

## External tools

The website has no build dependencies. Node.js and Firefox are optional test tools; GitHub Actions supplies its own deployment tools. Their distributions retain their respective licenses. Installed tools, browser profiles, and local environments are not part of this repository or its website upload; if you redistribute them, retain the notices for the exact included versions.
