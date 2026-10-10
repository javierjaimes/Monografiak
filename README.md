# monografiak.works

An independent press for monographs. This is a static site served by GitHub Pages at <https://monografiak.works>, with no build step, no JavaScript and no web fonts.

## Layout

```
/                    index of works
/xyz/                Monografiak Nº 1 — XYZ (Cryptography & PSI)
/xyz/xyz.md          plain-text source (Markdown + TeX) for readers, crawlers and LLMs
/xyz/figures/        figures (SVG preferred, with <title>/<desc>)
/license/            CC BY 4.0 statement
/assets/style.css    the only stylesheet
/assets/lauburu.svg  the mark (ikurriña red)
robots.txt, sitemap.xml, llms.txt, CNAME, .nojekyll, 404.html
```

## Publishing

1. Push this folder to a GitHub repository.
2. Go to **Settings → Pages → Build and deployment** and choose *Deploy from a branch*, `main`, `/ (root)`.
3. In your DNS, point `monografiak.works` at GitHub Pages: four `A` records (185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153), and optionally a `CNAME` for `www` to `<user>.github.io`. Then enable **Enforce HTTPS**.

To preview locally, run `python3 -m http.server` and open <http://localhost:8000>. Paths are root-relative, so open the site through a server rather than as `file://` URLs.

## Adding a work

1. Copy `xyz/` to `<slug>/` and edit `index.html`: the `<title>`, the meta description, `canonical`, the `citation_*` / `dc.*` / Open Graph tags and the JSON-LD.
2. Write `<slug>/<slug>.md` as the plain-text mirror.
3. Add the work to `/index.html` (both the list and the JSON-LD `hasPart`), `/sitemap.xml` and `/llms.txt`.

## Blocks

**Text** — normal HTML: `<p>`, `<h2><span class="secno">2</span>Title</h2>`, lists, `<blockquote>`.

**Note / definition**

```html
<aside class="note" aria-label="Note"><p><span class="label">Note.</span> …</p></aside>
<div class="definition" role="note" aria-label="Definition 1"><p><span class="label">Definition 1.</span> …</p></div>
```

**Image / figure.** Always include `alt`, plus a caption that adds information beyond the alt text.

```html
<figure id="fig-2" aria-labelledby="fig-2-cap">
  <img src="/slug/figures/name.svg" width="720" height="400" loading="lazy" alt="…">
  <figcaption id="fig-2-cap"><b>Figure 2.</b> …</figcaption>
</figure>
```

Add `class="wide"` to a figure to let it break out of the text column.

**Math.** Use native MathML, which needs no JavaScript and works with screen readers. Keep the TeX source in an annotation so machines can read it too.

```html
<div class="eq" id="eq-9">
  <math display="block">
    <semantics>
      <mrow><msup><mi>e</mi><mrow><mi>i</mi><mi>π</mi></mrow></msup><mo>+</mo><mn>1</mn><mo>=</mo><mn>0</mn></mrow>
      <annotation encoding="application/x-tex">e^{i\pi} + 1 = 0</annotation>
    </semantics>
  </math>
  <span class="eq-num">(9)</span>
</div>
```

Write inline math as `<math><mi>x</mi></math>`. Tools such as `temml` or `pandoc --mathml` can convert TeX to MathML if you prefer to write TeX.

**Table.** Wrap tables in `<div class="table-wrap">`, put the caption in `<caption>`, and add `scope` attributes to header cells.

## Design

- **The text is the design.** One readable column, system serif fonts, generous line height, and no ornament beyond what the text needs.
- **Basque palette.** The accent colours are ikurriña red (`#b3121f`) and green (`#00673a`). Both are tuned for WCAG AA contrast and lightened in dark mode. The mark is the lauburu. Section labels carry Euskera glosses tagged `lang="eu"`.
- **Accessibility.** Pages have a skip link, landmarks, visible focus styles, native MathML, alt text plus long descriptions, dark mode, reduced-motion support and a print stylesheet.

## License

Content: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Site code (HTML/CSS): MIT. All crawlers, including AI crawlers, are allowed; see `robots.txt` and `llms.txt`.
