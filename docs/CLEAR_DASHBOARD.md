# Permanently Clear the Axeom Dashboard

This action is intentionally different from "restore the October 6 challenge baseline."

## What the owner sees
1. Open **Manage Data → Reset Business Data**.
2. Review the actual, live record totals.
3. Enter **DELETE ALL BUSINESS DATA** exactly.
4. Accept the final browser warning and authorize using the owner PIN.
5. On success, the dashboard shows zero clients, money, leads, bookings, messages and requests.
6. Upload new CSVs to build a new workspace from scratch.

## Required secure setup
The reset button remains disabled unless the Vercel deployment has non-default environment variables:
- `OWNER_PIN`: a private, unique value at least 6 characters long.
- `SECRET_KEY`: an unpredictable secret at least 32 characters long.

Add both to the Vercel project settings and redeploy. Do not commit these secrets, send them in chat, or reuse the repo's documented demonstration values.

## Data and irreversibility
The backend atomically deletes records from the business tables and verifies zero rows before committing. It preserves only the SQL table structure and `app_settings` metadata that prevents initial Pack 01 data from reappearing on restart. There is no automatic re-seeding, no auto-undo and no system-managed backup created by this button.

**Back up your Neon database externally before using it if you might ever need these records again.** The reset does not remove GitHub repository files, previous backups, Neon project history, or external copies. It changes only the database used by the running dashboard.

An exact confirmation phrase, secure owner session, fresh preview record count, and a final warning are required. Concurrent changes cause a safe refusal, not a partial wipe. No records are deleted by deployment or by CI.

## Verification and troubleshooting
- Refresh `/api/manage/reset/preview` to see the current counts.
- If the button is disabled, verify secure environment variables in Vercel and redeploy.
- If the preview count changed, refresh the page and repeat the confirmation.
- A successful response includes `cleared: true`, `deleted_records`, and `table_counts_after` where every business table is zero.
- `/api/state` then reports `workspace_cleared: true` and zero KPI counts.
- Resetting cannot delete local files from a visitor's browser or backups stored outside the application database.

The only automatic test of the destructive PostgreSQL operation runs against a disposable **localhost** container, never a real Neon instance.
