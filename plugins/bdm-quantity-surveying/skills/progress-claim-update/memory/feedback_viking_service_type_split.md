---
name: viking-service-type-split-and-cross-source-service-resolution
description: Viking Group invoices come from one supplier entity but multiple service types (Plumbing, Electrical, Mechanical, Hydraulic, Temp Power). Skill must determine service type from Xero description or invoice line items, not just supplier name. Identified Claim 16 May 2026 when Viking Inv 1048 $79,773.58 (Mechanical) became a floating CTD row with no subtotal.
metadata:
  type: feedback
---

# Viking-style suppliers — service-type split required

**Rule:** when a supplier provides multiple service types under one trading name (Viking Group is the canonical example — they bill across Plumbing, Hydraulic, Electrical, Mechanical, and Temp Power), the skill must determine the specific service type for each invoice BEFORE assigning a CTD block. Don't pile them into a generic "Viking Group" block — there's no such Summary row, no code, and the entry stays uncategorised.

**Why:** Found on Claim 16 May 2026 v0.6. Four Viking Group invoices (Inv 1043, 1048, 1049, 1050) were inserted at CTD rows 643-646 as floating entries with descriptions "Viking Group - ; Inv NNNN" — no service-type qualifier. No subtotal row aggregates them. No Summary row for "Viking - Mechanical" was created (despite YAML's `new_ctd_blocks` already containing `Viking - Mechanical Subtotal: 04-6.3.S`). Net effect: $79,773.58 of mechanical and $14,743.28 of electrical floated in CTD but contributed $0 to Detail Sheet N. Andrew caught it during v0.6 review.

**How to apply:**

1. **For every invoice from a multi-service supplier, resolve service type before block-mapping.** Sources in priority order:
   - **Xero description** — the `Account_Transactions` xlsx Description column often says "The Viking Group - Mechanical Services" or "Viking Group - Electrical Services". Parse the segment after the dash for service keywords (Plumbing, Hydraulic, Electrical, Mechanical, Temp Power).
   - **Invoice content** — pdftotext the invoice and look for service keywords in headings or line descriptions.
   - **Invoice number prefix or pattern** — if the supplier uses different invoice-number ranges per service.
   - **Folder name** — if the user files them in subject-named subfolders (e.g. `Viking - Mechanical/`).
2. **Maintain a per-project `service_type_map` block in YAML:**
   ```yaml
   service_type_map:
     Viking Group:
       Plumbing: Viking TH Plumbing Subtotal
       Hydraulic: Viking TH Plumbing Subtotal     # same block, same code
       Electrical: Viking - TH Electrical Subtotal
       Mechanical: Viking - Mechanical Subtotal    # new block per YAML
       Temp Power: Viking - Temp Power Subtotal
   ```
3. **When mapping each Viking invoice**, look up the supplier + resolved service type, get the destination block, then proceed with insertion. If service type can't be resolved, flag the invoice for manual review rather than dropping it into a generic catch-all.

**Other multi-service suppliers likely needing the same treatment** (apply same pattern as they appear): Bespoke (Engineering, Pest, Structural), Building Connection Group (Framing materials, generic supplies), Carilla Williams (Carpentry labour, Dayworks).

**Audit log addition:** the audit should show resolved service types for any multi-service supplier on a per-invoice basis, so Andrew can sanity-check the allocation before issue.

Related: [[reference-progress-claim-update-skill]], [[feedback-xero-orphan-dedup]]
