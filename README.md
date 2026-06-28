# Deduplicated access counter patch

This patch keeps the existing `daily_access` format and adds a hidden deduplication sheet named `daily_access_clients`.

## Files

- `assets/js/access-log.js`
  - Replace the existing website file with this version.
  - Japanese top page sends `page=jp`.
  - English top page sends `page=en`.
  - A browser-level anonymous `client_id` is stored in `localStorage` and sent to Apps Script.

- `apps-script/Code.gs`
  - Replace the entire Google Apps Script `Code.gs` with this file.
  - IMPORTANT: Replace `YOUR_SPREADSHEET_ID_HERE` with your actual Spreadsheet ID before saving.

## Spreadsheet sheets

### daily_access

Keep the current format:

```csv
date,year,month,day,page,access_count
```

### daily_access_clients

The script creates this sheet automatically when `initializeSheet()` runs:

```csv
date,page,client_id,last_access_at
```

## Setup steps

1. Replace `assets/js/access-log.js` on GitHub Pages.
2. Replace `Code.gs` in Apps Script.
3. In `Code.gs`, set the correct `SPREADSHEET_ID`.
4. Save Apps Script.
5. Run `initializeSheet()` once.
6. Run `repairSheet()` once.
7. Redeploy the Web app:
   - Deploy
   - Manage deployments
   - Edit/pencil icon
   - Version: New version
   - Deploy
8. Open the Japanese top page and confirm `page=jp` is counted once.
9. Reload the same page in the same browser and confirm the count does not increase.
10. Open the English top page and confirm `page=en` is counted once.

## Manual direct test URLs

After deployment, use test client IDs:

```text
https://script.google.com/macros/s/AKfycbyT31uXmkw1rh8MFzEmwbet3LHPDDo_-twwaTDNKzyPe9TgNCuXX9XDf5wVOYUznuLD/exec?page=jp&key=access_log&client_id=test_jp_001
```

```text
https://script.google.com/macros/s/AKfycbyT31uXmkw1rh8MFzEmwbet3LHPDDo_-twwaTDNKzyPe9TgNCuXX9XDf5wVOYUznuLD/exec?page=en&key=access_log&client_id=test_en_001
```

If you open the same URL again on the same day, the response should be `counted:false` and `daily_access` should not increase.

## Notes

- This removes duplicate counts for the same browser, same day, and same page.
- It does not perfectly identify a physical device. Chrome and Safari on the same computer are counted separately.
- If the browser's site data is deleted, a new `client_id` is generated.
