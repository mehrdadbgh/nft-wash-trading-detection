# Wash Trading on LooksRare, January–February 2022

### An investigation into three zero-royalty NFT collections during the token-reward era

---

## Executive Summary

Between 10 January and 1 March 2022, three NFT collections — Meebits, Terraforms and
Loot — recorded **14,186 sales on LooksRare totalling 5.68 million ETH**. This
investigation finds that the substantial majority of that activity was not trading.

**71% of all sales occurred inside concentrated wallet pairs**, of which 108 of 129
were fully closed: both wallets trading at least 90% exclusively with each other.
**53 tokens — 6.6% of everything sold — carried 66.7% of all market activity.** For
617 of 808 traded tokens (76.4%), a single wallet pair was responsible for more than
70% of that token's entire recorded history.

Four structurally distinct wash-trading methods were identified, each defeating a
different class of detector. Ten operator groups were attributed to single controllers
through funding analysis; the largest operations could not be attributed, and that
asymmetry is reported rather than concealed.

The economic driver is unambiguous. LooksRare paid LOOKS tokens pro-rata to each
trader's share of platform volume, and for a period those rewards exceeded the 2%
platform fee. Wash trading was not merely deceptive; it was profitable. The surviving
cost was creator royalties, which is why the activity concentrated in collections that
charged none.

One transaction illustrates the whole period. On 1 February 2022, the wallet
`iven.eth` sold Meebit #16938 **to itself** for 5,238.98 WETH. The exchange returned
5,134.22 WETH and took 104.78 as its fee. The NFT did not change hands. The operator
paid approximately **$265,000 to move an asset from himself to himself** — a rational
decision only if the rewards generated exceeded that cost.

---

## Scope and Method

| | |
|---|---|
| **Period** | 10 Jan 2022 00:00 – 1 Mar 2022 00:00 UTC |
| **Marketplace** | LooksRare Exchange v1 (`0x59728544…17ce3a`) |
| **Collections** | Meebits (`0x7bd29408…716bc7`), Terraforms (`0x4e1f4161…480e56`), Loot (`0xff9c1b15…0113d7`) |
| **Source** | Etherscan API V2 — ERC-721 transfer logs and exchange event logs, independently |
| **Method** | KNIME pipeline → Neo4j property graph → seven Cypher detectors |

Collections were selected for a structural reason rather than notoriety: all three
charged **zero creator royalties**, removing the only cost that made round-trip wash
trading unprofitable under the reward scheme. The period begins on LooksRare's launch
day, when emissions were highest.

Two independent data sources were used deliberately. ERC-721 transfer logs record what
moved; exchange event logs record what was sold and for how much. Joining them on
transaction hash allows each to check the other, and that check produced the first
finding of the investigation (see *Atomic round-trips*, below).

**Dataset:** 21,943 in-window token movements, of which 14,186 were LooksRare sales
and 7,757 were unpriced transfers. 5,948 distinct wallets, 5,512 tokens that moved,
808 that were sold at least once.

---

## 1 · Market Structure

The three collections behaved differently from one another, and the differences are
informative.

| Collection | Tokens sold | Sales | Sales in 50+ tokens | Concentration | LooksRare share of all movements |
|---|---:|---:|---:|---:|---:|
| Terraforms | 341 | 6,952 | 4,874 | **70%** | 66.7% |
| Meebits | 346 | 6,362 | 4,314 | **68%** | 69.8% |
| Loot | 121 | 872 | 270 | **31%** | 36.4% |

Two observations carry weight.

First, for Meebits and Terraforms, **roughly 70% of every recorded movement of these
tokens — including wallet-to-wallet transfers and sales on other marketplaces — was a
LooksRare sale.** A single venue accounting for that share of an asset's total
movement is not a feature of organic markets.

Second, **Loot diverges sharply**. It is the cheapest of the three, and wash farming
scales with token value: a given volume target requires proportionally more
transactions, and therefore more gas, at a lower price point. Loot was the least
efficient vehicle available and attracted correspondingly less industrialised
activity. Its 31% concentration is not evidence of a clean market — an independent
public methodology flags 88.6% of its trades — but it is measurably less saturated
than the other two, which demonstrates that the detectors discriminate rather than
flagging uniformly.

---

## 2 · Typologies

### 2.1 Bilateral mills — 56 wallets

