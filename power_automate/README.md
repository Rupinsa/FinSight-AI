# Power Automate monthly board-pack workflow

This folder documents the cloud automation. The flow must be configured in your Microsoft 365 tenant.

## Recommended flow
1. Trigger: Recurrence, every month (e.g. first business day after close).
2. Action: Run a scheduled script or call an approved HTTPS endpoint that executes the report-generation job.
3. Action: Save `monthly_board_pack.pdf` to OneDrive or SharePoint.
4. Action: Send an email (Outlook) with the PDF attached or a secure file link.
5. Action: Log success/failure and notify the owner.

## Important implementation notes
- Power Automate cloud cannot directly execute a local Python script on a Mac.
- For a fully unattended flow, host the Python reporting job on an always-available server/cloud service, or use an approved on-premises data gateway / desktop flow where appropriate.
- Use a service account, least-privilege permissions, secure secret storage, and a test recipient first.
- Add failure handling, retry policy, run history, and a reconciliation check before sending.
- Qlik PDF export/refresh may require Qlik Application Automation, APIs, and suitable licensing. Validate your tenant's capabilities before promising an end-to-end Qlik export.
