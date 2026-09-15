// ─────────────────────────────────────────────────────────────────────────────
// D1 — SELF-SALE
// Buyer and seller are the same address. The crudest wash pattern and, in this
// dataset, the rarest: LooksRare v1 did not block maker = taker, yet only one
// operator used it. Every other wash structure here uses two or more wallets.
//
// Returns: 1 row (iven.eth, Meebit #16938, 5,238.98 WETH)
// Note: the seller received 5,134.22 back — net cost was the 104.78 WETH fee.
// hildobby's filter_1_same_buyer_seller returns the same single trade.
// ─────────────────────────────────────────────────────────────────────────────

MATCH (w:Wallet)-[s:SOLD_TO]->(w)
RETURN w.address AS wallet,
       s.nft_id  AS nft_id,
       s.price_eth AS price_eth,
       s.tx      AS tx
ORDER BY s.price_eth DESC;
