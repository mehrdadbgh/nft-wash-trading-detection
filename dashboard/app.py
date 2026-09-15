import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="NFT Wash Trading Detection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #111418; color: #dce3ec; }
.stApp { background-color: #111418; }
section[data-testid="stSidebar"] { background-color: #161a1f; border-right: 1px solid #2a3040; }
section[data-testid="stSidebar"] * { color: #b0bfcf !important; font-size: 0.95rem !important; }
h1 { font-family: 'Space Mono', monospace; color: #ffffff; font-size: 1.6rem; }
.metric-card { background: linear-gradient(135deg,#1a1e25 0%,#1e232b 100%); border:1px solid #2a3040; border-top:3px solid #e8500a; border-radius:8px; padding:18px 20px; margin-bottom:12px; }
.metric-value { font-family:'Space Mono',monospace; font-size:1.9rem; font-weight:700; color:#ff6b2b; line-height:1; }
.metric-label { font-size:0.72rem; color:#6a8aaa; text-transform:uppercase; letter-spacing:1.5px; margin-top:6px; }
.section-title { font-family:'Space Mono',monospace; font-size:0.68rem; color:#4a6a8a; text-transform:uppercase; letter-spacing:3px; border-bottom:1px solid #2a3040; padding-bottom:8px; margin:24px 0 16px 0; }
.badge { display:inline-block; padding:3px 10px; border-radius:3px; font-family:'Space Mono',monospace; font-size:0.68rem; font-weight:700; letter-spacing:1px; }
.badge-HIGH     { background:#3d1010; color:#ff6b6b; border:1px solid #8b2020; }
.badge-MEDIUM   { background:#2d1800; color:#ff8c42; border:1px solid #8b4000; }
.badge-LOW      { background:#2d2200; color:#ffd166; border:1px solid #8b6400; }
.badge-NONE     { background:#0a2010; color:#56e39f; border:1px solid #1a6030; }
.mono { font-family:'Space Mono',monospace; }
#MainMenu, footer, header { visibility:hidden; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:#111418; }
::-webkit-scrollbar-thumb { background:#2a3a4a; border-radius:2px; }
.stTabs [data-baseweb="tab-list"] { background-color:#161a1f; border-bottom:1px solid #2a3040; }
.stTabs [data-baseweb="tab"] { color:#8fa8c8; font-family:'Space Mono',monospace; font-size:0.8rem; }
.stTabs [aria-selected="true"] { color:#ff6b2b !important; border-bottom:2px solid #ff6b2b !important; }
</style>
""", unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load(filename):
    return pd.read_csv(DATA_DIR / filename)

wallets   = load("wallet_evidence.csv")
tokens    = load("token_attribution.csv")
operators = load("operator_clusters.csv")
cases     = load("case_studies.csv")
summary   = load("summary_stats.csv")
atomic    = load("atomic_round_trips.csv")

# ── Normalize: tolerate optional columns so the app never hard-fails ──────────
for col, default in [
    ("collection_focus", "unknown"),
    ("funder", ""),
    ("funder_tag", ""),
    ("avg_price_per_trade", 0.0),
    ("ring_appearances", 0),
    ("self_sale_eth", 0.0),
    ("round_trips_total", 0),
]:
    if col not in wallets.columns:
        wallets[col] = default

wallets["funder_tag"] = wallets["funder_tag"].fillna("")
wallets["funder"] = wallets["funder"].fillna("")
wallets["collection_focus"] = wallets["collection_focus"].fillna("unknown")

if "funder_tag" not in operators.columns:
    operators["funder_tag"] = ""
operators["funder_tag"] = operators["funder_tag"].fillna("")

# summary_stats as a lookup dict
STATS = dict(zip(summary["metric"].astype(str), summary["value"].astype(str)))

def stat(key, default="—"):
    v = STATS.get(key, default)
    try:
        return f"{int(float(v)):,}"
    except (TypeError, ValueError):
        return v

COLLECTION_COLORS = {
    "Meebits":    "#f97316",
    "Terraforms": "#f59e0b",
    "Loot":       "#22c55e",
    "unknown":    "#4a6a8a",
}

STRUCTURE_COLORS = {
    "bilateral_mill":           "#ef4444",
    "concentrated_pair":        "#f97316",
    "mesh_cluster":             "#a855f7",
    "ring_member":              "#f59e0b",
    "multi_pair_operator":      "#38bdf8",
    "inventory_shuffle_review": "#56e39f",
    "unclassified":             "#4a6a8a",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:8px 0 20px 0;'>
        <div style='font-family:Space Mono,monospace;font-size:1.05rem;color:#ff6b2b;font-weight:700;'>
            WASH TRADING
        </div>
        <div style='font-size:0.75rem;color:#4a6a8a;letter-spacing:2px;margin-top:4px;'>
            NFT FORENSICS MVP
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "Overview",
        "Typologies",
        "Wallets",
        "Tokens",
        "Cases & Validation",
    ], label_visibility="collapsed")

    st.markdown(f"""
    <div style='font-size:0.82rem;color:#5a7a9a;line-height:2;margin-top:16px;'>
        <span style='color:#8a9aaa;font-weight:600;'>STACK</span><br>
        KNIME · Neo4j · Etherscan V2<br><br>
        <span style='color:#8a9aaa;font-weight:600;'>SCOPE</span><br>
        LooksRare v1<br>
        Meebits · Terraforms · Loot<br>
        10 Jan – 1 Mar 2022<br><br>
        <span style='color:#8a9aaa;font-weight:600;'>COVERAGE</span><br>
        {stat('wallets_in_graph')} wallets · {stat('total_sales')} sales<br>
        {stat('tokens_ever_sold')} tokens · {len(wallets):,} flagged
    </div>
    """, unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def badge(level):
    return f'<span class="badge badge-{str(level).upper()}">{str(level).upper()}</span>'

def fmt_eth(v):
    try:
        v = float(v)
        if v >= 1e6: return f"{v/1e6:.2f}M ETH"
        if v >= 1e3: return f"{v/1e3:.1f}K ETH"
        return f"{v:,.1f} ETH"
    except (TypeError, ValueError):
        return str(v)

def short(addr, n=10):
    s = str(addr)
    return s[:n] + "…" if len(s) > n else s

def plotly_base():
    return dict(
        paper_bgcolor="#111418",
        plot_bgcolor="#161a1f",
        font=dict(family="Inter", color="#8fa8c8", size=11),
        margin=dict(l=20, r=20, t=30, b=20),
    )

def card(content, border_color="#2a3040", left_color=None):
    lc = left_color or border_color
    return f"""<div style='background:#1a1e25;border:1px solid {border_color};
        border-left:3px solid {lc};border-radius:6px;
        padding:14px 20px;margin-bottom:8px;'>{content}</div>"""

def metric(value, label):
    return f"""<div class='metric-card'>
        <div class='metric-value'>{value}</div>
        <div class='metric-label'>{label}</div></div>"""

def section(title):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1 — OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
if page == "Overview":
    st.markdown("# NFT Wash Trading Detection")
    st.markdown(
        "<div style='color:#6a8aaa;font-size:0.9rem;margin-bottom:20px;'>"
        "Graph-based detection across three zero-royalty collections during the "
        "LooksRare token-reward era, January–February 2022."
        "</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric(stat("total_sales"), "Marketplace sales"), unsafe_allow_html=True)
    c2.markdown(metric(f"{len(wallets):,}", "Wallets flagged"), unsafe_allow_html=True)
    c3.markdown(metric(stat("tokens_ever_sold"), "Tokens ever sold"), unsafe_allow_html=True)
    c4.markdown(metric(fmt_eth(STATS.get("total_volume_eth", 0)), "Total volume"), unsafe_allow_html=True)

    section("Concentration")
    hot = tokens[tokens["sales"] >= 50]
    pct_hot = 100 * hot["sales"].sum() / tokens["sales"].sum() if len(tokens) else 0
    dom70 = (tokens["dominance_pct"] >= 70).mean() * 100 if len(tokens) else 0

    c1, c2, c3 = st.columns(3)
    c1.markdown(card(
        f"<div class='metric-value' style='font-size:1.5rem;'>{len(hot)}</div>"
        f"<div class='metric-label'>Tokens with 50+ sales</div>"
        f"<div style='color:#8fa8c8;font-size:0.82rem;margin-top:8px;'>"
        f"carrying {hot['sales'].sum():,} sales — <b>{pct_hot:.1f}%</b> of all activity</div>",
        left_color="#ef4444"), unsafe_allow_html=True)
    c2.markdown(card(
        f"<div class='metric-value' style='font-size:1.5rem;'>{dom70:.1f}%</div>"
        f"<div class='metric-label'>Tokens pair-dominated</div>"
        f"<div style='color:#8fa8c8;font-size:0.82rem;margin-top:8px;'>"
        f"a single wallet pair drove 70%+ of their entire sales history</div>",
        left_color="#f97316"), unsafe_allow_html=True)
    c3.markdown(card(
        f"<div class='metric-value' style='font-size:1.5rem;'>{stat('attributed_operator_pairs')}</div>"
        f"<div class='metric-label'>Operators attributed</div>"
        f"<div style='color:#8fa8c8;font-size:0.82rem;margin-top:8px;'>"
        f"{stat('attributed_trades')} trades linked to single controllers via funding</div>",
        left_color="#a855f7"), unsafe_allow_html=True)

    section("Activity by collection")
    col_stats = (tokens.groupby("collection")
                 .agg(tokens_sold=("nft_id", "count"),
                      sales=("sales", "sum"),
                      volume=("volume_eth", "sum"))
                 .reset_index().sort_values("sales", ascending=False))

    c1, c2 = st.columns([3, 2])
    with c1:
        fig = px.bar(col_stats, x="collection", y="sales", color="collection",
                     color_discrete_map=COLLECTION_COLORS, text="sales")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(**plotly_base(), showlegend=False, height=320,
                          xaxis_title=None, yaxis_title="Sales")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.dataframe(
            col_stats.assign(volume=col_stats["volume"].map(lambda v: f"{v:,.0f}")),
            hide_index=True, use_container_width=True, height=320,
            column_config={
                "collection": "Collection",
                "tokens_sold": st.column_config.NumberColumn("Tokens", format="%d"),
                "sales": st.column_config.NumberColumn("Sales", format="%d"),
                "volume": "Volume (ETH)",
            })

    section("Detection output")
    c1, c2 = st.columns(2)
    with c1:
        conf_order = ["high", "medium", "low", "none"]
        cdist = (wallets["confidence"].value_counts()
                 .reindex(conf_order).dropna().reset_index())
        cdist.columns = ["confidence", "wallets"]
        fig = px.bar(cdist, x="wallets", y="confidence", orientation="h",
                     color="confidence",
                     color_discrete_map={"high": "#ef4444", "medium": "#f97316",
                                         "low": "#ffd166", "none": "#56e39f"},
                     text="wallets")
        fig.update_traces(textposition="outside")
        fig.update_layout(**plotly_base(), showlegend=False, height=280,
                          xaxis_title="Wallets", yaxis_title=None,
                          title="Confidence — detector families fired")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        sdist = wallets["structure_type"].value_counts().reset_index()
        sdist.columns = ["structure", "wallets"]
        fig = px.bar(sdist, x="wallets", y="structure", orientation="h",
                     color="structure", color_discrete_map=STRUCTURE_COLORS,
                     text="wallets")
        fig.update_traces(textposition="outside")
        fig.update_layout(**plotly_base(), showlegend=False, height=280,
                          xaxis_title="Wallets", yaxis_title=None,
                          title="Structure type")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(card(
        "<b style='color:#dce3ec;'>Reading the score.</b> "
        "<span style='color:#8fa8c8;'>Confidence counts how many <i>independent</i> detector "
        "families fired, not a weighted severity. Each topology in this data evades a different "
        "detector — bilateral mills are invisible to ring detection, mesh clusters are invisible "
        "to pair-concentration thresholds — so agreement across methods is the evidence. A wallet "
        "at <span class='mono'>medium</span> is not necessarily less severe than one at "
        "<span class='mono'>high</span>; it may simply be a purer example of a single "
        "typology.</span>", left_color="#38bdf8"), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2 — TYPOLOGIES
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Typologies":
    st.markdown("# Wash Trading Typologies")
    st.markdown(
        "<div style='color:#6a8aaa;font-size:0.9rem;margin-bottom:20px;'>"
        "Four structurally distinct patterns were identified. Each defeats a different "
        "detector, which is why the scoring rewards agreement across methods."
        "</div>", unsafe_allow_html=True)

    mills = wallets[wallets["structure_type"] == "bilateral_mill"]
    mesh  = wallets[wallets["structure_type"] == "mesh_cluster"]
    rings = wallets[wallets["structure_type"] == "ring_member"]
    fed   = tokens[tokens["token_structure"] == "distributed_federation"]

    t1, t2, t3, t4 = st.tabs(["Bilateral mills", "Mesh clusters",
                              "Distributed federations", "Atomic round-trips"])

    with t1:
        c1, c2, c3 = st.columns(3)
        c1.markdown(metric(f"{len(mills)}", "Wallets"), unsafe_allow_html=True)
        c2.markdown(metric(fmt_eth(mills["total_pair_volume_eth"].sum()), "Volume"), unsafe_allow_html=True)
        c3.markdown(metric(f"{mills['intensity_max'].max():.0f}", "Peak trades/token"), unsafe_allow_html=True)
        st.markdown(card(
            "Two wallets, one to three tokens, hundreds of round trips. The signature is "
            "<b style='color:#dce3ec;'>intensity</b> — trades divided by distinct tokens. "
            "Wash mills score 100–500; a legitimate high-volume trader scores near 1. "
            "Caught by pair concentration and ping-pong detection; invisible to ring queries.",
            left_color="#ef4444"), unsafe_allow_html=True)
        show = mills.nlargest(12, "total_pair_trades")[
            ["wallet", "total_pair_trades", "top_pair_tokens", "intensity_max",
             "total_pair_volume_eth", "collection_focus"]].copy()
        show["wallet"] = show["wallet"].map(short)
        st.dataframe(show, hide_index=True, use_container_width=True,
                     column_config={
                         "wallet": "Wallet", "total_pair_trades": "Trades",
                         "top_pair_tokens": "Tokens", "intensity_max": "Intensity",
                         "total_pair_volume_eth": st.column_config.NumberColumn("Volume ETH", format="%.0f"),
                         "collection_focus": "Collection"})

    with t2:
        c1, c2, c3 = st.columns(3)
        c1.markdown(metric(f"{len(mesh)}", "Wallets"), unsafe_allow_html=True)
        c2.markdown(metric(f"{mesh['pct_own_max'].max():.0f}%", "Peak pair concentration"), unsafe_allow_html=True)
        c3.markdown(metric(f"{len(tokens[tokens['token_structure']=='mesh_inventory'])}", "Tokens held"), unsafe_allow_html=True)
        st.markdown(card(
            "Six wallets trading with each other across a shared inventory, with nine of "
            "fifteen possible pairs active. <b style='color:#dce3ec;'>No individual pair exceeds "
            "40% concentration</b>, placing the cluster below every bilateral threshold — yet "
            "cluster-level control of its seven tokens is 100%. This is the clearest evidence "
            "of deliberate threshold evasion in the dataset, and it is only visible to ring "
            "detection.", left_color="#a855f7"), unsafe_allow_html=True)
        show = mesh[["wallet", "n_pairs", "pct_own_max", "total_pair_trades",
                     "ring_appearances", "collection_focus"]].copy()
        show["wallet"] = show["wallet"].map(short)
        st.dataframe(show, hide_index=True, use_container_width=True,
                     column_config={
                         "wallet": "Wallet", "n_pairs": "Partners",
                         "pct_own_max": st.column_config.NumberColumn("Concentration %", format="%.0f"),
                         "total_pair_trades": "Trades",
                         "ring_appearances": "Ring appearances",
                         "collection_focus": "Collection"})

    with t3:
        if len(fed):
            c1, c2, c3 = st.columns(3)
            c1.markdown(metric(f"{len(fed)}", "Tokens"), unsafe_allow_html=True)
            c2.markdown(metric(f"{fed['sales'].max():,}", "Peak sales on one token"), unsafe_allow_html=True)
            c3.markdown(metric(f"{fed['dominance_pct'].min():.1f}%", "Lowest dominance"), unsafe_allow_html=True)
        st.markdown(card(
            "Many small pairs grinding a single token, none individually anomalous. The most-traded "
            "token in the entire dataset sits here — highest volume, lowest concentration. "
            "Prices stay in a narrow, plausible band, unlike bilateral mills which run the same "
            "token across three orders of magnitude. <b style='color:#dce3ec;'>Volume and dominance "
            "are independent axes</b>; a detector using only one misses half the wash.",
            left_color="#f59e0b"), unsafe_allow_html=True)
        if len(fed):
            show = fed[["token_id", "collection", "sales", "dominance_pct",
                        "min_price", "max_price", "volume_eth"]].copy()
            st.dataframe(show, hide_index=True, use_container_width=True,
                         column_config={
                             "token_id": "Token", "collection": "Collection",
                             "sales": "Sales",
                             "dominance_pct": st.column_config.NumberColumn("Dominance %", format="%.1f"),
                             "min_price": st.column_config.NumberColumn("Min ETH", format="%.2f"),
                             "max_price": st.column_config.NumberColumn("Max ETH", format="%.0f"),
                             "volume_eth": st.column_config.NumberColumn("Volume ETH", format="%.0f")})

    with t4:
        c1, c2, c3 = st.columns(3)
        c1.markdown(metric(f"{len(atomic)}", "Round-trips"), unsafe_allow_html=True)
        c2.markdown(metric(f"{atomic['origin'].nunique()}", "Origin wallets"), unsafe_allow_html=True)
        c3.markdown(metric(fmt_eth(atomic["price_eth"].sum()), "Cycled volume"), unsafe_allow_html=True)
        st.markdown(card(
            "An NFT sold and returned to its seller <b style='color:#dce3ec;'>inside a single "
            "transaction</b>, routed through a proxy contract. Net ownership change is zero; "
            "the platform still records the volume. These were found by a data-integrity check "
            "comparing two independent Etherscan endpoints — not by a detector — and the "
            "intermediary being a deployed contract makes intent difficult to dispute.",
            left_color="#ef4444"), unsafe_allow_html=True)
        show = atomic.copy()
        for c in ("origin", "proxy", "tx"):
            if c in show.columns:
                show[c] = show[c].map(short)
        st.dataframe(show, hide_index=True, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 3 — WALLETS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Wallets":
    st.markdown("# Wallet Evidence")

    c1, c2, c3 = st.columns(3)
    f_conf = c1.multiselect("Confidence", sorted(wallets["confidence"].unique()),
                            default=sorted(wallets["confidence"].unique()))
    f_struct = c2.multiselect("Structure", sorted(wallets["structure_type"].unique()),
                              default=sorted(wallets["structure_type"].unique()))
    f_coll = c3.multiselect("Collection", sorted(wallets["collection_focus"].unique()),
                            default=sorted(wallets["collection_focus"].unique()))

    df = wallets[wallets["confidence"].isin(f_conf)
                 & wallets["structure_type"].isin(f_struct)
                 & wallets["collection_focus"].isin(f_coll)]

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric(f"{len(df):,}", "Wallets shown"), unsafe_allow_html=True)
    c2.markdown(metric(f"{df['total_pair_trades'].sum():,}", "Trades"), unsafe_allow_html=True)
    c3.markdown(metric(fmt_eth(df["total_pair_volume_eth"].sum()), "Volume"), unsafe_allow_html=True)
    c4.markdown(metric(f"{int(df['flag_attributed'].sum())}", "Attributed"), unsafe_allow_html=True)

    section("Detector coverage")
    flag_cols = [c for c in df.columns if c.startswith("flag_")]
    if flag_cols:
        fdist = pd.DataFrame({
            "detector": [c.replace("flag_", "") for c in flag_cols],
            "wallets": [int(df[c].sum()) for c in flag_cols],
        }).sort_values("wallets", ascending=True)
        fig = px.bar(fdist, x="wallets", y="detector", orientation="h", text="wallets",
                     color_discrete_sequence=["#ff6b2b"])
        fig.update_traces(textposition="outside")
        fig.update_layout(**plotly_base(), height=260, xaxis_title="Wallets", yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    section("Evidence table")
    cols = ["wallet", "collection_focus", "structure_type", "confidence",
            "detectors_fired", "n_pairs", "total_pair_trades", "top_pair_tokens",
            "pct_own_max", "intensity_max", "avg_price_per_trade",
            "total_pair_volume_eth", "funder_tag"]
    cols = [c for c in cols if c in df.columns]
    show = df[cols].sort_values(["detectors_fired", "total_pair_volume_eth"],
                                ascending=[False, False]).copy()
    show["wallet"] = show["wallet"].map(lambda a: short(a, 14))
    st.dataframe(show, hide_index=True, use_container_width=True, height=520,
                 column_config={
                     "wallet": "Wallet", "collection_focus": "Collection",
                     "structure_type": "Structure", "confidence": "Confidence",
                     "detectors_fired": st.column_config.NumberColumn("Detectors", format="%d"),
                     "n_pairs": "Pairs", "total_pair_trades": "Trades",
                     "top_pair_tokens": "Tokens",
                     "pct_own_max": st.column_config.NumberColumn("Conc. %", format="%.0f"),
                     "intensity_max": st.column_config.NumberColumn("Intensity", format="%.0f"),
                     "avg_price_per_trade": st.column_config.NumberColumn("Avg ETH/trade", format="%.1f"),
                     "total_pair_volume_eth": st.column_config.NumberColumn("Volume ETH", format="%.0f"),
                     "funder_tag": "Funder"})

    section("Concentration vs intensity")
    st.markdown(
        "<div style='color:#6a8aaa;font-size:0.85rem;margin-bottom:8px;'>"
        "Both axes are needed. High concentration alone flags legitimate bilateral trading; "
        "the intensity threshold separates wash mills from inventory movement."
        "</div>", unsafe_allow_html=True)
    fig = px.scatter(df, x="pct_own_max", y="intensity_max",
                     color="structure_type", color_discrete_map=STRUCTURE_COLORS,
                     size="total_pair_volume_eth", size_max=34,
                     hover_data={"wallet": True, "total_pair_trades": True})
    fig.update_layout(**plotly_base(), height=420,
                      xaxis_title="Pair concentration (%)",
                      yaxis_title="Trades per distinct token",
                      legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 4 — TOKENS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Tokens":
    st.markdown("# Token Attribution")

    hot = tokens[tokens["sales"] >= 50]
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric(f"{len(tokens):,}", "Tokens sold"), unsafe_allow_html=True)
    c2.markdown(metric(f"{len(hot)}", "With 50+ sales"), unsafe_allow_html=True)
    c3.markdown(metric(f"{100*hot['sales'].sum()/tokens['sales'].sum():.1f}%", "Of all activity"), unsafe_allow_html=True)
    c4.markdown(metric(f"{tokens['max_price'].max():,.0f}", "Peak sale (ETH)"), unsafe_allow_html=True)

    section("Volume against concentration")
    st.markdown(
        "<div style='color:#6a8aaa;font-size:0.85rem;margin-bottom:8px;'>"
        "The two axes are independent. Bilateral mills sit top-right — high volume, one pair "
        "controlling nearly everything. Distributed operations sit top-left: equally busy, "
        "no dominant pair, and invisible to any concentration threshold."
        "</div>", unsafe_allow_html=True)
    fig = px.scatter(tokens, x="dominance_pct", y="sales",
                     color="token_structure", size="volume_eth", size_max=38,
                     hover_data={"token_id": True, "collection": True, "max_price": True},
                     color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(**plotly_base(), height=440,
                      xaxis_title="Top-pair dominance (%)", yaxis_title="Sales",
                      legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        section("Token structure")
        tdist = tokens["token_structure"].value_counts().reset_index()
        tdist.columns = ["structure", "tokens"]
        fig = px.bar(tdist, x="tokens", y="structure", orientation="h", text="tokens",
                     color_discrete_sequence=["#ff6b2b"])
        fig.update_traces(textposition="outside")
        fig.update_layout(**plotly_base(), height=300, xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        section("By collection")
        cd = tokens.groupby("collection").agg(
            tokens=("nft_id", "count"), sales=("sales", "sum")).reset_index()
        fig = px.bar(cd, x="collection", y="sales", color="collection",
                     color_discrete_map=COLLECTION_COLORS, text="sales")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(**plotly_base(), height=300, showlegend=False,
                          xaxis_title=None, yaxis_title="Sales")
        st.plotly_chart(fig, use_container_width=True)

    section("Most-traded tokens")
    show = tokens.nlargest(40, "sales")[
        ["token_id", "collection", "sales", "dominance_pct", "min_price",
         "max_price", "volume_eth", "token_structure"]]
    st.dataframe(show, hide_index=True, use_container_width=True, height=460,
                 column_config={
                     "token_id": "Token", "collection": "Collection", "sales": "Sales",
                     "dominance_pct": st.column_config.NumberColumn("Dominance %", format="%.1f"),
                     "min_price": st.column_config.NumberColumn("Min ETH", format="%.2f"),
                     "max_price": st.column_config.NumberColumn("Max ETH", format="%.0f"),
                     "volume_eth": st.column_config.NumberColumn("Volume ETH", format="%.0f"),
                     "token_structure": "Structure"})

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 5 — CASES & VALIDATION
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Cases & Validation":
    st.markdown("# Cases & Validation")

    section("Attributed operators")
    st.markdown(
        "<div style='color:#6a8aaa;font-size:0.85rem;margin-bottom:8px;'>"
        "Trading pairs whose wallets share a non-exchange first funder. Every attributed funder "
        "seeded <b>exactly two</b> wallets — a setup procedure, not a coincidence. Nine exchange "
        "hot wallets were identified and excluded first; without that step, 23 false links would "
        "have been reported instead of these."
        "</div>", unsafe_allow_html=True)
    ops = operators.copy()
    for c in ("wallet_a", "wallet_b", "funder"):
        if c in ops.columns:
            ops[c] = ops[c].map(short)
    st.dataframe(ops, hide_index=True, use_container_width=True)

    section("Named cases")
    if "case_name" in cases.columns:
        cols = [c for c in ["case_name", "wallet", "structure_type", "confidence",
                            "detectors_fired", "total_pair_trades",
                            "total_pair_volume_eth", "avg_price_per_trade", "funder_tag"]
                if c in cases.columns]
        show = cases[cols].copy()
        show["wallet"] = show["wallet"].map(lambda a: short(a, 14))
        st.dataframe(show, hide_index=True, use_container_width=True,
                     column_config={
                         "case_name": "Case", "wallet": "Wallet",
                         "structure_type": "Structure", "confidence": "Confidence",
                         "detectors_fired": "Detectors",
                         "total_pair_trades": "Trades",
                         "total_pair_volume_eth": st.column_config.NumberColumn("Volume ETH", format="%.0f"),
                         "avg_price_per_trade": st.column_config.NumberColumn("Avg ETH/trade", format="%.1f"),
                         "funder_tag": "Funder"})

    section("Validation")
    v = pd.DataFrame([
        ["Data integrity", "Chunked fetch reconciled against independent single-query control totals",
         "Exact match"],
        ["Cross-endpoint", "Transfer log vs marketplace event agreement on buyer and seller",
         "9 disagreements (0.063%), all root-caused"],
        ["Detector correctness", "Synthetic injection: 3 positive patterns, 3 decoys",
         "All positives fired; both structural decoys rejected"],
        ["Discrimination", "Within-dataset comparison across the three collections",
         "31% vs 70% concentration"],
        ["Incentive thesis", "Royalty-bearing control collections, same window",
         "3.8% marketplace share vs 64.7%"],
        ["External benchmark", "Independent public wash-trade dataset, identical scope",
         "Trade counts matched exactly"],
    ], columns=["Layer", "Method", "Result"])
    st.dataframe(v, hide_index=True, use_container_width=True)

    st.markdown(card(
        "<b style='color:#dce3ec;'>No precision figure is claimed.</b> "
        "<span style='color:#8fa8c8;'>Ground-truth labels for wash trading do not exist, so any "
        "reported precision would have an invented denominator. The negative control confirmed "
        "the economic thesis but produced too few sales to measure a false-positive rate — that "
        "gap is stated rather than papered over. What the suite does establish: the detectors are "
        "correct, they discriminate, they agree with an independent methodology, and their known "
        "false-positive mode is separable by a documented feature.</span>",
        left_color="#38bdf8"), unsafe_allow_html=True)

    section("Summary statistics")
    st.dataframe(summary, hide_index=True, use_container_width=True, height=420,
                 column_config={"metric": "Metric", "value": "Value"})
