#!/usr/bin/env python3
"""Adversarial checks through the real verifier, with in-memory file overlays."""
from pathlib import Path
from unittest.mock import patch
import hashlib
import json
import unittest
from bs4 import BeautifulSoup
import verify


def add_notice(doc):
    notice = doc.new_tag('aside', attrs={'class': 'hosting-notice'})
    notice.string = 'About this review site'
    doc.select_one('[data-source-document]').insert(1, notice)


def add_footer_notice(doc):
    notice = doc.new_tag('p', attrs={'class': 'review-note'})
    notice.string = 'Private redesign for review.'
    doc.footer.append(notice)


def change_privacy_link(doc):
    doc.select_one('[data-source-document] a')['href'] = 'https://example.invalid/privacy/'


def change_privacy_text(doc):
    doc.select_one('[data-source-document] p').string = 'Changed privacy policy.'


def change_clause_number(doc):
    doc.select_one('#members-1')['value'] = '99'


def reverse_numbering(doc):
    doc.select_one('ol')['reversed'] = ''


def swap_membership_links(doc):
    links = doc.select('[data-source-document] a')
    links[0]['href'], links[1]['href'] = links[1]['href'], links[0]['href']


def swap_clause_anchors(doc):
    a, b = doc.select_one('#members-1'), doc.select_one('#members-2')
    a['id'], b['id'] = b['id'], a['id']


def swap_member_links(doc):
    a, b = doc.select('.member .org')[:2]
    a['href'], b['href'] = b['href'], a['href']


def swap_member_logos(doc):
    a, b = doc.select('.member-logo img')[:2]
    a['src'], b['src'] = b['src'], a['src']


def restore_hero_eyebrow(doc):
    eyebrow = doc.new_tag('p', attrs={'class': 'eyebrow'})
    eyebrow.string = 'The Open Website Alliance'
    doc.select_one('.hero-copy').insert(0, eyebrow)


def restore_main_navigation(doc):
    nav = doc.new_tag('nav', attrs={'aria-label': 'Main navigation'})
    doc.header.append(nav)


def remove_member_socials(doc):
    doc.select_one('.member-socials').decompose()


def change_social_profile(doc):
    doc.select_one('.member-socials a')['href'] = 'https://example.invalid/unofficial-profile'


def swap_platform_order(doc):
    a, b = doc.select('.member-socials li')[:2]
    a.insert_before(b.extract())


def remove_dark_logo(doc):
    doc.select_one('.member-logo source').decompose()


def swap_dark_logos(doc):
    a, b = doc.select('.member-logo source')[:2]
    a['srcset'], b['srcset'] = b['srcset'], a['srcset']


def break_system_logo(doc):
    doc.select_one('.member-logo source')['media'] = 'not all'


def swap_member_socials(doc):
    a, b = doc.select('.member')[:2]
    first, second = a.select_one('.member-socials').extract(), b.select_one('.member-socials').extract()
    a.append(second)
    b.append(first)


def remove_social_accessible_name(doc):
    del doc.select_one('.member-socials a')['aria-label']


def restore_members_tagline(doc):
    tag = doc.new_tag('p')
    tag.string = 'Independent projects. Shared principles.'
    doc.select_one('.member-heading').append(tag)


def change_header_wordmark(doc):
    doc.select_one('.brand-wordmark > span').string = 'Wrong'


def remove_icon(doc):
    doc.select_one('.member-socials svg').decompose()


def expose_icon(doc):
    doc.select_one('.member-socials svg')['aria-hidden'] = 'false'


def change_icon(doc):
    doc.select_one('.member-socials path')['d'] = 'M0 0L1 1'


def restore_social_text(doc):
    doc.select_one('.member-socials a').append('Facebook')


def remove_new_tab(doc):
    del doc.select_one('a[target="_blank"]')['target']


def unsafe_new_tab(doc):
    doc.select_one('a[target="_blank"]')['rel'] = ['opener']


def remove_new_tab_hint(doc):
    del doc.select_one('a[target="_blank"]')['aria-describedby']


def externalize_internal_link(doc):
    doc.select_one('.primary')['target'] = '_blank'


def expose_dead_theme_control(doc):
    del doc.select_one('.theme-control')['hidden']


def remove_theme_option(doc):
    doc.select_one('#theme-options button[data-theme-choice="dark"]').decompose()


def remove_theme_name(doc):
    del doc.select_one('#theme-mode')['aria-label']


