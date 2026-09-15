// ─────────────────────────────────────────────────────────────────────────────
// D2 — PING-PONG
// The same token traded back and forth between two wallets. Aggregated by pair
// and token: fwd and bwd are the trade counts in each direction, round_trips is
// the smaller of the two (a completed cycle needs both legs).
//
// Threshold: >= 2 completed round trips in each direction.
// Returns: 423 pair-token combinations.
// a.address < b.address prevents each pair being reported twice.
//
// WHY AGGREGATED: the naive form — pairing every sale with every later return —
// is O(n^2) and returns ~65,000 rows for a single heavily-washed token.
// ─────────────────────────────────────────────────────────────────────────────

MATCH (a:Wallet)-[s:SOLD_TO]->(b:Wallet)
WITH a, b, s.nft_id AS nft, count(s) AS fwd
MATCH (b)-[s2:SOLD_TO]->(a) WHERE s2.nft_id = nft
WITH a, b, nft, fwd, count(s2) AS bwd
WHERE a.address < b.address AND fwd >= 2 AND bwd >= 2
RETURN a.address AS wallet_a,
       b.address AS wallet_b,
       nft       AS nft_id,
       fwd, bwd,
       CASE WHEN fwd < bwd THEN fwd ELSE bwd END AS round_trips
ORDER BY round_trips DESC;
