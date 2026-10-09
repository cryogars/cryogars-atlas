# Documentation

Start with the [design document](design.md) ([Word version](design.docx)): the
sites, the pipeline and the full HDF5 schema. The [technical reference](technical-reference.md)
connects the sources, processing, archives and screen calculations in detail.

| Read this | For |
| --- | --- |
| [Design document](design.md) | Sites, data volume, pipeline steps, grid and resampling choices, HDF5 schema |
| [Technical reference](technical-reference.md) | All eight sites, 15 displayed product families, their mathematics, validation and accepted limitations |
| [Scientific notes](scientific-notes.md) | Detailed processing choices, display behavior and unresolved scientific limitations |
| [Data sources](data-sources.md) | Provider collections, original dataset references and citation guidance |
| [Repository layout](repository-layout.md) | Where source, generated files, tests and local evidence belong |
| [Workflow guide](workflows.md) | Environment, acquisition, enrichment, verification and viewer maintenance commands |
| [Browser comparison](BROWSER_COMPARISON.md) | A/B/difference calculations, GeoTIFF import and figure export |
| [Release checklist](release-checklist.md) | Completed work and remaining archive/release decisions |
| [Release notes](../CHANGELOG.md) | Project release history |
| [September 21 explorer rebuild](reviews/2026-09-21-explorer-rebuild.md) | Evidence for the installed eight-site display export |
| [September 22 public update](reviews/2026-09-22-public-viewer-update.md) | Published viewer commit and all-site HTTP/hash verification |
| [Color editor performance](reviews/2026-09-22-color-editor-performance.md) | Palette updates, idle rendering and regression evidence |

## Evidence and history

Files in [reviews](reviews/) are dated assessments. Their findings describe the
artifacts inspected at the stated time; later work can supersede their status.
The [product-notes installation record](PRODUCT_NOTES_ROLLOUT.md) and
[comparison browser acceptance](COMPARISON_BROWSER_ACCEPTANCE.md) preserve the
scope of earlier checks.

The development workspace also contains a local issue register and a detailed
product-trace dossier. They are intentionally excluded from source distribution.
The technical reference summarizes the relevant methods without requiring those local
files. A public, exhaustive granule/date/channel appendix remains to be curated;
the technical reference tables enumerate product families and site coverage.
