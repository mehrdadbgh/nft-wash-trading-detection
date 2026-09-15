// ─────────────────────────────────────────────────────────────────────────────
// TOKEN DOMINANCE — which wallet pair controls each token
// Returns the highest-volume pair per token. dominance_pct (computed downstream
// as top_pair_sales / sales) separates the typologies at token level:
//   ~90-100%  bilateral mill — one pair owns the token's entire history
//   ~20%      mesh inventory — spread evenly across ~5 qualifying pairs
//   <12%      distributed federation — many small pairs, no coordinator
//
// Returns: 808 rows.
//
// KNOWN LIMIT: this measures PAIR control, so it systematically understates
// coordinated multi-wallet clusters. The mesh's seven tokens read ~20% here and
// 100% at cluster level. Mesh membership is therefore applied as an override in
// the classification rules rather than inferred from this percentage.
// ─────────────────────────────────────────────────────────────────────────────

MATCH (a:Wallet)-[s:SOLD_TO]-(b:Wallet)
WHERE a.address < b.address
WITH s.nft_id AS nft, a.address AS wa, b.address AS wb, count(s) AS pair_sales
ORDER BY nft, pair_sales DESC
WITH nft, collect({a: wa, b: wb, n: pair_sales})[0] AS top
RETURN nft      AS nft_id,
       top.a    AS top_pair_a,
       top.b    AS top_pair_b,
       top.n    AS top_pair_sales;
