// ─────────────────────────────────────────────────────────────────────────────
// SUMMARY STATISTICS — graph-level headline figures as metric/value rows
// Deliberately COMPUTED rather than hardcoded: re-running the pipeline on a
// different scope updates every figure automatically, which is what makes the
// negative-control comparison trustworthy.
//
// Returns: 11 rows. KNIME concatenates three further GroupBy branches
// (structure_*, confidence_*, token_*) for the 26-row summary_stats.csv.
// ─────────────────────────────────────────────────────────────────────────────

CALL {MATCH ()-[s:SOLD_TO]->() RETURN count(s) AS v}
WITH "total_sales" AS metric, toString(v) AS value RETURN metric, value
UNION ALL
CALL {MATCH ()-[t:TRANSFERRED]->() RETURN count(t) AS v}
WITH "total_transfers" AS metric, toString(v) AS value RETURN metric, value
UNION ALL
CALL {MATCH (w:Wallet) RETURN count(w) AS v}
WITH "wallets_in_graph" AS metric, toString(v) AS value RETURN metric, value
UNION ALL
CALL {MATCH (n:NFT) RETURN count(n) AS v}
WITH "tokens_that_moved" AS metric, toString(v) AS value RETURN metric, value
UNION ALL
CALL {MATCH ()-[s:SOLD_TO]->() RETURN count(DISTINCT s.nft_id) AS v}
WITH "tokens_ever_sold" AS metric, toString(v) AS value RETURN metric, value
UNION ALL
CALL {MATCH ()-[s:SOLD_TO]->() RETURN toInteger(round(sum(s.price_eth))) AS v}
WITH "total_volume_eth" AS metric, toString(v) AS value RETURN metric, value
UNION ALL
CALL {MATCH ()-[s:SOLD_TO]->() WITH s.nft_id AS n, count(s) AS c WHERE c >= 50 RETURN count(*) AS v}
WITH "tokens_50plus_sales" AS metric, toString(v) AS value RETURN metric, value
UNION ALL
CALL {MATCH ()-[s:SOLD_TO]->() WITH s.nft_id AS n, count(s) AS c WHERE c >= 50 RETURN sum(c) AS v}
WITH "sales_in_top50plus_tokens" AS metric, toString(v) AS value RETURN metric, value
UNION ALL
CALL {MATCH (a:Wallet)-[:FUNDED_BY]->(f:Funder)<-[:FUNDED_BY]-(b:Wallet)
      WHERE a.address < b.address AND NOT f:Exchange
      MATCH (a)-[:SOLD_TO]-(b) WITH a, b
      RETURN count(DISTINCT a.address + ":" + b.address) AS v}
WITH "attributed_operator_pairs" AS metric, toString(v) AS value RETURN metric, value
UNION ALL
CALL {MATCH (a:Wallet)-[:FUNDED_BY]->(f:Funder)<-[:FUNDED_BY]-(b:Wallet)
      WHERE a.address < b.address AND NOT f:Exchange
      MATCH (a)-[s:SOLD_TO]-(b) RETURN count(s) AS v}
WITH "attributed_trades" AS metric, toString(v) AS value RETURN metric, value
UNION ALL
CALL {MATCH (a:Wallet)-[s:SOLD_TO]->(m:Wallet)-[t:TRANSFERRED]->(a)
      WHERE s.tx = t.tx RETURN count(s) AS v}
WITH "atomic_round_trips" AS metric, toString(v) AS value RETURN metric, value;
