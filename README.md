# monografiak.works

*Ideia bat. Urte bat. Sinadura bat.* One idea. One year. One signature.

An independent press for monographs, served by GitHub Pages at <https://monografiak.works>. The site is plain HTML and one stylesheet, with no JavaScript, no build step to view it, and self-hosted fonts.

## Layout

```
/                         cover: wordmark, motto, numbered contents
/01/                      Monografia 01 · XYZ (Cryptography & PSI)
/01/monografia-01.md      canonical source (Markdown + TeX); its SHA-256 is the fingerprint
/01/monografia-01.md.sha256
/xyz/                     redirect to /01/ (meta refresh + canonical)
/license/                 CC BY-NC 4.0 statement
/assets/style.css         the only stylesheet
/assets/fonts/            Gasoek One, Archivo, Source Serif 4, IBM Plex Mono (latin woff2 + OFL)
/assets/gurutzea.svg      the mark (symbol #g), used as favicon, end mark and section ornament
/tools/cipher.py          computes every hash and protocol value printed on the site
robots.txt  ai.txt  llms.txt  sitemap.xml  .well-known/tdmrep.json  CNAME  .nojekyll  404.html
```

## Editing a monograph

1. Edit the text in **both** `01/monografia-01.md` (canonical) and `01/index.html`.
2. Run `python3 tools/cipher.py` from the repo root. It recomputes the section hashes, the abstract hash, the fingerprint and the worked P-256 examples, and rewrites the `<!--cipher:NAME-->…<!--/cipher:NAME-->` regions in the HTML. It needs only the Python standard library.
3. Commit and push. Pages redeploys in about 30 seconds.

The fingerprint changes whenever the Markdown changes. Re-sign and re-timestamp after any edit.

## Adding Monografia 02

Copy `01/` to `02/`, rename the source to `monografia-02.md`, and update the metadata (`citation_*`, `dc.*`, JSON-LD, dates, and an expiry one year after publication). Add the new paths to `PAGES` and `SOURCE` in `tools/cipher.py`, or generalise them. Then add the work to `/index.html`, `sitemap.xml` and `llms.txt`.

A Basque edition goes at `/01/eu/index.html` with `<html lang="eu">`. Link the two editions with `<link rel="alternate" hreflang="eu|en">` once it exists.

## The three voices

| Voice | Font | Use |
|---|---|---|
| Big | Gasoek One | `.numero`, `.headline`, `.display-eu`, `.pull`, `.dropcap`, section `h2` |
| Small | Archivo, 11–13px, uppercase, tracked | `.label`, `.rubric`, `.byline`, `.running`, captions, table heads, `.sn` sidenotes |
| Cipher | IBM Plex Mono | `.hex`, `.cipher-rule`, `.cipher-table`, `.cipher-pair`, `.fingerprint` (real values only) |

Body text is Source Serif 4, 19–21px, line-height 1.55, with a 66ch measure. The palette is paper `#F3EBDD`, ink `#16120F` and muted `#5A5248`, and nothing else.

### Blocks

- **Bilingual label** (Euskara first, English below): `<span class="bi"><span lang="eu">Aurkibidea</span><span lang="en">Contents</span></span>`
- **Section:** `<section class="sub">` holding `<header class="sec-head"><span class="secno" aria-hidden="true">01</span><span class="label" lang="eu">…</span><h2>…</h2></header>`
- **Sidenote:** put `<span class="sn" role="note">…</span>` *inside* a paragraph. It floats into the right margin on wide screens and sits inline on narrow ones.
- **Pull quote:** `<p class="pull wide" aria-hidden="true">…</p>`. It duplicates body text, so it is hidden from screen readers.
- **Math:** `<div class="eq"><math display="block"><semantics>…<annotation encoding="application/x-tex">…</annotation></semantics></math><span class="eq-num">(n)</span></div>`
- **Breakouts:** add `.wide` (margins included) or `.full` (edge to edge) to a direct child of a `.sub`.

## Placeholders still to fill

Search the repo for `[YOUR FULL NAME]` and `[PLACEHOLDER`: the author's name, PGP signature, OpenTimestamps `.ots` proof, Arweave transaction ID, IPFS CID, Zenodo DOI and contact address. Never invent these values.

## License

Works: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Commercial use, including training commercial AI models, requires written permission. Site code: MIT. Fonts: SIL OFL 1.1. See `LICENSE.md`.

Provenance: the text of Monografia 01 was drafted by Claude (Anthropic) and is not the author's original writing.
