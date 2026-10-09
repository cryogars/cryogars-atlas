# SnowEx Field Atlas: HDF5 storage design

*Also available as a Word document: [design.docx](design.docx).*

## 1. Goal

Build a per-site HDF5 archive that puts NASA SnowEx LiDAR products (DEM, snow
depth, vegetation height) and the matching NASA/JPL UAVSAR L-band radar products
(interferometry and amplitude) pixel-aligned on one common 3 m grid per site, as
the training and evaluation data for snow-depth models and, later, snow water
equivalent (SWE) retrieval. Released as v1.0.05: a base file (product 0.1.0) and
an enriched file (enrichment 3.3.0) per site.

## 2. Sites and data inventory

8 sites have overlapping LiDAR + UAVSAR coverage, found by intersecting each
LiDAR granule's real footprint polygon with UAVSAR's catalog. A UAVSAR pair
counts as a match when it overlaps the footprint and comes within 5 days of the
LiDAR survey.

| Site | State | LIDAR product(s) | UAVSAR match | Notes |
| --- | --- | --- | --- | --- |
| Banner Summit | ID | DEM, SD (2 dates), VH (2 dates) | yes, 11 acquisitions | Shares flight lines w/ Dry Creek, Mores Creek |
| Dry Creek | ID | DEM, SD, VH | yes, 2 acquisitions | Shares flight lines w/ Banner Summit |
| Mores Creek | ID | DEM, SD (2 dates), VH (2 dates) | yes, 10 acquisitions | Shares flight lines w/ Banner Summit |
| Fraser | CO | DEM, SD (2 dates), VH (2 dates) | yes, 5 acquisitions | |
| Cameron Pass | CO | DEM, SD, VH | yes, 5 acquisitions | |
| Little Cottonwood Cyn | UT | DEM, SD, VH | yes, 6 acquisitions | |
| Grand Mesa | CO | DEM, SD (6 dates), VH (2 dates) | yes, 27 acquisitions | DEM is a 2016 lidar snow-off DTM (1 m); SD from 5 ASO surveys (2017) + SnowEx 2020 |
| Reynolds Creek | ID | DEM, VH | yes, 1 acquisition | DEM is the 2014 RCEW lidar DEM (1 m); no snow-depth survey exists |

### 2.1 Data volume (final archive)

Sizes of the released v1.0.05 files. The archive is larger than the downloaded
radar products (about 172 GB before clipping) because every layer is stored on
the 3 m grid, finer than UAVSAR's native pixels, and Grand Mesa's grid alone
holds 286 million cells.

| Site | Base file (.h5) | Enriched file (.enriched.h5) |
| --- | ---: | ---: |
| Banner Summit | 20.32 GB | 18.40 GB |
| Mores Creek | 4.61 GB | 4.13 GB |
| Fraser | 3.57 GB | 3.25 GB |
| Cameron Pass | 1.30 GB | 1.18 GB |
| Little Cottonwood Cyn | 3.32 GB | 2.87 GB |
| Dry Creek | 1.16 GB | 1.04 GB |
| Grand Mesa | 107.94 GB | 114.03 GB |
| Reynolds Creek | 1.08 GB | 0.95 GB |
| **Total (16 files, 289.15 GB)** | **143.31 GB** | **145.84 GB** |

## 3. Pipeline design

### 3.0 What the main script does, end to end

| Step | Action |
| --- | --- |
| 1. Plan | Read the frozen product inventory and the LIDAR/UAVSAR match list; group by unique UAVSAR product so a shared flight is downloaded once. |
| 2. Grid + LIDAR | Derive the site's common grid from its reference DEM (3.2); read each DEM/SD/VH product, resample it onto the grid (3.4) and write it into the site's .h5. |
| 3. Fetch UAVSAR | Download each unique product once, by its recorded product URL (found via footprint search). |
| 4. Reproject + clip | Resample onto the common grid of every site sharing that product (3.2, 3.4), reading only the site's extent plus a 500 m buffer. |
| 5. Write | Stream the clipped, aligned arrays straight into each site's .h5. |
| 6. Clean up | Delete the raw UAVSAR download once every site needing it has been written. |
| 7. Finalize | Write `identification/` and `matches/`; verify every array's shape + transform matches the site's common grid before marking the file complete. |
| 8. Enrich | Write `<site>.enriched.h5`: clean the layers, regroup radar by acquisition, add slope, aspect, canopy fraction, coherence masks and incidence angles (4). |
| 9. Verify | Re-check the enrichment from the stored values, audit every file independently, and write SHA-256 manifests. |

### 3.1 One download per flight, shared across sites

- Banner Summit, Dry Creek and Mores Creek are covered by the same UAVSAR flight
  lines (Lowman lines 05208 and 23205).
- Each unique product is downloaded once, clipped separately for every
  overlapping site, then the raw file is deleted.

### 3.2 Common grid per site

- Every array in a site's file (LIDAR and UAVSAR alike) shares one CRS, one
  affine transform, one pixel shape. The CRS, 3 m pixel size and pixel alignment
  come from the site's reference LiDAR DEM; the grid extent is where that DEM and
  the site's science data overlap.
- The same row and column are the same ground
  location in every layer, checked programmatically on every array before a file
  is marked complete.

Grand Mesa has no QSI DEM. Its reference is the 2016 lidar-derived snow-off DTM
from the SnowEx HRSI collection (1 m, resampled to 3 m, EPSG:32612).

Reynolds Creek has no snow-depth survey in the SnowEx collections. Its reference
is the 2014 Reynolds Creek Experimental Watershed lidar DEM (1 m, resampled to
3 m, EPSG:26911), so the site carries terrain, vegetation and radar but no
snow-depth labels.

