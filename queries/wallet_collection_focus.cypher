// ─────────────────────────────────────────────────────────────────────────────
// WALLET COLLECTION FOCUS
// Each wallet's dominant collection by trade count. Mapped to readable names
// downstream (Meebits / Terraforms / Loot).
//
// Used for the per-typology segmentation finding: ring and mesh topologies are
// overwhelmingly Meebits (11 of 13 ring members), while the largest bilateral
// mills are Terraforms. Different collections attracted different toolkits.
// ─────────────────────────────────────────────────────────────────────────────

MATCH (w:Wallet)-[s:SOLD_TO]-()
WITH w, split(s.nft_id, ":")[0] AS contract, count(s) AS n
ORDER BY w.address, n DESC
WITH w, collect(contract)[0] AS top_contract
RETURN w.address AS wallet, top_contract;
