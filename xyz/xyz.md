---
title: "XYZ: Cryptography and Private Set Intersection Protocols"
series: monografiak.works
number: 1
date: 2026-10-10
version: "1.0"
language: en
canonical: https://monografiak.works/xyz/
license: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
attribution: "XYZ — monografiak.works, https://monografiak.works/xyz/"
---

# XYZ

*Cryptography and Private Set Intersection Protocols: how two parties find what they have in common without revealing anything else.*

## Abstract

Private set intersection (PSI) lets two parties, each holding a set, learn the elements they share and nothing more. It sits behind contact discovery in messaging apps, leaked-password checks and privacy-preserving advertising measurement. This monograph explains why the obvious approach (comparing hashes) fails, then builds up the three main protocol families: Diffie–Hellman PSI, PSI from oblivious pseudorandom functions, and PSI from homomorphic encryption. It also sets out what these protocols do and do not protect against.

## 1. The problem

Two parties, Alice and Bob, each hold a private set. Alice holds $X$ with $n$ elements and Bob holds $Y$ with $m$ elements. Alice wants to compute

$$
X \cap Y = \{\, z : z \in X \text{ and } z \in Y \,\} \tag{1}
$$

She must learn nothing about the elements of $Y$ outside the intersection, and Bob must learn nothing about $X$ at all. The only things that may leak are the set sizes $n$ and $m$.

The problem shows up wherever two organisations or devices need to match records they are not allowed, or not willing, to share:

- **Contact discovery.** A messaging app wants to tell you which of your contacts already use it without uploading your address book.
- **Compromised credentials.** A browser checks whether your password appears in a breach corpus without disclosing the password.
- **Advertising measurement.** An advertiser and a publisher count how many people who saw an ad later bought the product, without exchanging customer lists.
- **Public health and finance.** Institutions cross-check watch lists or patient registries under strict data-protection rules.

## 2. Why hashing is not enough

The usual first attempt is for Bob to send $H(y)$ for every $y \in Y$, where $H$ is a cryptographic hash function such as SHA-256. Alice hashes her own elements and compares. Hashes cannot be inverted, so this looks private.

It is not. A hash hides its input only when the input is hard to guess. Phone numbers, e-mail addresses and national identifiers come from small, enumerable universes. With a universe $U$, Alice can recover all of $Y$ by brute force at a cost of

$$
|U| \text{ hash evaluations;}\quad |U| \approx 10^{10} \text{ for phone numbers.} \tag{2}
$$

Ten billion SHA-256 evaluations take a few seconds on a single modern GPU. Salting doesn't help, because both sides need the same salt for the comparison to work. Hashing hides structure. It doesn't hide *low-entropy* data.

> **Note.** PSI protocols remove the dictionary attack by making the value Alice compares depend on a secret that only Bob holds. Without Bob's participation, Alice cannot test a guess.

## 3. Preliminaries

Let $\mathbb{G}$ be a cyclic group of prime order $q$ with generator $g$. In practice this is an elliptic-curve group such as ristretto255 or P-256. We also need a hash function $H : \{0,1\}^* \to \mathbb{G}$ that maps arbitrary strings to group elements. It is standardised as *hash-to-curve* in RFC 9380 [9].

**Definition 1 (Decisional Diffie–Hellman).** For uniformly random $a, b, c \in \mathbb{Z}_q$, no efficient algorithm can distinguish

$$
(g, g^a, g^b, g^{ab}) \;\approx_c\; (g, g^a, g^b, g^c) \tag{3}
$$

where $\approx_c$ denotes computational indistinguishability.

Security is defined by comparison with an ideal world. In that world a trusted third party receives $X$ and $Y$ and returns $X \cap Y$ to Alice. A protocol is secure if anything a participant learns from a real run, it could also have computed from its own input and the ideal output. A *semi-honest* adversary follows the protocol but tries to learn more from the transcript. A *malicious* adversary may deviate arbitrarily.

## 4. Diffie–Hellman PSI

The oldest PSI protocol traces back to Meadows [1] and to Huberman, Franklin and Hogg [2]. It rests on one algebraic fact: exponentiation in $\mathbb{G}$ commutes.

