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


def vcard_escape(value):
    return value.replace('\\', '\\\\').replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\\n').replace(';', '\\;').replace(',', '\\,')


def fold_line(value):
    # RFC 2425-style folding, counting UTF-8 bytes without splitting characters.
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qr', action='store_true', help='Regenerate the QR SVG (requires qrcode==8.2).')
    args = parser.parse_args()
    profile = json.loads((CARD / 'profile.json').read_text(encoding='utf-8'))
    for key in ('website', 'cardUrl', 'linkedin', 'github', 'writing'):
        parsed = urlparse(profile[key])
        if parsed.scheme != 'https' or not parsed.netloc:
            raise ValueError(f'{key} must be an absolute HTTPS URL')
    if any(char in profile['email'] for char in '\r\n') or '@' not in profile['email']:
        raise ValueError('A valid public email address is required')
    card_url = profile['cardUrl']
    qr_meta = CARD / 'qr-metadata.json'
    if args.qr:
        try:
            import qrcode
            import qrcode.image.svg
        except ImportError as error:
            raise SystemExit('Install scripts/requirements-card.txt to regenerate the QR code.') from error
        code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4, box_size=10)
        code.add_data(card_url)
        code.make(fit=True)
        code.make_image(image_factory=qrcode.image.svg.SvgPathFillImage).save(CARD / 'qr.svg')
        qr_meta.write_text(json.dumps({'url': card_url, 'generator': 'qrcode', 'version': '8.2', 'errorCorrection': 'M', 'quietZoneModules': 4}, indent=2) + '\n', encoding='utf-8')
    if not qr_meta.exists() or json.loads(qr_meta.read_text())['url'] != card_url:
        raise SystemExit('Contact URL changed: regenerate the QR with --qr before building.')

    escaped = {key: html.escape(str(value), quote=True) for key, value in profile.items() if isinstance(value, str)}
    email_url = 'mailto:' + quote(profile['email'], safe='@.')
    variables = {
        'name': escaped['name'], 'given_name': escaped['givenName'], 'title': escaped['title'],
        'description': escaped['description'], 'email': escaped['email'], 'email_url': email_url,
        'project_email_url': email_url + '?subject=' + quote('Project inquiry for ' + profile['name']),
        'website': escaped['website'], 'work_url': escaped['website'] + '#work',
        'card_url': escaped['cardUrl'], 'display_url': html.escape(card_url.removeprefix('https://')),
        'portrait': escaped['portrait'], 'portrait_alt': escaped['portraitAlt'],
        'social_image': escaped['website'] + 'assets/social-preview.png',
        'linkedin': escaped['linkedin'], 'github': escaped['github'], 'writing': escaped['writing'],
        'expertise': ''.join('<li>' + html.escape(item) + '</li>' for item in profile['expertise']),
        'css_version': hashlib.sha256((CARD / 'card.css').read_bytes()).hexdigest()[:8],
        'js_version': hashlib.sha256((CARD / 'card.js').read_bytes()).hexdigest()[:8],
    }
    document = Template((CARD / 'template.html').read_text(encoding='utf-8')).substitute(variables)
    (CARD / 'index.html').write_text(document, encoding='utf-8')

    note = 'Practical software, automation, and AI. LinkedIn: ' + profile['linkedin'] + ' | GitHub: ' + profile['github']
    # vCard 3.0 is intentionally used for contact-import compatibility.
    lines = [
        'BEGIN:VCARD', 'VERSION:3.0',
        'N:' + ';'.join([vcard_escape(profile['familyName']), vcard_escape(profile['givenName']), '', '', '']),
        'FN:' + vcard_escape(profile['name']), 'TITLE:' + vcard_escape(profile['title']),
        'EMAIL;TYPE=INTERNET,WORK:' + profile['email'], 'URL:' + profile['website'],
        'UID:urn:uuid:' + str(uuid5(NAMESPACE_URL, card_url)), 'NOTE:' + vcard_escape(note), 'END:VCARD',
    ]
    (CARD / 'contact.vcf').write_bytes(('\r\n'.join(fold_line(line) for line in lines) + '\r\n').encode('utf-8'))
    print('Generated card/index.html and card/contact.vcf' + ('; regenerated card/qr.svg' if args.qr else ''))


if __name__ == '__main__':
    main()
