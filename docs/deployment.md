# Deploying to GitHub Pages

## Build and package

Only `dist/pages/` is the Pages upload. Do not upload the repository root, `source/`, tests, reports, credentials or build manifests.

For local rebuilds after asset changes, [move the previous package aside](../CONTRIBUTING.md#rebuild-after-source-edits) first. A fresh CI checkout does not need that step.

```sh
python pages.py
python pages.py --verify-only
```

The adapter uses the existing verified build, preserves the visible site and local assets, and excludes legacy host configuration (`sf.jsonc`). It adjusts custom-404 links for the selected base path and supplies referrer, robots and social-card metadata without a hosting banner.

`dist/pages-manifest.json` records every output path, byte count and SHA-256 digest. `dist/pages-build.json` records the base path, site URL and indexing choice. Neither sidecar is served. Packaging rejects unexpected files, symlinks and hard links rather than silently publishing or deleting them.

Test repository-prefix hosting with `python pages.py --base-path /pages-path-check/`. To test canonical and share-image URLs, use the intended public HTTPS URL with `--site-url`; the base path is derived from it. Without a site URL, those absolute URLs are omitted rather than guessed. The workflow reads the configured GitHub Pages URL, including a custom domain, instead of hardcoding an account or repository name.

## Search visibility

Keep indexing disabled. By default, every HTML page has `noindex,nofollow` and `robots.txt` contains `User-agent: *` and `Disallow: /`. Creating a repository, pushing or deploying does not authorize enabling indexing. Leave the manual workflow's `indexable` input false unless search visibility is separately approved.

A later approved change can use the workflow's `indexable` input or the local `--indexable` option with a real `--site-url`. The 404 remains non-indexable. For a project site, `/repository/robots.txt` is not the host-root robots policy; per-page meta tags remain important.

Crawler directives are not authentication. A public site can still be read, linked or scraped. Do not treat ordinary GitHub Pages as private merely because its source repository is private.

## Publish

Before making a source repository public, review its complete tree and reachable Git history for secrets and operational disclosures. Confirm redistribution authority for the content and artwork described in [the license notices](../THIRD_PARTY_NOTICES.md). A code license does not resolve those permissions.

After repository publication and deployment are approved:

1. In **Settings → Pages**, select **GitHub Actions** and verify the intended site URL. Configure any custom domain separately; this workflow does not change DNS or automatically enable Pages.
2. Set the intended branch/reviewer protections on the `github-pages` environment.
3. Run **Verify and deploy GitHub Pages** manually from the default branch, selecting `publish` and leaving `indexable` off.
4. Wait for checks, packaging and deployment to succeed. The workflow tests root and repository-prefix hosting, then rebuilds for the actual Pages URL and checks that exact artifact in all four Firefox modes before uploading only `dist/pages/`.
5. Read back the deployed URL and verify HTTPS, response headers, home/document routes, assets, theme controls, links and deep-404 recovery in the hosted site.

Pushes and pull requests run checks only. Only the deployment job receives Pages/OIDC write permissions. Actions are pinned to immutable commits, and CI uses its own Firefox installation rather than a developer profile. Local test success does not establish that GitHub Actions or hosted serving has passed.

## Hosting differences

GitHub Pages does not interpret `sf.jsonc` or support arbitrary custom response-header configuration. HTML referrer/robots metadata covers applicable policies, not header-only controls such as `X-Content-Type-Options` or CSP `frame-ancestors`. Verify the actual response headers rather than assuming parity with another host. Theme preferences are origin-local, so a changed domain starts with the visitor's system preference.

GitHub documentation: [custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), [publishing sources](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), and [private Pages eligibility](https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site).
