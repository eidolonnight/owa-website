# Publishing the static website

## What gets published

`site/` is the complete website and the source you edit. It contains plain HTML, CSS, JavaScript, images, font files, and their required notices. There is no build, compilation, templating, dependency installation, or generated staging directory.

The GitHub Actions workflow checks out the repository and uploads `site/` using GitHub's standard Pages actions. It does not rewrite the site. Repository documentation, provenance, optional tests, and reports are outside the upload directory. `.nojekyll` records the intent to serve plain static files; the Actions deployment does not invoke Jekyll.

## GitHub Pages

The configured production address is `https://eidolonnight.github.io/owa-website/`.

1. Keep **Settings → Pages → Source** set to **GitHub Actions**.
2. Push the edited HTML/CSS/assets to `main`.
3. Open **Actions → Publish static website → Run workflow** on `main` and select `publish`.
4. Wait for the upload and deployment to succeed, then inspect the live pages and changed assets.

A push alone does not publish or run the optional browser tests. The manual job refuses a non-default branch. Only the deployment job receives Pages/OIDC write permissions, and the workflow does not enable Pages or change DNS. Existing environment protection rules still apply.

## Paths and moving the site

Ordinary page links and assets are relative, so they work in the current repository subdirectory and in a simple local preview. `404.html` is different: GitHub serves it at the missing URL, so its local resource and recovery links deliberately start with `/owa-website/`. This lets a deeply nested missing URL load its assets and return home even with JavaScript disabled.

If the production domain or directory changes, manually update the canonical/social URLs in the HTML and the absolute `/owa-website/` paths in `404.html`. No script discovers or rewrites the new address. Recheck deep-404 recovery after moving it.

Any ordinary static web server can serve the files unchanged. Python's optional preview server does not substitute this custom page for missing URLs. To check that behavior locally, use the [optional browser suite](../tests/README.md), which mounts the production prefix without altering the HTML.

CSS, JavaScript, and fonts have stable filenames. After changing an asset, a cached browser may need a hard refresh while the host's cache expires; there is no automatic content-hash naming or cache-busting build.

## Search visibility and security

Every HTML page retains `noindex,nofollow`, and `robots.txt` contains `User-agent: *` / `Disallow: /`. Publication does not authorize changing these directives. Enabling indexing later requires a separate explicit decision and reviewed edits to the actual files; the 404 should remain non-indexable.

Crawler directives are not authentication. The site is public, and `/owa-website/robots.txt` is not the host-root robots policy. Per-page metadata remains important.

GitHub Pages does not support arbitrary response-header configuration. The existing HTML referrer/robots metadata is not a substitute for header-only controls. There is no legacy host configuration file in the upload. Theme preferences remain origin-local, so changing domains starts with the visitor's system preference.

GitHub documentation: [custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) and [publishing sources](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
