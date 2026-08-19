# Finding every invoice

The job folder is always behind the mailbox. Sweeping the folder alone will miss invoices; so will
searching Outlook by keyword. Use all three passes.

## Pass A — job folder

```
05_Consultants\04_Monthly Cost Report\_Invoices\   ← where they should be
05_Consultants\02_ Fee Proposals\
05_Consultants\03_ Consultant Agreements\          ← often per-discipline subfolders
02_Project Control\                                ← BDM's own fee proposal; sometimes an Invoices folder
```

Then sweep the whole tree by filename for `*invoice*` and `*INV-*`, because invoices get filed in
the wrong place routinely. Filter by modification date since the last report — but treat mtime as
a hint, not a fact: files copied or re-saved carry a misleading date. The invoice date printed on
the PDF is the authority.

Check the obvious folder is not simply empty. An empty `Invoices` folder is a finding.

## Pass B — project email folder

`00_Email Communication\` holds `.msg` files named `yyyy-mm-dd_hhmmss_Sender_Subject`. Filter on
the date prefix.

Reading `.msg` bodies: the plain-text body stream is the easiest source. Attachments are worth
extracting when the invoice PDF is attached — that gives you the line detail the email body won't
have.

Look for: consultant invoice emails, Docusign **Completed** notifications (execution evidence),
fee proposals, and any correspondence varying scope or fee.

## Pass C — Outlook

The highest-yield searches, in order:

**1. Project reference phrase.** Invoices carry the project reference in the subject or body.
Search that exact string — and get the dash character right. An address written `1168–1170` with an
en-dash will not match a hyphen. This one query typically finds the issue email, the reminders and
the client's replies.

**2. Consultant sender domain.** Search by sender, not keyword. Keyword search across a busy
mailbox returns too much noise to be reliable.

**3. Accounting-system senders.** Invoices issued through Xero come from `messaging-service@post.xero.com`;
reminders come from `invoicereminders@post.xero.com`. **Reminder emails carry no PDF** — only the
issue email does.

**4. Client's replies.** Search by the client's address to catch payment confirmations
("all paid"). Check *which* invoice the confirmation refers to — a client confirming payment of
one project's invoice in a thread about another is an easy misread, and it changes whether you
record an invoice as outstanding.

**5. Month batches.** Where invoices are issued in a monthly run, search the batch subject pattern
for each month in the period to confirm whether a batch exists and whether this project appears in
it. A project absent from a batch is evidence there is no invoice that month — much stronger than
simply not finding one.

**Reading the PDF:** request the attachment resource on the message. That returns the invoice text
including the line detail — quantity, rate, description — which is what the audit needs. The email
body alone gives you only a total.

## BDM's own invoices — the ones that get missed

Consultant invoices arrive in the mailbox and get filed. BDM's own invoices go *out*, often
directly from the accounting system to the client, and frequently never land in the job folder or
even in the PM's inbox. They are the most commonly missing item in a cost report, and they are
usually the largest single line.

Specifics worth knowing:

- BDM bills **monthly in arrears**, in a batch covering the whole portfolio.
- Invoice numbers are **sequential across all projects**, so never search a number range — filter
  by the project reference.
- The issue email may not be in the PM's mailbox at all. Sometimes the only trace is the client's
  reply to an overdue reminder, quoting the amount.
- Where the issue email exists, read the attached PDF for the line detail — it names the stage and
  the quantity (e.g. `0.60 × $11,800`), which is what tells you which register line it belongs to.
- Where it doesn't exist, you may have only an amount. Enter it, mark the stage allocation as
  **inferred**, name what would confirm it, and say so in the report. Never present it as read.
- Check whether the current period's batch has been issued yet before concluding an invoice is
  missing — an invoice that isn't due yet isn't missing.

## Recording what you found

Produce a complete table — every invoice on the project, not just the new ones — with invoice date
(from the PDF), company, invoice number, ex-GST, incl-GST, and status. It makes the next period's
reconciliation trivial and exposes gaps in the sequence.

File anything you obtained into `_Invoices\` as `yyyymmdd_Company_invoice-number.pdf`, dated from
the invoice, not the email. Where a PDF cannot be retrieved at all, say so explicitly and name what
the user needs to do — that's an action for them, not a silent omission.

State the nil findings too: which consultants have **not** invoiced, and where you checked.
