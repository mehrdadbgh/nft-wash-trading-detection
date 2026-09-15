// ─────────────────────────────────────────────────────────────────────────────
// D4 — TOKEN STATISTICS / RAPID FLIP
// Sales count, volume and price range per token. The rapid-flip threshold is
// applied downstream so this stays the raw feed and also supplies denominators.
//
// Returns: 808 rows (every token sold at least once).
// Key result: 53 tokens with >= 50 sales carry 9,458 sales — 66.7% of ALL
// marketplace activity in scope. 1% of tokens that moved; 6.6% of tokens sold.
//
// Note the price range as a signal: wash-milled tokens span three orders of
// magnitude (0.30 to 788 ETH on one token), while distributed operations keep
// prices in a narrow, plausible band.
//
// hildobby's filter_3 uses a 3-purchase threshold against this project's 50 —
// the main source of divergence in flag rates between the two methods.
// ─────────────────────────────────────────────────────────────────────────────

MATCH ()-[s:SOLD_TO]->()
RETURN s.nft_id AS nft_id,
       count(s) AS sales,
       round(sum(s.price_eth)) AS volume_eth,
       min(s.price_eth) AS min_price,
       max(s.price_eth) AS max_price,
       count(DISTINCT s.tx) AS distinct_txs
ORDER BY sales DESC;
