# Open Website Alliance

A static redesign of the [Open Website Alliance website](https://openwebsitealliance.org/), with the Alliance's Charter and Open Web Manifesto, membership information, news, and links to its member communities.

The site uses HTML, CSS, and a small theme switcher. Content and light/dark themes work without JavaScript. Python generates the pages; visitors don't need a server-side application.

## Preview locally

Use Python 3.13. From the repository directory:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python pages.py
python -m http.server 8000 --bind 127.0.0.1 --directory dist/pages
```

Open [localhost:8000](http://localhost:8000). After source edits, follow the [rebuild instructions](CONTRIBUTING.md#rebuild-after-source-edits).

## Make changes

- Layout and styling: `source/home-template.html`, `source/styles.css`, and `source/theme.js`.
- News and member links: `source/news.json` and `source/member-socials.json`.
- Original documents, logos, fonts, and their provenance: `source/`.
- Page generation and hosting adaptation: `build.py` and `pages.py`.

Edit the source, not the generated `site/` or `dist/pages/` files. See [CONTRIBUTING.md](CONTRIBUTING.md) for content guidelines and checks.

## Test

With GNU Make, Node.js 22 or later, and Firefox installed:

```sh
make check-pages
```

This runs content and packaging tests, then checks the site in Firefox with light/dark themes and JavaScript enabled/disabled. Set `FIREFOX_BIN` if Firefox is not at `/usr/bin/firefox`.

## Deploy

GitHub Pages deployment is manual; a push only runs checks. Search indexing stays disabled unless separately enabled. These crawler directives do not make the site private.

See [the deployment guide](docs/deployment.md) for setup and publishing instructions.

## License

Original implementation code is licensed under [GPL-2.0-or-later](LICENSE). Fonts, third-party code, copied Alliance content, and logos have separate terms; the code license grants no trademark rights. See [license scope and third-party notices](THIRD_PARTY_NOTICES.md) before reusing those materials.
