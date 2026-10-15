# Take-off method, tolerances and the traps (R4)

## The idea the whole method rests on

An architect's PDF is **vector linework with attributes**, not a picture. Area
zones are filled polygons; wall poche sits on its own layer, often named
(`Walls - External`, `A-WALL-EXT`); balconies, paving and landscape each carry
their own fill. So areas are isolated by **selecting the right linework and
taking its corners**, not by tracing pixels. A corner taken that way is the
drawing's own corner — repeatable, auditable, and exact to the CAD model.

`scripts/vector_takeoff.py` does this. Coordinates are PDF points in the page's
display space (rotation applied) — the space Datum uses — and
m² = pt² ÷ (72 / 25.4 / N)² ÷ 10⁶, with N = stated scale × sheet factor.

Why it matters, measured (October 2026 test job — a three-level house, design-development set): the vector
method matched the architect's zones to 0.03% on every zone. The R3 raster method,
unaided, was −46% (missed an open terrace — no walls to flood against), +17%
(swept in a hatched garden) and +2.4% (no void deduction), and read the external
walls as 25–36 mm thick against 190–260 mm measured off the poche. Its *measuring*
engine on a known outline is within ±1%; its errors are in deciding what is
inside the building.

## Order of work

### 1. Read the sheet
`python3 scripts/vector_takeoff.py plans.pdf --page N` — stated scale and paper,
sheet factor, layers, grey zones with areas, and which zones match a printed
figure. Do this on every plan sheet before measuring any of them.

### 2. Scale
Stated scale × sheet factor (A1 issued at A3 = 2). Then check it against figured
dimensions — ten pairs or more across two sheets, measuring between the vector
line ends the dimension refers to. Inside 0.5% → adopt the stated value. Worse →
the sheet was rescaled on issue: stop and resolve it. Every area is wrong by the
**square** of a scale error. Cross-check a dimension chain's arithmetic against
its drawn span as well.

### 3. Reconcile the architect's schedule to the zones
`VectorSheet.zone_near(printed_m2)` finds the zone behind each printed line. A
match to ~0.05% proves the schedule was taken from that zone (ArchiCAD prints
zones 0.02–0.03% above the exported geometry — a rounding in the export, not an
error). A printed line with no zone behind it, or a zone with no line, is a
question for the architect.

### 4. Envelope — GBA
Union the enclosed zone(s) and the unenclosed zones (balconies, terraces,
carports, entries) on the level. Close drafting gaps under 0.5 m² between
adjoining zones. Voids (stair, lift, double-height) are **deductions**, kept as
separate shapes — never folded into an outline.

Where no zones are drawn, the outer outline of the external-wall poche is the
outside face. Where the poche has openings (glazed runs), close the outline
along the glazing line, not across the room.

### 5. Test the zones — overlaps and gaps
`VectorSheet.overlaps({...})`. An enclosed zone overlapping a balcony zone is a
double count in the architect's schedule. Where it happens, the balcony zone
(drawn to the glazing line) wins and the enclosed zone is cut back to it. Record
the overlap on the Basis of Measurement tab and as a finding for the architect.
(On the October 2026 test job the upper living zone ran c.500 mm past the
glazing line into the balcony zone — 4.91 m² counted twice.)

### 6. Wall thickness — measure it, do not assume it
`VectorSheet.wall_depth(envelope)` samples the outer face every 100 mm and
measures the poche depth inward: median, p10, p90 and the **solid fraction** of
the perimeter (the rest is glazing or opening). Basements run 300–350 mm against
200–260 mm above; the difference is 40–60 m² on one level. Record the value per
level on the Basis of Measurement tab.

### 7. FECA
`VectorSheet.feca(envelope, wall_mm, voids=…)`: the envelope less the external
wall band — poche attached to the outer face, no deeper than the wall. Glazed
runs carry no band (FECA runs to the glazing line). Internal walls stay in.
Islands under 0.5 m² left by internal-wall junctions are dropped. Voids out.

