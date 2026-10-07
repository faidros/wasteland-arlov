# Arlövs Livs and Jouren Livs

- Added shopfront glazing, fascia signs and awnings for Arlövs Livs Tobak at Lundavägen 27 and Jouren Livs at Lundavägen 65.
- Anchored each sign to the street-facing wall nearest its mapped business pin; added both businesses to the tactical map labels.

# Arlöv Borggatan refinements

## 2026-10-06 — expanded play area

Expanded and recentered the square from 1200 m to 1600 m (55.6349, 13.0808) to include Rapsvägen,
Burlöv Center and the existing Borggatan spawn in one playable map.

Burlöv Center's official visitor information confirms one shopping floor and four entrances. Its OSM
footprint has 40 outline points and covers the full mall. Replaced the generated two-storey yellow
block with a low one-storey shell that follows the mapped outline, with four glazed entrances, canopies,
shopfront glazing, a center sign and roof lanterns. Roof details are an informed interpretation of
satellite imagery rather than a complete roof survey.

In the Rapsvägen/Kornvägen area, corrected four nearby older apartment blocks and added their observed
stacked or projecting balconies. Other nearby facades remain generated estimates.

## 2026-10-06 — Borggatan, first facade pass

Compared four houses with Google Street View panoramas dated December 2020. The imagery was viewed
only as a reference and was not saved to the repository.

- `w208689940` (Borggatan 25): white-painted brick, one full storey and attic, steep dark tiled roof,
    broad dormer, dark plinth. Generated as a grey two-storey house; corrected and given a single broad dormer.
- `w208689956` (Borggatan 23): red brick, one full storey and attic, steep dark roof and a small dormer.
- `w208689951` (Borggatan 21): yellow plaster, red tiled roof, broad dormer and entrance porch.
- `w208688034` (Borggatan 30): red brick, steep gabled roof and light window surrounds.

Each hand model uses the observed roof, facade and entrance details; the exact window counts and
decorative brickwork remain approximate where the panorama does not clearly resolve them.

The survey plan has 17 viewpoints for 30 houses along Borggatan. This round models the four observed
houses nearest the spawn area individually; the remaining houses are still generated estimates.

## 2026-10-06 — Dalbyvägen and Lundavägen

Reviewed representative Google Street View panoramas from May 2024 (Dalbyvägen and the central
Lundavägen frontage) and April 2026 (northern Lundavägen). No Google imagery was saved.

- Both roads are asphalt with sidewalks; OSM already has asphalt on most segments. Filled the two
    untagged wide Lundavägen segments and made the observed sidewalks explicit on both roads.
- `w170849544` (X-tra Dalbyvägen): corrected from a two-storey ochre house to a one-storey modern
    supermarket with grey cladding, glass storefront and red sign.
- `w89610390` (Burlövs bibliotek, Lundavägen): retained four storeys and red brick; corrected the
    flat roof and added the glazed entrance floor and street-facing metal balconies.
- Street imagery also shows a mix of shops, apartment blocks, brick row houses and detached villas.
    The full plans cover 34 houses on Dalbyvägen and 63 on Lundavägen; uninspected facades remain
    generated estimates. Painted crossing stripes and the low roadside rail are not modeled by the
    current pipeline.

## 2026-10-06 — Jakob Persvägen

Compared Street View panoramas dated August 2019 at Jakob Pers Plats. The images were viewed only as
references and were not saved.

- The street is asphalt, with paved pedestrian areas; kept asphalt and made both sidewalks explicit.
- `w89610407` and `w89610377`: corrected generic plaster to red brick and added the projecting glazed
    stairwell with red spandrel bands.
- `w252113047`: corrected generic grey plaster to red brick and added the repeated dark metal balconies.
- `w357244347`: corrected a generic two-storey brown-brick house to the low blue kiosk/cafe with a
    glazed service front and red canopy.

The mapped name is `Jakob Persvägen`; the house details are estimates beyond what the 2019 panoramas
show clearly.

## 2026-10-06 — Grönvägen, Segevägen and Storgatan

Compared Google Street View panoramas from November 2020 (Grönvägen), May 2024 (Segevägen) and the
Burlövs municipality's 2024 exterior photo and 1970 archival photo for Arlövs teater. Images were
viewed only as references and were not copied into the repository.

- Made asphalt and both sidewalks explicit on the three streets; filled Storgatan's missing surface
    tags.
- `w89605810` and `w89605835` (Grönvägen): corrected the generated tower colours and added repeated
    balcony/stairwell bays matching the red-brick and pale blocks.
- `w1379187964` (Segevägen): corrected the rose-plaster guess to a pale facade with brick base and
    street-side balconies.
- `w182238945` (Arlövs teater/Hundramannasalen): corrected the four-storey generic block to a
    single-storey historic hall with attic, ochre plaster, black sheet-metal roof, dormers and dentil
    cornice. Burlövs municipality dates it to 1892 and lists it as q1-protected; the 2024 palette
    recalls the original exterior.

Plans cover 9 houses on Grönvägen, 16 on Segevägen and 8 on Storgatan; other facades remain generated
estimates. Painted road markings and temporary renovation details are not modeled.

## 2026-10-06 — Burlöv Center, Rapsvägen and Kornvägen

Burlöv Center's official visitor information confirms that all shops are on one floor and that the
mall has four entrances. Its OSM outline contains 40 points and covers roughly 41,800 m². Replaced the
two-storey yellow placeholder with a low shell following that outline, four glazed entrance bays,
canopies, a center sign and roof lanterns. The lantern grid is an interpretation of aerial imagery,
not an exact roof survey.

Street View panoramas from November 2020 show the older apartment blocks:
- `w208960541` (Rapsvägen): yellow-brown brick and a narrow strip of pink balcony panels.
- `w36875735` (Rapsvägen): yellow brick and repeated dark balcony rails.
- `w361096438` (Kornvägen): yellow brick, turquoise stair glazing and garage doors at ground level.
- `w36875729` (Kornvägen): yellow brick with a narrow turquoise stair core and balconies.

Google images were viewed only as references and not saved to the repository. Four extra blocks in the
area remain generated estimates.

## 2026-10-07 — Dalbyvägen 4 and Lundavägen 9 signs

OSM names the food node inside `w208685399` **Arlövs kebab**. The four-storey red-brick building now
has that name on its ground-floor sign band and on the tactical map.

Google Maps identifies Lundavägen 9 as **OKQ8 Automat** (24-hour, diesel). OSM has no building
footprint for its forecourt, so an independent, coordinate-anchored model supplies a roadside pylon,
canopy and four pumps. The nearby Sopstationen building is left unchanged.

## 2026-10-07 — Geukahuset, Lundavägen 29

Matched address node 29 to OSM building `w357244353`. Replaced the generic five-storey salmon block
with yellow brick, a stone ground-floor arcade, dark timber framing, two street-facing front gables,
a steep dark metal roof and a round corner turret with green spire. The reference was Burlövs Bostäders
Geukahuset exterior photo; it was viewed for architectural details and not copied into the repository.
Added Geukahuset to the tactical map. Smaller facade details and exact shopfront layouts remain approximate.