# Member keyword font update patch

Apply these files on top of the current website directory.

Changed files:
- `members/index.html`
- `en/members/index.html`
- `assets/css/member-keywords.css`

Updates:
- Keeps the undergraduate member cards in a 3-column grid on desktop.
- Keeps the undergraduate member cards in a 1-column grid on mobile.
- Matches undergraduate names to the faculty-name typography.
- Matches undergraduate research-keyword text to the faculty research-field typography.
- Updates the keywords using `keywords2.xlsx`.
- Adds a query string to the CSS link (`?v=20260629-font`) to reduce browser-cache issues.
