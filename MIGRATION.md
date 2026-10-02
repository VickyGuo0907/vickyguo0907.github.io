# Migration record

The replacement is a fresh GitHub repository, initially prepared as `vicky-world-new` and renamed to `git-home` for the existing Pages address.
The original `git-home` is renamed to `git-home-archive` and archived after the replacement is verified live.

## Preserved original

- Original source commit: `f1c40bea70a72de8caa9c4da142420bbdc6f02d6`
- Original published commit: `775abda96bb69d6fe9e4dd3c1fa2a4628545f03d`
- Source backup branch in original repository: `archive/source-before-redesign-2026-09-30`
- Published backup branch in original repository: `archive/published-before-redesign-2026-09-30`
- All original published files are retained byte-for-byte under `archive/`.
- Existing blog and project paths are also retained at the root for old bookmarks.
- Original MkDocs sources and full history stay in the archived repository.

## Publication

GitHub Pages serves the root of `main` in the `vickyguo0907.github.io` user-site repository (moved from `git-home` on 2026-10-01).
Public URL: https://vickyguo0907.github.io/

## Restore

To restore the original design, make a new commit placing the contents of `archive/` at the root, keeping the archive itself intact. Do not force-push or erase history.

## Old addresses (2026-10-02)

- `404.html` on this site forwards old links: `/git-home/<path>` → `/<path>`, and `/my-git-home/...` → `/`.
- `git-home` and `my-git-home` are archived and private, kept only for their original source and history. Private repos on the free plan do not publish Pages, so the redirects above handle all old links.
- `git-home` keeps both backup branches (`archive/published-before-redesign-2026-09-30`, `archive/source-before-redesign-2026-09-30`); its `gh-pages` branch holds a superseded redirect page. `my-git-home` keeps `main` unchanged plus a superseded `redirect` branch.
- The planned rename to `git-home-archive` was not done; the original repo kept the name `git-home`.
