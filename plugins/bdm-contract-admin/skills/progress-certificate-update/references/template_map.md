# Form 335 / 335a template map and roll-forward logic

Verified cell by cell against the workbooks on 15 October 2026. Both builders check the
column headings and certificate labels below before writing and abort on any mismatch. When a
new revision is released, re-verify this map before building on it.

| Contract type | Form | Controlled file | Status |
|---|---|---|---|
| Fixed price (lump sum) | **335 R6** | `Working Copy\300 Project Management - Contract Delivery\335-Progress_Certificate_R6_2026-09.xlsm` | Released 25/9/26 under CN-2026-049 |
| Cost plus | **335a R1** | `Drafts for Review\CN-2026-049\v2_fixed_price_and_cost_plus\335a-Progress_Certificate_Cost_Plus_R1_2026-09.xlsm` | **Not released.** Held for Andrew Bentley's sign-off on the form number. There is no controlled cost-plus form until it reaches Working Copy |

Tabs, the same in both (the issued PDF is **01, 02, 03 and 04 only**):

| Tab | Role |
|---|---|
| 00 Project Details | Single source of truth. Every other tab pulls from here. Not issued. |
| 01 Cover Letter | AS4000 cl.37.2 cover. Takes the cert no. from `02!F6` and the parties from 00. |
| 02 Certificate | The signed certificate (recommended payment). |
| 03 Trade Breakdown | The engine: trade analysis, provisional sums, variations, retention. |
| 04 Cashflow Forecast | Forecast vs actual cashflow and chart. |
| SINGLE STAGE (3) | Legacy helper. Not issued. |

R6 has **no** `CashflowInput` or `Data` tab and **no** `scurve()` macro. Those belonged to R4/R5.

---

## Form 335 R6 — fixed price

### 03 Trade Breakdown — columns
```
A Description   C Value   D %Prev(=E/C)   E Prev Claimed   F %Done(=G/C)
G Claimed to Date   H This Claim(=G-E)   I To Complete(=C-G)
```
Column C heading by block: **CONTRACT PRICE** (trades), **PS ALLOWANCE** (provisional sums),
**APPROVED VALUE** (variations). R5's VARIANCE and CURRENT BUDGET columns are gone, so there is
nothing between the value and the claim columns.

| Block | Rows | Sub-total row |
|---|---|---|
| Trades | 14–45 (32 lines) | 46 (`C46` contract price, `E46`, `G46`, `H46`, `I46`) |
| Provisional sums | 51–57 (7 lines) | 58 |
| Variations | 63–70 (8 lines) | 71 |
| Trades + variations | — | 75 |
| Cash retention | — | `G76` |
| Sub-total / GST / total | — | 78 / 79 / 80 |

**Roll-forward:**
- `E` (prev claimed) := the prior certificate's **claimed to date** for that line. On an R6
  prior certificate that is column **G**. On an R5 or earlier prior certificate it is
  column **I**. Read the right one.
- `G` (claimed to date) := this claim's certified-to-date.
- `C` (value): the trade's contract price, the PS allowance, or, for a variation, the
  **CAR approved value**. A pending or rejected variation carries nil in C and G.
- `H` and `I` compute.

**Template defects the builders correct on every build:**
- **THIS CLAIM is hard-coded `0` on 46 of 49 input rows.** Only rows 14, 51 and 63 carry
  `=G-E`. Left alone, the THIS CLAIM column and its sub-totals under-report the claim. The
  builders write `=G-E` (and `=C-G`) on every input row.
- **Provisional sums do not feed the certificate.** Rows 75–80 and `02!F12`/`F20`/`F21` take
  trades + variations only. If the builder claims against a PS, the builders warn. Confirm with
  the reviewer how PS spend is to be certified.

**Retention** `G76`: `=-MIN((G46+G71)*rate, C46*cap)` for "10% of value to date capped at 5% of
Contract Sum" (the template default and label). The cap is measured on `C46`, the trade contract
price, which is also the certificate's Contract Sum (`02!F12`). Flat rate: `=-(G46+G71)*rate`.

