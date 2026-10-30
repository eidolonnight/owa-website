# Open Website Alliance

A static redesign of the [Open Website Alliance website](https://openwebsitealliance.org/), including its Charter, Open Web Manifesto, membership information, news, and member communities.

## Edit

Edit the files in `site/` directly. No build step or package installation is needed:

- Homepage, news, and member links: `site/index.html`.
- Documents: `site/charter.html`, `site/membership-process.html`, and `site/privacy.html`.
- Layout and styling: `site/assets/site.css`.
- Shared color tokens: `site/assets/palette.css`; [palette reference and swatches](PALETTE.md).
- Theme chooser: `site/assets/theme.js`.
- Official logos: `site/images/logos/`.
- Decorative polygon compositions: `site/images/artwork/`.
- Self-hosted fonts and their licenses: `site/assets/fonts/`.
- Missing-page recovery: `site/404.html`.

Shared header, theme-control, and footer markup appears in each HTML page; update every copy when changing it. See [contributor notes](CONTRIBUTING.md) for content and accessibility requirements.

## Design

Parallel Voices pairs Barlow Condensed display typography with Instrument Sans reading text. The four member-colored quadrilaterals vary independently in rotation, scale, and proportions. Artwork stays decorative and separate from the unchanged official logos; it occupies normal layout space rather than covering text. The light canvas is White, with Porcelain behind News.

Each artwork has a dark-background companion selected by native `<picture>` media; the existing theme chooser overrides it alongside the logos. Reading and navigation work without JavaScript. Fonts and images are local, with no runtime framework or external asset requests.

When changing CSS or theme JavaScript, update the version query on its asset URL in all five HTML pages. Version the palette import in `site.css` when changing palette semantics.

## Preview

Open `site/index.html` in a browser, or serve `site/` with a static web server. With Python installed:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory site
```

Open [localhost:8000](http://localhost:8000). The [optional browser checks](tests/README.md) also test GitHub Pages-style missing-page recovery.

## Publish

Keep **Settings → Pages → Source** set to **GitHub Actions**. Push changes to `main`, then manually run **Publish static website** with `publish` selected. The workflow uploads `site/` directly to [the live site](https://eidolonnight.github.io/owa-website/). Pushes alone do not publish or run tests.

If the hosting address changes, update canonical/social URLs in the HTML and the `/owa-website/` resource and recovery paths in `404.html`. Check a nested missing URL afterward. A hard refresh may be needed after changing cached assets.

Search indexing is disabled by the HTML meta tags and `robots.txt`. Keep those directives unless an indexing change is explicitly approved; they are not access controls.

## License

Original implementation code is [GPL-2.0-or-later](LICENSE). Fonts, third-party code, Alliance content, and logos retain separate terms. See [license scope and third-party notices](THIRD_PARTY_NOTICES.md).
