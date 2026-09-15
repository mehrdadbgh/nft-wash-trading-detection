// ─────────────────────────────────────────────────────────────────────────────
// D8 — PAIR CONCENTRATION
// For every wallet pair with >= 20 trades between them: how much of each
// wallet's total activity that single counterparty represents, plus the token
// spread.
//
// Returns: 139 rows (raw feed — the 50% concentration threshold is applied in
// KNIME so scoring can tune it without re-querying).
//
// INTENSITY = trades / distinct tokens. This column exists because of a
// synthetic decoy: a legitimate bulk seller (30 different NFTs, one buyer, one
// direction) fires concentration alone. Wash mills score 100-500 on intensity;
// legitimate bulk trading scores ~1.
//
// KNOWN BLIND SPOT: mesh clusters spread trades across 4-5 partners, so no
// single pair crosses 50%. The six-wallet mesh in this dataset reads 28-40%
// concentration while controlling 100% of its seven tokens. D3 catches it;
// this query structurally cannot.
// ─────────────────────────────────────────────────────────────────────────────

MATCH (a:Wallet)-[s:SOLD_TO]-(b:Wallet)
WHERE a.address < b.address
WITH a, b, count(s) AS pair_trades,
     sum(s.price_eth) AS pair_volume,
     count(DISTINCT s.nft_id) AS pair_tokens
WHERE pair_trades >= 20
WITH a, b, pair_trades, pair_volume, pair_tokens,
     COUNT { (a)-[:SOLD_TO]-() } AS a_total,
     COUNT { (b)-[:SOLD_TO]-() } AS b_total
RETURN a.address AS wallet_a,
       b.address AS wallet_b,
       pair_trades,
       round(pair_volume) AS pair_volume_eth,
       pair_tokens,
       round(100.0*pair_trades/a_total) AS pct_a,
       round(100.0*pair_trades/b_total) AS pct_b,
       round(1.0*pair_trades/pair_tokens) AS intensity
ORDER BY pair_trades DESC;
