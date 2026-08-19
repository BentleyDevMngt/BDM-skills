# Take-off method, tolerances and the traps

## The idea the whole method rests on

An architect's PDF is **vector linework with attributes**, not a picture. Wall
poche, balcony hatch, dimension text and site paving are each drawn on their own
layer at their own stroke colour and fill grey. So areas are isolated by
*selecting the right linework*, not by tracing pixels. That is what makes the
result repeatable and auditable rather than a hand trace.

`scripts/takeoff_geometry.py` wraps this. Work at **300 dpi** — 1 px ≈ 17 mm at
full size, which is finer than the drawing's own line weight.

## Order of work

### 1. Scale — before anything else
Compute the theoretical px/m from the stated scale and sheet size, then **measure
it** against as many figured dimension pairs as you can find (aim for 30+ across
at least two sheets). Take the median.

- Agreement inside 0.5% → adopt the **exact theoretical** value.
- Worse than that → the sheet has been rescaled on issue. Stop and resolve it.
  Every area is wrong by the *square* of a scale error.

Then cross-check a dimension **chain**: sum the figured segments and compare
against the drawn span of the same chain. Arithmetic that ties and geometry that
ties are two different checks; do both.

### 2. The envelope (GBA)
Seal the linework with a morphological close, flood-fill the space *outside* the
building from a corner of the clip box, keep the enclosed remainder. That gives
the area to the **outside face of the external walls** — which is GBA.

Set a clip box that excludes the title block, the DA approval stamp, the scale
bar and the drawing notes, or they get swept into the plate.

### 3. Wall thickness — measure it, do not assume it
Read the thickness off the **wall poche** on every level. Basement walls are
routinely 300–350 mm against 200 mm above ground, and that difference is worth
40–60 m² on a single level. Record the value used per level in the Basis of
Measurement tab.

### 4. FECA
Offset the envelope inward by the measured wall thickness. Then check the
result behaves like a perimeter band: **area lost ≈ perimeter × wall thickness**.
If it does not, the envelope has a hole or a spur in it.

Where the façade is glazed rather than solid the true offset is thinner, so a
uniform offset understates FECA slightly — of the order of 0.5–1% per level.
Say so in the reliability table rather than pretending to a precision you do not
have.

### 5. Balconies and the roofed test
Pull the balcony / terrace hatch as its own layer (`stroke_greys()` will show
you the candidate values — never assume one carries over between projects).

Then test **each** balcony geometrically against the slab of the level above,
and at the top level against the roof outline. **This is the single largest
source of error in an apartment take-off.** Where an upper level is set back,
the balcony below is open to the sky: it is GBA, it is *not* UCA, and it carries
no GFA. On a typical set-back tower that is 100–200 m² on one level.

Watch for **internal** areas carrying the same hatch — lift lobbies and light
wells often do. Test whether the region touches the building perimeter; if it
does not, it is enclosed area, not UCA.

### 6. Light wells
Deducted from FECA as the ASMM requires. Record the deduction level by level.

### 7. Apartments and NSA
Segment by wall-constrained region growing seeded from the **LIVING** room label
in each apartment, with the lift, stair, bin chute, lobby and corridors seeded
separately as core. Then **look at every level against the plan** — the
segmentation is a starting point, not an answer.

Level totals must reconcile: **apartments + core − light well = FECA**. Individual
apartment areas may move a few m² either way; the level totals are the firm
number.

### 8. Categories
Split each level by use — apartments, core & circulation, common amenity, plant
& services, car park & bike. Categories 1–5 sum to FECA. Adding back the light
well, the balconies and the external wall band gives GBA. Every row must tie.

## Tolerances to report

| Situation | Expected tolerance |
|---|---|
| Floor plate sitting in white space on the sheet | better than ±1% |
| Ground floor where building, terraces and site paving are one continuous surface | ±3% — apply manual cut lines along the external walls, verify against the drawing, and flag it as the level worth a hand check |
| FECA via uniform inward offset | 0.5–1% understated where the façade is glazed |
| UCA roofed test | slightly understated — eaves and soffit overhangs beyond the slab line are not picked up |
| Individual apartment areas | a few m² either way; level totals are firm |

Overall target for a feasibility-grade take-off: **±2%**. Say the number out
loud in the workbook; do not let a reader assume survey accuracy.

## Things to flag, never to guess

- **Site area** where none is figured on the drawings. Measure it from the
  chain-dot boundary, cross-check across three sheets, then mark it
  MEASURED, NOT CONFIRMED and ask for the survey plan or title. Site cover and
  plot ratio both collapse without it.
- **Apartment numbering** inferred from entry-label positions. The *positional*
  description (north-east, south) is the reliable identifier until the architect
  confirms the numbers.
- **Bed / bath / study / media counts** read from room-key labels. Fine for a
  mix summary, not for a price list.
- **Missing bay numbers** in a car park numbering run — either unlabelled or not
  provided. Worth a query either way.

## Cross-checks that catch real errors

- Adjacent levels with near-identical plates should come out within a few percent
  of each other.
- The roof plan must register with the top occupied level — same drawing origin.
- Basement GBA ÷ bays should land in 28–35 m²/bay.
- **GBA − wall bands − unroofed balcony ≈ GFA.**
- Site dimensions measured independently on three sheets should agree to 0.1%.
- A car-park numbering run that ends exactly at the counted total is an
  independent confirmation of the count.

## Where this method is not good enough

This is a **feasibility-grade** take-off from issued drawings. It is not an
architect-certified area schedule and it is not a surveyor's plan of
subdivision. Before figures reach a client, a lender or PAG, obtain the
architect's own area schedule and the survey plan and reconcile both. Resolve
any variance above about 2% on above-ground GBA.
