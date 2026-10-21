"""Pages packaging regressions, independent of a GitHub account/repository."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.parse import unquote, urljoin, urlsplit
import hashlib
import json
import unittest
from bs4 import BeautifulSoup
import pages


class PagesTests(unittest.TestCase):
    def test_base_paths(self):
        for supplied, expected in [(None, '/'), ('', '/'), ('/', '/'),
                                   ('/owa', '/owa/'), ('/any-repository/', '/any-repository/')]:
            with self.subTest(supplied=supplied):
                self.assertEqual(pages.configuration(supplied)['basePath'], expected)

    def test_invalid_paths(self):
        for value in ['owa', '//elsewhere/', '/../', '/a/../b/', '/a//b/',
                      '/a?b/', '/a#b/', '/a%2fb/', '/a\\b/', '/a\nb/']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                pages.configuration(value)

    def test_url_derives_path_and_strips_no_content(self):
        for url, base in [('https://example.org', '/'),
                          ('https://example.github.io/any-repository', '/any-repository/')]:
            result = pages.configuration(site_url=url)
            self.assertEqual(result['basePath'], base)
            self.assertEqual(result['siteUrl'], url + '/')

    def test_url_validation(self):
        for url in ['http://example.org/', 'https://user:password@example.org/',
                    'https://example.org/?secret=x', 'https://example.org/#fragment',
                    'https://example.org/a/../b/', 'https://example.org/a%2fb/',
                    'https://example.org\\evil/', 'https:///missing-host',
                    'https://example.org/\n']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                pages.configuration(site_url=url)
        with self.assertRaises(ValueError):
            pages.configuration('/different/', site_url='https://example.org/owa/')

    def test_indexing_requires_explicit_url(self):
        with self.assertRaises(ValueError):
            pages.configuration(indexable=True)
        self.assertFalse(pages.configuration()['indexable'])

    def test_visible_content_assets_and_links_preserved(self):
        for prefix in ['/', '/unknown-repo/']:
            config = pages.configuration(prefix)
            payload = pages.payload(config)
            for name, data in payload.items():
                if not name.endswith('.html'):
                    self.assertEqual(data, (pages.SITE / name).read_bytes())
                    continue
                before = BeautifulSoup((pages.SITE / name).read_text(), 'html.parser')
                after = BeautifulSoup(data, 'html.parser')
                if name == '404.html':
                    for node in before.select('[href],[src]'):
                        for attr in ['href', 'src']:
                            value = node.get(attr, '')
                            if value.startswith('/') and not value.startswith('//'):
                                node[attr] = prefix + value.lstrip('/')
                self.assertEqual(str(before.body), str(after.body))
                self.assertEqual(after.select_one('meta[name=referrer]')['content'], 'no-referrer')
                self.assertEqual(after.select_one('meta[name=robots]')['content'], 'noindex,nofollow')
                self.assertEqual(after.select_one('meta[property="og:title"]')['content'], after.title.string)
                self.assertFalse(after.select('link[rel=canonical],meta[property="og:url"],meta[property="og:image"]'))

    def test_absolute_social_metadata_and_canonicals(self):
        config = pages.configuration(site_url='https://example.org/owa/', indexable=True)
        for name, raw in pages.payload(config).items():
            if not name.endswith('.html'):
                continue
            doc = BeautifulSoup(raw, 'html.parser')
            self.assertEqual(doc.select_one('meta[property="og:image"]')['content'],
                             'https://example.org/owa/images/logos/OWA%20logo.png')
            self.assertEqual(doc.select_one('meta[name="twitter:card"]')['content'], 'summary')
            if name == '404.html':
                self.assertEqual(doc.select_one('meta[name=robots]')['content'], 'noindex,nofollow')
                self.assertFalse(doc.select('link[rel=canonical],meta[property="og:url"]'))
            else:
                expected = 'https://example.org/owa/' + ('' if name == 'index.html' else name)
                self.assertEqual(doc.select_one('link[rel=canonical]')['href'], expected)
                self.assertEqual(doc.select_one('meta[property="og:url"]')['content'], expected)
                self.assertEqual(doc.select_one('meta[name=robots]')['content'], 'index,follow')
        self.assertEqual(pages.payload(config)['robots.txt'], b'User-agent: *\nDisallow:\n')

    def test_allowlist_excludes_hosting_config_and_evidence(self):
        expected = {r['path'] for r in json.loads((pages.ROOT / 'site-manifest.json').read_text())['files']} - {'sf.jsonc'}
        actual = set(pages.payload(pages.configuration()))
        self.assertEqual(actual, expected)
        self.assertNotIn('sf.jsonc', actual)
        self.assertTrue(all(not p.startswith(('.', 'source/', 'test-assets/', 'qa-reports/')) for p in actual))

    def test_links_assets_and_deep_404_resolve_inside_mount(self):
        for prefix in ['/', '/repository-name/']:
            payload = pages.payload(pages.configuration(prefix))
            for name, raw in payload.items():
                if not name.endswith('.html'):
                    continue
                locations = [prefix + name]
                if name == '404.html':
                    locations += [prefix + 'missing/deep/page', prefix + 'missing/deep/']
                for location in locations:
                    doc = BeautifulSoup(raw, 'html.parser')
                    for node in doc.select('[href],[src],[srcset]'):
                        for attr in ['href', 'src', 'srcset']:
                            value = node.get(attr)
                            if not value or value.startswith('#') or urlsplit(value).scheme:
                                continue
                            resolved = urlsplit(urljoin('https://example.invalid' + location, value))
                            self.assertTrue(resolved.path.startswith(prefix), (name, location, value))
                            relative = unquote(resolved.path[len(prefix):]) or 'index.html'
                            self.assertIn(relative, payload, (name, location, value))

    def test_package_manifest_and_read_only_verification(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / 'pages'
            config = pages.configuration('/test/')
            result = pages.prepare(output, config)
            self.assertEqual(result['result'], 'pass')
            before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(tmp).rglob('*') if p.is_file()}
            self.assertEqual(pages.verify_output(output, config)['result'], 'pass')
            after = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in before}
            self.assertEqual(before, after)
            manifest = json.loads((Path(tmp) / 'pages-manifest.json').read_text())
            self.assertEqual(manifest['fileCount'], len(list(p for p in output.rglob('*') if p.is_file())))
            self.assertEqual(manifest['fileCount'], len(pages.payload(config)))
            self.assertEqual(json.loads((Path(tmp) / 'pages-build.json').read_text()), config)

    def test_tampered_file_fails_verification(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / 'pages'
            config = pages.configuration()
            pages.prepare(output, config)
            (output / 'index.html').write_text('wrong')
            with self.assertRaises(AssertionError):
                pages.verify_output(output, config)

    def test_unexpected_file_blocks_rebuild_without_removing_it(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / 'pages'
            config = pages.configuration()
            pages.prepare(output, config)
            marker = output / 'private.txt'
            marker.write_text('keep this local file')
            with self.assertRaises(AssertionError):
                pages.prepare(output, config)
            self.assertEqual(marker.read_text(), 'keep this local file')

    def test_symlink_blocks_packaging(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / 'pages'
            output.mkdir()
            (output / 'images').symlink_to(pages.SITE / 'images', target_is_directory=True)
            with self.assertRaises(AssertionError):
                pages.prepare(output, pages.configuration())

    def test_hardlinked_sidecars_are_rejected_before_any_write(self):
        for kind in ['manifest', 'build']:
            with self.subTest(kind=kind), TemporaryDirectory() as tmp:
                output = Path(tmp) / 'pages'
                config = pages.configuration()
                pages.prepare(output, config)
                before = pages.inventory(output)
                sidecar = pages.sidecar(output, kind)
                sidecar.unlink()  # Owned, disposable test fixture only.
                other = Path(tmp) / 'keep.txt'
                other.write_text('unrelated data')
                sidecar.hardlink_to(other)
                with self.assertRaisesRegex(AssertionError, 'Unsafe sidecar'):
                    pages.prepare(output, pages.configuration('/changed/'))
                self.assertEqual(other.read_text(), 'unrelated data')
                self.assertEqual(pages.inventory(output), before)

    def test_unowned_matching_filename_is_not_overwritten(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / 'pages'
            output.mkdir()
            marker = output / 'index.html'
            marker.write_text('unrelated content')
            with self.assertRaises(AssertionError):
                pages.prepare(output, pages.configuration())
            self.assertEqual(marker.read_text(), 'unrelated content')

    def test_source_and_ancestor_outputs_are_rejected(self):
        for output in [pages.ROOT, pages.ROOT.parent, pages.SITE,
                       pages.ROOT / 'source' / 'new', pages.ROOT / 'test-assets']:
            with self.subTest(output=output), self.assertRaises(AssertionError):
                pages.prepare(output, pages.configuration())

    def test_legacy_source_must_pass_fidelity_verifier(self):
        with patch('pages.verify.verify', side_effect=AssertionError('content drift')):
            with self.assertRaisesRegex(AssertionError, 'content drift'):
                pages.payload(pages.configuration())


if __name__ == '__main__':
    unittest.main()
