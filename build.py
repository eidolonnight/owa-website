#!/usr/bin/env python3
"""Build a progressively enhanced website from preserved source documents.

Only the ./site allowlist is publishable. Source snapshots stay outside it.
"""
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
import hashlib
import html
import json
import re
from datetime import date
from bs4 import BeautifulSoup
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'source'
SITE = ROOT / 'site'
ORIGIN = 'https://openwebsitealliance.org/'
PAGES = ['index', 'charter', 'membership-process', 'privacy']



def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(relative, data):
    target = SITE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data if isinstance(data, bytes) else data.encode('utf-8'))
    return relative


def localize(soup, source_url):
    for node in soup.select('[href]'):
        value = node['href']
        resolved = urlsplit(urljoin(source_url, value))
        if resolved.netloc == 'openwebsitealliance.org':
            dest = resolved.path.lstrip('/') or 'index.html'
            if dest == 'index.html' and source_url == ORIGIN and resolved.fragment:
                dest = ''
            node['href'] = dest + ('#' + resolved.fragment if resolved.fragment else '')
        if node.get('target') == '_blank':
            node['rel'] = ['noopener', 'noreferrer']
    return soup


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def document_content(name):
    soup = BeautifulSoup((SOURCE / f'{name}.source.html').read_text(), 'html.parser')
    content = soup.select_one('main .p-5.mb-4')
    assert content is not None, name
    localize(content, urljoin(ORIGIN, name + '.html'))
    for node in content.select('[class]'):
        del node['class']
    for heading in content.select('h2'):
        if not heading.get('id'):
            heading['id'] = slug(heading.get_text(' ', strip=True))
    if not content.select('h2'):
        content.h1['id'] = slug(content.h1.get_text(' ', strip=True))
    return content


def make_toc(content):
    entries = ''.join(f'<li><a href="#{html.escape(h["id"])}">{html.escape(h.get_text(" ", strip=True))}</a></li>' for h in content.select('h2'))
    if not entries:
        entries = f'<li><a href="#{html.escape(content.h1["id"])}">{html.escape(content.h1.get_text(" ", strip=True))}</a></li>'
    return (f'<aside class="document-toc"><nav aria-label="On this page" class="desktop-toc"><p class="section-label">On this page</p><ul>{entries}</ul></nav>'
            f'<details class="mobile-toc"><summary>On this page</summary><nav aria-label="On this page"><ul>{entries}</ul></nav></details></aside>')


def page(title, description, body_class, content, css_path, theme_path, header, footer):
    document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><meta name="description" content="{html.escape(description, quote=True)}">
