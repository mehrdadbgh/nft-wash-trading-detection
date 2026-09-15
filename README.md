# NFT Wash Trading Detection

**NFT wash trading detection pipeline — KNIME + Neo4j + Streamlit.** Analyses 14,186
LooksRare sales from the 2022 token-reward era, identifies four distinct wash-trading
topologies, and attributes ten operator clusters to single controllers.

Built entirely with KNIME and Cypher — no Python in the pipeline. Trade counts
reconcile **exactly** against hildobby's `nft.wash_trades` on Dune, the de facto
public standard for NFT wash-trade labelling.

---

## Results at a Glance

| | |
|---|---:|
| Marketplace sales analysed | **14,186** |
| Wallets in graph | **5,948** |
| Tokens ever sold | **808** |
| Total sale volume | **5,676,604 ETH** |
| Sales inside closed wallet pairs | **71%** |
| Tokens carrying 66.7% of all activity | **53** (6.6% of tokens sold) |
| Tokens with a single pair driving 70%+ of their history | **617** (76.4%) |
| Wallets flagged | **255** |
| Operator clusters attributed | **10** (684 trades) |
| Wash typologies identified | **4** |

---

## What This System Detects

- **Self-sales** — buyer and seller are the same address
- **Ping-pong trading** — the same token passed back and forth between two wallets
- **Trading rings** — chronological three-wallet cycles moving one token in a loop
- **Rapid flipping** — single tokens sold 50+ times inside a seven-week window
- **Atomic round-trips** — an NFT sold and returned to its seller *within one transaction*, routed through a proxy contract
- **Pair concentration** — wallets whose trading is dominated by one counterparty
- **Operator attribution** — trading pairs whose wallets share a non-exchange first funder

Each detector catches a topology the others miss. Scoring counts how many
**independent detector families** fired rather than applying weights, because
agreement across methods is the evidence.

---

## Architecture

```
Etherscan API V2
      │
      ├── tokennfttx  ──► ERC-721 transfers      ┐
      └── getLogs     ──► LooksRare sale events  ┘
                            │
                    KNIME  ── extract (cursor pagination)
                           ── transform (ABI decode, validation, join)
                           ── load
                            │
                          Neo4j
                    Wallet ─SOLD_TO→ Wallet
                    Wallet ─TRANSFERRED→ Wallet
                    Wallet ─FUNDED_BY→ Funder
                            │
                    7 Cypher detectors
                            │
                    KNIME scoring ──► 6 CSV exports ──► Streamlit dashboard
```

Wei values are decoded with a Java Snippet using `BigInteger` — a 15,200 ETH sale
price exceeds 64-bit integer range by three orders of magnitude, and floating-point
storage would silently lose exactness on the figures this report cites.

---

## Why This Scope

LooksRare launched on **10 January 2022** paying LOOKS tokens pro-rata to each
trader's share of platform volume. For a period the rewards exceeded the 2% platform
fee, which made wash trading *profitable* rather than merely deceptive.

The one cost that survived was **creator royalties** — a 5% royalty per round trip
destroys the arbitrage. So the activity concentrated in zero-royalty collections.

This project studies three of them — **Meebits**, **Terraforms** and **Loot** — over
the seven weeks from launch (10 Jan – 1 Mar 2022). The incentive structure makes the
period near-ground-truth: the economics predict dense wash trading without anyone
needing to label the data.

Contract addresses were verified against Etherscan's verified-contract labels before
ingestion. Several unrelated ERC-20 tokens reuse the "Loot" name, so address
verification is not optional.

---

## Findings

### The market was not a market

| Collection | Tokens sold | Sales | Sales in 50+ tokens | Concentration |
|---|---:|---:|---:|---:|
| Terraforms | 341 | 6,952 | 4,874 | **70%** |
| Meebits | 346 | 6,362 | 4,314 | **68%** |
| Loot | 121 | 872 | 270 | **31%** |

Across all three, **71% of sales occurred inside concentrated wallet pairs**, and 108
of 129 such pairs were fully closed — both wallets trading ≥90% exclusively with each
other.

### Four topologies

**1 · Bilateral mills** — 56 wallets. Two addresses, one to three tokens, hundreds of
round trips. The defining signature is *intensity*: trades divided by distinct tokens.
Wash mills score 100–500; a legitimate high-volume trader scores near 1.

> The largest pair traded **1,541 times over 41 days** — one trade every ~39 minutes,
> around the clock — cycling **636,464 ETH gross with a net flow of 1,609 ETH (0.25%)**.
> Their entire inventory was three Terraforms bought for **0.93 ETH total** in a
> nine-minute window, three minutes before the campaign began.

