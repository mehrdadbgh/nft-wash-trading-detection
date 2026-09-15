// ─────────────────────────────────────────────────────────────────────────────
// SCHEMA — run once per database, before any load
// Two uniqueness constraints (which auto-create their backing indexes) and two
// relationship indexes. All use IF NOT EXISTS, so they are safe to re-run.
// Constraints must exist before loading: without them every MERGE is a table
// scan and the 22k-relationship load crawls.
// In KNIME these run one statement per row via a Table Creator — the Neo4j
// node rejects multi-statement scripts.
// ─────────────────────────────────────────────────────────────────────────────

CREATE CONSTRAINT wallet_address IF NOT EXISTS FOR (w:Wallet) REQUIRE w.address IS UNIQUE;
CREATE CONSTRAINT nft_id IF NOT EXISTS FOR (n:NFT) REQUIRE n.nft_id IS UNIQUE;
CREATE INDEX sold_to_sale_id IF NOT EXISTS FOR ()-[r:SOLD_TO]-() ON (r.sale_id);
CREATE INDEX transferred_id IF NOT EXISTS FOR ()-[r:TRANSFERRED]-() ON (r.transfer_id);
