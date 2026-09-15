// ─────────────────────────────────────────────────────────────────────────────
// LOAD — reference copy of the four writer queries used by 05_Load_Graph
// Executed from KNIME with UNWIND $batch, one query per Neo4j Writer node.
// LOAD ORDER IS STRICT: wallets -> NFTs -> edges. The edge writers MATCH their
// endpoints and never create them, so a missing wallet silently drops its edges.
// MERGE keys (sale_id / transfer_id) make every re-run idempotent.
// Loaded: 5,948 Wallet · 5,512 NFT · 14,186 SOLD_TO · 7,757 TRANSFERRED
// ─────────────────────────────────────────────────────────────────────────────

// 1. Wallets — distinct union of from_addr / to_addr / buyer / seller
UNWIND $batch AS row
MERGE (w:Wallet {address: row.address});

// 2. NFTs — nft_id = contract:tokenID
UNWIND $batch AS row
MERGE (n:NFT {nft_id: row.nft_id})
SET n.collection = row.collection,
    n.contract   = row.contract,
    n.token_id   = row.tokenID;

// 3a. Priced sales  (marketplace = "LooksRare" AND direction_ok = "ok")
UNWIND $batch AS row
MATCH (s:Wallet {address: row.seller}), (b:Wallet {address: row.buyer})
MERGE (s)-[r:SOLD_TO {sale_id: row.sale_id}]->(b)
SET r.nft_id     = row.nft_id,
    r.price_eth  = row.price_eth,
    r.ts         = row.timeStamp,
    r.strategy   = row.strategy,
    r.event_type = row.event_type,
    r.tx         = row.hash,
    r.log_index  = row.logIndex;

// 3b. Movements — unpriced transfers plus the 9 demoted atomic round-trips
UNWIND $batch AS row
MATCH (f:Wallet {address: row.from_addr}), (t:Wallet {address: row.to_addr})
MERGE (f)-[r:TRANSFERRED {transfer_id: row.transfer_id}]->(t)
SET r.nft_id        = row.nft_id,
    r.ts            = row.timeStamp,
    r.transfer_type = row.transfer_type,
    r.tx            = row.hash;
