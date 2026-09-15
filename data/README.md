# Pipeline Checkpoints

KNIME-native table format. These are the outputs of the ETL stage, saved so that
the graph load, detection and scoring can be re-run without an Etherscan API key
or a 30-minute refetch.

| File | Rows | Contents |
|---|---:|---|
| `transfers_clean.table` | 21,943 | ERC-721 movements — deduplicated, typed, labelled mint/burn/transfer, filtered to the study window |
| `sales_enriched.table` | 21,943 | the above joined left-outer to LooksRare sale events — 14,195 matched, 23 columns |

`sales_enriched.table` is the single input to `05_Load_Graph`. To rebuild the graph
without refetching, point a Table Reader at it and execute the Load metanode onward.

## Why this format

`.table` preserves KNIME column types exactly. Two columns depend on that:
`price_wei` holds exact on-chain integers up to 23 digits and must stay a String —
CSV round-tripping would let a reader infer it as a float and silently lose the
precision the report cites. `tokenID` is a String for the same reason.

Readable only by KNIME. For a portable view of the same findings see `exports/`
(CSV) or `backup/` (Neo4j dump).

## Schema

**transfers_clean** — collection, contract, tokenID, hash, blockNumber, timeStamp
(zoned UTC), from_addr, to_addr, transfer_id, transfer_type

**sales_enriched** — the movement columns above, plus the trade layer: sale_id,
event_type, strategy, buyer, seller, price_eth (Double), price_wei (String),
order_nonce, logIndex, marketplace, direction_ok, violation_subtype.
Trade-layer columns are empty on the 7,748 unpriced movements by design.
