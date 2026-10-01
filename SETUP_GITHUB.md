# Upload and switch your GitHub website

This package contains the complete static website source: HTML, CSS, JavaScript, local images/fonts, the Next Career Path section, and a browsable copy of the original website.
No npm install or build step is required.

## 1. Upload the source to vicky-world-new

Unzip Vicky_World_Source.zip into your Downloads folder. The extracted folder is named vicky-world-source.
Use your normal authenticated Git setup on your Mac:

```bash
cd ~/Downloads
git clone https://github.com/VickyGuo0907/vicky-world-new.git
cp -R vicky-world-source/. vicky-world-new/
cd vicky-world-new
git status --short
git add .
git commit -m "Add complete personal website and legacy archive"
git push origin main
```

If you already cloned the repository, use that checkout instead and pull the latest main before copying the files.
The `cp` command includes `.nojekyll`. Keep index.html at the repository root, not inside another folder.
If using GitHub Desktop, clone vicky-world-new, copy the extracted folder's contents into that checkout, then commit and push to main. Ensure `.nojekyll` is included.

## 2. Preview the new repository with GitHub Pages

In VickyGuo0907/vicky-world-new, open Settings > Pages.
Choose Source: Deploy from a branch; Branch: main; Folder: /(root); Save.
Wait for the Pages deployment to finish, then open the URL GitHub shows.
Check both avatar modes, Next Career Path, social/email links, and the Archive link.

## 3. Keep the exact original website address

After confirming the new site works:

1. In the ORIGINAL VickyGuo0907/git-home repository, open Settings > General and rename it to git-home-archive. Do not delete it.
2. In the NEW VickyGuo0907/vicky-world-new repository, open Settings > General and rename it to git-home.
3. Check the NEW git-home repository's Settings > Pages. Confirm it publishes main / (root). Save if needed.
4. Wait for deployment. If the new URL has not deployed, trigger a fresh build from the new checkout:

```bash
git remote set-url origin https://github.com/VickyGuo0907/git-home.git
git commit --allow-empty -m "Redeploy after repository rename"
git push origin main
```

5. Verify https://vickyguo0907.github.io/git-home/ shows the NEW design. Also check /git-home/archive/, /git-home/blog/, and /git-home/projects/.
6. Only after the new site works, open git-home-archive > Settings > General > Danger Zone > Archive this repository. This preserves its source and commit history as read-only.

The rename sequence can briefly interrupt the public site. The replacement must be named git-home to retain the exact /git-home/ URL. The archived source retains both backup branches created earlier.

## Source layout

- index.html: page content and sections
- styles.css: responsive layout, colors, and animation
- app.js: interactions and avatar switching
- assets/: local portraits, avatars, fonts, and legacy assets
- archive/: exact snapshot of the old published site
- blog/ and projects/: retained legacy URLs
- .nojekyll: static GitHub Pages publishing

## Local preview

```bash
cd ~/Downloads/vicky-world-source
python3 -m http.server 8000
```

Open http://localhost:8000/.

## Current handoff status

The new repository vicky-world-new was created. Automated source uploads were interrupted; this ZIP is the complete source for your manual check-in. The original repository has not been renamed or archived, and the original GitHub Pages site remains unchanged.

## GitHub reference

https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository
