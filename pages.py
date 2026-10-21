#!/usr/bin/env python3
"""Package the verified OWA site for GitHub Pages, without publishing it.

The legacy build remains untouched. Only metadata, robots.txt and 404 paths
change. Manifests and build settings live beside, never inside, the web root.
"""
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import argparse
import hashlib
import json
import re
from bs4 import BeautifulSoup
import build
import verify

ROOT = Path(__file__).resolve().parent
SITE = ROOT / 'site'


def base_path(value):
    value = value or '/'
    if (not re.fullmatch(r'/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]*', value)
            or any(part in {'.', '..'} for part in value.split('/'))):
        raise ValueError('Use a root path or a repository path, such as /owa/.')
    return value.rstrip('/') + '/'


def configuration(base=None, site_url=None, indexable=False):
    if site_url:
        if any(c.isspace() for c in site_url) or '\\' in site_url:
            raise ValueError('Invalid site URL.')
        parsed = urlsplit(site_url)
        if (parsed.scheme != 'https' or not parsed.hostname or parsed.username
                or parsed.password or parsed.query or parsed.fragment
                or not re.fullmatch(r'[A-Za-z0-9.-]+', parsed.netloc)):
            raise ValueError('Use the public HTTPS site URL without credentials, query or fragment.')
        derived = base_path(parsed.path)
        if base is not None and base_path(base) != derived:
            raise ValueError('Base path and site URL disagree.')
        base = derived
        site_url = 'https://' + parsed.netloc + derived
    if indexable and not site_url:
        raise ValueError('Enabling indexing requires the intended public site URL.')
    return {'basePath': base_path(base), 'siteUrl': site_url, 'indexable': bool(indexable)}


def render_page(raw, name, config):
    doc = BeautifulSoup(raw, 'html.parser')
    doc.select_one('meta[name=robots]')['content'] = (
        'index,follow' if config['indexable'] and name != '404.html' else 'noindex,nofollow')

    def meta(key, value, attribute='name'):
        doc.head.append(doc.new_tag('meta', attrs={attribute: key, 'content': value}))

    meta('referrer', 'no-referrer')
    title = doc.title.get_text()
    description = doc.select_one('meta[name=description]')['content']
    for key, value in [('og:type', 'website'), ('og:site_name', 'Open Website Alliance'),
                       ('og:title', title), ('og:description', description)]:
        meta(key, value, 'property')
    for key, value in [('twitter:card', 'summary'), ('twitter:title', title),
                       ('twitter:description', description)]:
        meta(key, value)
    if config['siteUrl']:
        image = urljoin(config['siteUrl'], 'images/logos/OWA%20logo.png')
        meta('og:image', image, 'property')
        meta('og:image:alt', 'Open Website Alliance logo', 'property')
        meta('twitter:image', image)
        meta('twitter:image:alt', 'Open Website Alliance logo')
        if name != '404.html':
            canonical = urljoin(config['siteUrl'], '' if name == 'index.html' else name)
            doc.head.append(doc.new_tag('link', rel='canonical', href=canonical))
            meta('og:url', canonical, 'property')
    if name == '404.html':
        # Served at arbitrary missing URLs; relative paths alone cannot recover.
        for node in doc.select('[href],[src]'):
            for attr in ['href', 'src']:
                value = node.get(attr, '')
                if value.startswith('/') and not value.startswith('//'):
                    node[attr] = config['basePath'] + value.lstrip('/')
    return str(doc).encode('utf-8')


def payload(config):
    assert config == configuration(config['basePath'], config['siteUrl'], config['indexable'])
    verify.verify()  # Includes the exact legacy allowlist and all content guards.
    source_manifest = json.loads((ROOT / 'site-manifest.json').read_text())
    files = {}
    for entry in source_manifest['files']:
        name = entry['path']
        if name == 'sf.jsonc':
            continue
        raw = (SITE / name).read_bytes()
        if name.endswith('.html'):
            raw = render_page(raw, name, config)
        elif name == 'robots.txt' and config['indexable']:
            raw = b'User-agent: *\nDisallow:\n'
        files[name] = raw
    return files