def remove_theme_expanded(doc):
    del doc.select_one('#theme-mode')['aria-expanded']


def expose_theme_icon(doc):
    doc.select_one('#theme-mode svg')['aria-hidden'] = 'false'


def remove_news_list_semantics(doc):
    doc.select_one('ol.news-list').name = 'div'


def add_script(doc):
    node = doc.new_tag('script')
    node.string = 'alert(1)'
    doc.body.append(node)


def remove_news_article(doc):
    doc.select_one('#news article').decompose()


def change_news_date(doc):
    doc.select_one('#news time')['datetime'] = '1999-01-01'


def change_news_source(doc):
    doc.select_one('#news h3 a')['href'] = 'https://example.invalid/wrong'


def remove_news_hero_link(doc):
    doc.select_one('.hero a[href="#news"]').decompose()


def revert_foundation_destination(doc):
    doc.select_one('#wordpress-card .org')['href'] = 'https://wordpress.org'


def restore_internal_arrow(doc):
    arrow = doc.new_tag('span', attrs={'aria-hidden': 'true'})
    arrow.string = '↗'
    doc.select_one('.primary').append(arrow)


def add_external_hero_arrow(doc):
    link = doc.new_tag('a', href='https://example.org/', attrs={'target': '_blank', 'rel': ['noopener', 'noreferrer'], 'aria-describedby': 'external-link-hint'})
    link.string = 'External fixture '
    arrow = doc.new_tag('span', attrs={'aria-hidden': 'true'})
    arrow.string = '↗'
    link.append(arrow)
    doc.select_one('.hero').append(link)


CASES = [
    ('foundation_destination_reverted', 'index.html', revert_foundation_destination),
    ('internal_arrow_restored', '404.html', restore_internal_arrow),
    ('external_hero_arrow_added', 'index.html', add_external_hero_arrow),
    ('restored_members_tagline', 'index.html', restore_members_tagline),
    ('changed_header_wordmark', 'privacy.html', change_header_wordmark),
    ('missing_social_icon', 'index.html', remove_icon),
    ('exposed_decorative_icon', 'index.html', expose_icon),
    ('altered_brand_icon', 'index.html', change_icon),
    ('restored_social_text', 'index.html', restore_social_text),
    ('external_same_tab', 'charter.html', remove_new_tab),
    ('unsafe_external_tab', 'privacy.html', unsafe_new_tab),
    ('missing_tab_hint', 'index.html', remove_new_tab_hint),
    ('internal_new_tab', 'index.html', externalize_internal_link),
    ('dead_theme_control_visible', '404.html', expose_dead_theme_control),
    ('dark_option_removed', 'membership-process.html', remove_theme_option),
    ('theme_name_removed', 'index.html', remove_theme_name),
    ('theme_state_removed', 'privacy.html', remove_theme_expanded),
    ('theme_icon_exposed', '404.html', expose_theme_icon),
    ('news_list_semantics_removed', 'index.html', remove_news_list_semantics),
    ('extra_runtime_script', 'index.html', add_script),
    ('missing_news_item', 'index.html', remove_news_article),
    ('wrong_news_date', 'index.html', change_news_date),
    ('wrong_news_source', 'index.html', change_news_source),
    ('missing_news_hero_link', 'index.html', remove_news_hero_link),
    ('restored_hero_eyebrow', 'index.html', restore_hero_eyebrow),
    ('restored_main_navigation', 'index.html', restore_main_navigation),
    ('restored_404_navigation', '404.html', restore_main_navigation),
    ('missing_member_socials', 'index.html', remove_member_socials),
    ('unofficial_social_profile', 'index.html', change_social_profile),
    ('social_platform_order_changed', 'index.html', swap_platform_order),
    ('dark_logo_removed', 'index.html', remove_dark_logo),
    ('dark_logos_swapped', 'index.html', swap_dark_logos),
    ('system_logo_broken', 'index.html', break_system_logo),
    ('swapped_member_socials', 'index.html', swap_member_socials),
    ('missing_social_accessible_name', 'index.html', remove_social_accessible_name),
    ('additional_privacy_notice', 'privacy.html', add_notice),
    ('additional_footer_notice', 'index.html', add_footer_notice),
    ('privacy_policy_wrong_destination', 'privacy.html', change_privacy_link),
    ('privacy_policy_changed_wording', 'privacy.html', change_privacy_text),
    ('incorrect_clause_number', 'charter.html', change_clause_number),
    ('reversed_clause_numbering', 'charter.html', reverse_numbering),
    ('swapped_membership_links', 'membership-process.html', swap_membership_links),
    ('swapped_clause_anchors', 'charter.html', swap_clause_anchors),
    ('swapped_member_organization_links', 'index.html', swap_member_links),
    ('swapped_member_logos', 'index.html', swap_member_logos),
]


