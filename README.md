# Vicky Guo — Personal site

Personal introduction, enterprise product experience, career direction, writing, and interests.

- Live URL: https://vickyguo0907.github.io/
- Original repository and history: https://github.com/VickyGuo0907/git-home-archive
- Browsable original site: [archive/](archive/)

## Preview

Run `python3 -m http.server 8000` from this directory and open http://localhost:8000/.

## Edit and publish

Edit `index.html`, `styles.css`, or `app.js`. Images and fonts live in `assets/`.
GitHub Pages publishes the root of `main`. Push a normal commit to publish updates.
After editing `styles.css` or `app.js`, bump the `?v=` hash on their links so browsers skip the cached copy:

```bash
v=$(md5 -q styles.css | cut -c1-8); sed -i '' -E "s#styles\.css\?v=[a-f0-9]+#styles.css?v=$v#" index.html projects/index.html 404.html
j=$(md5 -q app.js | cut -c1-8); sed -i '' -E "s#app\.js\?v=[a-f0-9]+#app.js?v=$j#" index.html
```
No build tools, server, or secrets are required. The `.nojekyll` file preserves static assets.

The `archive/` directory is a historical snapshot. Legacy blog and project paths are retained for existing bookmarks.
