---
name: quarantine-unallocated-costs-at-close-out
description: When a cost can't be allocated to a budget code now (e.g. Xero residuals, untraced multi-pay components), quarantine it visibly in the workbook and log to a per-project Quarantine Register. Resolution deferred to project close-out.
metadata:
  type: feedback
---

# Quarantine unallocated costs — don't force-fit, don't delete

**Rule:** when a cost line can't be cleanly allocated to a budget code or supplier — e.g. an Xero "Multi-Pay" residual that doesn't match any pick-up, an orphan payment with no invoice, a fee Xero is silent on — DO NOT (a) silently absorb it into a nearby code, (b) force-allocate to keep the math clean, or (c) delete it. Quarantine it visibly until close-out.

**Why:** Andrew's standing instruction on Claim 16 (23 May 2026). The $2,780.90 Multi-pay residual at 818 South Pine Road could not be matched to any of the 790 invoice PDFs after exhaustive search; rather than fudging, Andrew chose to park it for end-of-project reconciliation. The pattern: unallocated costs go on a register and get resolved when there's time and complete visibility (final Xero recon, supplier statement reviews, etc.), not under monthly-claim time pressure.

**How to apply:**

1. **In the workbook (Summary + CTD Breakdown)**
   - Append `(QUARANTINED — allocate at project close-out)` to the description in both tabs.
   - Set the budget-code cell to `QUARANTINE` so the SUMIF chain naturally excludes it from per-code aggregations.
   - Apply BDM Orange Lighter 80% fill (`FFFCE4D6`) to the row — same convention as new/pending items in the variation register.
   - Add an Excel cell comment explaining the residual: amount ex/inc GST, what was searched, why quarantined, when to revisit.

2. **In the project folder**
   - Maintain a `202415_QuarantineRegister.md` (or similar) under the project's Alfred working folder.
   - One entry per quarantined item: amount, source row, what was checked, likely cause, resolution path at close-out.

3. **Reconciliation impact**
   - The quarantine isolates the item from per-code Detail Sheet aggregation but leaves it in the Summary totals (Paid + Unpaid). This is the right behaviour — the cost IS real (the bank moved money), it just isn't yet tied to a code.
   - Expect a known gap between Summary grand total and Detail Sheet code-aggregated total equal to the quarantined sum. Call this out explicitly in the audit memo.

4. **Resolution at close-out**
   - Pull the original Xero transaction (drill into the Spend Money / multi-pay line) to see the actual bank-side breakdown.
   - Allocate the residual to the correct code (or fix the Xero entry), remove the orange fill, restore the budget code, close the register entry.

Related: [[reference-progress-claim-update-skill]] — the skill should preserve quarantine markers across monthly rolls (don't strip the orange fill or QUARANTINE F-column when re-running on a fresh month folder).
