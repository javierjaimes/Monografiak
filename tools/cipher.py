#!/usr/bin/env python3
"""
cipher.py: compute the real ciphertext printed on monografiak.works.

Nothing on the site is decorative noise. Every hex string shown in monospace
is produced by this script, and anyone can reproduce it:

  * section rules:   SHA-256 of each section's Markdown source
  * abstract hash:   SHA-256 of the abstract's Markdown source
  * fingerprint:     SHA-256 of the canonical source file 01/monografia-01.md
  * worked examples: Diffie-Hellman PSI and a DH-OPRF evaluated on NIST P-256.
                     Secret scalars are derived from *published* labels, so the
                     values are reproducible (and therefore not secret).

Run it from the repository root after editing the Markdown source:

    python3 tools/cipher.py

It rewrites the regions between <!--cipher:NAME--> and <!--/cipher:NAME-->
markers in the HTML pages. It needs only the Python 3.8+ standard library.

The hash-to-curve used here is try-and-increment. It is fine for an
illustration but it is NOT constant-time; production systems use RFC 9380.
"""
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "01" / "monografia-01.md"
PAGES = [ROOT / "01" / "index.html", ROOT / "index.html"]

# ---------------------------------------------------------------- P-256 ----
P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
B = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B


def on_curve(pt):
    x, y = pt
    return (y * y - (x * x * x - 3 * x + B)) % P == 0


def add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    (x1, y1), (x2, y2) = p1, p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if p1 == p2:
        lam = (3 * x1 * x1 - 3) * pow(2 * y1, -1, P) % P
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    return (x3, (lam * (x1 - x3) - y1) % P)


def mul(k, pt):
    result = None
    for bit in bin(k % N)[2:]:
        result = add(result, result)
        if bit == "1":
            result = add(result, pt)
    return result