def run_overlay(filename, mutate):
    file = verify.SITE / filename
    doc = BeautifulSoup(file.read_text(), 'html.parser')
    mutate(doc)
    changed = str(doc).encode()
    manifest = json.loads((verify.ROOT / 'site-manifest.json').read_text())
    for entry in manifest['files']:
        if entry['path'] == filename:
            entry.update(bytes=len(changed), sha256=hashlib.sha256(changed).hexdigest())
    manifest['totalBytes'] = sum(row['bytes'] for row in manifest['files'])
    overlay = {file: changed, verify.ROOT / 'site-manifest.json': (json.dumps(manifest) + '\n').encode()}
    original_text, original_bytes = Path.read_text, Path.read_bytes
    def read_text(path, *args, **kwargs):
        return overlay[path].decode() if path in overlay else original_text(path, *args, **kwargs)
    def read_bytes(path, *args, **kwargs):
        return overlay[path] if path in overlay else original_bytes(path, *args, **kwargs)
    with patch.object(Path, 'read_text', read_text), patch.object(Path, 'read_bytes', read_bytes):
        return verify.verify()


class FidelityRegressionTests(unittest.TestCase):
    def test_foundation_and_arrow_contract(self):
        home = BeautifulSoup((verify.SITE / 'index.html').read_text(), 'html.parser')
        self.assertEqual(home.select_one('#wordpress-card .org')['href'], 'https://wordpressfoundation.org/')
        self.assertNotRegex(home.select_one('.hero').get_text(), '[\u2190-\u21ff]')
        for file in verify.SITE.glob('*.html'):
            doc = BeautifulSoup(file.read_text(), 'html.parser')
            for a in doc.select('a[href]'):
                if '↗' in a.get_text():
                    self.assertTrue(a['href'].startswith(('https://', 'http://', '//')))
                    self.assertIsNone(a.find_parent(class_='hero'))

    def test_picture_variants(self):
        home = BeautifulSoup((verify.SITE / 'index.html').read_text(), 'html.parser')
        self.assertEqual(len(home.select('.member-logo picture > source[data-dark-logo]')), 4)
        self.assertEqual(len(home.select('.member-logo picture > img')), 4)

    def test_complete_ordered_profiles(self):
        order = json.loads((verify.SOURCE / 'social-platform-order.json').read_text())
        records = json.loads((verify.SOURCE / 'member-socials.json').read_text())
        home = BeautifulSoup((verify.SITE / 'index.html').read_text(), 'html.parser')
        self.assertEqual(order, sorted(set(order)))
        for record, member in zip(records, home.select('.member')):
            labels = [p['label'] for p in record['profiles']]
            self.assertEqual(labels, sorted(labels, key=order.index))
            self.assertEqual([(a['data-platform'], a['href'], a['aria-label']) for a in member.select('.member-socials a')], [(p['label'], p['url'], p['name']) for p in record['profiles']])

    def test_refinement_semantics(self):
        for route in verify.PAGES + ['404']:
            doc = BeautifulSoup((verify.SITE / (route + '.html')).read_text(), 'html.parser')
            self.assertEqual([verify.normal(x) for x in doc.select('.brand-wordmark > span')], ['Open', 'Website', 'Alliance'])
            self.assertEqual([x.get('data-theme-choice') for x in doc.select('#theme-options button')], ['system', 'light', 'dark'])
            self.assertEqual(doc.select_one('#theme-mode').name, 'button')
            self.assertEqual(doc.select_one('#theme-mode').get('aria-label'), 'Color theme: System')
            self.assertEqual(doc.select_one('#theme-mode').get('aria-expanded'), 'false')
            self.assertEqual(len(doc.select('#theme-mode svg[aria-hidden="true"][focusable="false"]')), 3)
            self.assertIsNotNone(doc.select_one('#theme-options[hidden]'))
            self.assertTrue(doc.select_one('.theme-control').has_attr('hidden'))
            for link in doc.select('a[href]'):
                external = link['href'].startswith(('https://', 'http://', '//'))
                self.assertEqual(link.get('target'), '_blank' if external else None)
                if external:
                    self.assertTrue({'noopener', 'noreferrer'} <= set(link.get('rel', [])))
                    self.assertIn('external-link-hint', link.get('aria-describedby', '').split())
        home = BeautifulSoup((verify.SITE / 'index.html').read_text(), 'html.parser')
        self.assertNotIn('Independent projects. Shared principles.', verify.normal(home))
        self.assertIsNotNone(home.select_one('.hero a[href="#news"]'))
        self.assertGreater(len(home.select('#news article')), 0)
        self.assertEqual(len(home.select('#news ol.news-list > li > article')), len(home.select('#news article')))
        for link in home.select('.member-socials a'):
            self.assertEqual(verify.normal(link), '')
            self.assertEqual(link.svg.get('aria-hidden'), 'true')
            self.assertEqual(link.svg.get('focusable'), 'false')
            self.assertTrue(link.get('data-platform'))

    def test_unchanged_candidate_passes(self):
        self.assertEqual(verify.verify()['result'], 'pass')