**2 · Mesh clusters** — 6 wallets, nine of fifteen possible pairs active, 998 trades
across seven Meebits. No individual pair exceeded 40% concentration, placing the
cluster **below every bilateral threshold** — yet cluster-level control of those seven
tokens was **100%**: every recorded sale involved a member. Only ring detection sees
this.

**3 · Distributed federations** — many small pairs grinding one token. Token #8319 had
**726 sales, more than any token in the dataset**, with its top pair responsible for
just **7.3%**. Prices stayed in a narrow 51–260 ETH band; bilateral mills ran the same
token from 0.30 to 788 ETH. Volume and concentration are independent axes.

**4 · Atomic round-trips** — 9 instances, 2 origin wallets, ~9,005 ETH. An NFT sold
and returned to its seller inside a single transaction via a proxy contract. Net
ownership change zero; recorded volume unaffected. These were surfaced by a
data-integrity check comparing two independent Etherscan endpoints, before any
detector existed.

### Named cases

| Case | Detail |
|---|---|
| **Highest-value sale** | Meebit #4092 for **15,200 WETH** (~$38M), 18 Jan 2022 — a self-priced listing, bought at its own asking price |
| **Self-sale** | `iven.eth` sold Meebit #16938 to itself for **5,238.98 WETH**. Net cost: the **104.78 WETH platform fee** (~$265k) — paid to move an NFT from himself to himself |
| **Vanity pair** | `0xb00b51bf…` and `0xb00b5b48…` — matching vanity prefixes, shared funder `usem.eth`, exclusive bilateral trading. Three independent signals converging |
| **Multi-technique operator** | `iven.eth` fired five detector families: self-sale, ping-pong, ring membership, two concentrated pairs, and funding attribution |

### Attribution

Ten operator pairs were linked to single controllers by shared non-exchange funding —
**684 trades (4.8% of sales), 20 wallets** — and every attributed funder seeded
**exactly two wallets**. That uniformity is itself evidence: it is a setup procedure.
Two funders carry ENS identities, `luca.eth` and `usem.eth`.

The largest operations resisted attribution. Their wallets were funded independently
through exchanges, so no link exists to find. **Detection substantially outperforms
attribution** — the honest result rather than the flattering one.

---

## Screenshots

### Dashboard

![Overview](docs/screenshots/dashboard-overview.png)

![Typologies](docs/screenshots/dashboard-typologies.png)

![Wallets](docs/screenshots/dashboard-wallets.png)

![Tokens](docs/screenshots/dashboard-tokens.png)

![Cases and validation](docs/screenshots/dashboard-cases.png)

### Graph

**Atomic round-trip** — sold out and returned home inside one transaction.

![Atomic round-trip](docs/screenshots/neo4j-atomic-round-trip.png)

**Mesh cluster** — six wallets, nine connected pairs, no pair above 40% concentration.

![Mesh cluster](docs/screenshots/neo4j-mesh-cluster.png)

**The largest bilateral mill** — two wallets, 1,541 trades between them.

![Twins pair](docs/screenshots/neo4j-twins-pair.png)

**An attributed operator** — one funder, two wallets, trading exclusively with each other.

![Attributed operator](docs/screenshots/neo4j-attributed-operator.png)

---

## Configuring the Pipeline

Double-click **`00_Init`** and enter four values in the configuration dialog:

- Etherscan API key (free tier is sufficient)
- Neo4j bolt URL, username, password

![Initialization dialog](docs/screenshots/knime-initialization.png)

Nothing else needs configuring to reproduce the study. To re-scope the pipeline, edit
the collection seed table inside the component and point the connection at a different
database.

![Inside initialization](docs/screenshots/knime-init-inside.png)

The component also holds both seed tables and the schema statements — two uniqueness
constraints and two relationship indexes, written one statement per row because the
Neo4j node rejects multi-statement scripts. All use `IF NOT EXISTS`, so they re-run
safely.

---

## Pipeline Stages

![Workflow overview](docs/screenshots/knime-workflow-overview.png)

Execution order is enforced by Neo4j connection ports rather than data ports:
`06_Funding` reads the graph that `ETL` writes, and `08_Evidence_Export` reads what
both produced.

### ETL

![ETL](docs/screenshots/knime-etl.png)

#### Extract

![Extract](docs/screenshots/knime-extract.png)