def hash_to_curve(msg: str):
    """Try-and-increment onto P-256 (illustrative, not constant-time)."""
    dst = b"monografiak-01-P256-TAI"
    for ctr in range(256):
        x = int.from_bytes(hashlib.sha256(dst + bytes([ctr]) + msg.encode()).digest(), "big") % P
        rhs = (x * x * x - 3 * x + B) % P
        y = pow(rhs, (P + 1) // 4, P)  # P = 3 mod 4
        if y * y % P == rhs:
            pt = (x, y if y % 2 == 0 else P - y)
            assert on_curve(pt)
            return pt
    raise ValueError("no point found")


def scalar(label: str) -> int:
    return int.from_bytes(hashlib.sha256(label.encode()).digest(), "big") % N


def xhex(pt) -> str:
    """A point is printed as its 32-byte x-coordinate in hex."""
    return f"{pt[0]:064x}"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ------------------------------------------------------------- display ----
def hexwrap(h: str, cls="hex") -> str:
    """Hex in groups of 8, with break opportunities that copy cleanly."""
    groups = [h[i:i + 8] for i in range(0, len(h), 8)]
    return f'<code class="{cls}">' + "<wbr>".join(groups) + "</code>"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------- sections ---
def split_sections(md: str):
    """Return {key: markdown} for '## Abstract' and '## n. Title' sections.

    A section runs from its '## ' heading line up to (not including) the next
    '## ' heading or the closing '---' rule; trailing whitespace is stripped
    and a single newline appended before hashing.
    """
    body = md.split("\n---\n", 2)  # front matter, body, footer
    text = body[1] if len(body) > 1 else md
    parts = re.split(r"(?m)^(?=## )", text)
    out = {}
    for part in parts:
        m = re.match(r"## (Abstract|(\d+)\. )", part)
        if not m:
            continue
        key = "abstract" if m.group(1) == "Abstract" else f"s{int(m.group(2))}"
        out[key] = part.rstrip() + "\n"
    return out


# ------------------------------------------------------------ examples ----
ALICE = ["amaia@example.eus", "iker@example.eus", "nerea@example.eus"]
BOB = ["iker@example.eus", "jon@example.eus", "nerea@example.eus", "unai@example.eus"]
LABEL_A, LABEL_B = "monografiak/01/alice", "monografiak/01/bob"
LABEL_K, LABEL_R = "monografiak/01/oprf-key", "monografiak/01/oprf-blind"
OPRF_INPUT = "iker@example.eus"
PHONE = "+34 943 123 456"


def dh_psi_block() -> str:
    a, b = scalar(LABEL_A), scalar(LABEL_B)
    u = [mul(a, hash_to_curve(x)) for x in ALICE]          # step 1
    w = [mul(b, ui) for ui in u]                           # step 2, in order
    v = sorted((mul(b, hash_to_curve(y)) for y in BOB), key=xhex)  # step 2, shuffled
    t = [mul(a, vj) for vj in v]                           # step 3
    found = [x for x, wi in zip(ALICE, w) if wi in t]
    assert found == [x for x in ALICE if x in BOB], found

    rows = []
    rows.append(f'<tr><th scope="row">1 · Alice → Bob</th><td colspan="2">Blinded set <math><mi>H</mi><mo>(</mo><msub><mi>x</mi><mi>i</mi></msub><msup><mo>)</mo><mi>a</mi></msup></math></td></tr>')
    for x, ui in zip(ALICE, u):
        rows.append(f'<tr><td></td><td class="pt">{esc(x)}</td><td>{hexwrap(xhex(ui))}</td></tr>')
    rows.append(f'<tr><th scope="row">2 · Bob → Alice</th><td colspan="2">Same values raised to <math><mi>b</mi></math>, in Alice’s order</td></tr>')
    for x, wi in zip(ALICE, w):
        rows.append(f'<tr><td></td><td class="pt">{esc(x)}</td><td>{hexwrap(xhex(wi))}</td></tr>')
    rows.append(f'<tr><th scope="row">2 · Bob → Alice</th><td colspan="2">Bob’s set <math><mi>H</mi><mo>(</mo><msub><mi>y</mi><mi>j</mi></msub><msup><mo>)</mo><mi>b</mi></msup></math>, sorted by value (hides his order)</td></tr>')
    for j, vj in enumerate(v, 1):
        rows.append(f'<tr><td></td><td class="pt"><math><msub><mi>v</mi><mn>{j}</mn></msub></math></td><td>{hexwrap(xhex(vj))}</td></tr>')
    rows.append(f'<tr><th scope="row">3 · Alice, locally</th><td colspan="2"><math><msubsup><mi>v</mi><mi>j</mi><mi>a</mi></msubsup></math>, compared with step 2</td></tr>')
    for j, tj in enumerate(t, 1):
        hit = next((x for x, wi in zip(ALICE, w) if wi == tj), None)
        mark = f'<span class="match">● {esc(hit)}</span>' if hit else '<span class="nomatch">no match</span>'
        rows.append(f'<tr><td></td><td class="pt"><math><msubsup><mi>v</mi><mn>{j}</mn><mi>a</mi></msubsup></math> {mark}</td><td>{hexwrap(xhex(tj))}</td></tr>')

    return (
        '<div class="table-wrap wide cipher-table">\n<table>\n'
        '<caption><span class="bi"><span lang="eu">Adibide landua</span><span lang="en">Worked example</span></span> '
        f'Diffie–Hellman PSI on NIST P-256. Alice holds {len(ALICE)} addresses and Bob holds {len(BOB)}. '
        f'Each value is the x-coordinate of a curve point, in hex. The secrets are derived as <code>a = SHA-256("{LABEL_A}") mod n</code> and '
        f'<code>b = SHA-256("{LABEL_B}") mod n</code>, so anyone can reproduce them with <code>tools/cipher.py</code>.</caption>\n'
        '<thead><tr><th scope="col">Step</th><th scope="col">Element</th><th scope="col">Value (hex)</th></tr></thead>\n<tbody>\n'
        + "\n".join(rows)
        + "\n</tbody>\n</table>\n</div>"
    )


def oprf_block() -> str:
    k, r = scalar(LABEL_K), scalar(LABEL_R)
    hx = hash_to_curve(OPRF_INPUT)
    blinded = mul(r, hx)
    evaluated = mul(k, blinded)
    unblinded = mul(pow(r, -1, N), evaluated)
    assert unblinded == mul(k, hx)
    output = hashlib.sha256(OPRF_INPUT.encode() + bytes.fromhex(xhex(unblinded))).hexdigest()
    rows = [
        ("Alice", "Input", f'<span class="pt">{esc(OPRF_INPUT)}</span>'),
        ("Alice", "<math><mi>H</mi><mo>(</mo><mi>x</mi><mo>)</mo></math>", hexwrap(xhex(hx))),
        ("Alice → Bob", "Blinded <math><mi>H</mi><mo>(</mo><mi>x</mi><msup><mo>)</mo><mi>r</mi></msup></math>", hexwrap(xhex(blinded))),
        ("Bob → Alice", "Evaluated <math><msup><mrow><mo>(</mo><mi>H</mi><mo>(</mo><mi>x</mi><msup><mo>)</mo><mi>r</mi></msup><mo>)</mo></mrow><mi>k</mi></msup></math>", hexwrap(xhex(evaluated))),
        ("Alice", "Unblinded <math><mi>H</mi><mo>(</mo><mi>x</mi><msup><mo>)</mo><mi>k</mi></msup></math>", hexwrap(xhex(unblinded))),
        ("Alice", "Output <math><msub><mi>F</mi><mi>k</mi></msub><mo>(</mo><mi>x</mi><mo>)</mo></math>", hexwrap(output)),
    ]
    body = "\n".join(f'<tr><th scope="row">{p}</th><td class="pt">{label}</td><td>{val}</td></tr>' for p, label, val in rows)
    return (
        '<div class="table-wrap wide cipher-table">\n<table>\n'
        '<caption><span class="bi"><span lang="eu">Adibide landua</span><span lang="en">Worked example</span></span> '
        'One OPRF evaluation on P-256. The output is SHA-256 of the input followed by the x-coordinate of <math><mi>H</mi><mo>(</mo><mi>x</mi><msup><mo>)</mo><mi>k</mi></msup></math>, a simplified form of RFC 9497. '
        f'The scalars are derived as <code>k = SHA-256("{LABEL_K}") mod n</code> and <code>r = SHA-256("{LABEL_R}") mod n</code>. '
        'The unblinded value equals the one Bob would compute directly from <math><mi>x</mi></math>, but Bob never sees <math><mi>x</mi></math>.</caption>\n'
        '<thead><tr><th scope="col">Party</th><th scope="col">Value</th><th scope="col">Hex</th></tr></thead>\n<tbody>\n'
        + body + "\n</tbody>\n</table>\n</div>"
    )


def dictionary_block() -> str:
    digest = sha(PHONE)
    return (
        '<details class="cipher-pair">\n'
        f'<summary><span class="label">SHA-256 · <span lang="eu">Zifratua</span></span> {hexwrap(digest)}</summary>\n'
        f'<p><span class="label"><span lang="eu">Testu argia</span> · Plaintext</span> <code class="pt">{esc(PHONE)}</code>. '
        'A phone number has about ten digits, so this hash can be inverted by trying every possible number. '
        'Opening this box takes one click. Enumerating every Spanish phone number would take a laptop minutes.</p>\n'
        '</details>'
    )


def section_rule(n: int, digest: str) -> str:
    return (
        '<div class="cipher-rule wide" aria-hidden="true">'
        '<svg class="gurutzea" width="13" height="13"><use href="/assets/gurutzea.svg#g"/></svg>'
        f'<span>§ {n:02d} · SHA-256</span> <code>{digest}</code></div>'
    )


def fingerprint_block(fp: str, sections: dict) -> str:
    noise_rows = [sections[k] for k in sorted(sections, key=lambda k: (k != "abstract", k))]
    above = "".join(f"<span>{sha(s)}</span>" for s in noise_rows[:4])
    below = "".join(f"<span>{sha(s)}</span>" for s in noise_rows[4:])
    lines = "".join(f"<span>{fp[i:i + 16]}</span>" for i in range(0, 64, 16))
    return (
        '<figure class="fingerprint">\n'
        f'<div class="hexgrid" aria-hidden="true">{above}</div>\n'
        f'<p class="fp" aria-label="SHA-256 fingerprint {fp}"><code>{lines}</code></p>\n'
        f'<div class="hexgrid" aria-hidden="true">{below}</div>\n'
        '<figcaption><span class="bi"><span lang="eu">Hatz-marka</span><span lang="en">Fingerprint</span></span> '
        'SHA-256 of the canonical source, <a href="/01/monografia-01.md">monografia-01.md</a>. '
        'Verify with <code>shasum -a 256 monografia-01.md</code>. The surrounding rows are the hashes of the abstract and of each section.</figcaption>\n'
        '</figure>'
    )


def inject(html: str, name: str, content: str) -> str:
    pattern = re.compile(rf"<!--cipher:{name}-->.*?<!--/cipher:{name}-->", re.S)
    if not pattern.search(html):
        return html
    return pattern.sub(lambda _: f"<!--cipher:{name}-->{content}<!--/cipher:{name}-->", html)


def main():
    raw = SOURCE.read_bytes()
    md = raw.decode("utf-8")
    fp = hashlib.sha256(raw).hexdigest()
    sections = split_sections(md)

    blocks = {
        "fingerprint": fingerprint_block(fp, sections),
        "fingerprint-short": f'<p class="fp-short"><span class="label">SHA-256 · <span lang="eu">Hatz-marka</span></span> {hexwrap(fp)}</p>',
        "abstract-hash": f'<span class="label">SHA-256 · <span lang="eu">Laburpena</span></span> {hexwrap(sha(sections["abstract"]))}',
        "dh-psi": dh_psi_block(),
        "oprf": oprf_block(),
        "dictionary": dictionary_block(),
    }
    for key, text in sections.items():
        if key.startswith("s"):
            blocks[f"rule-{key}"] = section_rule(int(key[1:]), sha(text))

    for page in PAGES:
        html = page.read_text("utf-8")
        for name, content in blocks.items():
            html = inject(html, name, content)
        page.write_text(html, "utf-8")

    (SOURCE.parent / (SOURCE.name + ".sha256")).write_text(f"{fp}  {SOURCE.name}\n")
    print(f"fingerprint  {fp}")
    for key in sorted(sections, key=lambda k: (k != "abstract", k)):
        print(f"{key:<12} {sha(sections[key])}")


if __name__ == "__main__":
    main()
