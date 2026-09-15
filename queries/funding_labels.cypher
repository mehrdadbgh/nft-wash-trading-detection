// ─────────────────────────────────────────────────────────────────────────────
// FUNDER LABELS — manually verified on Etherscan
// MUST RUN BEFORE funding_attribution.cypher.
//
// WHY THIS EXISTS: shared funder != shared control. This population is
// KYC-indifferent — reward farmers, not launderers — so most first funders are
// exchange hot wallets. FTX alone seeded 17 of 304 target wallets, and Binance
// and Kraken accounted for most of the rest of the top 20.
//
// Without this exclusion the attribution query reports 23 links, of which 13
// are merely "both parties withdrew from Binance". With it: 10 real ones.
//
// SCOPE-SPECIFIC: re-scoping the pipeline surfaces new top funders that must be
// checked by hand. This list does not generalise.
//
// In KNIME this runs as a Table Creator feeding a Neo4j Writer with
// UNWIND $batch; inline below for standalone use.
// ─────────────────────────────────────────────────────────────────────────────

// Exchange hot wallets — excluded from attribution evidence
MATCH (f:Funder) WHERE f.address IN [
  "0xc098b2a3aa256d2140208c3de6543aaef5cd3a94",   // FTX 2
  "0x21a31ee1afc51d94c2efccaa2092ad1028285549",   // Binance 15
  "0x56eddb7aa87536c09ccc2793473599fd21a8b17f",   // Binance 17
  "0x9696f59e4d72e237be84ffd425dcad154bf96976",   // Binance 18
  "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0",   // Kraken 4
  "0xdfd5293d8e347dfe59e90efd55b2956a1343963d",   // Binance 16
  "0x4976a4a02f38326660d17bf34b431dc6e2eb2327",
  "0x3cd751e6b0078be393132286c442345e5dc49699",
  "0x25eaff5b179f209cf186b1cdcbfa463a69df4c45"
]
SET f:Exchange;

// Named operator wallets — personal addresses, not infrastructure.
// Both were themselves funded by an exchange, then seeded exactly two wash
// wallets each. That two-hop pattern is what clustering looks for.
MATCH (f:Funder {address:"0x534c8bc9781a8072b524b853147a69bc6bf2b552"}) SET f.name_tag = "luca.eth";
MATCH (f:Funder {address:"0x4e1e9ef8da3e4a727beb01b26e0f9204056bd381"}) SET f.name_tag = "usem.eth";
