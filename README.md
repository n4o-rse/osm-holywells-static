# osm-holywells-static

A static, read-only Wikibase (GitHub Pages) for OpenStreetMap elements: holy wells (`place_of_worship=holy_well`) of Ireland and Northern Ireland.
It is built with [wikibase-static](https://github.com/n4o-rse/wikibase-static) and follows the site
[osm-benchmarks-static](https://github.com/n4o-rse/osm-benchmarks-static), whose model it takes over unchanged.

Each OSM element becomes one item with one QID, as OSM itself knows only one ID per element. The
element's version history is tracked as statements on that item, and every item is anchored on
a CIDOC CRM class: `crm:E26 Physical Feature` (proposal, see PRIMER.md). The geometry of each version is kept as WKT, so the model also carries ways and relations.

**State (S1, S2):** the skeleton and the model (the class “Holy well”, the fourteen properties of the benchmarks site) are in place; there are no data yet. The first harvest is step S4 (736 elements in the osm2lod run of 2026-03-28), after a small change in the package (`wikibase-static` 0.25.0, PRIMER.md step S3). The work plan, the decisions made so far and the steps ahead are in [`PRIMER.md`](PRIMER.md) (German).

## Build

Needs Python 3.10 or later. In a Windows `cmd` window, in this folder:

    pip install -r requirements.txt && python main.py --strict

`python main.py --list` shows the steps. `python main.py import-osm --probe` sends one Overpass request and writes nothing (it asks for the selection `holywells` by itself).
`update.cmd` installs the current `wikibase-static` again, builds with `--strict`, and commits and pushes
only if something changed.

## Related repositories

- [`Research-Squirrel-Engineers/osm2lod`](https://github.com/Research-Squirrel-Engineers/osm2lod): the prototype that exports OSM data via Overpass into RDF and a Wikibase; the queries come from there.
- [`n4o-rse/wikibase-static`](https://github.com/n4o-rse/wikibase-static): the package that turns CSV tables into the static Wikibase pages, RDF and SPARQL page.
- [`n4o-rse/osm-benchmarks-static`](https://github.com/n4o-rse/osm-benchmarks-static): the sibling site for the benchmarks, from which the model is taken.

## Licence and attribution

The code of this repository is under the [MIT licence](LICENSE).

The data are derived from OpenStreetMap: © OpenStreetMap contributors, available under the
[Open Database Licence (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
Every page of the site carries that notice (`license` in `site.yaml`).

The logo (`assets/logo.png`, a pen drawing of a holy well with a stone cross) are by Florian Thiery, generated with ChatGPT and
published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The licence of the code (MIT) does not cover them.
