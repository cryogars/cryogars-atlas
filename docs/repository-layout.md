# Repository layout

```text
README.md                  project introduction and primary links
CHANGELOG.md               release history
LICENSE, CITATION.cff      license and citation
environment.yml            Python environment
get_dataset.py             rebuild the archive from NASA into any folder
snowex_inventory.json      frozen product inventory used by get_dataset.py

src/                       pipeline and viewer-generation modules
  build_hdf5.py            download LiDAR + UAVSAR and align them -> <site>.h5
  enrich_hdf5.py           derivatives, masks, geometry -> <site>.enriched.h5
  verify_enriched.py       re-check the enrichment from the stored values
  audit_archive.py         independent read of every array in every file
  manifest.py              SHA-256 manifests and per-dataset fingerprints
  make_explorer.py         export one site's 3D explorer page
  make_index.py            the atlas home page
  refresh_explorers.py,    install reviewed interface changes into
  explorer_addon.py,       existing explorer pages without
  comparison_addon.py      regenerating their data
  ...                      provenance and metadata helpers

web/                       browser code and templates
  explorer_template.html   the explorer application
  index_template.html      the home page
  product_guide.js         product notes
  logo_notes_addon.html    logo and notes panel
  compare/                 A/B comparison, GeoTIFF import and PNG export

tests/                     Python tests (unittest)
  web/                     Node.js tests and page checks for web/

scripts/                   publication and maintenance entry points
  package_public_viewer.py prepare the public viewer bundle
  freeze_inventory.py      rebuild snowex_inventory.json from an archive
  dev/                     build local review previews into ui_preview/

docs/                      design, technical reference, workflows, reviews
assets/                    logos, screenshots and vendored browser libraries
```

Generated and local material is ignored: `out/` (HDF5 archives), `viewer/`
(generated explorers), `ui_preview/` (review previews), `tmp/`, `backups/`,
caches and logs.

## Running things

Run everything from the repository root:

```bash
python -m unittest discover -s tests -t .
node --test tests/web/test_*.js
python src/make_explorer.py --site mores_creek --out-dir path/to/archive --viewer-dir viewer
```

Modules in `src/` import each other by name; scripts outside `src/` (and
`tests/__init__.py`) add `src/` to the import path.
