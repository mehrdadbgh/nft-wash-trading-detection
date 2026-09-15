// ─────────────────────────────────────────────────────────────────────────────
// FUNDING ATTRIBUTION — trading pairs under common control
// Wallet pairs that (a) trade with each other and (b) share a first funder that
// is NOT a labelled exchange.
//
// REQUIRES funding_labels.cypher to have run. Without the :Exchange exclusion
// this returns 23 rows, most of them meaningless.
//
// Returns: 10 rows — 684 trades (4.8% of all sales), 20 wallets.
// Every attributed funder seeded EXACTLY TWO wallets. That uniformity is itself
// evidence: it is a setup procedure, not a coincidence.
//
// HONEST LIMIT: the largest operations are absent. The highest-volume pair in
// the dataset (1,541 trades) and the mesh cluster were funded independently
// through exchanges, so no link exists to find. Detection substantially
// outperforms attribution.
// ─────────────────────────────────────────────────────────────────────────────

MATCH (a:Wallet)-[:FUNDED_BY]->(f:Funder)<-[:FUNDED_BY]-(b:Wallet)
WHERE a.address < b.address AND NOT f:Exchange
MATCH (a)-[s:SOLD_TO]-(b)
RETURN a.address  AS wallet_a,
       b.address  AS wallet_b,
       f.address  AS funder,
       f.name_tag AS funder_tag,
       count(s)   AS trades,
       round(sum(s.price_eth)) AS volume_eth
ORDER BY volume_eth DESC;
