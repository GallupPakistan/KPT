"""
overview.py  —  Karachi Port Dashboard | Overview Page
Convention  :  every views/*.py exposes  def render(df)
Called by   :  app.py  →  from views.overview import render  →  render(df)
Columns     :  Category | Cargo | Figures | Month
Color rule  :  Imports = RED (#E63946)  |  Exports = GREEN (#2DC653)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS — exact values found in dataset columns
# ══════════════════════════════════════════════════════════════════════════════
CAT_IMP = "Imports / Million Tons"
CAT_EXP = "Exports / Million Tons"
CAT_TOT = "Total Imports & Exports / Million Tons"
CAT_TEU = "Total TEU(s) in Millions"

CRG_BULK    = "Bulk Cargo"
CRG_GENERAL = "General Cargo"
CRG_DRY     = "Total Dry Cargo"
CRG_LIQUID  = "Total Liquid Cargo"
CRG_TOTAL   = "Total Cargo"
CRG_TEU_IMP = "Imports"
CRG_TEU_EXP = "Exports"

# ── Colour palette ─────────────────────────────────────────────────────────
C_IMP   = "#cc2233"
C_EXP   = "#1a8a3c"
C_TOT   = "#0d8a7a"
C_DRY   = "#5c2db8"
C_LIQ   = "#1a6fcc"
C_BULK  = "#c87800"
C_GEN   = "#4a2d80"

MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]

_BASE = dict(
    plot_bgcolor  = "#ffffff",
    paper_bgcolor = "#ffffff",
    hovermode     = "x unified",
    font          = dict(family="Segoe UI, Arial", size=12, color="#333333"),
)

_AXIS = dict(
    gridcolor='#dddddd', linecolor='#bbbbbb', zeroline=False,
    tickfont=dict(color='#333333'), title_font=dict(color='#333333')
)

_LEGEND = dict(font=dict(color='#222222'))

# ══════════════════════════════════════════════════════════════════════════════
#  PRIVATE HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "Period Start" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Period Start"]):
        df["Date"] = df["Period Start"]
    else:
        df["Month_Clean"] = (
            df["Month"].astype(str).str.strip()
            .str.lstrip("=").str.lstrip("-").str.strip()
        )
        df["Date"] = pd.to_datetime(df["Month_Clean"], format="mixed", errors="coerce")
    return df.sort_values("Date").reset_index(drop=True)


def _get(df: pd.DataFrame, category: str, cargo: str) -> pd.DataFrame:
    mask = (df["Category"] == category) & (df["Cargo"] == cargo)
    return df[mask][["Date", "Figures"]].set_index("Date").sort_index()


def _layout(**kw) -> dict:
    return {**_BASE, **kw}


def _div() -> None:
    st.markdown("---")


def _sec(label: str) -> None:
    st.markdown(
        f'<div style="font-size:14px;font-weight:700;color:#111111;'
        f'letter-spacing:1px;border-bottom:1px solid #0077aa33;'
        f'padding-bottom:8px;margin:28px 0 14px 0;">{label}</div>',
        unsafe_allow_html=True
    )


def _apply_axes(fig, xtitle=None, ytitle=None, slider=False,
                tickangle=-45, tickformat="%b %Y", nticks=None,
                categoryorder=None, categoryarray=None,
                ticksuffix=None, yrange=None):
    xcfg = {**_AXIS, 'tickangle': tickangle, 'tickformat': tickformat}
    if slider:
        xcfg['rangeslider'] = dict(visible=True, thickness=0.06)
    if nticks:
        xcfg['nticks'] = nticks
    if categoryorder:
        xcfg['categoryorder'] = categoryorder
    if categoryarray:
        xcfg['categoryarray'] = categoryarray
    if xtitle:
        xcfg['title'] = dict(text=xtitle, font=dict(color='#333333'))
    fig.update_xaxes(**xcfg)

    ycfg = {**_AXIS}
    if ytitle:
        ycfg['title'] = dict(text=ytitle, font=dict(color='#333333'))
    if ticksuffix:
        ycfg['ticksuffix'] = ticksuffix
    if yrange:
        ycfg['range'] = yrange
    fig.update_yaxes(**ycfg)


def _line(traces, height=420, ytitle="Million Tons", slider=True, nticks=None):
    fig = go.Figure()
    for x, y, name, color in traces:
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines+markers", name=name,
            line=dict(color=color, width=2.5), marker=dict(size=4),
            hovertemplate=f"%{{x|%b %Y}}<br>{name}: <b>%{{y:.3f}}</b><extra></extra>",
        ))
    fig.update_layout(
        **_layout(height=height, margin=dict(l=55, r=20, t=10, b=60)),
        legend=dict(orientation="h", y=1.08, **_LEGEND),
    )
    _apply_axes(fig, ytitle=ytitle, slider=slider, nticks=nticks)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT  —  app.py calls render(df)
# ══════════════════════════════════════════════════════════════════════════════
def render(df: pd.DataFrame) -> None:

    df = _prepare(df)

    # ── Pre-extract series ─────────────────────────────────────────────────
    imp_tot  = _get(df, CAT_IMP, CRG_TOTAL)
    exp_tot  = _get(df, CAT_EXP, CRG_TOTAL)
    tot_tot  = _get(df, CAT_TOT, CRG_TOTAL)
    dry_tot  = _get(df, CAT_TOT, CRG_DRY)
    liq_tot  = _get(df, CAT_TOT, CRG_LIQUID)
    bulk_tot = _get(df, CAT_TOT, CRG_BULK)
    gen_tot  = _get(df, CAT_TOT, CRG_GENERAL)
    teu_imp  = _get(df, CAT_TEU, CRG_TEU_IMP)
    teu_exp  = _get(df, CAT_TEU, CRG_TEU_EXP)

    tot_df = (
        df[(df["Category"] == CAT_TOT) & (df["Cargo"] == CRG_TOTAL)]
        [["Date", "Figures"]].copy()
    )
    tot_df["Year"]      = tot_df["Date"].dt.year
    tot_df["MonthNum"]  = tot_df["Date"].dt.month
    tot_df["MonthName"] = tot_df["Date"].dt.strftime("%b")

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 1 — Total Combined Cargo
    # ══════════════════════════════════════════════════════════════════════
    _sec("📈  Total Cargo Volume — Imports + Exports Combined")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=tot_tot.index, y=tot_tot["Figures"],
        mode="lines+markers", name="Total Cargo",
        line=dict(color=C_TOT, width=2.5), marker=dict(size=4),
        fill="tozeroy", fillcolor="rgba(46,196,182,0.12)",
        hovertemplate="%{x|%b %Y}<br>Total Cargo: <b>%{y:.3f}</b> M Tons<extra></extra>",
    ))
    fig1.update_layout(
        **_layout(height=420, margin=dict(l=55, r=20, t=10, b=60)),
        legend=dict(orientation="h", y=1.08, **_LEGEND),
    )
    _apply_axes(fig1, ytitle="Million Tons", slider=True)
    st.plotly_chart(fig1, use_container_width=True)
    _div()

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 2 — Imports vs Exports
    # ══════════════════════════════════════════════════════════════════════
    _sec("🔄  Imports vs Exports — Monthly Total Cargo")
    st.plotly_chart(
        _line([
            (imp_tot.index, imp_tot["Figures"], "Imports", C_IMP),
            (exp_tot.index, exp_tot["Figures"], "Exports", C_EXP),
        ]),
        use_container_width=True,
    )
    _div()

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 3 — Dry vs Liquid Stacked Area
    # ══════════════════════════════════════════════════════════════════════
    _sec("🌊  Dry Cargo vs Liquid Cargo — Stacked Area (Total I+E)")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=liq_tot.index, y=liq_tot["Figures"],
        name="Liquid Cargo", fill="tozeroy",
        line=dict(color=C_LIQ, width=2),
        fillcolor="rgba(58,134,255,0.28)",
        hovertemplate="%{x|%b %Y}<br>Liquid: <b>%{y:.3f}</b><extra></extra>",
    ))
    fig3.add_trace(go.Scatter(
        x=dry_tot.index, y=dry_tot["Figures"],
        name="Dry Cargo", fill="tonexty",
        line=dict(color=C_DRY, width=2),
        fillcolor="rgba(131,56,236,0.28)",
        hovertemplate="%{x|%b %Y}<br>Dry: <b>%{y:.3f}</b><extra></extra>",
    ))
    fig3.update_layout(
        **_layout(height=420, margin=dict(l=55, r=20, t=10, b=60)),
        legend=dict(orientation="h", y=1.08, **_LEGEND),
    )
    _apply_axes(fig3, ytitle="Million Tons", slider=True)
    st.plotly_chart(fig3, use_container_width=True)
    _div()

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 4 — Bulk vs General Cargo
    # ══════════════════════════════════════════════════════════════════════
    _sec("📦  Bulk Cargo vs General Cargo — Total I+E Trend")
    st.plotly_chart(
        _line([
            (bulk_tot.index, bulk_tot["Figures"], "Bulk Cargo",    C_BULK),
            (gen_tot.index,  gen_tot["Figures"],  "General Cargo", C_GEN),
        ]),
        use_container_width=True,
    )
    _div()

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 5 — TEU Imports vs Exports
    # ══════════════════════════════════════════════════════════════════════
    _sec("🏗️  Container Volume (TEU) — Imports vs Exports")
    st.plotly_chart(
        _line([
            (teu_imp.index, teu_imp["Figures"], "TEU Imports", C_IMP),
            (teu_exp.index, teu_exp["Figures"], "TEU Exports", C_EXP),
        ], ytitle="Million TEUs"),
        use_container_width=True,
    )
    _div()

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 6 — Year-over-Year Grouped Bar
    # ══════════════════════════════════════════════════════════════════════
    _sec("📅  Year-over-Year Total Cargo — Same Month Across Years")
    years   = sorted(tot_df["Year"].unique())
    palette = px.colors.qualitative.Bold
    fig6 = go.Figure()
    for i, yr in enumerate(years):
        sub = tot_df[tot_df["Year"] == yr].sort_values("MonthNum")
        fig6.add_trace(go.Bar(
            x=sub["MonthName"], y=sub["Figures"],
            name=str(yr),
            marker_color=palette[i % len(palette)],
            hovertemplate=f"{yr} — %{{x}}: <b>%{{y:.3f}}</b> M Tons<extra></extra>",
        ))
    fig6.update_layout(
        **_layout(height=460, barmode="group",
                  margin=dict(l=55, r=20, t=10, b=100),),
        legend=dict(orientation="h", y=-0.28, font=dict(size=11, color='#222222')),
    )
    _apply_axes(fig6, ytitle="Million Tons", tickformat="",
                categoryorder="array", categoryarray=MONTH_ORDER)
    st.plotly_chart(fig6, use_container_width=True)
    _div()

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 7 — Monthly Heatmap
    # ══════════════════════════════════════════════════════════════════════
    _sec("🌡️  Total Cargo Heatmap — Year × Month")
    heat = tot_df.pivot_table(
        index="Year", columns="MonthName", values="Figures", aggfunc="sum"
    ).reindex(columns=MONTH_ORDER)
    z_vals    = np.round(heat.values.astype(float), 3)
    text_vals = np.where(np.isnan(z_vals), "", z_vals.astype(str))
    fig7 = go.Figure(go.Heatmap(
        z=z_vals,
        x=MONTH_ORDER,
        y=[str(y) for y in heat.index.tolist()],
        colorscale="Blues",
        text=text_vals, texttemplate="%{text}", textfont=dict(size=10, color='#222222'),
        hoverongaps=False,
        colorbar=dict(title="M Tons", thickness=14,
                      tickfont=dict(color='#333333'),
                      title_font=dict(color='#333333')),
        hovertemplate="Year: %{y} | %{x}<br>Cargo: <b>%{z:.3f}</b> M Tons<extra></extra>",
    ))
    fig7.update_layout(
        **_layout(height=360, margin=dict(l=65, r=20, t=10, b=40)),
    )
    _apply_axes(fig7, xtitle="Month", ytitle="Year", tickformat="", tickangle=0)
    st.plotly_chart(fig7, use_container_width=True)
    _div()

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 8 & 9 — Donut Charts
    # ══════════════════════════════════════════════════════════════════════
    _sec("🍩  Import vs Export Share &nbsp;&nbsp;|&nbsp;&nbsp;  Cargo Type Composition")
    col8, col9 = st.columns(2)

    imp_sum  = imp_tot["Figures"].sum()
    exp_sum  = exp_tot["Figures"].sum()
    fig8 = go.Figure(go.Pie(
        labels=["Imports", "Exports"],
        values=[imp_sum, exp_sum],
        hole=0.58,
        marker=dict(colors=[C_IMP, C_EXP], line=dict(color="#ffffff", width=2)),
        textinfo="label+percent",
        textfont=dict(color='#222222'),
        hovertemplate="%{label}: <b>%{value:.3f}</b> M Tons (%{percent})<extra></extra>",
    ))
    fig8.update_layout(
        **_layout(height=380, margin=dict(l=20, r=20, t=40, b=20)),
        title=dict(text="Import vs Export Split<br><sub>Full Period Totals</sub>",
                   x=0.5, font=dict(size=13, color='#222222')),
        legend=dict(orientation="h", y=-0.12, **_LEGEND),
        annotations=[dict(text=f"Total<br>{imp_sum + exp_sum:.1f} MT",
                          x=0.5, y=0.5, showarrow=False,
                          font=dict(size=13, color='#222222'))],
    )
    col8.plotly_chart(fig8, use_container_width=True)

    bulk_sum = bulk_tot["Figures"].sum()
    gen_sum  = gen_tot["Figures"].sum()
    liq_sum  = liq_tot["Figures"].sum()
    fig9 = go.Figure(go.Pie(
        labels=["Bulk Cargo", "General Cargo", "Liquid Cargo"],
        values=[bulk_sum, gen_sum, liq_sum],
        hole=0.58,
        marker=dict(colors=[C_BULK, C_GEN, C_LIQ],
                    line=dict(color="#ffffff", width=2)),
        textinfo="label+percent",
        textfont=dict(color='#222222'),
        hovertemplate="%{label}: <b>%{value:.3f}</b> M Tons (%{percent})<extra></extra>",
    ))
    fig9.update_layout(
        **_layout(height=380, margin=dict(l=20, r=20, t=40, b=20)),
        title=dict(text="Cargo Type Composition<br><sub>Total Imports + Exports</sub>",
                   x=0.5, font=dict(size=13, color='#222222')),
        legend=dict(orientation="h", y=-0.12, **_LEGEND),
    )
    col9.plotly_chart(fig9, use_container_width=True)
    _div()

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 10 — Month-over-Month Growth
    # ══════════════════════════════════════════════════════════════════════
    _sec("📉  Month-over-Month Growth Rate — Total Cargo (%)")
    mom = tot_df.sort_values("Date").copy()
    mom["MoM_pct"] = mom["Figures"].pct_change() * 100
    mom = mom.dropna(subset=["MoM_pct"])
    bar_colors = [C_EXP if v >= 0 else C_IMP for v in mom["MoM_pct"]]

    fig10 = go.Figure()
    fig10.add_trace(go.Bar(
        x=mom["Date"], y=mom["MoM_pct"],
        marker_color=bar_colors,
        hovertemplate="%{x|%b %Y}<br>MoM Change: <b>%{y:.2f}%</b><extra></extra>",
        name="MoM %",
    ))
    fig10.add_hline(y=0, line_dash="dot", line_color="#aaaaaa", line_width=1)
    fig10.update_layout(
        **_layout(height=400, margin=dict(l=55, r=20, t=10, b=60), showlegend=False),
    )
    _apply_axes(fig10, ytitle="% Change")
    st.plotly_chart(fig10, use_container_width=True)
    _div()

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 11 — 3-Month Rolling Average
    # ══════════════════════════════════════════════════════════════════════
    _sec("📊  3-Month Rolling Average — Smoothed Total Cargo Trend")
    roll = tot_df.sort_values("Date").copy()
    roll["Roll3"] = roll["Figures"].rolling(3, min_periods=1).mean()
    fig11 = go.Figure()
    fig11.add_trace(go.Scatter(
        x=roll["Date"], y=roll["Figures"],
        mode="lines", name="Actual",
        line=dict(color="rgba(100,100,100,0.4)", width=1.5),
        hovertemplate="%{x|%b %Y}<br>Actual: <b>%{y:.3f}</b><extra></extra>",
    ))
    fig11.add_trace(go.Scatter(
        x=roll["Date"], y=roll["Roll3"],
        mode="lines", name="3-Month Rolling Avg",
        line=dict(color=C_TOT, width=3),
        hovertemplate="%{x|%b %Y}<br>Rolling Avg: <b>%{y:.3f}</b><extra></extra>",
    ))
    fig11.update_layout(
        **_layout(height=420, margin=dict(l=55, r=20, t=10, b=60)),
        legend=dict(orientation="h", y=1.08, **_LEGEND),
    )
    _apply_axes(fig11, ytitle="Million Tons", slider=True)
    st.plotly_chart(fig11, use_container_width=True)
    _div()

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 12 — Cargo % Composition Stacked Bar
    # ══════════════════════════════════════════════════════════════════════
    _sec("📊  Cargo Composition (%) — Bulk, General, Liquid Monthly Share")
    common_idx = (
        bulk_tot.index
        .intersection(gen_tot.index)
        .intersection(liq_tot.index)
    )
    comp = pd.DataFrame({
        "Bulk":    bulk_tot.loc[common_idx, "Figures"],
        "General": gen_tot.loc[common_idx,  "Figures"],
        "Liquid":  liq_tot.loc[common_idx,  "Figures"],
    })
    row_sum = comp.sum(axis=1).replace(0, np.nan)
    pct     = comp.div(row_sum, axis=0) * 100
    fig12 = go.Figure()
    for col, name, color in [
        ("Bulk",    "Bulk %",    C_BULK),
        ("General", "General %", C_GEN),
        ("Liquid",  "Liquid %",  C_LIQ),
    ]:
        fig12.add_trace(go.Bar(
            x=pct.index, y=pct[col], name=name, marker_color=color,
            hovertemplate=f"%{{x|%b %Y}}<br>{name}: <b>%{{y:.1f}}%</b><extra></extra>",
            text=sub['Figures'].round(2),
            textposition='outside',          # or 'inside', 'auto'
            textfont=dict(color='#444444', size=9),
        ))
    fig12.update_layout(
        **_layout(height=420, barmode="stack",
                  margin=dict(l=55, r=20, t=10, b=60)),
        legend=dict(orientation="h", y=1.08, **_LEGEND),
    )
    _apply_axes(fig12, ytitle="% of Total Cargo", ticksuffix="%", yrange=[0, 100])
    st.plotly_chart(fig12, use_container_width=True)
    _div()

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 13 — Liquid Cargo: Imports vs Exports
    # ══════════════════════════════════════════════════════════════════════
    _sec("💧  Liquid Cargo — Imports vs Exports Over Time")
    liq_imp = _get(df, CAT_IMP, CRG_LIQUID)
    liq_exp = _get(df, CAT_EXP, CRG_LIQUID)
    st.plotly_chart(
        _line([
            (liq_imp.index, liq_imp["Figures"], "Liquid Imports", C_IMP),
            (liq_exp.index, liq_exp["Figures"], "Liquid Exports", C_EXP),
        ]),
        use_container_width=True,
    )
    _div()

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 14 & 15 — Bulk/General split per direction
    # ══════════════════════════════════════════════════════════════════════
    _sec("📦  Import: Bulk vs General &nbsp;&nbsp;|&nbsp;&nbsp;  Export: Bulk vs General")
    col14, col15 = st.columns(2)

    def _bg_fig(cat: str, title: str) -> go.Figure:
        b = _get(df, cat, CRG_BULK)
        g = _get(df, cat, CRG_GENERAL)
        fig = go.Figure()
        for series, name, color in [
            (b, "Bulk Cargo",    C_BULK),
            (g, "General Cargo", C_GEN),
        ]:
            fig.add_trace(go.Scatter(
                x=series.index, y=series["Figures"],
                mode="lines", name=name,
                line=dict(color=color, width=2),
                hovertemplate=f"%{{x|%b %Y}}<br>{name}: <b>%{{y:.3f}}</b><extra></extra>",
            ))
        fig.update_layout(
            **_layout(height=390, margin=dict(l=40, r=10, t=40, b=70)),
            title=dict(text=title, x=0.5, font=dict(size=13, color='#222222')),
            legend=dict(orientation="h", y=1.08, **_LEGEND),
        )
        _apply_axes(fig, ytitle="Million Tons", nticks=10)
        return fig

    col14.plotly_chart(_bg_fig(CAT_IMP, "Imports — Bulk vs General"),
                       use_container_width=True)
    col15.plotly_chart(_bg_fig(CAT_EXP, "Exports — Bulk vs General"),
                       use_container_width=True)
    _div()

    # ══════════════════════════════════════════════════════════════════════
    #  CHART 16 — Annual Totals Grouped Bar
    # ══════════════════════════════════════════════════════════════════════
    _sec("📊  Annual Total Cargo — Imports, Exports & Grand Total")

    def _annual(cat, cargo):
        sub = df[(df["Category"] == cat) & (df["Cargo"] == cargo)].copy()
        return (
            sub.groupby(sub["Date"].dt.year)["Figures"]
            .sum().reset_index()
            .rename(columns={"Date": "Year"})
        )

    ann_imp = _annual(CAT_IMP, CRG_TOTAL)
    ann_exp = _annual(CAT_EXP, CRG_TOTAL)
    ann_tot = _annual(CAT_TOT, CRG_TOTAL)

    fig16 = go.Figure()
    for data, name, color in [
        (ann_imp, "Imports",     C_IMP),
        (ann_exp, "Exports",     C_EXP),
        (ann_tot, "Grand Total", C_TOT),
    ]:
        fig16.add_trace(go.Bar(
            x=data["Year"].astype(str), y=data["Figures"],
            name=name, marker_color=color,
            hovertemplate=f"Year: %{{x}}<br>{name}: <b>%{{y:.3f}}</b> M Tons<extra></extra>",
            text=data['Figures'].round(2),
            textposition='outside',          # or 'inside', 'auto'
            textfont=dict(color='#444444', size=9),
        ))
    fig16.update_layout(
        **_layout(height=440, barmode="group",
                  margin=dict(l=55, r=20, t=10, b=60)),
        legend=dict(orientation="h", y=1.08, **_LEGEND),
    )
    _apply_axes(fig16, xtitle="Year", ytitle="Million Tons (Annual Sum)", tickformat="")
    st.plotly_chart(fig16, use_container_width=True)

    # ── Footer ────────────────────────────────────────────────────────────
    _div()
    st.markdown(
        "<p style='text-align:center;color:#888888;font-size:12px;'>"
        "⚓ Karachi Port Authority — Data Analytics Dashboard &nbsp;|&nbsp;"
        "Overview Page &nbsp;|&nbsp; Jul 2020 – Apr 2026"
        "</p>",
        unsafe_allow_html=True,
    )