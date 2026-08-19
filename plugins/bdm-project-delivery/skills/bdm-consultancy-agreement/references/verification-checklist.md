# Verification checklist — before hand-back

Work from the rendered document, not the XML.

## Arithmetic
- [ ] Fee stages sum to the stated total. State the sum in the hand-back.
- [ ] Any negotiated adjustment reconciles (e.g. offer minus discount = accepted figure).
- [ ] Fee in the agreement matches the last **written** acceptance, not a verbal one.

## Transcription — character-for-character against the source
- [ ] Every rate in the rate card, in order.
- [ ] Consultant ABN/ACN and entity name (from the signature block).
- [ ] Principal ACN and registered office.
- [ ] Proposal reference number and date.
- [ ] Site address, lot/plan.
- [ ] Every exclusion carried across.

## Template integrity
- [ ] Header and footer show the revision you intended to use.
- [ ] `styles.xml` default font is Calibri; no `w:ascii="Aptos"` anywhere.
- [ ] No tracked changes and no comments left in the file.
- [ ] `validate.py --original <template>` passes.
- [ ] File opens clean; no orphaned headings, no split words in narrow columns.

## Commercial and status
- [ ] Consultant's PI and public liability certificates current (clause 4.2 blocks
      commencement without them).
- [ ] Every unsourced field carries a `[... — to be confirmed]` marker and appears in the
      hand-back list.
- [ ] DOCUMENT STATUS reads DRAFT.
- [ ] No PDF produced. Render images deleted.
