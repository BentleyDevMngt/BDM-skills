---
name: bdm-consultancy-agreement
description: "Draft a BDM Consultancy Agreement (Form 105) appointing a consultant to a project, from the consultant's fee proposal. Trigger on 'prepare/draft a consultancy agreement', 'consultancy fee agreement', 'fee agreement for [consultant]', 'Form 105', 'appoint [consultant] for [project]', 'engage the structural/civil/services engineer', 'put [consultant]'s fee on our terms', or whenever a consultant fee proposal, fee submission or fee variation letter is handed over with a request to formalise the appointment. Produces a DRAFT .docx built on the current controlled Form 105, with Annexure 1 schedule populated and Annexure 2 carrying the scope, exclusions, fee stages and rates transcribed from the proposal. Held for Director sign-off — never issued, never PDF'd. NOT for head contracts (AS4000 / AS4902), subcontracts, purchase orders, Heads of Agreement or deeds of novation."
---

# BDM Consultancy Agreement (Form 105)

Formalises a consultant appointment on **BDM's terms**, not the consultant's. The whole
point of the form is Annexure 1 Items 13 and 14: the Agreement takes precedence over the
consultant's proposal and over the standard conditions inside it.

## 1. Always start from the controlled template

**Use only:**

```
Standard - Documents\BDM TEMPLATES\Working Copy\100 Development Management\
  105-Consultancy_Agreement_Simple_R<latest>_<YYYY-MM>.docx
```

Glob `105-Consultancy_Agreement_Simple_R*.docx` and take the highest revision. Never take
the newest file by date — check the `R` number.

**Do not use** any consultancy agreement sitting in
`Standard - Documents\Contracts\Consultant Agreements\`. Those are historical working
drafts and superseded redlines. As at Aug 2026 that folder held
`Consultancy_Agreement_TEMPLATE_REDLINE_2026-05-26.docx`, an R1-era draft with live review
comments and **Aptos** as its default font — a breach of the R3 brand standard (Calibri
only). Building from it produced an off-brand agreement carrying an R1 header. If a file
there looks like the right template, it isn't; go to the Working Copy.

Verify before populating: `word/styles.xml` default font is **Calibri**, and `header1.xml`
carries the revision you expected.

## 2. Confirm the Principal before drafting

The contracting Principal is a fact, not an inference. Consultant proposals are routinely
addressed to the PM, the development manager, or the wrong group entity. Establish it from
BDM's own records — invoices, prior executed agreements, the project summary — and if two
sources disagree, **ask one sharp question and wait**. Never guess a party name into a
contract.

Capture: full legal name, ACN/ABN, registered office. Same for the consultant — take the
entity name from the signature block of their proposal, not the letterhead prose.

## 3. Populate Annexure 1

Placeholders are square-bracketed and listed in `references/form-105-idiom.md`. Notes on
the ones that need judgement:

- **Item 2 Commencement** — if the consultant has already been directed to proceed, state
  the direction and its date, and note clause 3.3 applies (it back-captures work already
  started). Don't leave "To be agreed at each stage" when there's a real date.
- **Item 3 Completion** — set a real date against the design/construction programme where
  one exists. Flag it if you can't.
- **Item 6 Personnel** — name the individuals the consultant is committing, with roles.
  Clause 2(g) is unenforceable without them.
- **Item 11 Insurances** — check the consultant's PI certificate is current. An expired
  certificate is a pre-execution blocker under clause 4.2; say so.
- **DOCUMENT STATUS** — `DRAFT — for Director review, not for issue`.
- Anything you genuinely cannot source, leave as `[... — to be confirmed]` and list it in
  the hand-back. Never invent an email, project number or date.

## 4. Build Annexure 2 — don't just staple the proposal

The template says "attach the consultant's proposal". Attaching alone is weak: it leaves
the consultant's own conditions doing the work. Transcribe the substance into Annexure 2
so the Agreement stands on its own, then attach the proposal behind it.

Structure:

- Opening note naming the proposal reference and date, and stating this Annexure prevails
  where the two differ (Annexure 1 Items 13 and 14).
- **A. Scope of Services** — a short project description, then the scope bullets.
- **B. Exclusions and Clarifications** — every exclusion from the proposal, verbatim in
  substance. These are what BDM is accepting; don't summarise them away.
- **C. Fees** — stage table, with a TOTAL row. Rate-based and unit-based items get their
  basis in the fee column, not a dollar figure.
- **D. Schedule of Rates** — the full rate card, with its effective date and the annual
  adjustment right.
- **E.** Line directing the proposal to be attached immediately following.

XML idiom for the tables and headings: `references/form-105-idiom.md`.

## 5. Verify before hand-back

Run `references/verification-checklist.md`. Non-negotiable: fee stages must sum to the
stated total, and every rate, ABN/ACN, reference number and date must match the source
document character-for-character. Check the rendered file, don't trust the XML.

## 6. Hand back as a draft

- **.docx only. No PDF.** A draft PDF reads as issuable. Render to images for your own
  visual check, then delete them.
- Save to the project's `00_ai_sandbox`, not the contract admin folder — that's for the
  executed document.
- Report the open commercial points plainly: unresolved fee movements, expired insurances,
  fields you couldn't source. If the fee is still being negotiated, say the figure is
  drafted from the last written acceptance and shouldn't be executed until it's closed.
- BDM drafts and recommends; Andrew or the Senior PM decides and issues. Never send.