$$
\bigl(H(x)^a\bigr)^b = H(x)^{ab} = \bigl(H(x)^b\bigr)^a \tag{4}
$$

Alice picks a secret $a$ and Bob a secret $b$, both uniform in $\mathbb{Z}_q$. An element blinded by both exponents comes out the same whichever order the exponents were applied in. Without the exponents, however, a blinded value looks random. Figure 1 shows the exchange.

![Figure 1. Message flow of Diffie–Hellman PSI. Alice sends one message and Bob replies once. The intersection is found locally by Alice in step 3.](https://monografiak.works/xyz/figures/dh-psi.svg)

1. Alice sends $u_i = H(x_i)^a$ for each $x_i \in X$.
2. Bob replies with $u_i^b$ in the original order, so Alice can tell which value belongs to which $x_i$. He also sends $v_j = H(y_j)^b$ for each $y_j \in Y$, randomly permuted.
3. Alice computes $v_j^a$. If $u_i^b = v_j^a$ for some $j$, then $x_i \in X \cap Y$.

Each party performs $n + m$ exponentiations, and the parties exchange $2n + m$ group elements in total. Against semi-honest adversaries the protocol is secure under the DDH assumption when $H$ is modelled as a random oracle. Bob sees only values of the form $H(x)^a$, which look random. Alice sees $H(y)^b$ for every $y$, but she cannot test a guess $y'$ without knowing $b$. That closes the dictionary attack from §2.

The protocol fits in a page of code and needs only a standard elliptic-curve library. It still runs in production today, for example in Google's *Private Join and Compute* [7].

## 5. PSI from oblivious pseudorandom functions

A pseudorandom function $F_k$ is a keyed function whose outputs look random to anyone without $k$. It is *oblivious* (an OPRF) when two parties evaluate it together, with the following roles:

$$
\underset{\text{Bob}}{(k)},\ \underset{\text{Alice}}{(x)} \;\longmapsto\; \underset{\text{Bob}}{(\bot)},\ \underset{\text{Alice}}{(F_k(x))} \tag{5}
$$

Bob learns nothing and Alice learns only the output. PSI follows directly. Bob publishes $\{F_k(y) : y \in Y\}$. Alice obtains $F_k(x)$ for each of her elements through the OPRF and checks for membership.

The Diffie–Hellman construction is itself an OPRF, standardised in RFC 9497 [10]:

$$
F_k(x) = H'\bigl(x,\, H(x)^k\bigr) \tag{6}
$$

Alice never reveals $x$. She sends the blinded value $H(x)^r$ for a random $r$, Bob applies his key to get $\bigl(H(x)^r\bigr)^k$, and Alice removes the blind by raising the result to $r^{-1} \bmod q$.

For very large sets, the fastest protocols avoid public-key operations on each element. Pinkas, Schneider and Zohner [4] built PSI from *oblivious transfer extension*, which turns a small number of public-key operations into millions of cheap symmetric ones. Kolesnikov et al. [5] recast this as a batched OPRF. Later work based on vector oblivious linear evaluation (VOLE) [8] reduces communication further. These protocols intersect sets of millions of elements in seconds on a fast network.

## 6. PSI from homomorphic encryption

Freedman, Nissim and Pinkas [3] encode Alice's set as the roots of a polynomial:

$$
P(z) = \prod_{i=1}^{n} (z - x_i) = \sum_{i=0}^{n} \alpha_i z^i \tag{7}
$$

Alice encrypts the coefficients $\alpha_i$ under an additively homomorphic scheme such as Paillier and sends them to Bob. Bob can evaluate the encrypted polynomial at his own points without decrypting anything. For each $y \in Y$, with fresh randomness $\rho$, he returns

$$
\mathrm{Enc}\bigl(\rho \cdot P(y) + y\bigr) \tag{8}
$$

If $y \in X$ then $P(y) = 0$ and Alice decrypts $y$ itself. Otherwise she decrypts a uniformly random value. Bucketing with hashing keeps the cost from growing as $n \cdot m$.

Modern lattice-based homomorphic encryption makes this approach effective for *unbalanced* PSI, where a phone with a few hundred contacts queries a server holding hundreds of millions of records. Chen, Laine and Rindal [6] give a protocol whose communication is linear in the small set and only logarithmic in the large one.

## 7. What PSI does not promise

PSI computes a function. It does not judge whether revealing that function's output is wise. Three limits are worth stating plainly:

1. **Input choice is free.** No protocol stops Alice from putting every phone number in a city into $X$. The output then reveals exactly which of those numbers are in $Y$. Deployments defend against this outside the cryptography: they cap set sizes, rate-limit queries, or attest the client.
2. **Sizes leak.** Standard protocols reveal $n$ and $m$. Padding with dummy elements hides the true sizes at extra cost.
3. **The output may be too much.** Often only the size $|X \cap Y|$ (PSI-cardinality) or an aggregate over matched records (PSI-sum [7]) is needed. Asking for the narrower function is the cheapest privacy gain there is.

## 8. Choosing a protocol

| Family | Core primitive | Communication | Best suited to |
|---|---|---|---|
| Diffie–Hellman [1] [2] | Group exponentiation | Linear, in group elements | Simplicity, low bandwidth, small to medium sets |
| OT / VOLE OPRF [5] [8] | Symmetric crypto + OT extension | Linear, small constants | Very large balanced sets on fast networks |
| Lattice HE [6] | Leveled homomorphic encryption | Linear in small set, logarithmic in large | Unbalanced: light client, huge server |
| Polynomial / Paillier [3] | Additive homomorphic encryption | Linear, in ciphertexts | Historical foundation; teaching |

*Table 1. The main PSI families compared qualitatively. Concrete performance depends on the implementation, the network and the security model.*

Diffie–Hellman PSI over a modern curve is the right default for most first deployments. It is easy to audit, it is built from standardised parts (RFC 9380, RFC 9497), and its cost is predictable. Move to OT- or VOLE-based protocols when the sets reach millions of elements, and to homomorphic encryption when one side is far smaller than the other.

## References

1. C. Meadows. "A More Efficient Cryptographic Matchmaking Protocol for Use in the Absence of a Continuously Available Third Party." *IEEE Symposium on Security and Privacy*, 1986.
2. B. A. Huberman, M. Franklin, T. Hogg. "Enhancing Privacy and Trust in Electronic Communities." *ACM Conference on Electronic Commerce*, 1999.
3. M. J. Freedman, K. Nissim, B. Pinkas. "Efficient Private Matching and Set Intersection." *EUROCRYPT*, 2004.
4. B. Pinkas, T. Schneider, M. Zohner. "Faster Private Set Intersection Based on OT Extension." *USENIX Security Symposium*, 2014.
5. V. Kolesnikov, R. Kumaresan, M. Rosulek, N. Trieu. "Efficient Batched Oblivious PRF with Applications to Private Set Intersection." *ACM CCS*, 2016.
6. H. Chen, K. Laine, P. Rindal. "Fast Private Set Intersection from Homomorphic Encryption." *ACM CCS*, 2017.
7. M. Ion, B. Kreuter, A. E. Nergiz, S. Patel, S. Saxena, K. Seth, M. Raykova, D. Shanahan, M. Yung. "On Deploying Secure Computing: Private Intersection-Sum-with-Cardinality." *IEEE EuroS&P*, 2020.
8. P. Rindal, P. Schoppmann. "VOLE-PSI: Fast OPRF and Circuit-PSI from Vector-OLE." *EUROCRYPT*, 2021.
9. A. Faz-Hernández, S. Scott, N. Sullivan, R. S. Wahby, C. A. Wood. "Hashing to Elliptic Curves." RFC 9380, 2023. https://www.rfc-editor.org/rfc/rfc9380
10. A. Davidson, A. Faz-Hernández, N. Sullivan, C. A. Wood. "Oblivious Pseudorandom Functions (OPRFs) Using Prime-Order Groups." RFC 9497, 2023. https://www.rfc-editor.org/rfc/rfc9497

---

© 2026 monografiak.works. Licensed under CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/
