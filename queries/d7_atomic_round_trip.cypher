// ─────────────────────────────────────────────────────────────────────────────
// D7 — ATOMIC ROUND-TRIP
// An NFT sold and returned to its seller INSIDE ONE TRANSACTION (s.tx = t.tx),
// routed through a proxy contract. Net ownership change is zero; the platform
// still records the volume and pays rewards on it.
//
// Returns: 9 rows — 2 origin wallets, ~9,005 ETH cycled.
//   Terraforms #8099: one origin, one proxy, 4 identical round trips at 2,000 ETH
//   Terraforms #2005: one origin, TWO proxy contracts, 5 trips at 250/5 ETH
//
// HOW THESE WERE FOUND: not by this query. They surfaced as disagreements in a
// cross-endpoint data-quality check — tokennfttx said the token moved somewhere
// getLogs did not expect. A validation step acted as a zeroth detector.
//
// Requires BOTH edge types, which is why unpriced movements are kept in the
// graph: the return leg is a TRANSFERRED edge, not a sale.
// ─────────────────────────────────────────────────────────────────────────────

MATCH (a:Wallet)-[s:SOLD_TO]->(m:Wallet)-[t:TRANSFERRED]->(a)
WHERE s.tx = t.tx
RETURN a.address AS origin,
       m.address AS proxy,
       s.nft_id  AS nft_id,
       s.price_eth AS price_eth,
       s.tx      AS tx
ORDER BY s.price_eth DESC;
