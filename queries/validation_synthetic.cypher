// ─────────────────────────────────────────────────────────────────────────────
// VALIDATION — synthetic injection
// The only test that can prove RECALL, because the answers are known by
// construction. Real data can never prove what a detector missed.
//
// Injects three positive patterns and three decoys under a :TestWallet label,
// runs the detectors, then deletes everything. All fake tokens use the prefix
// "0xtest:" so leakage is trivially visible.
//
// RESULT OF THIS SUITE:
//   D1 returned the self-sale only                            PASS
//   D2 returned the ping-pong pair at fwd=3 bwd=3             PASS
//   D3 returned the ring trio only — both decoys rejected     PASS
//   D8 flagged the bulk seller (30 tokens, intensity 1)       EXPECTED
//
// The bulk-seller decoy firing D8 is the point, not a failure: it established
// trades-per-distinct-token as a scoring feature. Wash mills score 100-500 on
// that ratio; this decoy scores 1.
// ─────────────────────────────────────────────────────────────────────────────

// ── POSITIVE 1: self-sale (must fire D1) ─────────────────────────────────────
CREATE (s1:TestWallet:Wallet {address:"0xtest_self_01"});
MATCH (s1:TestWallet {address:"0xtest_self_01"})
CREATE (s1)-[:SOLD_TO {sale_id:"t_self_1", nft_id:"0xtest:100", price_eth:50.0,
       ts:datetime("2022-02-01T10:00:00Z"), tx:"0xtest_tx_1"}]->(s1);

// ── POSITIVE 2: ping-pong, 3 round trips on one token (must fire D2) ─────────
CREATE (p1:TestWallet:Wallet {address:"0xtest_pong_01"}),
       (p2:TestWallet:Wallet {address:"0xtest_pong_02"});
MATCH (p1:TestWallet {address:"0xtest_pong_01"}), (p2:TestWallet {address:"0xtest_pong_02"})
FOREACH (i IN range(1,3) |
  CREATE (p1)-[:SOLD_TO {sale_id:"t_pp_f"+i, nft_id:"0xtest:200", price_eth:20.0,
         ts:datetime("2022-02-02T10:00:00Z") + duration({hours: 2*i}), tx:"0xtest_pp_f"+i}]->(p2)
  CREATE (p2)-[:SOLD_TO {sale_id:"t_pp_b"+i, nft_id:"0xtest:200", price_eth:21.0,
         ts:datetime("2022-02-02T11:00:00Z") + duration({hours: 2*i}), tx:"0xtest_pp_b"+i}]->(p1));

// ── POSITIVE 3: chronological 3-wallet ring, same token (must fire D3) ───────
CREATE (r1:TestWallet:Wallet {address:"0xtest_ring_01"}),
       (r2:TestWallet:Wallet {address:"0xtest_ring_02"}),
       (r3:TestWallet:Wallet {address:"0xtest_ring_03"});
MATCH (r1:TestWallet {address:"0xtest_ring_01"}), (r2:TestWallet {address:"0xtest_ring_02"}),
      (r3:TestWallet {address:"0xtest_ring_03"})
CREATE (r1)-[:SOLD_TO {sale_id:"t_r1", nft_id:"0xtest:300", price_eth:30.0,
       ts:datetime("2022-02-03T10:00:00Z"), tx:"0xtest_r1"}]->(r2),
       (r2)-[:SOLD_TO {sale_id:"t_r2", nft_id:"0xtest:300", price_eth:31.0,
       ts:datetime("2022-02-03T11:00:00Z"), tx:"0xtest_r2"}]->(r3),
       (r3)-[:SOLD_TO {sale_id:"t_r3", nft_id:"0xtest:300", price_eth:32.0,
       ts:datetime("2022-02-03T12:00:00Z"), tx:"0xtest_r3"}]->(r1);

// ── DECOY A: 3-wallet loop, DIFFERENT tokens (must NOT fire D3) ──────────────
CREATE (d1:TestWallet:Wallet {address:"0xtest_decoy_01"}),
       (d2:TestWallet:Wallet {address:"0xtest_decoy_02"}),
       (d3:TestWallet:Wallet {address:"0xtest_decoy_03"});
MATCH (d1:TestWallet {address:"0xtest_decoy_01"}), (d2:TestWallet {address:"0xtest_decoy_02"}),
      (d3:TestWallet {address:"0xtest_decoy_03"})
CREATE (d1)-[:SOLD_TO {sale_id:"t_d1", nft_id:"0xtest:401", price_eth:5.0,
       ts:datetime("2022-02-04T10:00:00Z"), tx:"0xtest_d1"}]->(d2),
       (d2)-[:SOLD_TO {sale_id:"t_d2", nft_id:"0xtest:402", price_eth:6.0,
       ts:datetime("2022-02-04T11:00:00Z"), tx:"0xtest_d2"}]->(d3),
       (d3)-[:SOLD_TO {sale_id:"t_d3", nft_id:"0xtest:403", price_eth:7.0,
       ts:datetime("2022-02-04T12:00:00Z"), tx:"0xtest_d3"}]->(d1);

// ── DECOY B: reverse-chronology ring, same token (must NOT fire D3) ──────────
CREATE (x1:TestWallet:Wallet {address:"0xtest_rev_01"}),
       (x2:TestWallet:Wallet {address:"0xtest_rev_02"}),
       (x3:TestWallet:Wallet {address:"0xtest_rev_03"});
MATCH (x1:TestWallet {address:"0xtest_rev_01"}), (x2:TestWallet {address:"0xtest_rev_02"}),
      (x3:TestWallet {address:"0xtest_rev_03"})
CREATE (x1)-[:SOLD_TO {sale_id:"t_x1", nft_id:"0xtest:500", price_eth:9.0,
       ts:datetime("2022-02-05T12:00:00Z"), tx:"0xtest_x1"}]->(x2),
       (x2)-[:SOLD_TO {sale_id:"t_x2", nft_id:"0xtest:500", price_eth:9.0,
       ts:datetime("2022-02-05T11:00:00Z"), tx:"0xtest_x2"}]->(x3),
       (x3)-[:SOLD_TO {sale_id:"t_x3", nft_id:"0xtest:500", price_eth:9.0,
       ts:datetime("2022-02-05T10:00:00Z"), tx:"0xtest_x3"}]->(x1);

// ── DECOY C: legitimate one-way bulk seller, 30 tokens (fires D8 by design) ──
CREATE (b1:TestWallet:Wallet {address:"0xtest_bulk_01"}),
       (b2:TestWallet:Wallet {address:"0xtest_bulk_02"});
MATCH (b1:TestWallet {address:"0xtest_bulk_01"}), (b2:TestWallet {address:"0xtest_bulk_02"})
FOREACH (i IN range(1,30) |
  CREATE (b1)-[:SOLD_TO {sale_id:"t_bulk"+i, nft_id:"0xtest:6"+i, price_eth:3.0,
         ts:datetime("2022-02-06T10:00:00Z") + duration({hours:i}), tx:"0xtest_bulk"+i}]->(b2));

// ── VERIFY injection: expect 46 test relationships ───────────────────────────
// MATCH ()-[r:SOLD_TO]->() WHERE r.nft_id STARTS WITH "0xtest" RETURN count(r);

// ── CLEANUP — run after every test pass, then re-verify baseline counts ──────
// MATCH (n:TestWallet) DETACH DELETE n;
// MATCH ()-[r:SOLD_TO]->() RETURN count(r);   // must return 14,186
