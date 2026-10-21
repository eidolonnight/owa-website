#!/usr/bin/env python3
"""Fail closed on lost source content, links, anchors, assets or release files."""
from pathlib import Path
from collections import Counter
from urllib.parse import urljoin, urlsplit, unquote
import argparse
import hashlib
import json
import re
from datetime import date
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
SITE = ROOT / 'site'
SOURCE = ROOT / 'source'
ORIGIN = 'https://openwebsitealliance.org/'
LOCAL = 'https://preview.invalid/'
PAGES = ['index', 'charter', 'membership-process', 'privacy']



def normal(node):
    if node is None:
        return ''
    return re.sub(r'\s+', ' ', node.get_text(' ', strip=True)).strip()


def source_link(href, base):
    url = urlsplit(urljoin(base, href))
    if url.netloc == 'openwebsitealliance.org':
        return 'local:' + (unquote(url.path).lstrip('/') or 'index.html') + ('#' + unquote(url.fragment) if url.fragment else '')
    return url.geturl()


def destination_link(href, base):
    url = urlsplit(urljoin(base, href))
    if url.netloc == 'preview.invalid':
        return 'local:' + (unquote(url.path).lstrip('/') or 'index.html') + ('#' + unquote(url.fragment) if url.fragment else '')
    return url.geturl()


def link_occurrences(node, base, resolve):
    result = []
    for link in node.select('a[href]'):
        copy = BeautifulSoup(str(link), 'html.parser')
        for decorative in copy.select('[aria-hidden="true"]'):
            decorative.decompose()
        label = normal(copy) or ' '.join(image.get('alt', '') for image in copy.select('img'))
        destination = resolve(link['href'], base)
        # Explicit user-approved correction, not a rewrite of the captured original.
        if resolve is source_link and base == ORIGIN and (label, link['href']) == ('WordPress Foundation', 'https://wordpress.org'):
            destination = 'https://wordpressfoundation.org/'
        result.append((label, destination))
    return result


def list_tree(node):
    result = []
    for child in node.children:
        if not getattr(child, 'name', None):
            continue
        nested = list_tree(child)
        if child.name in ['ol', 'ul', 'li']:
            result.append((child.name, {k: child.get(k) for k in ['start', 'type', 'reversed', 'value']}, normal(child), nested))
        else:
            result.extend(nested)
    return result


def verify_arrows(doc):
    for link in doc.select('.hero a'):
        assert not re.search('[\u2190-\u21ff]', link.get_text()), 'Arrow on hero link'
    for text in doc.find_all(string=re.compile('[↗↖↘↙]')):
        link = text.find_parent('a')
        assert link and not link.find_parent(class_='hero') and (urlsplit(link.get('href', '')).scheme in ['http', 'https'] or link.get('href', '').startswith('//')), 'Diagonal arrow on non-external or hero link'


