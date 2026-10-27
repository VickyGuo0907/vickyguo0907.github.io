"""Generate static contact assets. Deployment needs no Python or server runtime."""

import argparse
import hashlib
import html
import json
from pathlib import Path
from string import Template
from urllib.parse import quote, urlparse
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "card"
URL_KEYS = ('website', 'cardUrl', 'linkedin', 'github')
TEXT_KEYS = ('name', 'givenName', 'familyName', 'title', 'description', 'email', 'portrait',
             'portraitAlt', 'linkedinLabel', 'githubLabel', 'fileSlug', 'contactNote')


def vcard_escape(value: str) -> str:
    """Escape a vCard 3.0 text value (backslash, newline, semicolon, comma)."""
    return value.replace('\\', '\\\\').replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\\n').replace(';', '\\;').replace(',', '\\,')


def fold_line(value: str) -> str:
    """Fold a content line at 75 UTF-8 bytes (RFC 2425) without splitting characters."""
    lines, current, size = [], '', 0
    for char in value:
        encoded_size = len(char.encode('utf-8'))
        if size + encoded_size > 75:
            lines.append(current)
            current, size = ' ', 1
        current += char
        size += encoded_size
    lines.append(current)
    return '\r\n'.join(lines)


def validate_profile(profile: dict) -> None:
    """Raise ValueError unless every required field is present and well-formed."""
    missing = [key for key in URL_KEYS + TEXT_KEYS if not isinstance(profile.get(key), str) or not profile[key].strip()]
    if missing:
        raise ValueError('profile.json is missing: ' + ', '.join(missing))
    for key in URL_KEYS:
        parsed = urlparse(profile[key])
        if parsed.scheme != 'https' or not parsed.netloc:
            raise ValueError(f'{key} must be an absolute HTTPS URL')
    if any(char in profile['email'] for char in '\r\n') or '@' not in profile['email']:
        raise ValueError('A valid public email address is required')
    if not all(char.isalnum() or char in '-_' for char in profile['fileSlug']):
        raise ValueError('fileSlug may only contain letters, digits, "-" and "_"')


def regenerate_qr(card_url: str, card_dir: Path = CARD) -> None:
    """Write qr.svg and qr-metadata.json for card_url (requires qrcode==8.2)."""
    try:
        import qrcode
        import qrcode.image.svg
    except ImportError as error:
        raise SystemExit('Install scripts/requirements-card.txt to regenerate the QR code.') from error
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4, box_size=10)
    code.add_data(card_url)
    code.make(fit=True)
    code.make_image(image_factory=qrcode.image.svg.SvgPathFillImage).save(card_dir / 'qr.svg')
    metadata = {'url': card_url, 'generator': 'qrcode', 'version': '8.2', 'errorCorrection': 'M', 'quietZoneModules': 4}
    (card_dir / 'qr-metadata.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')


def check_qr_matches(card_url: str, card_dir: Path = CARD) -> None:
    """Exit if the committed QR code was generated for a different URL."""
    metadata = card_dir / 'qr-metadata.json'
    if not metadata.exists() or json.loads(metadata.read_text(encoding='utf-8'))['url'] != card_url:
        raise SystemExit('Contact URL changed: regenerate the QR with --qr before building.')


def asset_version(path: Path) -> str:
    """Return a short content hash used to bust browser caches."""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def render_page(profile: dict, template_text: str, css_version: str, js_version: str) -> str:
    """Fill the HTML template with HTML-escaped profile values."""
    escaped = {key: html.escape(value, quote=True) for key, value in profile.items() if isinstance(value, str)}
    card_url = profile['cardUrl']
    variables = {
        'name': escaped['name'], 'title': escaped['title'], 'description': escaped['description'],
        'email': escaped['email'], 'email_url': 'mailto:' + quote(profile['email'], safe='@.'),
        'website': escaped['website'], 'card_url': escaped['cardUrl'],
        'display_url': html.escape(card_url.removeprefix('https://')),
        'portrait': escaped['portrait'], 'portrait_alt': escaped['portraitAlt'],
        'social_image': escaped['website'] + 'assets/social-preview.png',
        'linkedin': escaped['linkedin'], 'github': escaped['github'],
        'linkedin_label': escaped['linkedinLabel'], 'github_label': escaped['githubLabel'],
        'file_slug': escaped['fileSlug'], 'css_version': css_version, 'js_version': js_version,
    }
    return Template(template_text).substitute(variables)


def build_vcard(profile: dict) -> bytes:
    """Return the vCard 3.0 contact as UTF-8 bytes with CRLF line endings."""
    note = profile['contactNote'] + ' LinkedIn: ' + profile['linkedin'] + ' | GitHub: ' + profile['github']
    # vCard 3.0 is intentionally used for contact-import compatibility.
    # X-SOCIALPROFILE makes the profiles tappable on iPhone; NOTE keeps them visible elsewhere.
    lines = [
        'BEGIN:VCARD', 'VERSION:3.0',
        'N:' + ';'.join([vcard_escape(profile['familyName']), vcard_escape(profile['givenName']), '', '', '']),
        'FN:' + vcard_escape(profile['name']), 'TITLE:' + vcard_escape(profile['title']),
        'EMAIL;TYPE=INTERNET,WORK:' + profile['email'], 'URL:' + profile['website'],
        'X-SOCIALPROFILE;TYPE=linkedin:' + profile['linkedin'],
        'X-SOCIALPROFILE;TYPE=github:' + profile['github'],
        'UID:urn:uuid:' + str(uuid5(NAMESPACE_URL, profile['cardUrl'])), 'NOTE:' + vcard_escape(note), 'END:VCARD',
    ]
    return ('\r\n'.join(fold_line(line) for line in lines) + '\r\n').encode('utf-8')


def main() -> None:
    """Build card/index.html and card/contact.vcf from card/profile.json."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qr', action='store_true', help='Regenerate the QR SVG (requires qrcode==8.2).')
    args = parser.parse_args()
    profile = json.loads((CARD / 'profile.json').read_text(encoding='utf-8'))
    validate_profile(profile)
    if args.qr:
        regenerate_qr(profile['cardUrl'])
    check_qr_matches(profile['cardUrl'])
    template_text = (CARD / 'template.html').read_text(encoding='utf-8')
    page = render_page(profile, template_text, asset_version(CARD / 'card.css'), asset_version(CARD / 'card.js'))
    (CARD / 'index.html').write_text(page, encoding='utf-8')
    (CARD / 'contact.vcf').write_bytes(build_vcard(profile))
    print('Generated card/index.html and card/contact.vcf' + ('; regenerated card/qr.svg' if args.qr else ''))


if __name__ == '__main__':
    main()
