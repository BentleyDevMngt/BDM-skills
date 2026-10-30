# Config schema — build_certificate.ps1 / build_certificate.py

A single JSON object. Claude assembles it after reading the project folder, the claim documents
and the CAR. Both builders take the same config. Save it as UTF-8.

## Fields

| Field | Type | Notes |
|---|---|---|
| `output_basename` | string | Filename stem (no extension), following the project's existing claim-file naming. Never `_DRAFT`. The builders refuse to overwrite an existing file. |
| `contract_type` | `"fixed_price"` \| `"cost_plus"` | **MANDATORY — no default.** Read it off the executed contract. Selects the form: fixed price → Form 335 R6+; cost plus → Form 335a R1+ (SKILL.md step 2). |
| `contract_form` | string | **MANDATORY — no default.** e.g. "Amended AS4000-1997". Read it off the executed contract. Drives the cl.37.2 wording in the cover letter, strapline, footnote and certificate footer. A silent `AS4000-2024` default once put the wrong edition on two issued certificates. |
| `project.name` / `address` / `principal` / `contractor` | string | Parties and site. |
| `project.client` | string | Defaults to principal. |
| `project.development_type` / `stage` | string | `stage` defaults to "Construction". |
| `project.builder_contact` / `builder_address` / `builder_email` | string | Cover-letter addressee. |
| `contract_sum` | number | Contract sum ex GST (00 Project Details C15; default cashflow total). |
| `cert_no` | int | This certificate number. |
| `valuation_date` | "YYYY-MM-DD" | "Work completed to" date. Overwrites the template's `=TODAY()` in `02!F5`. |
| `issue_date` | "YYYY-MM-DD" | Date BDM issues the certificate. |
| `previous_net` | number | Prior certificate's NET recommendation ex GST (positive; the builder negates it). |
| `revision` / `status` | string | 00 Project Details C19 / C20. Never "DRAFT". |
| `signatory` / `reviewer` | string | 00 Project Details C21 / C22. |
| `retention.rate` | number | Fraction, e.g. 0.10. |
| `retention.cap_pct` | number | Optional. Fraction of the contract price (`03!C46`), e.g. 0.05 → "10% of value to date capped at 5% of Contract Sum". Omit for a flat rate. |
| `invoice_total` | number | Builder's invoice incl GST. The build PASSES only if the certificate ties to it. |
| `trades` | list | `{"desc", "value", "prev", "todate"}` per trade line (max 32). Cost plus adds `"variance"`. |
| `provisional_sums` | list | Optional. Same shape (max 7). `value` = PS allowance. Does **not** feed the certificate in R6 — a claimed PS triggers a warning. |
| `variations` | list | Optional. `{"ref", "desc", "car_status", "value", "prev", "todate"}` (max 8). See below. |
| `cashflow.total` | number | S-curve total (defaults to `contract_sum`). |
| `cashflow.start` / `finish` | "YYYY-MM-DD" | Programme dates. Max 21 months. |
| `cashflow.actuals` | list | `[{"month":"YYYY-MM","monthly":amount}, …]` certified per month. |
| `cashflow.reforecast` | list | Optional. Same shape — re-forecast monthly (column D). |

**Removed in R3:** `builders_margin` (R6 has no margin row — the builders abort if it is present).
`original` is still read as a fallback for `value`.

## The roll-forward, per line

- `value` = column C: trade contract price, PS allowance, or the **CAR approved value** for a variation.
- `prev` = the prior certificate's **claimed to date** for that line (R6 column G; R5 and earlier column I).
- `todate` = the new certified-to-date.
- This claim (column H) computes as `todate − prev`. The sum of trade + variation `todate` must
  equal the claim's total certified-to-date ex GST.

## Variations — the CAR governs

`car_status` is the CAR's status (`Approved` / `Pending` / `Rejected` / `Superseded`), not the
builder's. Only an `Approved` line may carry a `value` or `todate`. Anything else must be nil, and
the builders abort if it isn't. A superseding CSA carries the restated value, not a delta.

## Worked example (ties to invoice $69,300)

```json
{
  "output_basename": "PC02_Test-Project_2026-09",
  "contract_type": "fixed_price", "contract_form": "Amended AS4000-1997",
  "project": {"name": "Test Project", "address": "1 Test St", "principal": "Test Principal Pty Ltd",
              "contractor": "Test Builder Pty Ltd", "builder_contact": "Pat Builder",
              "builder_address": "PO Box 1", "builder_email": "pat@test.com.au"},
  "contract_sum": 350000, "cert_no": 2, "valuation_date": "2026-09-30", "issue_date": "2026-10-10",
  "previous_net": 18000, "retention": {"rate": 0.10, "cap_pct": 0.05}, "invoice_total": 69300,
  "trades": [{"desc": "Preliminaries", "value": 100000, "prev": 20000, "todate": 50000},
             {"desc": "Earthworks", "value": 200000, "prev": 0, "todate": 30000},
             {"desc": "Concrete", "value": 50000, "prev": 0, "todate": 0}],
  "variations": [{"ref": "VO-01", "desc": "Extra stormwater pit", "car_status": "Approved",
                  "value": 10000, "prev": 0, "todate": 10000},
                 {"ref": "VO-02", "desc": "Upgrade tiles", "car_status": "Pending",
                  "value": 0, "prev": 0, "todate": 0}],
  "cashflow": {"start": "2026-08-01", "finish": "2027-05-31",
               "actuals": [{"month": "2026-08", "monthly": 20000}, {"month": "2026-09", "monthly": 70000}]}
}
```
Trades to date 80,000 + VO-01 10,000 = 90,000; retention 9,000 (under the 17,500 cap);
net to date 81,000; less previous 18,000 = 63,000 ex GST = **$69,300 incl GST**. Built and
checked on Form 335 R6 through Excel COM on 15 October 2026.

**Cost plus.** The same claim on Form 335a, with `"contract_type": "cost_plus"` and a
`"variance"` on each trade (Preliminaries +5,000, Earthworks 0, Concrete −2,000), still ties to
**$69,300**: variance moves the budget, not the value of work done. The certificate shows variance
adjustments of 3,000 and an adjusted contract sum of 363,000 (350,000 + VO-01 10,000 + 3,000).
Built and checked on Form 335a R1 through Excel COM on 30 October 2026.