def manifest(files):
    entries = [{'path': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
               for name, raw in sorted(files.items())]
    return {'files': entries, 'fileCount': len(entries), 'totalBytes': sum(e['bytes'] for e in entries)}


def sidecar(output, name):
    return output.parent / (output.name + '-' + name + '.json')


def inventory(output):
    assert not output.is_symlink(), 'Output must not be a symlink'
    assert output.absolute() == output.resolve(), 'Output ancestors must not be symlinks'
    files = {}
    if output.exists():
        assert output.is_dir(), 'Output must be a directory'
        for path in sorted(output.rglob('*')):
            assert not path.is_symlink(), 'Symlinks are not publishable'
            if path.is_file():
                assert path.stat().st_nlink == 1, 'Hard-linked output is not publishable'
                files[path.relative_to(output).as_posix()] = path.read_bytes()
    return files


def prepare(output, config):
    output = Path(output).absolute()
    assert output != ROOT and output not in ROOT.parents and output != Path.home(), 'Unsafe output directory'
    for protected in ['source', 'site', '.git', 'test-assets']:
        directory = ROOT / protected
        assert output != directory and directory not in output.parents, 'Source/test directories are not staging areas'
    expected = payload(config)
    existing = inventory(output)
    for name in ['manifest', 'build']:
        target = sidecar(output, name)
        assert not target.is_symlink(), 'Sidecar must not be a symlink'
        assert not target.exists() or (target.is_file() and target.stat().st_nlink == 1), 'Unsafe sidecar'
    if existing:
        assert sidecar(output, 'manifest').is_file() and sidecar(output, 'build').is_file(), 'Existing output is not an owned Pages build'
        assert manifest(existing) == json.loads(sidecar(output, 'manifest').read_text()), 'Existing output drift; refusing to overwrite it'
    assert set(existing) <= set(expected), 'Unexpected files in Pages output; refusing to erase them'
    output.mkdir(parents=True, exist_ok=True)
    for name, raw in expected.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    for name, data in [('manifest', manifest(expected)), ('build', config)]:
        target = sidecar(output, name)
        assert not target.is_symlink(), 'Sidecar must not be a symlink'
        target.write_text(json.dumps(data, indent=2) + '\n')
    return verify_output(output, config)


def verify_output(output, config):
    output = Path(output).absolute()
    expected = payload(config)
    actual = inventory(output)
    assert actual == expected, 'Pages output differs from verified source/metadata/path contract'
    record = manifest(actual)
    assert json.loads(sidecar(output, 'manifest').read_text()) == record, 'Pages manifest mismatch'
    assert json.loads(sidecar(output, 'build').read_text()) == config, 'Pages settings mismatch'
    return {'result': 'pass', 'target': 'github-pages', **config,
            'fileCount': record['fileCount'], 'totalBytes': record['totalBytes'],
            'manifestSha256': hashlib.sha256(sidecar(output, 'manifest').read_bytes()).hexdigest(),
            'published': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/pages')
    parser.add_argument('--base-path', help='Defaults to / or the path in --site-url.')
    parser.add_argument('--site-url', help='Full public HTTPS base URL, once known.')
    parser.add_argument('--indexable', action='store_true', help='Explicit public-launch SEO opt-in.')
    parser.add_argument('--verify-only', action='store_true', help='Read back the existing package; do not rebuild.')
    args = parser.parse_args()
    if args.verify_only:
        if args.base_path is not None or args.site_url or args.indexable:
            parser.error('--verify-only uses the saved package settings, not new options')
        config = json.loads(sidecar(args.output, 'build').read_text())
        result = verify_output(args.output, config)
    else:
        config = configuration(args.base_path, args.site_url, args.indexable)
        build.build()
        result = prepare(args.output, config)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