**No builder's margin row.** R4/R5's `I56` margin cell does not exist; in R6 `I56` is a
provisional sum's TO COMPLETE formula. Margin is carried as a trade line, as the builder claims it.
The builders refuse a `builders_margin` config key.

**No unfixed-materials row.** The R4 guard that rewrote `02!F28` from `='03 Trade Breakdown'!G88*-1`
to `=-(G88-G58)` has nothing to act on in R6. The lesson stands for any revision that brings the
row back: prior unfixed materials must be added back, or the certificate deducts them twice.
Left unfixed, that defect over-certified one draft by $1,533,071.32 ex GST.

### 02 Certificate — chain
```
F5  Valuation date (template =TODAY(); the builders overwrite it)   F6 Certificate No.
F12 Contract Sum                 = 03!C46
F13 Plus: Approved Variations    = 03!C71
F14 Adjusted Contract Sum        = F12+F13
F15 Pending Variations (memo)    input
F20 Contract Works               = 03!G46
F21 Approved Variations          = 03!G71
F22 Pending Variations (paid on account)   input
F23 Total Value of Works Completed
F24 Less: Work Not in Accordance with Contract   input
F25 Less: Cash Retention         = 03!G76
F26 Net Value of Payment to Date = F23+F24+F25
F27 Less: Previous Net Recommendation   = -(prior net ex GST)   <- certificate-level roll-forward
F28 Net Sum Recommended (excl GST)      = F26+F27
F39 GST = F38*0.1    F40 Net incl GST = F38+F39   (must equal the builder's tax invoice)
F47 Signature date = F5          B50 contract-form footer
```
R5 → R6: the "Plus: Variance Adjustments (cost-plus)" row was deleted, so everything below
row 13 moved up one.

### 01 Cover Letter
`B17` cert no., `B19` cl.37.2 paragraph (contract form), `B22` Annexure A, `C27:C29` summary
(`=02!F38:F40`), `B39` strapline, `B42` footnote. `C1` carries "Form 335 · R6 · 2026-09".

---

## Form 335a R1 — cost plus (draft — re-verify on release)

The R5 column layout, kept for cost plus:
```
A Description   C Original Budget / Submitted Value   D Variance   E Current Budget / Approved Value (=C+D)
F %Prev   G Prev Claimed   H %Done   I Claimed to Date   J This Claim(=I-G)   K To Complete(=E-I)
```
Same row blocks as R6 (trades 14–45, PS 51–57, variations 63–70). Retention `I76`
(`=-MIN((I46+I71)*rate, C46*cap)`). Roll-forward: `G` := prior certificate's `I`; `I` := this
claim's certified-to-date.

02 Certificate keeps the variance row, so it sits one row lower than R6: `F13` approved variations
(`=03!E71`), `F14` variance adjustments (`=03!D46+03!D58`), `F15` adjusted contract sum,
`F28` previous net, `F29` net ex GST, `F40` GST, `F41` net incl GST, `F48` signature date,
`B51` footer. Cover letter summary reads `02!F39:F41`.

The builders map 335a, but refuse to build from it while the file sits in `Drafts for Review\`.

---

## 04 Cashflow Forecast (R6 and 335a)

```
A12:A32  month (21 rows)          B  forecast monthly   (input)
C        actual monthly (input — claimed months only)   D  re-forecast monthly (input)
E        forecast cumulative      F  actual cumulative   G  re-forecast cumulative   H  variance
J:L      hidden chart feed — #N/A on purpose, outside the print area. Do not delete.
Row 33   totals (E33:G33 take the MAX, not the SUM)
D75/D76  "Commence construction" date / "Construction period" in the notes
```
The builders fill A from `cashflow.start`, B from the BDM S-curve, C from `cashflow.actuals`,
and D from `cashflow.reforecast` (optional). S-curve, end of month i of n:
```
x = i / n
y = x - 0.016x^2 + 0.016x - (1/3.021)(6x^3 - 9x^2 + 3x)
cumulative = total*y, floored to $1,000 except the final month (= total)
monthly B = cumulative(i) - cumulative(i-1)
```
A programme longer than 21 months needs the template extended — the builders abort and say so.
