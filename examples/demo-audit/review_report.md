# Review Report

> READ-ONLY ANALYSIS ONLY
> DirStat_Skill never changes files automatically. It only explains what a human should review.

- root: `examples/sample-data`
- total_findings: 1
- configured_dominant_percent: `0.8`

## How To Read This

- Start from `dominant space` to see where the volume is concentrated.
- Use `path safety` and `protected huge hotspots` to understand sensitive areas.
- Treat `probable duplicates` as a strong suspicion, not as byte-level proof.
- Treat `nearby references` as contextual evidence, not as certainty of active use.

## Dominant Space

Shows the paths that explain most space under the configured dominant-space threshold.

### `examples/sample-data`

- size_bytes: `479232`
- size_human: `468.0 KB`
- attention_level: `review carefully`
- review_reason: directory dominates parent space under the dominant-space walk
- evidence: selected by dominant-space walk with no nearby references found
- confidence: `low`
- selection_source: `dominant_subtree`

## Path Safety

Shows paths whose location changes their risk posture even before deeper inspection.

- none

## Nearby References

Shows paths with local evidence pointing to nearby configs, manifests, or workflow references.

- none

## Signature Heuristics

Shows paths matched by obvious signatures such as cache, temp, trash, or incomplete-download patterns.

- none

## Probable Duplicates

Shows large assets that look duplicated by basename, size, and extension across different directories.

- none

## Protected Huge Hotspots

Shows very large protected areas that matter for visibility but should stay handled carefully.

- none

## Limits

- `probable duplicates` uses fast structural signals by default, not full-content hashing.
- `protected huge hotspots` are visibility findings, not an invitation to act blindly.
- low-confidence findings still need human judgment.
