# code

## experiments

lookit protocols for both studies. each file is a self-contained `generateProtocol()` function passed to the Lookit platform.

- `chance.js` — exp 1 (probability game). randomizes condition (cued/uncued) and counterbalances response option order.
- `memory.js` — exp 2 (memory game). same CHOICE → PREDICTION → REVEAL & SURPRISE flow.

## python

- `preprocessing.py` — reads raw JSON exports from Lookit, extracts trial-level responses, outputs cleaned CSVs to `data/chance/` and `data/memory/`. raw data not included in repo (identifiable).

## R

- `analysis.Rmd` — main analyses and figures. knit to reproduce results. outputs plots to `figures/chance/` and `figures/memory/`.