Two addresses, one to three tokens, hundreds of round trips. The defining measurement
is **intensity**: trades divided by distinct tokens. Wash mills score 100–500; a
legitimate high-volume trader scores close to 1.

These operations are visible to pair-concentration and ping-pong detection and
invisible to ring detection, because they never involve a third party.

### 2.2 Mesh clusters — 6 wallets

A single cluster of six wallets traded among themselves across a shared inventory of
seven Meebits, with **nine of fifteen possible pairs active** and 998 trades in total.

The design defeats concentration thresholds by construction. Because activity is
spread across four or five counterparties, **no individual pair exceeds 40%
concentration** — well below the 50% flagging threshold. Measured at cluster level,
however, control of those seven tokens was **100%**: every recorded sale of all seven
involved a cluster member.

| Token | Total sales | Sales involving the cluster |
|---|---:|---:|
| Meebits #689 | 226 | 226 |
| Meebits #1938 | 206 | 206 |
| Meebits #19564 | 167 | 167 |
| Meebits #1657 | 119 | 119 |
| Meebits #8475 | 110 | 110 |
| Meebits #18277 | 97 | 97 |
| Meebits #13531 | 89 | 89 |

Only ring detection surfaces this structure, and it does so because rings do not
measure concentration at all — they look for closed cycles regardless of how thinly
each participant's activity is spread.

### 2.3 Distributed federations — 2 tokens

Many small pairs, each individually unremarkable, grinding a single token.

**Meebits #8319 recorded 726 sales — more than any token in the dataset — while its
most active pair was responsible for only 7.3%.** Twelve distinct pairs traded it
between 22 and 27 times each, none crossing any pair-level threshold. Terraforms #2811
shows the same pattern at 411 sales and 11.4% dominance.

Price behaviour differs from the mills in a way that suggests deliberate discipline.
The federation tokens stayed within a 51–260 ETH band; bilateral mills ran the same
token from 0.30 to 788 ETH. Where a pair controls both sides of every trade, absurd
pricing carries no risk. Where many independent parties transact, prices must remain
plausible.

The general principle: **volume and concentration are independent axes**, and a
detector relying on either alone misses half the wash.

### 2.4 Atomic round-trips — 9 instances

An NFT sold and returned to its seller **inside a single transaction**, routed through
a proxy contract. Net ownership change is zero; the recorded volume is not.

These were not found by a detector. They surfaced as disagreements in a data-quality
check comparing the two independent data sources — the transfer log showed the token
somewhere the exchange event did not expect. Nine of 14,195 matched sales disagreed
(0.063%), and all nine proved to be this pattern.

| Origin wallet | Token | Proxy contracts | Executions | Price |
|---|---|---:|---:|---|
| `0x95c2937f…3c5ec` | Terraforms #8099 | 1 | 4 | 2,000 ETH each |
| `0x116a4ea2…5d94e` | Terraforms #2005 | 2 | 5 | 250 ETH ×4, 5 ETH ×1 |

Two details matter. The intermediary in each case is a **deployed contract**, not a
second personal wallet — the round trip must be atomic, and only a contract can
execute a purchase and a return within one transaction. Second, one operator used
**two different proxy contracts** within the same campaign, switching tooling
mid-course.

---

## 3 · Case Studies

### 3.1 The largest operation — 636,000 ETH in forty-one days

**Wallets:** `0xa53496b67eec749ac41b4666d63228a0fb0409cf` and
`0xd73e0def01246b650d8a367a4b209be59c8be8ab`

These two addresses traded with each other **1,541 times** between 17 January and 28
February 2022 — approximately one trade every 39 minutes, continuously, for 41 days.
A cadence of that regularity over that duration is automated.

Their combined activity was 1,543 trades. **1,541 of those were with each other.** In
41 days, they interacted with the other 5,946 wallets in the dataset exactly twice.

| | |
|---|---:|
| Gross volume between them | 636,463.81 ETH |
| Net flow | **1,609.69 ETH (0.25%)** |
| Distinct tokens | 3 |
| Price range | 113.88 – 788 ETH (avg 413) |
| Estimated platform fees paid | ~12,700 ETH |

**99.75% of more than half a million ETH moved in circles.** The operators paid an
estimated 12,700 ETH — roughly $38 million — in platform fees to achieve a net asset
movement of 0.25%.

The acquisition is the most revealing part of the record:

