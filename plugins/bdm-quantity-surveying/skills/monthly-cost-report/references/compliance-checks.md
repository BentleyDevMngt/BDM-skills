# Invoice vs agreement audit

Run this on every invoice **before** any figure goes into the register. The point is not to find
arithmetic errors — consultants' accounts systems rarely add up wrong. The point is to find claims
that don't match what was agreed.

## Establish the governing document first

For each invoice, identify what governs it, in this order of authority:

1. **Executed consultancy agreement** (Form 105) — check it is actually executed. A Docusign
   *Completed* email, or signatures and dates in the signature block. "Viewed" is not executed.
   An agreement sitting unsigned governs nothing, however carefully drafted.
2. **Signed fee proposal / authorisation to proceed** — where no Form 105 exists.
3. **Unsigned fee proposal** — where the consultant is demonstrably working to it. Note that
   nothing is formally agreed.
4. **Nothing on file** — a finding in itself. Report it; don't infer terms from the invoice.

Where an agreement exists, its Annexure 2 (or equivalent fee schedule) is the reference, not the
consultant's original proposal — agreements routinely supersede and re-cut the proposal's stages.

## The checks

### Line exists in the agreement
Every claimed line should map to a stage, a schedule item, an engaged additional service, or an
approved variation. A line with no home is an exception, whatever its size.

Watch for **transposed or renamed descriptions** — a line whose amount is right but whose label
doesn't match the agreement. Correct today, but it causes the wrong item to be treated as complete
later. Flag it and ask the consultant to correct their template.

### Cumulative claim vs stage value
Consultants bill cumulatively: contract sum, % complete, value of work completed, less previous
claims. Two things to reconcile:

- **This claim's "previous claims" against the register's recorded to-date.** A mismatch means
  either an invoice you haven't found, or a re-claim of something already paid.
- **Value of work completed against the stage value.** Cumulative claims should never exceed the
  stage unless a variation has been approved.

### Percentage complete is supportable
A stage at 100% should have a deliverable behind it. Check the drawings register, the issue
correspondence, the meeting minutes. A concept stage claimed complete when the concept is still
being revised is the classic case.

Be proportionate — you're sanity-checking, not auditing every drawing. But a jump from 20% to 100%
in one month deserves a look.

### Omitted or unengaged scope
If a discipline or service was:
- **omitted by notice** (e.g. a variation directing omission under the agreement's variations
  clause), or
- listed in the agreement as **optional / not engaged**,

then it must not appear as a claim. Where a consultant has part-performed omitted work before the
notice, they are usually entitled to a reasonable portion — that's assessed against the notice,
not simply paid as claimed.

Equally: check the **absence** of a claim. A consultant quietly dropping omitted items from their
invoice is how you learn they've accepted the omission. That's a material fact for the register
and worth confirming in writing.

### Disbursements and pass-through costs
Each needs to trace to a clause permitting it or a written instruction. Check:
- the underlying cost is evidenced
- any administration percentage matches the agreement
- it hasn't already been claimed
- it isn't something the agreement says is included in the lump sum

Site inspections, authority fees, printing, network assessment fees and travel are the usual
suspects.

### Rates and hourly claims
Where a claim is on rates rather than lump sum, check the rate against the agreement's schedule
and that the role claimed matches the person who did the work. Rates escalate between a proposal
and an agreement more often than you'd expect.

### GST
The register runs **excluding GST**. Fee proposals frequently quote GST-inclusive totals, and some
mix the two in one document. Convert, and note where you did it — an inclusive figure entered as
exclusive overstates the commitment by 10% and is very hard to spot later.

### Payment terms and status
Note the due date and whether it's been paid. An invoice that's overdue, or one where the client
has confirmed payment of a *different* invoice in the same thread, is worth surfacing — especially
for BDM's own invoices, where nobody else is watching.

### Insurance and preconditions
When a newly signed agreement or proposal comes in, check currency of PI and PL cover against the
agreement's minimums. An expired certificate on a proposal is a precondition to appointment, not a
detail — and it will not fix itself.

## Recording the result

Report as a table before you populate:

| Invoice | Governing document | Claimed | Accords? | Exception |
|---|---|---|---|---|

Then:

- **Accords** → enter it.
- **Doesn't accord** → enter what was *claimed*, flag the exception in the cell comment and in
  the notes, and raise it in your write-up. Do not adjust the claim to fit, and do not adjust the
  approved fee to accommodate it. Both are decisions for the Director.
- **No governing document** → enter the amount, flag that nothing governs it, and recommend the
  agreement be put in place.

## Exception patterns seen in practice

- A stage priced for one month billed across several because the phase extended. Often
  contractually sound — most fee proposals let a prolonged stage increase on the monthly rate —
  but it produces a claim above the stage value and needs a variation to regularise. Show the
  over-claim as a negative remaining rather than quietly lifting the approved fee.
- Optional services invoiced as though engaged.
- Descriptions transposed between two additional-services line items.
- A disbursement appearing on the contract-sum schedule at 0% for months before it's claimed —
  easy to miss until the month it lands.
- A consultant continuing to invoice after their scope was omitted.
- Proposals predating BDM's appointment, addressed to the Principal or the architect, with
  validity periods long lapsed — the fees are real but nothing is agreed.