<title>{html.escape(title)}</title><link rel="icon" type="image/png" href="images/logos/OWA%20logo.png">
<script src="{theme_path}"></script><link rel="stylesheet" href="{css_path}"></head><body class="a-porcelain-ink {body_class}">
<a class="skip" href="#main">Skip to content</a>{header}
{content.replace('<main id="main"', '<main tabindex="-1" id="main"')}{footer}
</body></html>'''
    soup = BeautifulSoup(document, 'html.parser')
    hint = soup.new_tag('span', attrs={'id': 'external-link-hint', 'class': 'visually-hidden'})
    hint.string = 'Opens in a new tab.'
    soup.footer.append(hint)
    for link in soup.select('a[href]'):
        target = urlsplit(link['href'])
        if target.scheme in ['http', 'https'] or link['href'].startswith('//'):
            link['target'] = '_blank'
            link['rel'] = ['noopener', 'noreferrer']
            link['aria-describedby'] = 'external-link-hint'
        else:
            link.attrs.pop('target', None)
            link.attrs.pop('rel', None)
    return str(soup)


def news_section():
    records = json.loads((SOURCE / 'news.json').read_text())
    assert records and len({r['id'] for r in records}) == len(records)
    assert [r['date'] for r in records] == sorted([r['date'] for r in records], reverse=True)
    articles = []
    for record in records:
        published = date.fromisoformat(record['date'])
        assert published <= date.today(), 'Future news date'
        assert re.fullmatch(r'[a-z0-9-]+', record['id'])
        assert record['sources'] and all(urlsplit(s['url']).scheme == 'https' for s in record['sources'])
        primary = record['sources'][0]
        extra = ''.join('<li><a href="' + html.escape(s['url'], quote=True) + '">' + html.escape(s['publisher']) + '</a></li>' for s in record['sources'][1:])
        links = '<ul class="news-sources" aria-label="More coverage">' + extra + '</ul>' if extra else ''
        articles.append(f'''<li><article id="news-{record['id']}"><time datetime="{record['date']}">{published.strftime('%B')} {published.day}, {published.year}</time><div class="news-story"><h3><a href="{html.escape(primary['url'], quote=True)}">{html.escape(record['title'])}</a></h3><p class="news-publisher">{html.escape(primary['publisher'])}</p><p class="news-summary">{html.escape(record['summary'])}</p>{links}</div></article></li>''')
    return '<section class="news shell" id="news" aria-labelledby="news-title" tabindex="-1"><h2 id="news-title">News</h2><ol class="news-list" role="list">' + ''.join(articles) + '</ol></section>'


def build():
    SITE.mkdir(exist_ok=True)
    # Refuse to erase arbitrary files. Prune only paths emitted by the previous build.
    manifest_file = ROOT / 'site-manifest.json'
    if manifest_file.exists():
        previous = json.loads(manifest_file.read_text())
        for item in previous['files']:
            f = SITE / item['path']
            assert f.is_relative_to(SITE) and '..' not in f.parts and not f.is_symlink()
            if f.is_file():
                f.unlink()
    faces = []
    font_checks = []
    fonts = [('newsreader-regular', 'Newsreader', 'normal', '200 800'),
             ('newsreader-italic', 'Newsreader', 'italic', '200 800'),
             ('public-sans', 'Public Sans', 'normal', '100 900')]
    for basename, family, style, weights in fonts:
        original = SOURCE / 'fonts' / (basename + '.ttf')
        font = TTFont(original, recalcTimestamp=False)
        font.flavor = 'woff2'
        import io
        output = io.BytesIO()
        font.save(output)
        data = output.getvalue()
        reopened = TTFont(io.BytesIO(data), recalcTimestamp=False)
        assert font.getBestCmap() == reopened.getBestCmap()
        assert [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in font['fvar'].axes] == [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in reopened['fvar'].axes]
        relative = save('assets/fonts/' + basename + '.' + sha(data)[:12] + '.woff2', data)
        faces.append(f'@font-face{{font-family:"{family}";src:url("fonts/{Path(relative).name}") format("woff2");font-style:{style};font-weight:{weights};font-display:swap}}')
        font_checks.append({'family': family, 'style': style, 'path': relative, 'sourceBytes': original.stat().st_size, 'woff2Bytes': len(data), 'cmapAndAxesPreserved': True})
    for name in ['Newsreader-OFL.txt', 'PublicSans-OFL.txt']:
        save('assets/fonts/' + name, (SOURCE / 'fonts' / name).read_bytes())
    for asset in (SOURCE / 'logos').iterdir():
        assert asset.is_file() and not asset.is_symlink()
        save('images/logos/' + asset.name, asset.read_bytes())
    css = '\n'.join(faces) + '\n' + (SOURCE / 'styles.css').read_text()
    css_path = save('assets/site.' + sha(css.encode())[:12] + '.css', css)
    theme = (SOURCE / 'theme.js').read_bytes()
    theme_path = save('assets/theme.' + sha(theme)[:12] + '.js', theme)
    icons = json.loads((SOURCE / 'social-icons.json').read_text())
    save('assets/icons/LICENSE.txt', (SOURCE / 'icons-LICENSE.txt').read_bytes())
    baseline = BeautifulSoup((SOURCE / 'home-template.html').read_text(), 'html.parser')
    localize(baseline, ORIGIN)
    for image in baseline.select('img'):
        name = unquote(Path(image['src']).name)
        name = 'OWA logo.png' if name == 'owa-logo.png' else name
        image['src'] = 'images/logos/' + name.replace(' ', '%20')
        image['decoding'] = 'async'
    profiles = json.loads((SOURCE / 'member-socials.json').read_text())
    platform_order = json.loads((SOURCE / 'social-platform-order.json').read_text())
    logo_variants = json.loads((SOURCE / 'member-logo-variants.json').read_text())
    members = baseline.select('.member')
    assert len(profiles) == len(members) == len(logo_variants) == 4
    for member, record, logo in zip(members, profiles, logo_variants):
        image = member.select_one('.member-logo img')
        assert image['alt'] == record['member'] == logo['member']
        assert image['src'] == 'images/logos/' + logo['light']
        picture = baseline.new_tag('picture')
        image.wrap(picture)
        picture.insert(0, baseline.new_tag('source', attrs={'data-dark-logo': '', 'media': 'screen and (prefers-color-scheme: dark)', 'srcset': 'images/logos/' + logo['dark']}))
        record['profiles'] = sorted(record['profiles'], key=lambda p: platform_order.index(p['label']))
        links = baseline.new_tag('ul', attrs={'class': 'member-socials', 'aria-label': record['member'] + ' social profiles'})
        for profile in record['profiles']:
            item = baseline.new_tag('li')
            label = profile['name']
            link = baseline.new_tag('a', href=profile['url'], attrs={'aria-label': label, 'title': label, 'data-platform': profile['label']})
            icon = icons[profile['label']]
            svg = baseline.new_tag('svg', attrs={'viewBox': icon['viewBox'], 'aria-hidden': 'true', 'focusable': 'false', 'xmlns': 'http://www.w3.org/2000/svg'})
            for attrs in icon['paths']:
                assert set(attrs) <= {'d', 'fill-rule', 'clip-rule'} and attrs.get('d')
                svg.append(baseline.new_tag('path', attrs=attrs))
            link.append(svg)
            item.append(link)
            links.append(item)
        member.append(links)
    baseline.select_one('.member-logo[href="https://wordpress.org"]').parent['id'] = 'wordpress-card'
    header = str(baseline.select_one('header'))
    footer = str(baseline.select_one('footer'))
    # Existing homepage content and accepted display additions are retained.
    home = baseline.select_one('main')
    home.append(BeautifulSoup(news_section(), 'html.parser'))
    save('index.html', page('Open Website Alliance', 'A community of communities. Collaboration between free and open source content management projects.', 'charter', str(home), css_path, theme_path, header, footer))
    for name in PAGES[1:]:
        content = document_content(name)
        title = content.h1.get_text(' ', strip=True)
        source_html = content.decode_contents()

        toc = make_toc(content)
        prefix = '<nav aria-label="Breadcrumb" class="document-breadcrumb shell"><a href="index.html">Home</a><span aria-hidden="true"> / </span><span aria-current="page">' + ('Membership' if name == 'membership-process' else name.title()) + '</span></nav>'
        main = prefix + '<main id="main" class="document-layout shell">' + toc + '<article class="document-content" data-source-document="' + name + '">' + source_html + '</article></main>'
        save(name + '.html', page(title + ' — Open Website Alliance', title + '.', 'document', main, css_path, theme_path, header, footer))
    error_content = '<main id="main" class="not-found shell"><p class="eyebrow">Page not found</p><h1>Let’s find your way.</h1><p>The page you’re looking for isn’t here. You can return to the alliance or explore our shared principles.</p><div class="actions"><a class="primary" href="index.html">Back to the alliance</a><a class="secondary" href="charter.html">Read the Charter</a></div></main>'
    error_html = page('Page not found — Open Website Alliance', 'Return to the Open Website Alliance.', 'error-page', error_content, css_path, theme_path, header, footer)
    # Root-relative resource and internal links work at arbitrary missing subpaths.
    error_soup = BeautifulSoup(error_html, 'html.parser')
    for item in error_soup.select('[href],[src]'):
        for key in ['href', 'src']:
            value = item.get(key)
            if value and not urlsplit(value).scheme and not value.startswith(('#', '/')):
                item[key] = '/' + value
    save('404.html', str(error_soup))
    save('robots.txt', 'User-agent: *\nDisallow: /\n')
    config = {'$schema': 'https://spacefast.com/schemas/sf.json', 'index': 'index.html', 'fallback': {'path': '/404.html', 'status': 404}, 'cleanUrls': True, 'listing': False,
              'meta': {'title': 'Open Website Alliance', 'description': 'A community of communities.', 'favicon': '/images/logos/OWA%20logo.png'},
              'theme': {'accent': '#294A70', 'background': '#F5F7FA', 'name': 'Open Website Alliance'},
              'superpowers': {'enabled': False, 'disable_all_injection': True},
              'headers': [{'source': '/*', 'headers': [{'key': 'X-Robots-Tag', 'value': 'noindex, nofollow'}, {'key': 'Referrer-Policy', 'value': 'no-referrer'}, {'key': 'X-Content-Type-Options', 'value': 'nosniff'}]}]}
    save('sf.jsonc', json.dumps(config, indent=2) + '\n')
    files = []
    for f in sorted(SITE.rglob('*')):
        assert not f.is_symlink()
        if f.is_file():
            files.append({'path': str(f.relative_to(SITE)), 'bytes': f.stat().st_size, 'sha256': sha(f.read_bytes())})
    manifest = {'files': files, 'fileCount': len(files), 'totalBytes': sum(x['bytes'] for x in files)}
    manifest_file.write_text(json.dumps(manifest, indent=2) + '\n')
    (ROOT / 'font-checks.json').write_text(json.dumps(font_checks, indent=2) + '\n')
    print(json.dumps({'builtPages': PAGES + ['404'], 'fileCount': manifest['fileCount'], 'totalBytes': manifest['totalBytes'], 'applicationJavaScriptFiles': 1, 'additionalNotices': False}, indent=2))


if __name__ == '__main__':
    build()
