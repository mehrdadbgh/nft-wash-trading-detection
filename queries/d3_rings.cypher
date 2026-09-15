// ─────────────────────────────────────────────────────────────────────────────
// D3 — TRADING RINGS (3-wallet cycles)
// A token travels A -> B -> C -> A, chronologically, with all three legs moving
// the SAME token. Returns one row per (trio, token) with the trade count on
// each leg.
//
// Returns: 107 rows — 46 distinct wallets across 24 tokens, dominated by one
// six-wallet mesh cluster cycling seven Meebits.
//
// THREE CONSTRAINTS THAT MATTER:
//   s1.ts < s2.ts < s3.ts   the token actually travelled the loop; without it
//                            a reverse-chronology "ring" is reported
//   same nft_id on all legs  otherwise unrelated trades form fake cycles
//   a.address < ... < c      canonical ordering, so each ring appears once
//
// DO NOT use a variable-length form (-[:SOLD_TO*3..5]->). Parallel edges between
// wash-trading wallets make path enumeration combinatorial — one pair with 250
// edges generates billions of paths and the query never returns.
// ─────────────────────────────────────────────────────────────────────────────

MATCH (a:Wallet)-[s1:SOLD_TO]->(b:Wallet)-[s2:SOLD_TO]->(c:Wallet)-[s3:SOLD_TO]->(a)
WHERE a.address < b.address AND a.address < c.address AND b <> c
  AND s1.nft_id = s2.nft_id AND s2.nft_id = s3.nft_id
  AND s1.ts < s2.ts AND s2.ts < s3.ts
WITH DISTINCT a, b, c, s1.nft_id AS nft
MATCH (a)-[x:SOLD_TO]->(b) WHERE x.nft_id = nft
WITH a, b, c, nft, count(x) AS ab
MATCH (b)-[y:SOLD_TO]->(c) WHERE y.nft_id = nft
WITH a, b, c, nft, ab, count(y) AS bc
MATCH (c)-[z:SOLD_TO]->(a) WHERE z.nft_id = nft
RETURN a.address AS w_a, b.address AS w_b, c.address AS w_c,
       nft AS nft_id, ab, bc, count(z) AS ca
ORDER BY ab + bc + ca DESC;
