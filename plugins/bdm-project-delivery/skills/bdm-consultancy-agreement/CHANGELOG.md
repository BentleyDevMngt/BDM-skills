# CHANGELOG — Consultancy Agreement Skill

## R1 / August 2026 — first issue

Built from a structural engineering appointment, August 2026 — a fixed fee plus rates and per-inspection units, arriving as a fee
*variation* letter under the consultant's existing contract rather than as
a fresh proposal. That is the normal starting point and the reason this skill
exists.

### What went into it

- **The template source rule.** Forms come from
  `BDM TEMPLATES\Working Copy\`, selected by highest **R** number. Nowhere else,
  and never by newest file date.
- **The Principal-entity gate.** The contracting party is established from BDM's
  own records — invoices, executed agreements, the project summary — and asked
  if sources disagree. Never inferred from the consultant's addressee line.
- **The Annexure 2 build.** Scope, exclusions, fee stages and rate card are
  transcribed into the Agreement so Items 13 and 14 have something to bite on.
- **The verification pass.** Fee stages must sum to the stated total, and every
  rate, ABN/ACN, reference and date must match the source character-for-character.

### Lessons from the pilot that are now built in

- **A look-alike template cost a rebuild.** The first cut was built from
  `Standard - Documents\Contracts\Consultant Agreements\Consultancy_Agreement_TEMPLATE_REDLINE_2026-05-26.docx`
  — an R1-era working draft, not the controlled form. Two consequences: its
  `styles.xml` default is **Aptos** against the R3 brand standard of Calibri
  only, and it still carried live tracked changes and review comments. Accepting
  those changes reproduced by hand every improvement **R2 already contained** —
  GST, Notices, Governing Law, Survival, Entire Agreement, WHS, BIF Act, the
  fitness-for-purpose softening, 6-year PI, termination for cause. Same
  substance, wrong font, wrong revision in the header. The skill now checks
  `styles.xml` and `header1.xml` before populating.
- **A file with live tracked changes or comments is a draft, not a template.**
  If the controlled form appears to need hand-editing to bring it up to date,
  the wrong file is open.
- **The consultant's addressee line is not evidence of the Principal.** The
  consultant's first letter named one entity; the later letter named another.
  Neither settled it — BDM's own invoicing records did.
- **Consultants restructure fees between revisions.** The consultant went from a
  single lump line, to a four-stage table at a higher total, then a discounted
  total. Stage
  tables must be summed, and the figure taken from the last *written*
  acceptance, not a verbal one.
- **Schema element order breaks validation silently.** In `pPr`, `spacing`
  precedes `ind`; in `rPr`, `spacing` sits between `color` and `sz`. Wrong order
  passes a rezip and fails the validator.
- **Emit runs without `rFonts`.** The controlled template carries none — Calibri
  comes from `styles.xml`. Writing an explicit font is how off-brand output
  happens.

### Deliberately not automated

The commercial call. The skill drafts the fee from the last written acceptance
and flags any movement it can see, but does not decide whether the fee is
accepted. Nor does it clear expired insurances — it reports them as a
pre-execution blocker under clause 4.2.

### Known limits

- Written for the simple Principal-based form. Not for head contracts
  (AS4000 / AS4902), subcontracts, purchase orders, Heads of Agreement or deeds
  of novation.
- Where a consultant frames the work as a variation to an existing contract,
  the skill produces a standalone agreement. If a variation instrument is
  actually wanted, that is a different document and a Director call.
- Annexure 2 transcription is only as good as the source PDF's text layer.
  Scanned proposals need checking by eye.

### Open item flagged with this release

`Standard - Documents\Contracts\Consultant Agreements\` still holds the
superseded redline plus two older simple-form copies. Recommended they be
renamed `_superseded_YYYY-MM-DD` so nobody else picks them up. Awaiting Director
sign-off — supersede by rename, never delete.
