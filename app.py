import streamlit as st
import pandas as pd
import os
import importlib.util

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KPT Port Intelligence",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
    background-color: #f5f5f5;
    color: #1a1a1a;
}
.stApp { background-color: #f5f5f5; }
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e0e0e0;
}
[data-testid="stSidebar"] * { color: #333333 !important; }
.sidebar-section-label {
    color: #0077aa !important;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 18px 0 8px 4px;
    border-left: 3px solid #0077aa;
    padding-left: 8px;
    display: block;
}
header[data-testid="stHeader"] {
    background-color: #ffffff !important;
    border-bottom: 1px solid #e0e0e0 !important;
}

header[data-testid="stHeader"] * {
    color: #333333 !important;
}

header[data-testid="stHeader"] button {
    background-color: #f0f0f0 !important;
    color: #333333 !important;
    border: 1px solid #cccccc !important;
}
/* Sidebar buttons — force light mode */
[data-testid="stSidebar"] .stButton > button {
    background-color: #f0f0f0 !important;
    color: #222222 !important;
    border: 1px solid #cccccc !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #e0e0e0 !important;
    color: #000000 !important;
    border: 1px solid #aaaaaa !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background-color: #0077aa !important;
    color: #ffffff !important;
    border: 1px solid #0077aa !important;
}           
/* Multiselect dropdown — light mode */
[data-testid="stMultiSelect"] > div {
    background-color: #ffffff !important;
    border-color: #cccccc !important;
    color: #222222 !important;
}
[data-testid="stMultiSelect"] span {
    color: #222222 !important;
}
/* Dropdown popup list */
[data-baseweb="popover"] ul,
[data-baseweb="menu"] {
    background-color: #ffffff !important;
    color: #222222 !important;
}
[data-baseweb="popover"] li,
[data-baseweb="menu"] li {
    color: #222222 !important;
}
[data-baseweb="popover"] li:hover,
[data-baseweb="menu"] li:hover {
    background-color: #f0f0f0 !important;
}
/* Selected tags inside multiselect */
[data-baseweb="tag"] {
    background-color: #0077aa22 !important;
    color: #0077aa !important;
}
/* Selectbox dropdown (Start/End Month) */
[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border-color: #cccccc !important;
    color: #222222 !important;
}
.top-banner {
    background: linear-gradient(135deg, #ffffff 0%, #eaf4fb 60%, #ffffff 100%);
    border: 1px solid #0077aa22;
    border-left: 4px solid #0077aa;
    border-radius: 10px;
    padding: 16px 24px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 18px;
}
.top-banner h1 {
    color: #111111;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0 0 3px 0;
}
.top-banner .sub { color: #888; font-size: 11px; letter-spacing: 1px; }
.top-banner .sub span { color: #0077aa; }
.banner-text { flex: 1; }
.section-heading {
    font-size: 12px;
    font-weight: 700;
    color: #111111;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-bottom: 1px solid #0077aa33;
    padding-bottom: 8px;
    margin: 24px 0 14px 0;
}
div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e0e0e0 !important;
    border-top: 3px solid #0077aa !important;
    border-radius: 8px !important;
    padding: 14px 18px !important;
}
div[data-testid="stMetricValue"] { color: #0077aa !important; font-size: 22px !important; font-weight: 800 !important; }
div[data-testid="stMetricLabel"] { color: #555 !important; font-size: 10px !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; }
div[data-testid="stMetricDelta"] { font-size: 11px !important; }
.coming-soon {
    background: #f9f9f9;
    border: 1px dashed #cccccc;
    border-radius: 10px;
    padding: 80px 20px;
    text-align: center;
    margin-top: 20px;
}
.coming-soon .icon  { color: #0077aa55; font-size: 48px; display: block; margin-bottom: 14px; }
.coming-soon .title { color: #aaaaaa; font-size: 16px; margin-bottom: 6px; }
.coming-soon .msg   { color: #bbbbbb; font-size: 12px; letter-spacing: 1px; }
.sidebar-img-area {
    text-align: center;
    padding: 14px 16px 10px 16px;
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 12px;
}
.sidebar-img-area p {
    color: #aaaaaa !important;
    font-size: 10px;
    letter-spacing: 1px;
    margin: 6px 0 0 0;
    text-transform: uppercase;
}
.sidebar-bottom-img {
    padding: 16px;
    border-top: 1px solid #e0e0e0;
    margin-top: 20px;
    text-align: center;
}
.sidebar-bottom-img p {
    color: #cccccc !important;
    font-size: 9px;
    letter-spacing: 1px;
    margin: 6px 0 0 0;
}
.stSelectbox > div > div { background: #ffffff !important; border-color: #dddddd !important; }
label { color: #555555 !important; font-size: 11px !important; letter-spacing: 0.5px !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #f5f5f5; }
::-webkit-scrollbar-thumb { background: #cccccc; border-radius: 3px; }
footer, #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Theme (shared with views) ───────────────────────────────────────────────────
PLOT_BG = dict(
    paper_bgcolor='#ffffff',
    plot_bgcolor='#ffffff',
    font=dict(color='#333333', size=11),
    xaxis=dict(gridcolor='#dddddd', linecolor='#bbbbbb', zeroline=False,
               tickfont=dict(color='#333333'), title_font=dict(color='#333333')),
    yaxis=dict(gridcolor='#dddddd', linecolor='#bbbbbb', zeroline=False,
               tickfont=dict(color='#333333'), title_font=dict(color='#333333')),
    legend=dict(bgcolor='#f9f9f9', bordercolor='#e0e0e0', borderwidth=1),
    margin=dict(l=10, r=10, t=30, b=10),
    hoverlabel=dict(bgcolor='#ffffff', bordercolor='#cccccc', font_color='#333'),
)
COLORS = {
    'imports': '#00d4ff',
    'exports': '#ff6b6b',
    'bulk':    '#ffd700',
    'general': '#a29bfe',
    'liquid':  '#fd79a8',
    'teu_imp': '#00d4ff',
    'teu_exp': '#ff6b6b',
}

# ── Load Data ───────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    candidates = ["KPT_Data.csv", "KPT_Data_-_KPT_csv.csv"]
    for name in os.listdir("."):
        if name.endswith(".csv") and name not in candidates:
            candidates.append(name)
    for path in candidates:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                df.columns = df.columns.str.strip()
                if 'Month' in df.columns and 'Period Start' not in df.columns:
                    # Clean up any stray leading '=' or '-' characters left over
                    # from CSV/Excel exports (e.g. "=-Jul-2020", "-Jul-20").
                    df['Month'] = (
                        df['Month'].astype(str)
                        .str.strip()
                        .str.lstrip('=')
                        .str.lstrip('-')
                        .str.strip()
                    )
                    # Use format='mixed' so pandas auto-detects the format per
                    # row instead of forcing a single strict pattern like
                    # '%b-%Y'. This handles inconsistent variants such as
                    # "Jul-20", "Jul-2020", "20-Jul", "7/1/2020", etc.
                    df['Period Start'] = pd.to_datetime(
                        df['Month'], format='mixed', errors='coerce'
                    )
                    # If the CSV's Month column is now in the recommended
                    # unambiguous 'YYYY-MM-DD' format, this will parse
                    # correctly with no year/month confusion. 'mixed' is
                    # kept as a safety net for any leftover legacy rows.
                elif 'Period Start' in df.columns:
                    df['Period Start'] = pd.to_datetime(df['Period Start'], dayfirst=True, errors='coerce')
                df['Figures']    = pd.to_numeric(df['Figures'], errors='coerce')
                df['Year']       = df['Period Start'].dt.year
                df['MonthNum']   = df['Period Start'].dt.month
                df['MonthLabel'] = df['Period Start'].dt.strftime('%b-%Y')
                return df
            except Exception:
                continue
    return pd.DataFrame()

df_raw = load_data()

# ── Helper: image as base64 for HTML embed ──────────────────────────────────────
def img_to_b64(path):
    import base64
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

IMG_PATH   = "Gallup_img.png"
img_b64    = img_to_b64(IMG_PATH)
img_tag    = f'<img src="data:image/png;base64,{img_b64}" style="width:110px;border-radius:6px;">' if img_b64 else '<div style="color:#333;font-size:11px;">Gallup_img.png not found</div>'
img_tag_sm = f'<img src="data:image/png;base64,{img_b64}" style="width:80px;border-radius:4px;">' if img_b64 else ''

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:

    # Logo image at top of sidebar
    st.markdown(f"""
    <div class="sidebar-img-area">
        {img_tag}
        <p>KARACHI PORT TRUST</p>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown('<span class="sidebar-section-label">📋 Dashboard Pages</span>', unsafe_allow_html=True)

    pages = {
        "🏠  Overview":       "overview",
        "📥  Imports":        "imports",
        "📤  Exports":        "exports",
        "📦  TEU Containers": "teu",
    }

    if "active_page" not in st.session_state:
        st.session_state.active_page = "overview"

    for label, key in pages.items():
        is_active = st.session_state.active_page == key
        if st.button(label, key=f"nav_{key}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.active_page = key
            st.rerun()

    # Filters
    if not df_raw.empty:
        st.markdown('<span class="sidebar-section-label">🔧 Global Filters</span>', unsafe_allow_html=True)

        periods = sorted(df_raw['Period Start'].dropna().dt.to_period('M').unique())

        start_sel = st.selectbox(
            "📅 Start Month", periods, index=0, key="f_start",
            format_func=lambda p: p.strftime('%b %Y'),
        )
        end_sel = st.selectbox(
            "📅 End Month", periods, index=len(periods) - 1, key="f_end",
            format_func=lambda p: p.strftime('%b %Y'),
        )

        if start_sel > end_sel:
            st.warning("⚠️ Start must be before End month.")
            end_sel = start_sel

        all_years = sorted(df_raw['Year'].dropna().unique().astype(int))
        sel_years = st.multiselect("📆 Year(s) — optional", all_years, default=[], key="f_years")

        st.markdown("""
        <div style='color:#2a2a2a;font-size:10px;letter-spacing:1px;margin-top:14px;'>
        RANGE: JUL 2020 – APR 2026<br>70 MONTHS · KPT OFFICIAL
        </div>""", unsafe_allow_html=True)
    else:
        start_sel, end_sel, sel_years = None, None, []

    # Image again at bottom of sidebar (like Gallup example)
    st.markdown(f"""
    <div class="sidebar-bottom-img">
        {img_tag_sm}
        <p>KPT TRADE INTELLIGENCE</p>
    </div>
    """, unsafe_allow_html=True)

# ── Apply Filters ───────────────────────────────────────────────────────────────
if not df_raw.empty and start_sel and end_sel:
    s_dt = start_sel.to_timestamp()
    e_dt = end_sel.to_timestamp(how='end')
    df   = df_raw[(df_raw['Period Start'] >= s_dt) & (df_raw['Period Start'] <= e_dt)].copy()
    if sel_years:
        df = df[df['Year'].isin(sel_years)]
else:
    df = df_raw.copy()

# Share with views
st.session_state["df_filtered"] = df
st.session_state["PLOT_BG"]     = PLOT_BG
st.session_state["COLORS"]      = COLORS

# ── Header Banner (image + title, like Gallup) ──────────────────────────────────
active_filter_note = (
    f"{start_sel.strftime('%b %Y')} → {end_sel.strftime('%b %Y')}"
    if start_sel else "Jul-2020 → Apr-2026"
)

st.markdown(f"""
<div class="top-banner">
    {img_tag}
    <div class="banner-text">
        <h1>Karachi Port · Dashboard</h1>
        <div class="sub">
            <span>{active_filter_note}</span> &nbsp;·&nbsp;
            Imports · Exports · Cargo Types · Containers
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards — shown on EVERY page ────────────────────────────────────────────
def render_kpis(df):
    if df.empty:
        return

    imp_tot = df[
        df['Category'].str.contains('Import', case=False, na=False) &
        ~df['Category'].str.contains('Total Imports & Exports', case=False, na=False) &
        (df['Cargo'].str.strip().str.lower() == 'total cargo')
    ]['Figures'].sum()

    exp_tot = df[
        df['Category'].str.contains('Export', case=False, na=False) &
        ~df['Category'].str.contains('Total Imports & Exports', case=False, na=False) &
        ~df['Category'].str.contains('Import', case=False, na=False) &
        (df['Cargo'].str.strip().str.lower() == 'total cargo')
    ]['Figures'].sum()

    teu_tot  = df[df['Category'].str.contains('TEU', case=False, na=False)]['Figures'].sum()
    months_n = df['Period Start'].dt.to_period('M').nunique()
    balance  = imp_tot - exp_tot
    avg_mo   = (imp_tot + exp_tot) / months_n if months_n else 0

    st.markdown('<div class="section-heading">📊 Key Performance Indicators</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: st.metric("📥 Total Imports",     f"{imp_tot:,.2f}",  "Million Tons")
    with c2: st.metric("📤 Total Exports",     f"{exp_tot:,.2f}",  "Million Tons")
    with c3: st.metric("📦 Total TEUs",         f"{teu_tot:,.3f}", "Million Containers")
    with c4: st.metric("⚖️ Trade Balance",     f"{balance:+.2f}", "M Tons (I−E)")
    with c5: st.metric("📈 Avg Monthly Trade", f"{avg_mo:,.2f}",  "M Tons / Month")
    with c6: st.metric("🗓️ Months in View",    f"{months_n}",     "Months")

# Always render KPIs (all pages)
render_kpis(df)

# ── View Loader ─────────────────────────────────────────────────────────────────
def _coming_soon(msg=""):
    extra = f'<div class="msg">{msg}</div>' if msg else ''
    st.markdown(f"""
    <div class="coming-soon">
        <span class="icon">🚧</span>
        <div class="title">Under Development</div>
        <div class="msg">This section is being built — check back soon!</div>
        {extra}
    </div>""", unsafe_allow_html=True)

def try_load_view(path, name):
    if os.path.exists(path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod  = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            if hasattr(mod, "render"):
                mod.render(df)
            else:
                st.info("render() function not found in this view.")
        except Exception as e:
            _coming_soon(str(e))
    else:
        _coming_soon()

# ── Page Router ────────────────────────────────────────────────────────────────
active = st.session_state.active_page

if active == "overview":
    if df.empty:
        st.error("⚠️ Could not load data. Make sure **KPT_Data.csv** is in the same folder as **app.py**.")
        st.stop()
    try_load_view("views/overview.py", "overview")

elif active == "imports":
    st.markdown('<div class="section-heading">📥 Imports — Deep Dive</div>', unsafe_allow_html=True)
    try_load_view("views/imports.py", "imports")

elif active == "exports":
    st.markdown('<div class="section-heading">📤 Exports — Deep Dive</div>', unsafe_allow_html=True)
    try_load_view("views/exports.py", "exports")

elif active == "teu":
    st.markdown('<div class="section-heading">📦 TEU Container Analysis</div>', unsafe_allow_html=True)
    try_load_view("views/teu_containers.py", "teu_containers")

# ── Footer ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:36px 0 16px 0;color:#1f1f1f;
    font-size:10px;letter-spacing:2px;border-top:1px solid #161616;margin-top:48px;">
    KARACHI PORT TRUST · TRADE INTELLIGENCE DASHBOARD &nbsp;·&nbsp; JUL 2020 – APR 2026
</div>
""", unsafe_allow_html=True)