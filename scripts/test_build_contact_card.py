"""Tests for build-contact-card.py. Run from the repository root: pytest scripts/"""

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name('build-contact-card.py')
_spec = importlib.util.spec_from_file_location('build_contact_card', SCRIPT)
card = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(card)


@pytest.fixture
def profile() -> dict:
    """Return a fresh copy of the real profile.json."""
    return json.loads((card.CARD / 'profile.json').read_text(encoding='utf-8'))


def unfold(data: bytes) -> list[str]:
    """Undo vCard line folding and split into content lines."""
    return data.decode('utf-8').replace('\r\n ', '').split('\r\n')


def test_vcard_escape_escapes_special_characters() -> None:
    """Backslash, semicolon, comma and newlines are escaped."""
    assert card.vcard_escape('a\\b;c,d\r\ne\nf') == 'a\\\\b\\;c\\,d\\ne\\nf'


def test_fold_line_leaves_short_lines_alone() -> None:
    """Lines within 75 bytes are unchanged."""
    assert card.fold_line('FN:Vicky Guo') == 'FN:Vicky Guo'


def test_fold_line_limits_bytes_and_keeps_characters_whole() -> None:
    """Folded lines stay within 75 bytes, never split a multi-byte character, and unfold losslessly."""
    value = 'NOTE:' + '’é' * 60
    folded = card.fold_line(value)
    assert all(len(part.encode('utf-8')) <= 75 for part in folded.split('\r\n'))
    assert folded.replace('\r\n ', '') == value


def test_validate_profile_accepts_real_profile(profile: dict) -> None:
    """The committed profile is valid."""
    card.validate_profile(profile)


@pytest.mark.parametrize('key, value, message', [
    ('fileSlug', None, 'missing'),
    ('github', 'http://github.com/x', 'HTTPS'),
    ('email', 'not-an-email', 'email'),
    ('email', 'a@b.c\r\nBCC:x', 'email'),
    ('fileSlug', '../evil', 'fileSlug'),
])
def test_validate_profile_rejects_bad_values(profile: dict, key: str, value: str | None, message: str) -> None:
    """Missing fields, non-HTTPS URLs, bad emails and unsafe slugs are rejected."""
    if value is None:
        del profile[key]
    else:
        profile[key] = value
    with pytest.raises(ValueError, match=message):
        card.validate_profile(profile)


def test_check_qr_matches(tmp_path: Path) -> None:
    """Passes for a matching URL; exits for a different or missing QR record."""
    (tmp_path / 'qr-metadata.json').write_text(json.dumps({'url': 'https://example.com/card/'}), encoding='utf-8')
    card.check_qr_matches('https://example.com/card/', tmp_path)
    with pytest.raises(SystemExit):
        card.check_qr_matches('https://example.com/other/', tmp_path)
    with pytest.raises(SystemExit):
        card.check_qr_matches('https://example.com/card/', tmp_path / 'missing')


def test_regenerate_qr_writes_svg_and_metadata(tmp_path: Path) -> None:
    """Writes qr.svg plus metadata recording the encoded URL."""
    pytest.importorskip('qrcode')
    card.regenerate_qr('https://example.com/card/', tmp_path)
    assert (tmp_path / 'qr.svg').read_text().startswith('<?xml')
    assert json.loads((tmp_path / 'qr-metadata.json').read_text())['url'] == 'https://example.com/card/'


def test_asset_version_is_short_and_content_based(tmp_path: Path) -> None:
    """The hash is 8 hex characters and changes when the file changes."""
    path = tmp_path / 'a.css'
    path.write_text('a')
    first = card.asset_version(path)
    path.write_text('b')
    assert len(first) == 8 and all(c in '0123456789abcdef' for c in first)
    assert card.asset_version(path) != first


def test_render_page_fills_profile_values_and_escapes_html(profile: dict) -> None:
    """Labels and file names come from the profile, and HTML in values is escaped."""
    profile.update(linkedinLabel='Li <Label>', githubLabel='Gh & Co', fileSlug='Jane-Doe')
    template = (card.CARD / 'template.html').read_text(encoding='utf-8')
    page = card.render_page(profile, template, 'css12345', 'js123456')
    assert 'Li &lt;Label&gt;' in page and 'Gh &amp; Co' in page
    assert 'download="Jane-Doe.vcf"' in page and 'download="Jane-Doe-QR.svg"' in page
    assert 'card.css?v=css12345' in page and '$' not in page


def test_build_vcard_format_and_social_profiles(profile: dict) -> None:
    """Valid vCard 3.0 with CRLF endings, folded lines, and tappable social profiles."""
    data = card.build_vcard(profile)
    assert data.endswith(b'\r\n') and b'\n' not in data.replace(b'\r\n', b'')
    assert all(len(line) <= 75 for line in data.split(b'\r\n'))
    lines = unfold(data)
    assert lines[:2] == ['BEGIN:VCARD', 'VERSION:3.0'] and lines[-2] == 'END:VCARD'
    assert 'X-SOCIALPROFILE;TYPE=linkedin:' + profile['linkedin'] in lines
    assert 'X-SOCIALPROFILE;TYPE=github:' + profile['github'] in lines
    assert any(line.startswith('NOTE:' + card.vcard_escape(profile['contactNote'])) for line in lines)


def test_main_builds_into_card_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """main() writes index.html and contact.vcf from a copy of the card directory."""
    shutil.copytree(card.CARD, tmp_path / 'card')
    monkeypatch.setattr(card, 'CARD', tmp_path / 'card')
    monkeypatch.setattr(sys, 'argv', ['build-contact-card.py'])
    (tmp_path / 'card' / 'index.html').unlink()
    card.main()
    assert (tmp_path / 'card' / 'index.html').read_text(encoding='utf-8').startswith('<!doctype html>')
    assert (tmp_path / 'card' / 'contact.vcf').read_bytes().startswith(b'BEGIN:VCARD')


def test_committed_outputs_are_up_to_date(profile: dict) -> None:
    """Committed index.html and contact.vcf match what the generator produces."""
    template = (card.CARD / 'template.html').read_text(encoding='utf-8')
    page = card.render_page(profile, template, card.asset_version(card.CARD / 'card.css'), card.asset_version(card.CARD / 'card.js'))
    assert (card.CARD / 'index.html').read_text(encoding='utf-8') == page, 'Run python3 scripts/build-contact-card.py'
    assert (card.CARD / 'contact.vcf').read_bytes() == card.build_vcard(profile), 'Run python3 scripts/build-contact-card.py'
