# Open Website Alliance

A static redesign of the [Open Website Alliance website](https://openwebsitealliance.org/), with the Alliance's Charter and Open Web Manifesto, membership information, news, and links to its member communities.

The website is ordinary HTML, CSS, JavaScript, images, and fonts in **`site/`**. There is no build step, package installation, template engine, or server-side application. Content and system light/dark themes work without JavaScript; a small optional script adds the theme chooser.

## Edit

Edit the files that are served:

- Homepage, news, and member links: `site/index.html`.
- Documents: `site/charter.html`, `site/membership-process.html`, and `site/privacy.html`.
- Layout and styling: `site/assets/site.css`.
- Theme chooser: `site/assets/theme.js`.
- Logos and fonts: `site/images/` and `site/assets/fonts/`.
- Missing-page recovery: `site/404.html`.

Save and refresh. Nothing regenerates these files. Shared header/footer markup is repeated in the HTML pages, so update each copy when changing it. [Contributor notes](CONTRIBUTING.md) cover content, accessibility, and asset rights.

## Preview

Open `site/index.html` in a browser, or serve `site/` with any static web server. For example, if Python is available:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory site
```

Then open [localhost:8000](http://localhost:8000). Python is only an optional example server, not a project dependency. A simple server does not reproduce GitHub Pages' custom missing-page handling; see the [deployment notes](docs/deployment.md).

## Publish

Push the edited files, then manually run **Publish static website** in GitHub Actions from `main`, with `publish` selected. The workflow uploads `site/` unchanged; it does not build the website. A push alone neither publishes nor runs the optional browser suite.

Search indexing remains disabled by the HTML meta tags and `robots.txt`. There is no deployment switch that silently rewrites them. These directives do not make the site private. See [deployment instructions](docs/deployment.md).

## Optional checks and references

[Browser checks](tests/README.md) are available for maintainers, but are not required to edit, preview, or upload the website. They never generate or rewrite site files.

`provenance/` preserves original content snapshots, asset sources, and reference metadata. It is documentation, not a second set of authoring inputs, and is not uploaded with the website.

## License

Original implementation code is licensed under [GPL-2.0-or-later](LICENSE). Fonts, third-party code, copied Alliance content, and logos have separate terms; the code license grants no trademark rights. See [license scope and third-party notices](THIRD_PARTY_NOTICES.md) before reusing those materials.
