# Placeholders: Monografia 01

These values are still missing. Never invent hashes, signatures, CIDs, DOIs or transaction IDs. To find every occurrence:

```sh
grep -rn -E "\[YOUR FULL NAME\]|\[PLACEHOLDER" . --exclude-dir=.git --exclude=PLACEHOLDERS.md
```

## Do these in order

The author's name appears in the canonical source, so filling it in changes the fingerprint. Sign and timestamp only after the text is final.

- [ ] **1. Author name** `[YOUR FULL NAME]`: replace in
  - `01/monografia-01.md` (front matter + footer, 2×)
  - `01/index.html` (byline, `citation_author`, `dc.creator`, JSON-LD, BibTeX, colophon signature, footer, 7×)
  - `index.html` (dateline, JSON-LD, footer, 3×)
  - `license/index.html`, `404.html`, `LICENSE.md` (1× each)
- [ ] **2. Contact address** for commercial-use permission: `license/index.html` → `[PLACEHOLDER: contact address]`
- [ ] **3. Recompute the fingerprint:** `python3 tools/cipher.py`, then commit. From here on, don't edit `01/monografia-01.md`.
- [ ] **4. Signature:** `01/index.html` colophon → `[PLACEHOLDER: PGP signature of monografia-01.md and key fingerprint]`
  - e.g. `gpg --armor --detach-sign 01/monografia-01.md`, publish `01/monografia-01.md.asc`, and show the key fingerprint
- [ ] **5. Timestamp:** `01/index.html` colophon → `[PLACEHOLDER: monografia-01.md.ots]`
  - `ots stamp 01/monografia-01.md`, commit the `.ots` file, and link it (proofs complete after a few hours: run `ots upgrade`)
- [ ] **6. Permanent copies:** `01/index.html` colophon → Arweave `[PLACEHOLDER: transaction ID]` · IPFS `[PLACEHOLDER: CID]`
- [ ] **7. DOI:** `01/index.html` colophon → `[PLACEHOLDER: 10.5281/zenodo.XXXXXXX]`
  - Deposit on Zenodo, then also add `<meta name="citation_doi">` and `doi = {…}` to the BibTeX entry

Steps 4–7 only touch `01/index.html`, so the fingerprint stays the same.

## Other open items

- [ ] **HTTPS:** Cloudflare proxies the domain. Set SSL/TLS → *Full* and turn on *Always Use HTTPS*, or switch the DNS records to DNS-only so GitHub can issue a certificate and enforce HTTPS.
- [ ] **Euskara review:** have a native speaker check the labels and section titles (Laburpen-funtzioak ez dira nahikoa, Oinarriak, Funtzio sasiausazko itsuak, Zifratze homomorfikoa, PSIk agintzen ez duena, Protokoloa aukeratzea, …).
- [ ] **Provenance:** the essay text was drafted by Claude (AI). Keep the disclosure, or remove it only if you replace the text with your own writing.
- [ ] **Expiry:** Monografia 01 expires on 2027-10-10. Decide what happens on that date.
