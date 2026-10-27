# Contact card

Public NFC/QR entry point: **https://vickyguo0907.github.io/card/**

This is a compact contact page in the existing GitHub Pages site: name, role, highlighted email, LinkedIn, GitHub, Save Contact, sharing and QR. A single portfolio link leads to the full introduction; biography, expertise, writing and slogans stay on the main site. It uses the site's existing portrait, locally hosted fonts, colors and verified public contact links. Save Contact, portfolio, email and professional links work without JavaScript. JavaScript adds sharing, copy-link fallback and a keyboard-accessible QR dialog. It adds no external analytics, API calls or third-party QR service.

## Edit once, generate both outputs

1. Update `profile.json` with details you intend to make public.
2. Run `python3 scripts/build-contact-card.py` from the repository root.
3. Commit the configuration and generated `card/index.html` and `card/contact.vcf` together. Styles and script hashes are refreshed automatically.

Edit `template.html` for layout changes; `index.html` is generated. Contact export uses vCard 3.0, UTF-8 and CRLF with byte-safe line folding. No phone number or address is included because none was provided. Updating this page does not silently update contact copies that someone has already saved.

## Change the entry URL or domain

Keep `/card/` stable after programming or printing. If changing `cardUrl`, regenerate the QR too:

```sh
python3 -m venv .venv-card
.venv-card/bin/python -m pip install -r scripts/requirements-card.txt
.venv-card/bin/python scripts/build-contact-card.py --qr
```

The generator rejects a URL/QR mismatch. `qr.svg` is a locally generated, black-on-white QR with four quiet-zone modules and medium error correction. `qr-metadata.json` records its URL and generator. This generation dependency is not required to visit or deploy the site.

## Program the physical NFC card

In an NFC-writing app, choose **Website / URL** and write exactly:

```text
https://vickyguo0907.github.io/card/
```

Use a standard NDEF URI record, rather than an app-specific contact or App Clip record. Read it back and confirm the stored URL. The `qr.svg` download can be printed on the card as a backup; retain the white border and avoid distortion. Keep the tag writable while testing.

## Preview and physical checks

Run `python3 -m http.server 8000` from the repository root, then open `/card/` on that server. Check desktop and small screens, QR open/close/Escape, sharing and manual copy fallback, Save Contact, and all profile links. The shared link always points to the public canonical URL, even in a local preview.

Before distributing the card, test the actual NFC tag and vCard import on iPhone/Safari and an NFC-enabled Android/Chrome device without the writing app installed. Device-specific import and native sharing need physical-device checks; desktop emulation cannot prove them. A recipient may need to confirm opening the link and saving the contact. The web page needs connectivity.

GitHub Pages publishes the committed static files when the publishing branch is updated; no server, database or secrets are required.