Two independent cursor-paginated loops. Etherscan's free tier caps responses at 1,000
records and 3 calls/second, so each loop requests a page, takes the maximum block
number seen, and restarts from there — exiting when a page returns fewer than 1,000
rows. Call count adapts to data density; nothing is guessed.

![Transfer extraction loop](docs/screenshots/knime-extract-transfers.png)

`startblock` is **inclusive**, so every restart re-serves its boundary block.
Deduplication downstream is load-bearing, not insurance — it removed 33 of 23,504
transfer rows (0.14%) and 95 of 80,555 sale events (0.118%), rates consistent across
both loops.

![Sale event extraction loop](docs/screenshots/knime-extract-sale-events.png)

The sales loop fetches LooksRare `TakerAsk` and `TakerBid` events platform-wide — the
collection filter is applied later at the join, which lets the same table support
market-share statistics. `getLogs` returns all numerics as hex, so block numbers are
decoded before cursor arithmetic.

*Integrity check:* the paginated fetch was reconciled against an independent
single-query control total — Meebits returned 9,796 rows both ways, exactly. This
check caught an off-by-one cursor bug during development, where `last_block + 1`
skipped remainder rows in boundary blocks.

#### Transform

![Transform](docs/screenshots/knime-transform.png)

Transfers are deduplicated, typed, labelled mint/burn/transfer, and filtered to the
study window. Sale events are decoded from the 7-word ABI payload — order nonce,
currency, collection, token ID, amount, price — with buyer and seller derived from the
event type:

```
TakerBid  ⇒  buyer = taker,  seller = maker
TakerAsk  ⇒  buyer = maker,  seller = taker
```

The two branches are joined left-outer from transfers, which inherits the collection
and window scopes automatically. Unpriced movements stay in the dataset: they carry no
price, so they are excluded from sale-based detectors, but they still link wallets in
the graph.

*Cross-endpoint validation:* the transfer log and the marketplace event describe the
same trades independently, so on matched rows the seller must equal the sender.
**Nine rows disagreed (0.063%)** — and all nine turned out to be atomic wash
round-trips, where the NFT was sold and returned inside one transaction. A
data-quality check functioned as a zeroth detector.

#### Load

![Load](docs/screenshots/knime-load.png)

Wallets, then NFTs, then edges. Order is strict: edge writers `MATCH` their endpoints
and never create them, so a missing wallet would silently drop its edges. `MERGE` keys
(`sale_id`, `transfer_id`) make every re-run idempotent.

Priced sales become `SOLD_TO`; unpriced movements and the nine flagged round-trips
become `TRANSFERRED` — a demotion, not a deletion, since they are real movements with
an unreliable sale attachment.

**Loaded:** 5,948 Wallet · 5,512 NFT · 14,186 SOLD_TO · 7,757 TRANSFERRED

### Funding Attribution

![Funding](docs/screenshots/knime-funding.png)

For each wallet in a concentrated pair, one API call with `offset=1&sort=asc` returns
its **first transaction ever**. If that transaction is inbound and non-zero, the sender
is the wallet's first funder. 304 of 308 targets resolved (98.7%).

**Shared funder is not shared control.** This population is KYC-indifferent — reward
farmers, not launderers — so most first funders are exchange hot wallets. Nine were
identified on Etherscan and tagged `:Exchange`. Without that exclusion the pipeline
reports **23 false links instead of 10 real ones**.

### Detection and Export

![Evidence export](docs/screenshots/knime-evidence-export.png)

The detectors live in the Cypher reader queries; KNIME joins their output and scores
it. Four sub-metanodes handle wallet evidence, token attribution, summary statistics
and export.

![Wallet evidence scoring](docs/screenshots/knime-wallet-evidence.png)

Scoring counts independent detector families rather than applying weights:

| Topology | Caught by | Invisible to |
|---|---|---|
| Bilateral mills | pair concentration, ping-pong | ring detection |
| Mesh clusters | ring detection | pair concentration (28% by design) |
| Distributed wash | sales volume | dominance metrics |
| Atomic loops | cross-endpoint validation | every threshold-based detector |

---

## Running It Yourself

### Dashboard only — no database required

```bash
cd dashboard
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Reads the six CSVs in `dashboard/data/`. Opens at `http://localhost:8501`.

### Explore the graph — restore the dump

```bash
neo4j-admin database load neo4j --from-path=backup/ --overwrite-destination=true
```

Then open Neo4j Browser and run the detector queries in `queries/`. This is the
fastest way to verify the findings independently — no API key, no pipeline run.

