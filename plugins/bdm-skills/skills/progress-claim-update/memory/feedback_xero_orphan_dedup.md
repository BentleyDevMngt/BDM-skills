---
name: xero-orphan-dedup-against-filed-invoices
description: The progress-claim-update skill is creating duplicate CTD entries when Xero descriptions vary from invoice names. Two patterns identified by Andrew during Claim 16 May 2026 run. Fix before next monthly run.
metadata:
  type: feedback
---

# Xero orphan cross-check needs better dedup against filed invoices

**Rule:** When the skill flags a Xero transaction as an orphan (RED row in CTD), it must first check whether that payment is already covered by one or more filed invoices in the same supplier section — accounting for name variations and statement-vs-individual-invoice splits. Otherwise the same payment gets recorded twice.

**Why:** Identified on Claim 16 May 2026 (v0.6 build). Two specific patterns produced duplicates:

1. **Supplier name variation between Xero and the invoice file.** Xero showed `JF Chatfeild` as the payment description — the skill flagged it as an orphan and added a RED row "JF Chatfeild - INVOICE TBC; Xero CC payment - CHASE SUPPLIER". But the actual invoice was filed under `Jesse Chatfield (Carpentry)` with reference "Bentley" — already a yellow row in the same section. Same payment recorded twice. The `xero_aliases` YAML map isn't catching this case because the Xero description doesn't include any of the recognised keywords.

2. **Single Xero payment against a supplier monthly statement, where individual invoices are filed separately.** Xero showed one payment to "Plaster Masta" (the supplier's monthly statement total) — flagged as orphan with description "Plaster Masta - INVOICE TBC; Xero CC payment - CHASE SUPPLIER". But the project folder had ALL the individual invoices that the statement covers, already filed in Paid and inserted into CTD as yellow rows. Sum of yellow rows = the statement amount. Same money recorded twice.

**How to apply (next skill iteration):**

Before flagging a Xero transaction as orphan, run two checks:

1. **Amount-equality check against single filed invoice.** If any filed invoice in the project folder has the same ex-GST amount within $1 tolerance AND falls in the same period, suppress the orphan — that's the same payment.

2. **Amount-equality check against the SUM of filed invoices for any supplier.** Group filed invoices by supplier (using the YAML's `supplier_to_ctd_block` to normalise). If the Xero amount equals the sum of one supplier's filed invoices (within $1 tolerance) and the Xero description contains any token from that supplier name OR vice versa, treat the Xero payment as a *statement payment* covering those invoices — suppress the orphan flag. Optionally annotate the supplier subtotal row "Statement paid via Xero ref X".

3. **Expand `xero_aliases` map** in the per-project YAML with the variants observed this month:
   - `jf chatfeild` → `jesse chatfield`
   - `plaster masta` → `plasta masta` (already-known supplier)
   - Add new aliases each month as fresh mismatches surface.

**Telemetry to surface:** the audit log should distinguish three orphan classes:
- *true orphan* — Xero payment with no matching invoice (genuine chase-list item)
- *name-mismatch* — amount matched a filed invoice; suppressing orphan flag; YAML alias to be added
- *statement payment* — amount matched a SUM of filed invoices; treating as supplier statement

Related: [[reference-progress-claim-update-skill]], [[feedback-quarantine-unallocated-costs]]