| Time (17 Jan 2022) | Event |
|---|---|
| 13:36:18 | Wallet B buys Terraforms #9559 for **0.31 ETH** from `0x3bfe8b28…293c` |
| 13:38:33 | Wallet A buys Terraforms #5283 for **0.31 ETH** from `0x6e82d570…dc32` |
| 13:42:16 | Wallet A buys Terraforms #9728 for **0.31 ETH** from the same seller |
| 13:45:30 | First trade between A and B |
| 28 Feb 00:14 | Final trade |

**Three tokens, 0.93 ETH total, acquired in a nine-minute window. The campaign began
three minutes after the last purchase.** The ratio of generated volume to inventory
cost is approximately 684,000 to 1.

Those three tokens rank second, third and fourth among all tokens by sales count in
the dataset, and this pair accounts for 83–89% of each token's entire trading history.

Critically, **the prices were never anomalous**. At 114–788 ETH for Terraforms, no
price-outlier detector would flag a single one of these 1,541 trades. The operation is
visible only through relationship structure — bilateral concentration and trade
frequency — which is the clearest argument in this investigation for why multiple
independent detection methods are necessary.

### 3.2 The highest-value sale — Meebit #4092

**Transaction:** `0x7b7bd3f6201e903b707b600ed48ff73106913440b497fa5334545b0caa5d77a9`
**Date:** 18 January 2022, 23:39:20 UTC
**Seller:** `0x35d0Ca92152d1fEA18240d6C67C2ADfE0cCA287C`
**Buyer:** `0xA99A76dDdBB9678bc33F39919Bc76d279C680C89`

Meebit #4092 sold for **15,200 WETH** — approximately $38 million at contemporary
prices, against a collection floor in the single-digit ETH range. The settlement:

| Party | Amount |
|---|---:|
| Buyer paid | 14,700.86 WETH + 499.14 ETH (wrapped in-transaction) |
| LooksRare fee address `0x5924A28c…f3c1` | 304 WETH |
| Seller received | 14,896 WETH |

The fee is exactly 2.000%, which independently confirms the price decoding used
throughout this investigation.

The listing used LooksRare's **standard fixed-price sale strategy**, meaning the seller
set the price and a buyer took it at that price. A collection-wide offer can be filled
by any holder; a fixed-price listing at 4,000× the floor can realistically only be
taken by its author. The buyer also required roughly $38 million in liquid WETH to
execute, which explains why most operators cycled at 200–800 ETH instead.

### 3.3 The multi-technique operator — `iven.eth`

**Wallet:** `0x18A4489a739ac9835DA14e006B35D65040e53a4A`

A single wallet employing four distinct wash-trading methods, the only wallet in the
dataset to fire five independent detector families:

1. **Self-sale** — Meebit #16938 sold to itself for 5,238.98 WETH on 1 February 2022. Net cost: the 104.78 WETH fee (~$265,000).
2. **Ring participation** — a three-wallet cycle with `0xd76114…` and `0xf1ddb5…` covering Meebit #16938 and Terraforms #4206.
3. **Bilateral pairs** — two separate concentrated trading pairs.
4. **Attributed funding** — first funded by `luca.eth` (`0x534c8bc9…b552`), which also seeded its trading counterparty.

This wallet's trades average **3,343 ETH each** — the highest per-trade value of any
flagged wallet. Its token #16938 recorded a peak sale of 6,100 ETH, higher than the
self-sale itself.

The self-sale is the single cleanest demonstration of the period's economics: an
operator knowingly paid a quarter of a million dollars in fees for a transaction that
changed nothing, which is rational only if the reward emissions exceeded that cost.

### 3.4 Three converging signals — the `b00b` pair

**Wallets:** `0xb00b51bf185c7da1e2b61a9d53df7bc863699274` and
`0xb00b5b48b26da7389888e01fa1eb2bbda2997d01`

Three independent indicators point to common control:

- **Shared funding** — both first funded by `usem.eth` (`0x4e1e9ef8…d381`), which funded no other wallet in the target set
- **Vanity prefixes** — both addresses begin `0xb00b`, which requires deliberate key generation
- **Exclusive trading** — 25 trades, overwhelmingly with each other

No single one of these would be conclusive. Together they are difficult to explain
otherwise, and they illustrate the investigation's general scoring principle:
independent methods agreeing is stronger evidence than any one method's confidence.