### Full pipeline

Import `workflow/NFT_Wash_Detection_Pipeline.knwf` into KNIME, configure `00_Init`,
and execute. Roughly 30 minutes of API calls end to end. Both ETL stages are
checkpointed to `.table` files so downstream work never forces a refetch.

---

## Validation

| Layer | Method | Result |
|---|---|---|
| Data integrity | Paginated fetch vs independent single-query control totals | **Exact match** (9,796) |
| Cross-endpoint | Transfer log vs marketplace event agreement | 9 disagreements (0.063%), all root-caused |
| Detector correctness | Synthetic injection — 3 positive patterns, 3 decoys | All positives fired, both structural decoys rejected |
| Discrimination | Within-dataset comparison across collections | 31% vs 70% concentration |
| Incentive thesis | Royalty-bearing control collections, same window | **3.8%** marketplace share vs 64.7% |
| External benchmark | Dune `nft.wash_trades` (hildobby), identical scope | **Trade counts matched exactly** |

**Benchmarked against hildobby's `nft.wash_trades`** (Dune Spellbook), the most widely
used public implementation of NFT wash-trade detection. Run on identical scope it
reconciled trade-for-trade across all three collections — 6,362 / 6,952 / 872 — and
matched on the rarest detector, one self-sale in both pipelines. Flag rates diverge
(his 88–96% against this project's concentration measure) because his third filter uses
a three-purchase threshold where this project uses fifty sales; the divergence is fully
explained by that choice. His method has no equivalent of ring, mesh or concentration
detection, and leaves `first_funded_by` NULL for exchange-funded wallets — the same
judgement this project reaches by labelling and excluding them explicitly.

**A synthetic decoy changed the design.** A fabricated legitimate bulk seller — 30
different NFTs, one buyer, one direction — fired the concentration detector as
expected. That established *trades per distinct token* as the discriminating feature:
wash mills score 100–500, legitimate bulk trading scores ~1. Manual review of the
resulting quarantine bucket then exposed the opposite error, high-value low-intensity
wash being excused, and added a price condition. Both corrections are documented in
the workflow annotations.

---

## Known Limitations

1. **No precision figure is claimed.** Ground-truth labels for wash trading do not exist. Any project reporting a precision percentage has invented its denominator.
2. **The negative control could not measure precision.** BAYC and Doodles produced only 423 LooksRare sales in the same window — enough to demonstrate that wash farming avoided royalty-bearing collections (3.8% marketplace share vs 64.7%), too few to establish a false-positive rate.
3. **Thresholds are judgment calls.** 50% concentration, intensity 10, 50 ETH, 50 sales — chosen with margin against observed data, not derived from theory.
4. **Single marketplace.** LooksRare v1 only. OpenSea settlement is not decoded, so a wallet's activity elsewhere is invisible to the sale layer.
5. **Pair-level dominance understates coordinated clusters.** The mesh reads ~20% at pair level and 100% at cluster level. The metric measures pair control, which is exactly the topology it is least able to see.
6. **First-funder attribution is weak for this population.** Reward farmers use exchanges freely, so most first funders are custodial. Nine were excluded manually; extending the scope would require re-checking new top funders by hand.
7. **Price decoding hardcodes WETH/18 decimals** — verified to hold for 100% of in-scope sales and enforced by QA checks retained in the workflow as executable documentation.
8. **Transfer-level atomic repeats are invisible.** `tokennfttx` exposes no log index, so two byte-identical hops of the same token within one transaction cannot be distinguished from pagination overlap. None were observed; the limitation is structural.

---

## Tech Stack

| Layer | Tool |
|---|---|
| ETL and orchestration | KNIME Analytics Platform |
| ABI decoding | Java Snippet (`BigInteger` for wei) |
| Graph database | Neo4j (Cypher) |
| Data source | Etherscan API V2 |
| Dashboard | Streamlit + Plotly |

---

## Repository

```
workflow/     KNIME workflow export
exports/      six CSV deliverables
backup/       Neo4j dump
dashboard/    Streamlit app + data
data/         KNIME table checkpoints (re-run the graph load without refetching)
queries/      detector Cypher, one file per detector
docs/         screenshots and investigation report
```

---

## Author

**Mehrdad Bagherzadeh** — data engineer, blockchain forensics and AML analytics
[github.com/mehrdadbgh](https://github.com/mehrdadbgh)

Related: [ethereum-aml-detection](https://github.com/mehrdadbgh/ethereum-aml-detection)
— money laundering detection across four DeFi exploits.
