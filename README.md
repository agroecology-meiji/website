# Member keyword cards patch

Apply these files on top of the current website directory.

Changed/added files:
- `members/index.html`
- `en/members/index.html`
- `assets/css/member-keywords.css`

Changes:
- Added research keywords for each undergraduate student based on `keywords.xlsx`.
- Changed the undergraduate student list from compact three-column cards to full-width profile cards matching the provided layout image.
- Added corresponding English keywords on the English members page.
- Kept the existing faculty section and global stylesheet intact.

Installation:
1. Copy `assets/css/member-keywords.css` to `assets/css/`.
2. Replace `members/index.html` and `en/members/index.html` with the patched files.
3. Commit and push to GitHub Pages.