---

## 4 · Attribution

For each wallet in a concentrated pair, the first inbound transaction was resolved —
the address that funded it into existence. 304 of 308 targets resolved successfully
(98.7%).

**The central methodological point: a shared funder is not shared control.**

This population consists of reward farmers, not launderers. They had no reason to
avoid regulated exchanges, and most first funders are exchange hot wallets. FTX alone
seeded 17 of the 304 target wallets; Binance and Kraken accounted for most of the
remaining top 20. Two wallets sharing Binance as their funding source have, in
evidentiary terms, nothing in common.

Nine exchange addresses were identified manually on Etherscan and excluded. Without
that step the analysis reports **23 operator links**; with it, **10**. The thirteen
discarded links were artefacts of common custody.

What survived:

| Wallets | Trades | Funder |
|---|---:|---|
| `0x8ce0d906…` / `0xea19b97a…` | 265 | `0xaf69aad6…` |
| `0x86cd4467…` / `0xb6a684ce…` | 117 | `0xb0449ec1…` |
| `0x0abd70eb…` / `0xaddb1860…` | 69 | `0xaa94e8ca…` |
| `0x6ee069db…` / `0x88eb2863…` | 50 | `0x70c26073…` |
| `0x770f01c2…` / `0x7cf424ac…` | 43 | `0x70dd6bda…` |
| `0x18a4489a…` / `0x25de83ca…` | 39 | **luca.eth** |
| `0xa236b5bb…` / `0xa8a51ad7…` | 31 | `0x85380efd…` |
| `0xb00b51bf…` / `0xb00b5b48…` | 25 | **usem.eth** |
| `0x3e3a5527…` / `0x6d608a93…` | 24 | `0xcd00e4cb…` |
| `0xe18285b6…` / `0xfbcb950f…` | 21 | `0xef15f4c1…` |

Total: **684 trades (4.8% of all sales), 20 wallets, 519,519 ETH.**

**Every attributed funder seeded exactly two wallets.** That uniformity is itself
evidence — it describes a setup procedure, not a coincidence.

Two funders carry ENS identities. Both were themselves funded by exchanges before
seeding their wash wallets, which is the ordinary two-hop pattern: buy on an exchange,
withdraw to a personal wallet, fund operational wallets from there.

**What attribution failed to establish.** The largest operations in the dataset — the
1,541-trade pair, the 496-trade single-token pair, the mesh cluster — could not be
attributed. Their wallets were funded independently through exchange withdrawals, so
no link exists to find. Detection substantially outperforms attribution in this
dataset, and that is the honest characterisation.

---

## 5 · Validation

Wash trading has no ground-truth labels. No authority publishes a verified list, so
precision cannot be measured and is not claimed. Five independent checks were applied
instead.

**Data integrity.** The paginated fetch was reconciled against an independent
single-query control total: Meebits returned 9,796 rows both ways, exactly. This check
caught a cursor off-by-one error during development that was silently dropping
boundary-block remainders.

**Cross-source agreement.** Transfer logs and exchange events describe the same trades
independently. On matched records the seller must equal the sender; nine of 14,195
disagreed (0.063%), and all nine were root-caused to atomic round-trips rather than
decoding errors.

**Detector correctness.** Synthetic patterns with known answers were injected into the
graph: a self-sale, a ping-pong pair, a chronological ring, and three decoys — a
cross-token loop, a reverse-chronology ring, and a legitimate one-way bulk seller. All
three positives fired. Both structural decoys were correctly rejected.

The bulk-seller decoy fired the concentration detector, as designed. It moved 30
different NFTs to one buyer in one direction — high concentration, no reciprocity.
This established **trades per distinct token** as the discriminating feature: wash
mills score 100–500, legitimate bulk trading scores approximately 1.

Manual review of the resulting quarantine category then exposed the opposite error.
Several pairs with low intensity were trading at 227, 406 and 1,016 ETH per
transaction — values at which "inventory movement between one owner's wallets" is not
a credible explanation, since each transfer incurs a 2% fee. A price condition was
added. Both corrections are documented in the workflow.

**Discrimination.** Within the dataset, Loot registers 31% concentration against 70%
for Terraforms — the detectors respond differently to differently-behaved data.