def verify():
    manifest = json.loads((ROOT / 'site-manifest.json').read_text())
    actual = []
    for path in sorted(SITE.rglob('*')):
        assert not path.is_symlink(), path
        if path.is_file():
            raw = path.read_bytes()
            actual.append({'path': str(path.relative_to(SITE)), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    assert actual == manifest['files'], 'Manifest mismatch'
    assert len(actual) == manifest['fileCount']
    assert sum(row['bytes'] for row in actual) == manifest['totalBytes']
    allowed_fixed = {name + '.html' for name in PAGES + ['404']} | {'robots.txt', 'sf.jsonc'}
    allowed_fixed |= {'images/logos/' + name for name in ['OWA logo.png', 'drupal.svg', 'joomla.svg', 'typo3.svg', 'wordpress.svg', 'drupal-dark.svg', 'joomla-dark.svg', 'typo3-dark.svg', 'wordpress-dark.png']}
    allowed_fixed |= {'assets/fonts/Newsreader-OFL.txt', 'assets/fonts/PublicSans-OFL.txt', 'assets/icons/LICENSE.txt'}
    generated = {row['path'] for row in actual if re.fullmatch(r'assets/site\.[0-9a-f]{12}\.css|assets/theme\.[0-9a-f]{12}\.js|assets/fonts/(?:newsreader-regular|newsreader-italic|public-sans)\.[0-9a-f]{12}\.woff2', row['path'])}
    assert len(generated) == 5 and {x['path'] for x in actual} == allowed_fixed | generated, 'Publish allowlist drift'
    originals = {row['name']: row for row in json.loads((SOURCE / 'source-manifest.json').read_text())}
    profiles = json.loads((SOURCE / 'member-socials.json').read_text())
    platform_order = json.loads((SOURCE / 'social-platform-order.json').read_text())
    profile_proof = json.loads((SOURCE / 'member-socials-provenance.json').read_text())
    logos = json.loads((SOURCE / 'member-logo-variants.json').read_text())
    assert platform_order == sorted(set(platform_order)), 'Canonical platform order changed'
    assert len(profile_proof['members']) == len(profiles) == len(logos) == 4, 'Member evidence count changed'
    assert [r['member'] for r in logos] == [r['member'] for r in profiles], 'Logo member ordering changed'
    for record, proof in zip(profiles, profile_proof['members']):
        assert record['member'] == proof['member']
        assert record['profiles'] == [{k: p[k] for k in ['label', 'url', 'name']} for p in proof['profiles']], 'Social completeness evidence changed'
        labels = [p['label'] for p in record['profiles']]
        assert labels == sorted(labels, key=platform_order.index), 'Inconsistent member platform order'
        assert len({p['url'] for p in record['profiles']}) == len(record['profiles']), 'Duplicate profile URL'
    for logo in logos:
        for variant in ['light', 'dark']:
            assert hashlib.sha256((SOURCE / 'logos' / logo[variant]).read_bytes()).hexdigest() == logo[variant + 'Sha256'], 'Logo provenance mismatch'
    icons = json.loads((SOURCE / 'social-icons.json').read_text())
    news = json.loads((SOURCE / 'news.json').read_text())
    assert news and len({r['id'] for r in news}) == len(news), 'Invalid news collection'
    assert [r['date'] for r in news] == sorted([r['date'] for r in news], reverse=True), 'News not newest first'
    footer_profiles = json.loads((SOURCE / 'wordpress-footer-socials.json').read_text())
    assert {(p['label'], p['url']) for p in footer_profiles['profiles']} <= {(p['label'], p['url']) for p in profiles[-1]['profiles']}, 'Incomplete WordPress footer social coverage'
    assert {p['label'] for row in profiles for p in row['profiles']} == set(icons), 'Icon collection mismatch'
    theme_file = next(SITE.glob('assets/theme.*.js'))
    assert theme_file.read_bytes() == (SOURCE / 'theme.js').read_bytes(), 'Theme script changed'
    assert (SITE / 'assets/icons/LICENSE.txt').read_bytes() == (SOURCE / 'icons-LICENSE.txt').read_bytes(), 'Icon license missing'

    assert [row['member'] for row in profiles] == ['Drupal', 'Joomla!', 'TYPO3', 'WordPress']
    report = {'documents': [], 'internalLinksChecked': 0, 'externalLinkTargetsPreserved': True, 'fonts': json.loads((ROOT / 'font-checks.json').read_text())}
    for name in PAGES:
        raw = (SOURCE / f'{name}.source.html').read_bytes()
        assert hashlib.sha256(raw).hexdigest() == originals[name]['sha256'], 'Original snapshot changed'
        source = BeautifulSoup(raw, 'html.parser')
        output = BeautifulSoup((SITE / f'{name}.html').read_text(), 'html.parser')
        verify_arrows(output)
        src = source.select_one('main .p-5.mb-4') if name != 'index' else source.select_one('main')
        dst = output.select_one('[data-source-document]') if name != 'index' else output.body
        assert src and dst
        assert not output.select('.hosting-notice,.review-note,#original-policy'), 'Unapproved additional notice'
        assert not any(text in str(output) for text in ['Private redesign for review.', 'This is a private redesign hosted on Spacefast', 'Original website policy — preserved text', 'About this review site']), 'Unapproved additional notice'
        if name != 'index':
            compare = BeautifulSoup(str(dst), 'html.parser')
            assert normal(src) == normal(compare), 'Source document text changed: ' + name
            for tag in ['ol', 'ul', 'li']:
                assert len(src.select(tag)) == len(dst.select(tag)), name + ' ' + tag + ' count'
            assert [x.get('start', '1') for x in src.select('ol')] == [x.get('start', '1') for x in dst.select('ol')]
            assert list_tree(src) == list_tree(compare), 'List structure/numbering changed: ' + name
            assert link_occurrences(src, originals[name]['url'], source_link) == link_occurrences(compare, LOCAL + name + '.html', destination_link), 'Source link associations changed: ' + name
        else:
            assert not output.select('.hero .eyebrow'), 'Removed hero eyebrow reintroduced'
            assert 'Independent projects. Shared principles.' not in normal(output), 'Removed members tagline reintroduced'
            text = normal(dst)
            for paragraph in source.select('main p'):
                if normal(paragraph):
                    assert normal(paragraph) in text, 'Missing homepage paragraph: ' + normal(paragraph)
            assert len(output.select('.member')) == 4
            assert len(output.select('.member-logo img')) == 4
            assert normal(output.select_one('.primary')) == 'Alliance Charter'
            assert output.select_one('#wordpress-card .org')['href'] == 'https://wordpressfoundation.org/', 'WordPress Foundation destination changed'
            assert 'Mary Hubbard' in normal(output.select_one('.leadership'))
            cards, members = source.select('.card'), output.select('.member')
            assert len(cards) == len(members) == 4
            assert len(output.select('.member-socials')) == 4, 'Member social groups changed'
            for card, member, record, logo in zip(cards, members, profiles, logos):
                old_image, new_image = card.img, member.select_one('.member-logo img')
                old_org, new_org = card.select_one('.card-body a'), member.select_one('.org')
                assert old_image['alt'] == new_image['alt'] and unquote(old_image['src']) == unquote(new_image['src']), 'Member logo mapping changed'
                source_variant = member.select_one('.member-logo picture > source[data-dark-logo]')
                assert source_variant and source_variant.get('srcset') == 'images/logos/' + logo['dark'], 'Dark logo mapping changed'
                assert source_variant.get('media') == 'screen and (prefers-color-scheme: dark)', 'Logo system fallback changed'
                assert new_image.parent.name == 'picture' and len(new_image.parent.select('source')) == 1, 'Logo picture semantics changed'
                expected_org = 'https://wordpressfoundation.org/' if record['member'] == 'WordPress' else old_org['href']
                assert normal(old_org) == normal(new_org) and expected_org == new_org['href'], 'Member organization mapping changed'
                old_project = old_image.find_parent('a')
                expected_project = old_project['href'] if old_project else old_org['href']
                assert member.select_one('.member-logo')['href'] == expected_project, 'Member project link changed'
                social = member.select_one(':scope > ul.member-socials')
                assert social and social.get('aria-label') == record['member'] + ' social profiles', 'Member social groups changed'
                expected = [(p['label'], p['url'], p['name']) for p in record['profiles']]
                actual_links = [(a.get('data-platform'), a.get('href'), a.get('aria-label')) for a in social.select('li > a')]
                assert actual_links == expected, 'Member social profile mapping changed'
                assert len(social.select('a')) == len(expected), 'Unexpected member social link'
                for link, profile in zip(social.select('li > a'), record['profiles']):
                    icon = icons[profile['label']]
                    svg = link.select_one(':scope > svg')
                    assert normal(link) == '' and len(link.select('svg')) == 1, 'Social icon presentation changed'
                    assert svg and svg.get('aria-hidden') == 'true' and svg.get('focusable') == 'false', 'Social icon accessibility changed'
                    assert svg.get('viewbox') == icon['viewBox'], 'Social icon geometry changed'
                    assert [dict(p.attrs) for p in svg.select('path')] == icon['paths'], 'Social icon geometry changed'
                    assert {tag.name for tag in svg.select('*')} == {'path'}, 'Unsafe icon markup'
                    assert link.get('title') == link.get('aria-label'), 'Missing social icon tooltip'
            assert output.select_one('.hero a[href="#news"]'), 'News hero link missing'
            section = output.select_one('#news')
            assert section and section.get('aria-labelledby') == 'news-title' and normal(section.h2) == 'News', 'News section semantics changed'
            articles = section.select('article')
            assert len(articles) == len(news), 'News coverage changed'
            assert section.select('ol.news-list[role="list"] > li > article') == articles, 'News list semantics changed'
            assert all(a.select_one(':scope > .news-story') for a in articles), 'News story grouping changed'
            for article, record in zip(articles, news):
                published = date.fromisoformat(record['date'])
                assert published <= date.today(), 'Future news date'
                assert article['id'] == 'news-' + record['id'], 'News identity changed'
                assert article.time['datetime'] == record['date'] and normal(article.time) == f"{published.strftime('%B')} {published.day}, {published.year}", 'News date changed'
                assert normal(article.h3) == record['title'] and normal(article.select_one('.news-summary')) == record['summary'], 'News content changed'
                assert [(record['sources'][0]['publisher'] if a == article.h3.a else normal(a), a['href']) for a in article.select('a')] == [(s['publisher'], s['url']) for s in record['sources']], 'News source association changed'
                assert normal(article.select_one('.news-publisher')) == record['sources'][0]['publisher'], 'News publisher changed'
            report['newsItems'] = len(news)
            report['memberSocialProfiles'] = {row['member']: len(row['profiles']) for row in profiles}
            source_body = BeautifulSoup(str(src), 'html.parser')
            for chrome in source_body.select('header,footer'):
                chrome.decompose()
            before = Counter(link_occurrences(source_body, ORIGIN, source_link))
            after = Counter(link_occurrences(output.main, LOCAL + 'index.html', destination_link))
            assert before <= after, 'Homepage source link association changed'
        original_ids = {e['id'] for e in source.select('[id]')}
        output_ids = {e['id'] for e in output.select('[id]')}
        assert original_ids <= output_ids, 'Missing anchors: ' + name + str(original_ids - output_ids)
        for anchor in original_ids:
            original, target = source.find(id=anchor), output.find(id=anchor)
            if name == 'index' and anchor == 'contact':
                # The accepted design moves this container ID to its own section heading.
                assert target.name == 'h2' and target.parent.name == 'section'
                target = target.parent
            if name == 'index' and anchor == 'wordpress-card':
                # Exact social mappings are verified above; retain the original anchor content contract.
                target = BeautifulSoup(str(target), 'html.parser')
                for social in target.select('.member-socials'):
                    social.decompose()
            assert normal(original) == normal(target), 'Anchor points at different content: ' + anchor
            if original.name in ['h1', 'h2', 'li']:
                assert original.name == target.name, 'Anchor target semantics changed: ' + anchor
        source_links = {source_link(a['href'], originals[name]['url']) for a in source.select('a[href]')}
        output_links = {destination_link(a['href'], LOCAL + name + '.html') for a in output.select('a[href]')}
        assert source_links <= output_links, 'Lost original links: ' + name + str(source_links - output_links)
        for paragraph in source.select('footer p'):
            assert normal(paragraph) in normal(output.footer), 'Lost legal/footer text: ' + name
        report['documents'].append({'page': name + '.html', 'sourceTextPreserved': True, 'sourceAnchorCount': len(original_ids), 'sourceLinkCount': len(source_links)})
    parsed = {file.name: BeautifulSoup(file.read_text(), 'html.parser') for file in SITE.glob('*.html')}
    for filename, page in parsed.items():
        verify_arrows(page)
        assert not page.select('header nav,nav[aria-label="Main navigation"]'), 'Removed main navigation reintroduced'
        assert not page.select('.hosting-notice,.review-note,#original-policy'), 'Unapproved additional notice'
        assert len(page.select('h1')) == 1 and len(page.select('main')) == 1, filename
        ids = [e['id'] for e in page.select('[id]')]
        assert len(ids) == len(set(ids)), 'Duplicate IDs: ' + filename
        assert page.html.get('lang') == 'en'
        assert page.select_one('meta[name="viewport"]')
        assert page.select_one('meta[name="robots"]')['content'] == 'noindex,nofollow'
        assert [normal(x) for x in page.select('.brand-wordmark > span')] == ['Open', 'Website', 'Alliance'], 'Header wordmark changed'
        assert [x.get('data-theme-choice') for x in page.select('#theme-options button[type="button"]')] == ['system', 'light', 'dark'], 'Theme options changed'
        assert page.select_one('.theme-control[hidden]') and page.select_one('#theme-options[hidden]'), 'Theme fallback changed'
        trigger = page.select_one('button#theme-mode[type="button"]')
        assert trigger and trigger.get('aria-label') == trigger.get('title') == 'Color theme: System', 'Theme label missing'
        assert trigger.get('aria-expanded') == 'false' and trigger.get('aria-controls') == 'theme-options', 'Theme disclosure state changed'
        assert trigger.get('data-preference') == 'system' and normal(trigger) == '', 'Theme icon presentation changed'
        assert len(trigger.select('svg')) == len(trigger.select('svg[aria-hidden="true"][focusable="false"]')) == 3, 'Theme icon accessibility changed'
        assert page.select_one('#theme-options[role="group"][aria-label="Color theme"]'), 'Theme group semantics changed'
        assert [x.get('aria-pressed') for x in page.select('#theme-options button')] == ['true', 'false', 'false'], 'Theme selected state changed'
        assert normal(page.select_one('#external-link-hint.visually-hidden')) == 'Opens in a new tab.', 'External link hint missing'
        assert not page.select('iframe,canvas,video,form'), 'Unexpected runtime/art: ' + filename
        scripts = page.select('script')
        assert len(scripts) == 1 and not scripts[0].get_text(strip=True), 'Unexpected application script'
        assert scripts[0].get('src', '').lstrip('/') == str(theme_file.relative_to(SITE)), 'Unexpected application script'
        assert len(page.select('svg')) == 3 + (sum(len(r['profiles']) for r in profiles) if filename == 'index.html' else 0), 'Unexpected icon/art'
        for link in page.select('a[href]'):
            external = urlsplit(link['href']).scheme in ['http', 'https'] or link['href'].startswith('//')
            if external:
                assert link.get('target') == '_blank', 'External link not new tab'
                assert {'noopener', 'noreferrer'} <= set(link.get('rel', [])), 'Unsafe external link'
                assert 'external-link-hint' in link.get('aria-describedby', '').split(), 'External link hint missing'
            else:
                assert not link.get('target'), 'Internal or email link changed tab behavior'
        for node in page.select('*'):
            assert not any(k.startswith('on') for k in node.attrs), 'Inline handler'
        for node in page.select('img'):
            assert node.has_attr('alt')
        for node in page.select('[href],[src]'):
            for key in ['href', 'src']:
                if not node.get(key):
                    continue
                target = urlsplit(urljoin(LOCAL + filename, node[key]))
                assert target.scheme in ['https', 'http', 'mailto'], target.scheme
                if target.netloc != 'preview.invalid':
                    continue
                relative = unquote(target.path.lstrip('/')) or 'index.html'
                assert (SITE / relative).is_file(), 'Broken local route: ' + node[key]
                if target.fragment:
                    target_page = parsed[Path(relative).name]
                    assert target_page.find(id=unquote(target.fragment)), 'Broken anchor: ' + node[key]
                report['internalLinksChecked'] += 1
    reached, pending = set(), ['index.html']
    while pending:
        filename = pending.pop()
        if filename in reached:
            continue
        reached.add(filename)
        for link in parsed[filename].select('a[href]'):
            target = urlsplit(urljoin(LOCAL + filename, link['href']))
            route = target.path.lstrip('/') or 'index.html'
            if target.netloc == 'preview.invalid' and route in parsed and route not in reached:
                pending.append(route)
    assert {name + '.html' for name in PAGES} <= reached, 'Document stranded after navigation removal'
    report['reachableDocuments'] = sorted(reached)
    report['approvedLinkCorrections'] = [{'label': 'WordPress Foundation', 'from': 'https://wordpress.org', 'to': 'https://wordpressfoundation.org/'}]
    report['diagonalArrowsExternalOnly'] = True
    report['heroArrowsAbsent'] = True
    for logo in (SOURCE / 'logos').iterdir():
        assert logo.read_bytes() == (SITE / 'images/logos' / logo.name).read_bytes()
    css = next(SITE.glob('assets/site.*.css')).read_text()
    for value, unit in re.findall(r'font-size:\s*(\d+(?:\.\d+)?)(px|rem)', css):
        assert float(value) >= (16 if unit == 'px' else 1), 'Text below minimum size'
    assert 'open-weave' not in css and 'b-sage-graphite' not in css and 'c-ivory-aubergine' not in css
    for url in re.findall(r'url\([\"\']?([^\"\')]+)', css):
        assert not urlsplit(url).scheme and (SITE / 'assets' / unquote(url)).is_file()
    config = json.loads((SITE / 'sf.jsonc').read_text())
    assert config['fallback'] == {'path': '/404.html', 'status': 404}
    assert config['listing'] is False and config['cleanUrls'] is True
    assert config['superpowers'] == {'enabled': False, 'disable_all_injection': True}
    assert 'access' not in config, 'No public grants in site config'
    assert (SITE / 'robots.txt').read_text() == 'User-agent: *\nDisallow: /\n'
    report.update({'result': 'pass', 'documentCount': len(report['documents']), 'generatedHtmlPages': len(parsed), 'fileCount': len(actual), 'totalBytes': sum(x['bytes'] for x in actual), 'manifestSha256': hashlib.sha256((ROOT / 'site-manifest.json').read_bytes()).hexdigest(), 'semanticBindingsVerified': True, 'additionalNotices': False, 'applicationJavaScriptFiles': 1, 'publicationAuthorization': 'tracked separately in release record'})
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = verify()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