### 3.3 Resolution

- LIDAR: QSI and ASO products are published at 3 m; Grand Mesa's DTM and Reynolds
  Creek's DEM are 1 m and are resampled to 3 m. UAVSAR: about 4.45 m × 6.18 m on
  the ground (non-square), recorded per product.
- The 3 m LIDAR grid is the common grid; UAVSAR is upsampled onto it, and its native resolution is stored as
  `uavsar_native_resolution_m`.

This keeps the LIDAR labels at full resolution; models can average to coarser
blocks when training.

### 3.4 Resampling method

- `.int` (complex interferogram): nearest-neighbor, to avoid averaging across a
  2π wrap boundary.
- `.unw`, `.cor`, amplitude and all LIDAR variables: bilinear.

### 3.5 Naming, documentation, and NISAR alignment

- In the base file, UAVSAR groups are named by site, source flight line and
  dates:

  ```text
  BANNERSUMMIT_CUTFROMLOWMAN23205_20200131_20200213
  ```

- The enriched file regroups radar by acquisition —
  `UAVSAR/<date1>_<date2>/<flight line>/` — with amplitude and interferometry
  together, since they come from the same pair of passes; the base group name is
  kept as `original_group_name`.
- Original JPL product ID and ASF file ID kept as attributes for traceability.
- Every group and array carries a plain-English `description` attribute plus
  units, grid and source lineage.
- The overall structure (science data under `science/`, file-level metadata in a
  separate `identification/` group) follows the layout NASA uses in NISAR HDF5
  products.

## 4. Full HDF5 schema (v1.0.05)

Shown for Banner Summit's enriched file — 2 SD dates, 2 VH dates, DEM, derived
layers and 11 UAVSAR acquisitions, on flight lines shared with Dry Creek and
Mores Creek. The base file (`banner_summit.h5`) holds the same LIDAR arrays and
stores radar by product type (`INTERFEROMETRY_GRD/`, `AMPLITUDE_GRD/`,
`DEM_TIFF/`). Arrows explain what each item actually is.

```text
banner_summit.enriched.h5
├─ identification/   → file-level metadata, no science data — the “label on the box”
│   common_crs_epsg, common_crs_wkt   → the shared map projection every array in this file uses
│   common_grid_transform, common_grid_shape, common_grid_resolution_m   → the exact 3 m pixel grid (origin, spacing, size) everything is resampled onto
│   reference_product, reference_filename, grid_extent_rule   → which lidar DEM defines the grid, and how its extent was chosen
│   uavsar_native_resolution_m, resampling_note   → UAVSAR's true original pixel size, and how/why it was resampled
│   site_name, site_key, state, product_version, enrichment_version, created_date   → basic identifying info about this file
│
├─ science/   → the measured and derived data, split into LIDAR/ and UAVSAR/
│   ├─ LIDAR/   → data from the airborne laser surveys
│   │   ├─ DEM/   → bare-earth elevation — the ground surface with snow and plants stripped away
│   │   │     grids/elevation   → the actual elevation values (meters), plus the source file and survey date
│   │   ├─ SD/   → snow depth — how deep the snow was, in meters (snow-on survey minus snow-off survey)
│   │   │     20200218/snow_depth,  20210315/snow_depth   → one snow depth map per survey date
│   │   ├─ VH/   → vegetation height — how tall the trees/brush are
│   │   │     20200218/veg_height, 20210315/veg_height   → one vegetation height map per survey date
│   │   └─ DERIVED/   → computed from the layers above
│   │         slope, aspect   → terrain steepness and downhill direction, in degrees
│   │         forest_cover_fraction_20200218, _20210315   → share of nearby cells with vegetation ≥ 2 m
│   │
│   └─ UAVSAR/   → data from the airplane-mounted radar — clipped to this site, resampled onto the LIDAR grid
│         20200131_20200213/LOWMAN23205/   → one acquisition: the Lowman flight line, comparing Jan 31 to Feb 13, 2020
│           attrs: original_product_id, original_group_name, acquisition_dates,   → traceability: JPL's product ID, the base-file group name and the two real flight dates
│                  radar_wavelength_cm, radar_look_direction, platform_altitude_m   → radar and flight geometry from JPL's annotation file
│           HH/  amp1, amp2, int, unw, cor, coherence_mask   → horizontal-send / horizontal-receive antenna combination — 6 arrays (below)
│                • amp1, amp2 = amplitude   → radar brightness on each pass — how much energy bounced back
│                • int = raw interferogram   → the radar phase difference between the passes — a complex number, wraps every 360°
│                • unw = unwrapped phase   → the int value “unrolled” into a continuous number — the usable surface-change signal
│                • cor = coherence   → 0 to 1, how trustworthy the phase measurement is at that pixel (1 = reliable)
│                • coherence_mask   → 1 where coherence ≥ 0.30, 0 below, 255 where missing
│           HV/, VH/, VV/  (same 6)   → the other send/receive combinations, where the flight recorded them
│           GEOMETRY/  incidence_angle_flat, local_incidence_angle   → the angle the radar meets the ground, ignoring and including the slope
│
└─ matches/   → a table recording which LIDAR date was paired with which UAVSAR acquisition, how many days apart, and whether it counted as a match
    lidar_product_type, lidar_date, lidar_filename, uavsar_level, uavsar_dates, uavsar_flight_id, gap_days, group_name, verdict
```

Processing details, the mathematics behind every product, validation and the
accepted limitations are in the [technical reference](technical-reference.md).