EXPECTED_FAILURE = {
    'foundation_destination_reverted': 'WordPress Foundation destination changed',
    'internal_arrow_restored': 'Diagonal arrow on non-external or hero link',
    'external_hero_arrow_added': 'Arrow on hero link',
    'restored_members_tagline': 'Removed members tagline reintroduced',
    'changed_header_wordmark': 'Header wordmark changed',
    'missing_social_icon': 'Social icon presentation changed',
    'exposed_decorative_icon': 'Social icon accessibility changed',
    'altered_brand_icon': 'Social icon geometry changed',
    'restored_social_text': 'Social icon presentation changed',
    'external_same_tab': 'External link not new tab',
    'unsafe_external_tab': 'Unsafe external link',
    'missing_tab_hint': 'External link hint missing',
    'internal_new_tab': 'Internal or email link changed tab behavior',
    'dead_theme_control_visible': 'Theme fallback changed',
    'dark_option_removed': 'Theme options changed',
    'theme_name_removed': 'Theme label missing',
    'theme_state_removed': 'Theme disclosure state changed',
    'theme_icon_exposed': 'Theme icon accessibility changed',
    'news_list_semantics_removed': 'News list semantics changed',
    'extra_runtime_script': 'Unexpected application script',
    'missing_news_item': 'News coverage changed',
    'wrong_news_date': 'News date changed',
    'wrong_news_source': 'News source association changed',
    'missing_news_hero_link': 'News hero link missing',
    'restored_hero_eyebrow': 'Removed hero eyebrow reintroduced',
    'restored_main_navigation': 'Removed main navigation reintroduced',
    'restored_404_navigation': 'Removed main navigation reintroduced',
    'missing_member_socials': 'Member social groups changed',
    'unofficial_social_profile': 'Member social profile mapping changed',
    'social_platform_order_changed': 'Member social profile mapping changed',
    'dark_logo_removed': 'Dark logo mapping changed',
    'dark_logos_swapped': 'Dark logo mapping changed',
    'system_logo_broken': 'Logo system fallback changed',
    'swapped_member_socials': 'Member social groups changed',
    'missing_social_accessible_name': 'Member social profile mapping changed',
    'additional_privacy_notice': 'Unapproved additional notice',
    'additional_footer_notice': 'Unapproved additional notice',
    'privacy_policy_wrong_destination': 'Source link associations changed',
    'privacy_policy_changed_wording': 'Source document text changed',
    'incorrect_clause_number': 'List structure/numbering changed',
    'reversed_clause_numbering': 'List structure/numbering changed',
    'swapped_membership_links': 'Source link associations changed',
    'swapped_clause_anchors': 'Anchor points at different content',
    'swapped_member_organization_links': 'Member organization mapping changed',
    'swapped_member_logos': 'Member logo mapping changed',
}


def make_test(filename, mutate, expected_failure):
    def test(self):
        with self.assertRaisesRegex(AssertionError, expected_failure):
            run_overlay(filename, mutate)
    return test


for name, filename, mutate in CASES:
    setattr(FidelityRegressionTests, 'test_' + name, make_test(filename, mutate, EXPECTED_FAILURE[name]))

if __name__ == '__main__':
    unittest.main(verbosity=2)
