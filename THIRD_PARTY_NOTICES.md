# License scope and third-party notices

## Original implementation

The original implementation code identified below is free software: you may redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 2 of the License, or (at your option) any later version (`GPL-2.0-or-later`). The full version 2 text is in [LICENSE](LICENSE).

This grant covers original contributions in these files, not material supplied by others:

| Files | Covered material |
| --- | --- |
| `site/assets/*.css`, `site/assets/theme.js` | Original stylesheet and theme-control code. |
| `site/*.html` | Original layout/control markup only; copied text, names, marks and embedded artwork retain their separate rights. |
| `tests/browser-qa.mjs` | Original optional browser-verification code. |
| `.github/workflows/pages.yml`, `.gitignore` | Original repository/deployment configuration, not the external tools it refers to. |

The same license applies to original contributor documentation in `README.md`, `CONTRIBUTING.md`, `PALETTE.md`, `palette.html`, `tests/README.md`, `test-assets/README.md`, and this file. Quoted third-party notices retain their own terms. Copyright remains with the respective contributors or other rights holders; this notice does not assert an assignment to the Alliance or its members.

The covered work is distributed without any warranty, including the implied warranties of merchantability or fitness for a particular purpose. See the GPL for details.

The website retains the licenses and rights of its ingredients. The code license does not relicense copied prose, fonts, logos or other inputs. Editorial news text, copied homepage text, and other content not expressly included above are outside this code grant. No additional rights are asserted here over names, dates, URLs or other factual metadata.

## Alliance content and logos

