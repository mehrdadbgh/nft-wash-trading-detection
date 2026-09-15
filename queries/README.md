# Detector Queries

Every detector in this project is a Cypher query. KNIME executes them through
Neo4j Reader nodes and does the joining and scoring; the detection logic itself
lives here.

Restore `backup/` into Neo4j and run any of these to verify a finding
independently — no API key, no pipeline run.

## Order

| File | Purpose | Returns |
|---|---|---:|
| `00_schema.cypher` | constraints and indexes — run once, before loading | — |
| `01_load_graph.cypher` | reference copy of the four writer queries | — |
| `d1_self_sale.cypher` | buyer = seller | 1 |
| `d2_ping_pong.cypher` | token traded back and forth between two wallets | 423 |
| `d3_rings.cypher` | chronological 3-wallet cycles on one token | 107 |
| `d4_token_stats.cypher` | sales, volume and price range per token | 808 |
| `d7_atomic_round_trip.cypher` | sold and returned inside one transaction | 9 |
| `d8_pair_concentration.cypher` | counterparty concentration and intensity | 139 |
| `token_dominance.cypher` | which pair controls each token | 808 |
| `wallet_collection_focus.cypher` | each wallet's dominant collection | 255 |
| `funding_targets.cypher` | which wallets to resolve first-funder for | 302 + 6 |
| `funding_labels.cypher` | **run before attribution** — tag exchanges | — |
| `funding_attribution.cypher` | pairs under common control | 10 |
| `summary_stats.cypher` | headline figures as metric/value rows | 11 |
| `validation_synthetic.cypher` | injection test with known answers | — |

## Two things to read before trusting the output

**`funding_labels.cypher` is not optional.** Shared funder is not shared control.
Without the exchange exclusion, attribution reports 23 links instead of 10 — the
extra thirteen are pairs whose only connection is that both parties withdrew
from Binance.

**No single detector is sufficient.** Each topology in this dataset evades a
different one: bilateral mills are invisible to ring detection, mesh clusters
are invisible to pair concentration, distributed wash is invisible to dominance
metrics, and the atomic round-trips sit below every threshold. Scoring counts
how many independent families fired, which is why they are all here.