**Incentive control.** The pipeline was re-run unchanged against BAYC and Doodles,
royalty-bearing collections, over the identical window. Result: **423 LooksRare sales
out of 11,205 token movements — 3.8%, against 64.7% for the zero-royalty
collections.** A seventeen-fold difference in marketplace share, in the same window on
the same venue.

This confirms the economic thesis. It does **not** measure a false-positive rate: 423
sales is too small a sample to distinguish precise detectors from an absence of
material to find. That gap is stated rather than papered over.

**External benchmark.** The dataset was compared against `nft.wash_trades` in the Dune
Spellbook — hildobby's implementation, the most widely used public methodology for NFT
wash-trade labelling. Run on identical scope:

| Collection | Trades (this study) | Trades (hildobby) |
|---|---:|---:|
| Meebits | 6,362 | **6,362** |
| Terraforms | 6,952 | **6,952** |
| Loot | 872 | **872** |

**Exact reconciliation across all three collections**, trade for trade — two
independent pipelines, independent decoding, independent marketplace attribution,
identical universe. The rarest detector also agrees precisely: one self-sale in the
period, both methods.

Flag rates diverge — his method flags 94.2%, 96.2% and 88.6% respectively — and the
divergence is explained by a specific design choice: his third filter flags any token
bought three or more times, against this study's threshold of fifty sales. His
approach has no equivalent of ring, mesh or concentration detection.

One further point of agreement emerged. For the mesh-cluster wallets, hildobby's
`first_funded_by` field is **NULL** — his pipeline declines to resolve funding for
exchange-funded wallets rather than recording a misleading link. This study reaches the
same judgement by a different route: resolving the funder, labelling it as an
exchange, and excluding it. Two independent implementations arriving at the same
methodological conclusion is meaningful corroboration.

---

## 6 · Limitations

1. **No precision figure is claimed.** Ground-truth labels do not exist; any reported precision would have an invented denominator.
2. **The negative control could not measure specificity** — 423 sales is too thin a sample.
3. **Thresholds are judgment calls**: 50% concentration, intensity 10, 50 ETH per trade, 50 sales per token. Each was set with margin against observed distributions, not derived from theory.
4. **Single marketplace.** LooksRare v1 only. A flagged wallet's activity on OpenSea is invisible here, so the concentration figures describe LooksRare behaviour rather than total market behaviour.
5. **Pair-level dominance understates coordinated clusters.** The mesh reads approximately 20% at pair level and 100% at cluster level. The metric measures pair control, which is precisely the structure it is least equipped to see — hence mesh membership is applied as an override rather than inferred from the percentage.
6. **Attribution is scope-specific.** The nine excluded exchange addresses were identified by hand for this dataset. A different scope would surface different funders requiring fresh manual review.
7. **Price decoding assumes WETH with 18 decimals** — verified across 100% of in-scope sales and enforced by checks retained in the workflow, but a simplification nonetheless.
8. **Transfer-level atomic repeats are undetectable.** The transfer endpoint exposes no log index, so two identical hops of one token within a single transaction cannot be distinguished from pagination artefacts. None were observed; the limitation is structural rather than empirical.

---

## Appendix — Detector Definitions

| ID | Detector | Rule | Flagged |
|---|---|---|---:|
| D1 | Self-sale | buyer address = seller address | 1 |
| D2 | Ping-pong | ≥2 completed round trips of one token between two wallets | 253 |
| D3 | Rings | chronological 3-wallet cycle, same token on all legs | 19 |
| D4 | Rapid flip | token sold ≥50 times in the window | 53 tokens |
| D7 | Atomic round-trip | sale and return within one transaction hash | 9 |
| D8 | Pair concentration | ≥50% of a wallet's trades with one counterparty, and (intensity ≥10 or ≥50 ETH per trade) | 245 |
| — | Funding | shared non-exchange first funder | 20 |

Scoring counts the number of **independent detector families** that fired per wallet,
not a weighted severity. Each typology evades a different detector, so agreement
across methods is the evidence rather than any single detector's confidence.

**Result:** 255 wallets flagged — 33 at high confidence (3+ families), 217 medium, 5
low or none.

---

*Analysis pipeline, detector queries, graph database export and underlying data:
[github.com/mehrdadbgh/nft-wash-trading-detection](https://github.com/mehrdadbgh)*

*Mehrdad Bagherzadeh — data engineering, blockchain forensics and AML analytics*
