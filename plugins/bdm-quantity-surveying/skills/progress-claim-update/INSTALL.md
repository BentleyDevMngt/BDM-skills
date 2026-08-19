# INSTALL — progress-claim-update R4

1. Save the `.skill` file when prompted (Cowork will offer to add it to your account).
2. Verify the extraction rules on install:

       python3 scripts/selftest.py          # expect ALL PASS

3. Before issuing any claim, run the reconciliation gate:

       python3 scripts/reconcile.py --claim DRAFT.xlsx --xero ACCOUNT_TRANSACTIONS.xlsx \
           --period-start DD/MM/YYYY --period-end DD/MM/YYYY --prior ISSUED_PRIOR_CLAIM.xlsx

   Exit 0 = RECONCILED. Exit 1 = variance; do not issue.

Project configs live in `projects/`. `202415_south_pine_rd.yaml` is current as at
27 July 2026 and carries four proposed new blocks awaiting Director sign-off.
