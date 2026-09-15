// ─────────────────────────────────────────────────────────────────────────────
// FUNDING TARGETS — which wallets to resolve first-funder for
// Union of: wallets in concentrated pairs (>= 20 trades AND >= 50% of at least
// one side's activity), the distributed federation around token #8319, and
// three named wallets identified during manual review.
//
// Returns: 302 addresses. The six mesh-cluster wallets are added from a second
// reader and concatenated in KNIME — they do not appear here, because the mesh
// keeps every pair below the 50% threshold by design.
//
// Fetching all 5,948 wallets would cost ~5,900 API calls for no analytical gain;
// attribution only matters where a structural detector already fired.
// ─────────────────────────────────────────────────────────────────────────────

MATCH (a:Wallet)-[s:SOLD_TO]-(b:Wallet)
WHERE a.address < b.address
WITH a, b, count(s) AS pt
WHERE pt >= 20
WITH a, b, pt,
     COUNT { (a)-[:SOLD_TO]-() } AS at,
     COUNT { (b)-[:SOLD_TO]-() } AS bt
WHERE 100.0*pt/at >= 50 OR 100.0*pt/bt >= 50
UNWIND [a.address, b.address] AS w
WITH collect(DISTINCT w) AS pair_wallets

CALL {
  MATCH (x:Wallet)-[r:SOLD_TO]-()
  WHERE r.nft_id ENDS WITH ":8319"
  RETURN collect(DISTINCT x.address) AS fed
}

WITH pair_wallets + fed AS combined
WITH combined + ["0x6e82d57018bc95ef6d8b82bdc42449f77941dc32",
                 "0x3bfe8b28de68aba3723b801f5d0f0d10a701293c",
                 "0x18a4489a739ac9835da14e006b35d65040e53a4a"] AS all_w
UNWIND all_w AS addr
RETURN DISTINCT addr AS address;


// ── Mesh cluster wallets (second reader, concatenated with the above) ────────
MATCH (w:Wallet)
WHERE w.address STARTS WITH "0x140793" OR w.address STARTS WITH "0x2edadf"
   OR w.address STARTS WITH "0xcaee6d" OR w.address STARTS WITH "0x26c01a"
   OR w.address STARTS WITH "0xc32575" OR w.address STARTS WITH "0xc02201"
RETURN w.address AS address;
