# JP/EN separated access counter patch

## Website-side change
Replace the existing file:
- `assets/js/access-log.js`

This update records the top pages separately:
- Japanese top page -> `page=jp`
- English top page -> `page=en`

## Apps Script change
Replace the entire `Code.gs` in Google Apps Script with:
- `apps-script/Code.gs`

After replacing the script:
1. Save the Apps Script project.
2. Run `repairSheet()` once to merge duplicated same-day rows and normalize data.
3. Deploy a new version of the Web app (`Deploy` -> `Manage deployments` -> edit/pencil -> `New version` -> `Deploy`).

## Notes
- Existing old rows recorded as `top` are not automatically split into `jp` and `en`, because their origin cannot be distinguished after the fact.
- `repairSheet()` will merge rows that have the same `date` and `page`.