Check it behaves: band ≈ perimeter × solid fraction × wall thickness. The R3
uniform inward offset is **not** an acceptable substitute on a glazed façade — it
understated FECA by 1.6% and 3.5% on two levels of the test job.

### 8. UCA and the roofed test
Test each unenclosed area against the slab of the level above, and at the top
level against the roof outline. **This is the single largest source of error in
an apartment take-off.** Where an upper level is set back, the balcony below is
open to the sky: GBA, not UCA, no GFA — put it in `UNROOFED`. Watch for internal
areas carrying a balcony hatch (lift lobbies, light wells): if the region does
not touch the perimeter it is enclosed area.

### 9. Light wells
Deducted from FECA as the ASMM requires — a deduction shape on FECA, recorded
level by level.

### 10. Apartments and NSA
Use the architect's apartment zones where drawn (test them as in step 5). Where
not, segment with `takeoff_geometry.Drawing.segment()` seeded from each LIVING
label, then `snap()` the outlines. **Look at every level against the plan.**
Level totals must reconcile: **apartments + core − light well = FECA**.

### 11. Categories
Split each level by use — apartments, core & circulation, common amenity, plant &
services, car park & bike. Categories sum to FECA. Category shapes go in
`category_shapes` so the 405a can carry a category sheet.

## Raster fallback — sheets with no usable vectors

A scanned or flattened sheet has no zones, layers or poche to read. Use
`scripts/takeoff_geometry.py` (render at 300 dpi, seal, flood from outside,
erode by the wall) for that sheet, then `VectorSheet.snap()` the result onto any
vector line ends that exist. Ground floors where the building, terraces and site
paving are one surface need manual cut lines. Tolerance is the R3 tolerance —
record on the Verification tab which sheets were measured this way.

## Tolerances to report

| Situation | Expected tolerance |
|---|---|
| Vector zones / poche on a CAD export | exact to the drawing; report ±2% feasibility grade overall for drafting and convention risk |
| FECA to the inside face from poche | within ~0.5% where the poche is complete; flag levels with no wall types drawn |
| Raster fallback, plate in white space | better than ±1% |
| Raster fallback, building / terrace / paving continuous | ±3% — manual cut lines; flag for a hand check |
| UCA roofed test | slightly understated — eaves and soffits beyond the slab line are not picked up |
| Individual apartment areas | a few m² either way when segmented; level totals are firm |

## Things to flag, never to guess

- **Site area** where none is figured. Measure it from the boundary, cross-check
  across three sheets, mark it MEASURED, NOT CONFIRMED and ask for the survey plan
  or title.
- **Apartment numbering** inferred from label positions.
- **Bed / bath / study / media counts** read from room labels.
- **Missing bay numbers** in a car-park numbering run.
- **Zone overlaps, gaps or zones stopping short of the wall face** — the
  architect's schedule is then wrong, not BDM's measure.

## Cross-checks that catch real errors

- Each printed schedule line against its zone (step 3); the schedule total
  against the sum of zones less overlaps.
- Adjacent levels with near-identical plates within a few percent of each other.
- The roof plan registers with the top occupied level — same drawing origin.
- Basement GBA ÷ bays in 28–35 m²/bay.
- **GBA − wall band − unroofed ≈ GFA**; band ≈ perimeter × solid fraction × wall.
- `build_405a.py` alignment: polygon edges on the drawing's ink ≥ 85% per sheet.
- `build_405a.py` containment: no FECA / UCA outside the GBA outline.
- Site dimensions measured on three sheets agree to 0.1%.

## Where this method is not good enough

This is a **feasibility-grade** take-off from issued drawings. It is not an
architect-certified area schedule and not a surveyor's plan of subdivision.
Before figures reach a client, a lender or PAG, reconcile to the architect's own
area schedule and the survey plan, and resolve any variance above about 2% on
above-ground GBA.
