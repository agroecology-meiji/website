# Access counter patch

Apply these files on top of the latest website directory.

Changed/added files:
- `index.html`
- `en/index.html`
- `assets/js/access-log.js`
- `assets/css/style.css`
- `CLEANUP_REPORT.md`

The hidden counter sends `page=top` to the Google Apps Script Web app when the site is viewed on `agroecology-meiji.github.io`. Local previews do not increment the spreadsheet.