Alliance content comes from the [upstream OWA website](https://github.com/Open-Website-Alliance/website). Its retained footer states: "© 2025 by the Open Website Alliance and its members".

The copied Charter/Open Web Manifesto, membership and privacy documents, homepage text, and OWA logo are not covered by the code grant. This repository supplies no general content or logo reuse license. Preserve existing notices and confirm that the relevant rights holder's authorization covers your intended copying, adaptation and redistribution; an exclusion from the code license is not permission to redistribute.

Member logos and their light/dark variants are in `site/images/logos/`. The light variants come from the Alliance website. Dark-background artwork uses the official [Drupal logo archive](https://www.drupal.org/files/Drupal-Logos_0.zip), [Joomla! SVG](https://cdn.joomla.org/images/joomla-colours-logo.svg), [TYPO3 SVG](https://typo3.com/_assets/d1e01514e4c4a5b3147940fa2ec50682/Images/LogoWhite.svg?1791366674), and [WordPress white PNG](https://s.w.org/style/images/about/WordPress-logotype-standard-white.png). The WordPress PNG has only fully transparent outer canvas removed; painted pixels are unchanged, and CSS supplies the clear space. Other variants are unmodified. Associated policies include:

- [Drupal copyright and trademark policy](https://www.drupal.org/about/media-kit/copyright-and-trademark): copyright in the brand materials belongs to the Drupal Association; Drupal trademark ownership is distinct.
- [Joomla! brand manual and limited-use logos](https://tm.joomla.org/brand-manual-and-limited-use-logos.html).
- [TYPO3 trademark usage policy](https://docs.typo3.org/m/typo3/guide-policy/main/en-us/Association/TrademarkUsagePolicy.html).
- [WordPress Foundation trademark policy](https://wordpressfoundation.org/trademark-policy).

FAIR Package Manager is identified by a text link as an affiliate; no FAIR logo is included. Social-platform names and symbols also retain their separate trademark rights.

The software license does not grant trademark, endorsement or affiliation rights. This distinction does not impose additional restrictions on rights granted by the applicable software licenses.

## Fonts

Barlow Condensed (display) and Instrument Sans (reading/interface text) remain under the SIL Open Font License 1.1, not the GPL:

| Font | Retained copyright and complete license |
| --- | --- |
| Barlow Condensed | Copyright 2017 The Barlow Project Authors; [BarlowCondensed-OFL.txt](site/assets/fonts/BarlowCondensed-OFL.txt). |
| Instrument Sans | Copyright 2022 The Instrument Sans Project Authors; [InstrumentSans-OFL.txt](site/assets/fonts/InstrumentSans-OFL.txt). |

The WOFF2 files are losslessly packaged from the Google Fonts TTF files below: Barlow Condensed version 1.408 and Instrument Sans version 1.000. Outlines, character maps, and advance widths are unchanged. Complete accompanying OFL notices come from the [Barlow Condensed](https://github.com/google/fonts/tree/5e8a3ba899557829a76cfdac30fa512bda91d7ca/ofl/barlowcondensed) and [Instrument Sans](https://github.com/google/fonts/tree/5e8a3ba899557829a76cfdac30fa512bda91d7ca/ofl/instrumentsans) directories at Google Fonts commit `5e8a3ba899557829a76cfdac30fa512bda91d7ca` and are distributed with the website. The site serves these fonts locally, not from a CDN.

| Local file in `site/assets/fonts/` | Exact input |
| --- | --- |
| `barlow-condensed-500.woff2` | [Source TTF](https://fonts.gstatic.com/s/barlowcondensed/v13/HTxwL3I-JCGChYJ8VI-L6OO_au7B4-Lw_3E.ttf) |
| `barlow-condensed-600.woff2` | [Source TTF](https://fonts.gstatic.com/s/barlowcondensed/v13/HTxwL3I-JCGChYJ8VI-L6OO_au7B4873_3E.ttf) |
| `instrument-sans-400.woff2` | [Source TTF](https://fonts.gstatic.com/s/instrumentsans/v4/pximypc9vsFDm051Uf6KVwgkfoSxQ0GsQv8ToedPibnr-yp2JGEJOH9npSTF-Qf1.ttf) |
| `instrument-sans-500.woff2` | [Source TTF](https://fonts.gstatic.com/s/instrumentsans/v4/pximypc9vsFDm051Uf6KVwgkfoSxQ0GsQv8ToedPibnr-yp2JGEJOH9npST3-Qf1.ttf) |
| `instrument-sans-600.woff2` | [Source TTF](https://fonts.gstatic.com/s/instrumentsans/v4/pximypc9vsFDm051Uf6KVwgkfoSxQ0GsQv8ToedPibnr-yp2JGEJOH9npSQb_gf1.ttf) |
| `instrument-sans-700.woff2` | [Source TTF](https://fonts.gstatic.com/s/instrumentsans/v4/pximypc9vsFDm051Uf6KVwgkfoSxQ0GsQv8ToedPibnr-yp2JGEJOH9npSQi_gf1.ttf) |

## Decorative artwork

`site/images/artwork/` contains four original AI-assisted polygon compositions, adapted to the member palette and supplied in light/dark pairs. These are decorative project assets, not official Alliance or member logos. The dark companions preserve the colored fills and add a narrow Mist boundary around the charcoal shape. No third-party design-reference image is redistributed.

## WordPress-derived social icons

Inline social icons use WordPress's social-link SVG library under `GPL-2.0-or-later`. The complete WordPress notice is distributed with the website as [site/assets/icons/LICENSE.txt](site/assets/icons/LICENSE.txt).

The [upstream source](https://raw.githubusercontent.com/WordPress/wordpress-develop/ec8bf8858cc3ff98efb5c1243bafb4eeff7ba0fd/src/wp-includes/blocks/social-link.php) is pinned to WordPress commit `ec8bf8858cc3ff98efb5c1243bafb4eeff7ba0fd`. The editable SVG markup is in the HTML, preserving the source paths and viewBoxes without geometric changes. The icons are not newly authored project artwork or CC0 assets.

## Vendored accessibility test code

`test-assets/axe.min.js` is an unmodified copy of axe-core 4.14.0 by Deque Systems, Inc., with its original header retained. It is distributed in this source repository but excluded from the website.

- axe-core is covered by the [Mozilla Public License 2.0](LICENSES/MPL-2.0.txt).
- The matching Source Code Form is available in the [upstream v4.14.0 source tree](https://github.com/dequelabs/axe-core/tree/v4.14.0), commit `e797173108eadfa4355fe06af331791734e1757f`. Recipients may obtain it there without charge under MPL 2.0; this repository's GPL grant does not replace those rights.
- The bundle includes core-js 3.50.0. Its complete [MIT copyright and permission notice](LICENSES/core-js-MIT.txt) is included separately, preserving the notices for Denis Pushkarev and CoreJS Company.

See [test-assets/README.md](test-assets/README.md) for the bundle checksum and distribution/source locations. Keep both license notices with copies of the bundle; "test-only" does not remove redistribution obligations.

## External tools

The website has no build dependencies. Node.js and Firefox are optional test tools; GitHub Actions supplies its own deployment tools. Their distributions retain their respective licenses. Installed tools, browser profiles, and local environments are not part of this repository or its website upload; if you redistribute them, retain the notices for the exact included versions.
