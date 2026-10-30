<#
build_certificate.ps1 - BDM Progress Certificate builder (Excel COM, Windows).

For PCs with Excel and no Python. Same job as build_certificate.py:
takes the controlled template + a project/claim config (JSON) and produces
  - the populated .xlsm (saved by Excel, so branding and calcChain stay intact)
  - a PDF of tabs 01-04 only, with -Pdf (signed-off certificates only)
and verifies the net incl GST equals the builder's tax invoice.

Layouts supported (see references/template_map.md):
  fixed_price -> Form 335 R6+   (335-Progress_Certificate_R6_2026-09.xlsm)
  cost_plus   -> Form 335a R1+  (335a-Progress_Certificate_Cost_Plus_R1_2026-10.xlsm)

Keep this file ASCII-only. Windows PowerShell 5.1 reads a BOM-less script as
ANSI, so an em dash or curly quote in a string literal arrives corrupted.

Usage:
  powershell -NoProfile -ExecutionPolicy Bypass -File build_certificate.ps1 `
    -Template <335 .xlsm> -Config <config.json> -OutDir <claim folder> [-Pdf]

No PDF is written without -Pdf. A certificate awaiting sign-off is never PDF'd:
a PDF reads as an issued instrument.
#>
param(
  [Parameter(Mandatory = $true)][string]$Template,
  [Parameter(Mandatory = $true)][string]$Config,
  [Parameter(Mandatory = $true)][string]$OutDir,
  [switch]$Pdf
)
$ErrorActionPreference = 'Stop'

function Fail($msg) { Write-Output ("ABORT: " + $msg); exit 2 }
function Num($v) { if ($null -eq $v -or "$v" -eq '') { return 0.0 } return [double]$v }
function OADate($s) { return ([datetime]::ParseExact($s, 'yyyy-MM-dd', $null)).ToOADate() }

# All cell writes go through these two. PowerShell caches the COM binding per call site, so a
# plain `$range.Value2 = $x` that sees a string and then a double (or the reverse) throws
# "Unable to cast" / "Specified cast is not valid". InvokeMember bypasses that cache.
function SetV($ws, $addr, $v) {
  $rg = $ws.Range($addr)
  [void]$rg.GetType().InvokeMember('Value2', [Reflection.BindingFlags]::SetProperty, $null, $rg, @($v))
}
function SetF($ws, $addr, [string]$f) {
  $rg = $ws.Range($addr)
  [void]$rg.GetType().InvokeMember('Formula', [Reflection.BindingFlags]::SetProperty, $null, $rg, @($f))
}

# ------------------------------------------------------------------ layouts
$LAYOUTS = @{
  fixed_price = @{
    form = '335'; namePattern = '^335-Progress_Certificate_R(\d+)_'; minRev = 6
    # 03 Trade Breakdown
    tradeRows = 14..45; psRows = 51..57; varRows = 63..70
    colValue = 'C'; colVariance = $null; colPrev = 'E'; colToDate = 'G'; colThis = 'H'; colToComplete = 'I'
    headers = @{ C13 = 'CONTRACT PRICE'; E13 = 'PREV CLAIMED'; G13 = 'CLAIMED TO DATE'; H13 = 'THIS CLAIM'
                 C50 = 'PS ALLOWANCE'; C62 = 'APPROVED VALUE' }
    retCell = 'G76'; tradeSub = 'G46'; varSub = 'G71'; valueSub = 'C46'
    # 02 Certificate
    certNo = 'F6'; valDate = 'F5'; prevNet = 'F27'; netEx = 'F28'; gst = 'F39'; netIncl = 'F40'
    adjSum = 'F14'; certFooter = 'B50'
    certLabels = @{ B27 = 'Less: Previous Net Recommendation for Payment'; B40 = 'Net Sum Recommended for Payment (incl GST)' }
  }
  cost_plus = @{
    form = '335a'; namePattern = '^335a-Progress_Certificate_Cost_Plus_R(\d+)_'; minRev = 1
    tradeRows = 14..45; psRows = 51..57; varRows = 63..70
    colValue = 'C'; colVariance = 'D'; colPrev = 'G'; colToDate = 'I'; colThis = 'J'; colToComplete = 'K'
    headers = @{ C13 = 'ORIGINAL BUDGET'; D13 = 'VARIANCE'; E13 = 'CURRENT BUDGET'; G13 = 'PREV CLAIMED'; I13 = 'CLAIMED TO DATE' }
    retCell = 'I76'; tradeSub = 'I46'; varSub = 'I71'; valueSub = 'C46'
    certNo = 'F6'; valDate = 'F5'; prevNet = 'F28'; netEx = 'F29'; gst = 'F40'; netIncl = 'F41'
    adjSum = 'F15'; certFooter = 'B51'
    certLabels = @{ B28 = 'Less: Previous Net Recommendation for Payment'; B41 = 'Net Sum Recommended for Payment (incl GST)' }
  }
}
$KEEP = @('01 Cover Letter', '02 Certificate', '03 Trade Breakdown', '04 Cashflow Forecast')

# ------------------------------------------------------------------ config + preflight
if (-not (Test-Path $Template)) { Fail "template not found: $Template" }
$cfg = Get-Content $Config -Raw -Encoding UTF8 | ConvertFrom-Json

if (-not $cfg.contract_form) {
  Fail ("'contract_form' is mandatory and has no default. Read the EXECUTED contract and set it, " +
        "e.g. 'Amended AS4000-1997'. A silent default put the wrong edition on two issued certificates.")
}
$ctype = "$($cfg.contract_type)"
if (-not $LAYOUTS.ContainsKey($ctype)) {
  Fail "'contract_type' must be 'fixed_price' or 'cost_plus' (got '$ctype'). Read it off the executed contract."
}
$L = $LAYOUTS[$ctype]
$tname = Split-Path $Template -Leaf
$m = [regex]::Match($tname, $L.namePattern)
if (-not $m.Success) {
  if ($ctype -eq 'cost_plus') {
    Fail ("cost_plus needs the controlled Form 335a. Form 335 has no VARIANCE / CURRENT BUDGET columns, " +
          "so a cost-plus claim cannot be certified on it. Template given: $tname")
  }
  Fail "fixed_price needs Form 335 (335-Progress_Certificate_R6+). Template given: $tname"
}
if ([int]$m.Groups[1].Value -lt $L.minRev) {
  Fail "Form $($L.form) R$($m.Groups[1].Value) is older than the R$($L.minRev) layout this builder maps. Use the latest Working Copy revision."
}
if ($Template -match '\\Drafts for Review\\') {
  Fail ("Form $($L.form) at this path is an unreleased draft (Drafts for Review). Build from the " +
        "released form in Working Copy. Hold the certificate and tell the user.")
}
if ($null -ne $cfg.builders_margin) {
  Fail ("'builders_margin' is not supported from R6: the template has no margin row (old I56 is now a " +
        "provisional-sum row). Carry margin as a trade line exactly as the builder claims it.")
}
$trades = @($cfg.trades); $ps = @($cfg.provisional_sums | Where-Object { $_ }); $vars = @($cfg.variations | Where-Object { $_ })
if ($trades.Count -gt $L.tradeRows.Count) { Fail "$($trades.Count) trade lines; template holds $($L.tradeRows.Count). Extend the template (template change) and flag." }
if ($ps.Count -gt $L.psRows.Count) { Fail "$($ps.Count) provisional sums; template holds $($L.psRows.Count)." }
if ($vars.Count -gt $L.varRows.Count) { Fail "$($vars.Count) variations; template holds $($L.varRows.Count). Extend the template and flag." }
foreach ($v in $vars) {
  $st = "$($v.car_status)"
  if ($st -eq '') { Fail "variation '$($v.desc)' has no car_status. Every variation line is checked against the CAR (SKILL.md step 4a)." }
  if ($st -ne 'Approved' -and ((Num $v.todate) -ne 0 -or (Num $v.value) -ne 0)) {
    Fail "variation '$($v.desc)' is $st in the CAR but carries a value or claimed-to-date. Pending/rejected certify at nil."
  }
}

# ------------------------------------------------------------------ build
New-Item -ItemType Directory -Force $OutDir | Out-Null
$base = "$($cfg.output_basename)"
if ($base -match 'DRAFT') { Fail "output_basename must not carry DRAFT (CLAUDE.md s5)." }
$xlsm = Join-Path $OutDir ($base + '.xlsm')
$pdfPath = Join-Path $OutDir ($base + '.pdf')
$tmp = Join-Path $env:TEMP ('bdm_pc_' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force $tmp | Out-Null
$work = Join-Path $tmp $tname
Copy-Item $Template $work

$before = @(Get-Process EXCEL -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
$xl = New-Object -ComObject Excel.Application
$xlPid = @(Get-Process EXCEL -ErrorAction SilentlyContinue | ForEach-Object { $_.Id } | Where-Object { $before -notcontains $_ })
$xl.Visible = $false; $xl.DisplayAlerts = $false; $xl.EnableEvents = $false
$xl.AutomationSecurity = 3   # msoAutomationSecurityForceDisable - never run template macros

$report = [ordered]@{}
$warnings = New-Object System.Collections.ArrayList
$exit = 0
try {
  $wb = $xl.Workbooks.Open($work, 0, $false)
  $xl.ScreenUpdating = $false
  $xl.Calculation = -4135   # manual while writing; automatic recalcs the book on every cell (minutes)
  $d = $wb.Worksheets.Item('00 Project Details')
  $cl = $wb.Worksheets.Item('01 Cover Letter')
  $c = $wb.Worksheets.Item('02 Certificate')
  $tb = $wb.Worksheets.Item('03 Trade Breakdown')
  $cf = $wb.Worksheets.Item('04 Cashflow Forecast')

  # layout fingerprint - refuse to write into a layout this map does not describe
  foreach ($k in $L.headers.Keys) {
    $got = "$($tb.Range($k).Value2)".Trim()
    if ($got -ne $L.headers[$k]) { throw "LAYOUT MISMATCH: 03!$k reads '$got', expected '$($L.headers[$k])'. Update references/template_map.md before building." }
  }
  foreach ($k in $L.certLabels.Keys) {
    $got = "$($c.Range($k).Value2)".Trim()
    if ($got -ne $L.certLabels[$k]) { throw "LAYOUT MISMATCH: 02!$k reads '$got', expected '$($L.certLabels[$k])'." }
  }

  # 00 Project Details
  $p = $cfg.project
  $client = if ($p.client) { $p.client } else { $p.principal }
  $vals = [ordered]@{ C8 = $p.name; C9 = $p.address; C10 = $p.principal; C11 = $p.contractor; C12 = $client
    C13 = "$($p.development_type)"; C14 = $(if ($p.stage) { $p.stage } else { 'Construction' })
    C15 = (Num $cfg.contract_sum); C19 = "$($cfg.revision)"; C20 = "$($cfg.status)"
    C21 = $(if ($cfg.signatory) { $cfg.signatory } else { 'For and on Behalf of' })
    C22 = $(if ($cfg.reviewer) { $cfg.reviewer } else { '[Reviewer]' })
    C25 = "$($p.builder_contact)"; C26 = "$($p.builder_address)"; C27 = "$($p.builder_email)" }
  foreach ($kv in $vals.GetEnumerator()) { SetV $d ([string]$kv.Key) $kv.Value }
  SetV $d 'C18' (OADate $cfg.issue_date)

  # 03 Trade Breakdown - clear inputs, write lines, restore THIS CLAIM / TO COMPLETE formulas on every row
  function Write-Block($rows, $items, $isVar) {
    $i = 0
    foreach ($r in $rows) {
      $it = if ($i -lt $items.Count) { $items[$i] } else { $null }
      $desc = ''; $val = 0.0; $var = 0.0; $prev = 0.0; $td = 0.0
      if ($it) {
        $desc = "$($it.desc)"; if ($isVar -and $it.ref) { $desc = "$($it.ref) - $($it.desc)" }
        $val = if ($null -ne $it.value) { Num $it.value } else { Num $it.original }
        $var = Num $it.variance; $prev = Num $it.prev; $td = Num $it.todate
      }
      SetV $tb ("A$r") $desc
      SetV $tb ("$($L.colValue)$r") $val
      SetV $tb ("$($L.colPrev)$r") $prev
      SetV $tb ("$($L.colToDate)$r") $td
      SetF $tb ("$($L.colThis)$r") "=$($L.colToDate)$r-$($L.colPrev)$r"
      if ($L.colVariance) {
        SetV $tb ("$($L.colVariance)$r") $var
        SetF $tb ("E$r") "=C$r+D$r"
        SetF $tb ("$($L.colToComplete)$r") "=E$r-$($L.colToDate)$r"
      } else {
        SetF $tb ("$($L.colToComplete)$r") "=$($L.colValue)$r-$($L.colToDate)$r"
      }
      $i++
    }
  }
  Write-Block $L.tradeRows $trades $false
  Write-Block $L.psRows $ps $false
  Write-Block $L.varRows $vars $true

  # retention (cap measured on the trade contract price, as the template does)
  $ret = $cfg.retention; $rate = Num $ret.rate
  if ($null -ne $ret.cap_pct) {
    $cap = Num $ret.cap_pct
    SetF $tb ($L.retCell) "=-MIN(($($L.tradeSub)+$($L.varSub))*$rate,$($L.valueSub)*$cap)"
    SetV $tb ('A76') ('Less Cash Retention ({0:g}% of value to date capped at {1:g}% of Contract Sum)' -f ($rate * 100), ($cap * 100))
  } else {
    SetF $tb ($L.retCell) "=-($($L.tradeSub)+$($L.varSub))*$rate"
    SetV $tb ('A76') ('Less Cash Retention ({0:g}% of value to date)' -f ($rate * 100))
  }

  # 02 Certificate
  SetV $c $L.certNo ([double]$cfg.cert_no)
  SetV $c $L.valDate (OADate $cfg.valuation_date)     # replaces the template's =TODAY()
  SetV $c $L.prevNet (-[math]::Abs((Num $cfg.previous_net)))

  # contract form wording
  $cfm = "$($cfg.contract_form)"
  SetF $cl ('B19') ('="Pursuant to cl.37.2 of the General Conditions of the ' + $cfm +
    ' Contract, Bentley Development Management issues Progress Certificate No. "&TEXT(''02 Certificate''!F6,"00")&" for "&''00 Project Details''!C11&" relating to "&''00 Project Details''!C8&"."')
  SetV $cl 'B39' ('BENTLEY DEVELOPMENT MANAGEMENT  -  SUPERINTENDENT UNDER ' + $cfm.ToUpper())
  SetV $cl ('B42') ('This Certificate is issued under ' + $cfm + ' cl.37.2. The Superintendent is required to issue this ' +
    'Progress Certificate within the time stated in the Contract of receipt of the Claim.')
  SetV $c ($L.certFooter) ('Issued under ' + $cfm + " cl.37.2. Superintendent must issue within the time stated in the Contract of receipt of the Builder's Progress Claim.")

  # 04 Cashflow Forecast (R6 layout: A month, B forecast monthly, C actual monthly, D re-forecast monthly)
  $cfo = $cfg.cashflow
  for ($r = 12; $r -le 32; $r++) { foreach ($k in 'A', 'B', 'C', 'D') { $cf.Range("$k$r").ClearContents() | Out-Null } }
  if ($cfo -and $cfo.start -and $cfo.finish) {
    $s0 = [datetime]::ParseExact($cfo.start, 'yyyy-MM-dd', $null); $f0 = [datetime]::ParseExact($cfo.finish, 'yyyy-MM-dd', $null)
    $n = ($f0.Year - $s0.Year) * 12 + $f0.Month - $s0.Month + 1
    if ($n -gt 21) { throw "programme runs $n months; 04 Cashflow holds 21 (rows 12-32). Extend the template and flag." }
    $total = if ($null -ne $cfo.total) { Num $cfo.total } else { Num $cfg.contract_sum }
    $act = @{}; foreach ($a in @($cfo.actuals | Where-Object { $_ })) { $act["$($a.month)"] = Num $a.monthly }
    $ref = @{}; foreach ($a in @($cfo.reforecast | Where-Object { $_ })) { $ref["$($a.month)"] = Num $a.monthly }
    $prevCum = 0.0
    for ($i = 1; $i -le $n; $i++) {
      $r = 11 + $i
      $mdate = (Get-Date -Year $s0.Year -Month $s0.Month -Day 1).Date.AddMonths($i - 1)
      $x = $i / $n
      $y = $x - 0.016 * $x * $x + 0.016 * $x - (1 / 3.021) * (6 * [math]::Pow($x, 3) - 9 * $x * $x + 3 * $x)
      $cum = if ($i -eq $n) { $total * $y } else { [math]::Floor($total * $y / 1000) * 1000 }
      SetV $cf ("A$r") ($mdate.ToOADate())
      SetV $cf ("B$r") ([math]::Round($cum - $prevCum, 2))
      $prevCum = $cum
      $ym = $mdate.ToString('yyyy-MM')
      if ($act.ContainsKey($ym)) { SetV $cf ("C$r") $act[$ym] }
      if ($ref.ContainsKey($ym)) { SetV $cf ("D$r") $ref[$ym] }
    }
    SetV $cf 'D75' ($s0.ToOADate())
    $cf.Range('D75').NumberFormat = 'd mmmm yyyy'
    SetV $cf ('D76') "$n months"
  } else {
    [void]$warnings.Add('cashflow.start / finish not supplied - 04 Cashflow left blank.')
  }

  $xl.CalculateFull()
  $xl.Calculation = -4105   # back to automatic so the saved file opens in automatic mode

  # ---------------------------------------------------------------- verification
  $sumTd = ($trades | ForEach-Object { Num $_.todate } | Measure-Object -Sum).Sum
  $sumPrev = ($trades | ForEach-Object { Num $_.prev } | Measure-Object -Sum).Sum
  $sumVal = ($trades | ForEach-Object { if ($null -ne $_.value) { Num $_.value } else { Num $_.original } } | Measure-Object -Sum).Sum
  $sumVarTd = ($vars | ForEach-Object { Num $_.todate } | Measure-Object -Sum).Sum
  $sumPsTd = ($ps | ForEach-Object { Num $_.todate } | Measure-Object -Sum).Sum
  if ($null -eq $sumVarTd) { $sumVarTd = 0 }; if ($null -eq $sumPsTd) { $sumPsTd = 0 }
  $base2 = ($sumTd + $sumVarTd) * $rate
  if ($null -ne $ret.cap_pct) { $base2 = [math]::Min($base2, $sumVal * (Num $ret.cap_pct)) }
  $netToDate = $sumTd + $sumVarTd - $base2
  $netThis = $netToDate - [math]::Abs((Num $cfg.previous_net))
  $incl = [math]::Round($netThis * 1.1, 2)
  $sheetIncl = [double]$c.Range($L.netIncl).Value2
  $inv = $cfg.invoice_total
  $ties = ($null -eq $inv) -or ([math]::Abs($sheetIncl - (Num $inv)) -lt 0.5)
  $agree = [math]::Abs($sheetIncl - $incl) -lt 0.5
  if ($sumPsTd -ne 0) {
    [void]$warnings.Add(("provisional sums carry {0:N2} claimed to date, but the R6 PS block does not feed the certificate " +
      "(C75/G75 = trades + variations only). Confirm with the reviewer how PS spend is certified.") -f $sumPsTd)
  }

  $errors = New-Object System.Collections.ArrayList
  # scan the PRINT AREA only: 04's hidden chart feed (J:L) holds #N/A on purpose
  $errCount = 0
  foreach ($nm in $KEEP) {
    $ws = $wb.Worksheets.Item($nm)
    $rng = $null
    try { $rng = $ws.Names.Item('Print_Area').RefersToRange } catch { }
    if ($null -eq $rng) { $rng = $ws.Range('A1:I90') }
    try {
      $bad = $rng.SpecialCells(-4123, 16)
      $errCount += [int]$bad.Count
      foreach ($e in $bad.Cells) { if ($errors.Count -ge 20) { break }; [void]$errors.Add("$nm!$($e.Address($false,$false))=$($e.Text)") }
    } catch { }
  }

  $report.check = [ordered]@{
    trade_value = $sumVal; trade_prev = $sumPrev; trade_to_date = $sumTd; variations_to_date = $sumVarTd
    retention = -$base2; net_to_date = $netToDate; net_this_claim_excl = $netThis
    net_this_claim_incl_calc = $incl; net_this_claim_incl_sheet = $sheetIncl
    adjusted_contract_sum_sheet = [double]$c.Range($L.adjSum).Value2
    invoice_total = $inv; ties_to_invoice = $ties; sheet_agrees_with_calc = $agree }

  # save the workbook (Excel writes a consistent calcChain - no stale-index trap)
  if (Test-Path $xlsm) { throw "output exists, will not overwrite: $xlsm" }
  $wb.SaveAs($xlsm, 52)

  # PDF of tabs 01-04 only, on request (-Pdf) for a signed-off certificate: hide the rest on
  # the open copy, export, close without saving
  if ($Pdf) {
    if (Test-Path $pdfPath) { throw "output exists, will not overwrite: $pdfPath" }
    foreach ($ws in $wb.Worksheets) { if ($KEEP -notcontains $ws.Name) { $ws.Visible = 0 } }
    $wb.ExportAsFixedFormat(0, $pdfPath)
  } else { $pdfPath = $null }
  $wb.Close($false)

  $report.xlsm = $xlsm; $report.pdf = $pdfPath; $report.form = "$($L.form) ($ctype)"
  $report.formula_errors = @($errors); $report.error_count = $errCount
  $report.warnings = @($warnings)
  $report.car_crosscheck = 'REQUIRED before issue - see SKILL.md step 4a'
  $report.PASS = ($ties -and $agree -and $errCount -eq 0)
  if (-not $report.PASS) { $exit = 1 }
}
catch {
  $report.PASS = $false; $report.error = "$($_.Exception.Message) (line $($_.InvocationInfo.ScriptLineNumber))"; $exit = 1
  try { $wb.Close($false) } catch { }
}
finally {
  $xl.Quit()
  [void][Runtime.InteropServices.Marshal]::ReleaseComObject($xl)
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  Start-Sleep -Milliseconds 500
  foreach ($id in $xlPid) { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue }
  Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
$report | ConvertTo-Json -Depth 5
exit $exit
