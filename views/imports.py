# views/imports.py  —  Import Analysis  (13 charts)
# Called from app.py as:  mod.render(df)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ── Theme ───────────────────────────────────────────────────────────────────────
PLOT_BG = dict(
    paper_bgcolor='#ffffff',
    plot_bgcolor='#ffffff',
    font=dict(color='#333333', size=11),
    legend=dict(bgcolor='#f9f9f9', bordercolor='#e0e0e0', borderwidth=1,
                font=dict(color='#222222')),
    margin=dict(l=10, r=10, t=44, b=10),
    hoverlabel=dict(bgcolor='#ffffff', bordercolor='#cccccc', font_color='#333'),
)

_AXIS = dict(
    gridcolor='#dddddd', linecolor='#bbbbbb', zeroline=False,
    tickfont=dict(color='#333333'), title_font=dict(color='#333333')
)

C = {
    'total':   '#0077aa',
    'bulk':    '#e6a800',
    'general': '#6c5ce7',
    'dry':     '#00a878',
    'liquid':  '#d63384',
    'pos':     '#0077aa',
    'neg':     '#dd3333',
    'avg':     '#e6a800',
}

def _sec(title):
    st.markdown(f"""
    <div style="font-size:12px;font-weight:700;color:#111111;letter-spacing:2px;
        text-transform:uppercase;border-bottom:1px solid #0077aa33;
        padding-bottom:8px;margin:32px 0 16px 0;">{title}</div>
    """, unsafe_allow_html=True)

def _ax(fig, ytitle=None, xtitle=None, tickmode=None, dtick=None,
        categoryorder=None, categoryarray=None, autorange=None,
        side=None, gridcolor=None, xgridcolor=None):
    xcfg = {**_AXIS}
    if xtitle:
        xcfg['title'] = dict(text=xtitle, font=dict(color='#333333'))
    if tickmode:
        xcfg['tickmode'] = tickmode
    if dtick:
        xcfg['dtick'] = dtick
    if categoryorder:
        xcfg['categoryorder'] = categoryorder
    if categoryarray:
        xcfg['categoryarray'] = categoryarray
    if side:
        xcfg['side'] = side
    if xgridcolor:
        xcfg['gridcolor'] = xgridcolor
    fig.update_xaxes(**xcfg)

    ycfg = {**_AXIS}
    if ytitle:
        ycfg['title'] = dict(text=ytitle, font=dict(color='#333333'))
    if autorange:
        ycfg['autorange'] = autorange
    if gridcolor:
        ycfg['gridcolor'] = gridcolor
    fig.update_yaxes(**ycfg)

MONTH_ORDER = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def render(df):

    imp = df[df['Category'] == 'Imports / Million Tons'].copy()
    if imp.empty:
        st.warning("⚠️ No import data for the selected range.")
        return

    if not pd.api.types.is_datetime64_any_dtype(imp['Period Start']):
        imp['Period Start'] = pd.to_datetime(imp['Period Start'], format='mixed', errors='coerce')

    imp['Year']       = imp['Period Start'].dt.year
    imp['MonthNum']   = imp['Period Start'].dt.month
    imp['MonthName']  = imp['Period Start'].dt.strftime('%b')
    imp['MonthLabel'] = imp['Period Start'].dt.strftime('%b-%Y')

    bulk    = imp[imp['Cargo'] == 'Bulk Cargo'].sort_values('Period Start')
    general = imp[imp['Cargo'] == 'General Cargo'].sort_values('Period Start')
    dry     = imp[imp['Cargo'] == 'Total Dry Cargo'].sort_values('Period Start')
    liquid  = imp[imp['Cargo'] == 'Total Liquid Cargo'].sort_values('Period Start')
    total   = imp[imp['Cargo'] == 'Total Cargo'].sort_values('Period Start')

    # ── 1. Total Trend + Rolling Avg ────────────────────────────────────────────
    _sec("📈 Total Import Volume — Monthly Trend")

    t = total.copy()
    t['Roll6'] = t['Figures'].rolling(6, min_periods=1).mean()

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=t['Period Start'], y=t['Figures'],
        mode='lines+markers', name='Total Imports',
        line=dict(color=C['total'], width=2.5), marker=dict(size=5),
        fill='tozeroy', fillcolor='rgba(0,119,170,0.07)',
        hovertemplate='%{x|%b %Y}<br><b>%{y:.3f} M Tons</b><extra></extra>'
    ))
    fig1.add_trace(go.Scatter(
        x=t['Period Start'], y=t['Roll6'],
        mode='lines', name='6-Month Avg',
        line=dict(color=C['avg'], width=1.5, dash='dot'),
        hovertemplate='%{x|%b %Y}<br>6M Avg: %{y:.3f}<extra></extra>'
    ))
    fig1.update_layout(**PLOT_BG, height=340,
                       title=dict(text='Monthly Total Imports with 6-Month Rolling Average',
                                  font=dict(color='#444444', size=12)))
    _ax(fig1, ytitle='Million Tons')
    st.plotly_chart(fig1, use_container_width=True)

    # ── 2. All Cargo Types on One Line Chart ────────────────────────────────────
    _sec("📊 All Cargo Types — Monthly Trend Comparison")

    fig2 = go.Figure()
    for d, name, color in [
        (bulk,    'Bulk Cargo',         C['bulk']),
        (general, 'General Cargo',      C['general']),
        (liquid,  'Total Liquid Cargo', C['liquid']),
    ]:
        fig2.add_trace(go.Scatter(
            x=d['Period Start'], y=d['Figures'],
            mode='lines', name=name,
            line=dict(color=color, width=2),
            hovertemplate=f'%{{x|%b %Y}}<br>{name}: %{{y:.3f}} M Tons<extra></extra>'
        ))
    fig2.update_layout(**PLOT_BG, height=320,
                       title=dict(text='Bulk vs General vs Liquid — Monthly Comparison',
                                  font=dict(color='#444444', size=12)))
    _ax(fig2, ytitle='Million Tons')
    st.plotly_chart(fig2, use_container_width=True)

    # ── 3. Dry vs Liquid (2 cols) ───────────────────────────────────────────────
    _sec("🏗️ Dry Cargo vs Liquid Cargo — Side by Side")

    c1, c2 = st.columns(2)
    with c1:
        fig3a = go.Figure()
        fig3a.add_trace(go.Scatter(
            x=dry['Period Start'], y=dry['Figures'],
            mode='lines+markers', name='Total Dry',
            line=dict(color=C['dry'], width=2.5), marker=dict(size=4),
            fill='tozeroy', fillcolor='rgba(0,168,120,0.08)',
            hovertemplate='%{x|%b %Y}<br>Dry: %{y:.3f} M Tons<extra></extra>'
        ))
        fig3a.update_layout(**PLOT_BG, height=300,
                            title=dict(text='Total Dry Cargo Imports',
                                       font=dict(color='#444444', size=12)))
        _ax(fig3a, ytitle='Million Tons')
        st.plotly_chart(fig3a, use_container_width=True)

    with c2:
        fig3b = go.Figure()
        fig3b.add_trace(go.Scatter(
            x=liquid['Period Start'], y=liquid['Figures'],
            mode='lines+markers', name='Total Liquid',
            line=dict(color=C['liquid'], width=2.5), marker=dict(size=4),
            fill='tozeroy', fillcolor='rgba(214,51,132,0.08)',
            hovertemplate='%{x|%b %Y}<br>Liquid: %{y:.3f} M Tons<extra></extra>'
        ))
        fig3b.update_layout(**PLOT_BG, height=300,
                            title=dict(text='Total Liquid Cargo Imports',
                                       font=dict(color='#444444', size=12)))
        _ax(fig3b, ytitle='Million Tons')
        st.plotly_chart(fig3b, use_container_width=True)

    # ── 4. Stacked Area Chart ───────────────────────────────────────────────────
    _sec("🗂️ Cargo Composition — Stacked Area Chart")

    m = bulk[['Period Start','Figures']].rename(columns={'Figures':'Bulk'})
    m = m.merge(general[['Period Start','Figures']].rename(columns={'Figures':'General'}), on='Period Start')
    m = m.merge(liquid[['Period Start','Figures']].rename(columns={'Figures':'Liquid'}), on='Period Start')
    m = m.sort_values('Period Start')

    fig4 = go.Figure()
    for col_name, color, fill_color in [
        ('Liquid',  C['liquid'],  'rgba(214,51,132,0.65)'),
        ('General', C['general'], 'rgba(108,92,231,0.65)'),
        ('Bulk',    C['bulk'],    'rgba(230,168,0,0.65)'),
    ]:
        fig4.add_trace(go.Scatter(
            x=m['Period Start'], y=m[col_name],
            name=col_name, mode='lines',
            line=dict(width=0.5, color=color),
            stackgroup='one', fillcolor=fill_color,
            hovertemplate=f'%{{x|%b %Y}}<br>{col_name}: %{{y:.3f}} M Tons<extra></extra>'
        ))
    fig4.update_layout(**PLOT_BG, height=320,
                       title=dict(text='Import Composition: Bulk + General + Liquid (Stacked Area)',
                                  font=dict(color='#444444', size=12)))
    _ax(fig4, ytitle='Million Tons (Stacked)')
    st.plotly_chart(fig4, use_container_width=True)

    # ── 5. Year-wise Annual Bars (2 cols) ───────────────────────────────────────
    _sec("📅 Year-wise Annual Import Summary")

    c3, c4 = st.columns(2)

    with c3:
        yr = total.groupby('Year')['Figures'].sum().reset_index()
        fig5a = go.Figure(go.Bar(
            x=yr['Year'], y=yr['Figures'],
            marker_color=C['total'],
            marker_line_color='rgba(0,119,170,0.4)', marker_line_width=1,
            text=yr['Figures'].round(2), textposition='outside',
            textfont=dict(color='#444444', size=10),
            hovertemplate='%{x}<br>Total: %{y:.2f} M Tons<extra></extra>'
        ))
        fig5a.update_layout(**PLOT_BG, height=320,
                            title=dict(text='Annual Total Imports by Year',
                                       font=dict(color='#444444', size=12)))
        _ax(fig5a, ytitle='Million Tons', tickmode='linear', dtick=1)
        st.plotly_chart(fig5a, use_container_width=True)

    with c4:
        grp = imp[imp['Cargo'].isin(['Bulk Cargo','General Cargo','Total Liquid Cargo'])]
        grp = grp.groupby(['Year','Cargo'])['Figures'].sum().reset_index()
        fig5b = go.Figure()
        for cargo, color in [
            ('Bulk Cargo',         C['bulk']),
            ('General Cargo',      C['general']),
            ('Total Liquid Cargo', C['liquid']),
        ]:
            d = grp[grp['Cargo'] == cargo]
            fig5b.add_trace(go.Bar(
                x=d['Year'], y=d['Figures'], name=cargo,
                marker_color=color, opacity=0.9,
                hovertemplate=f'{cargo}<br>%{{x}}: %{{y:.2f}} M Tons<extra></extra>'
            ))
        fig5b.update_layout(**PLOT_BG, height=320, barmode='group',
                            title=dict(text='Annual Cargo Breakdown by Year',
                                       font=dict(color='#444444', size=12)))
        _ax(fig5b, ytitle='Million Tons', tickmode='linear', dtick=1)
        st.plotly_chart(fig5b, use_container_width=True)

    # ── 6. Heatmap Month × Year ─────────────────────────────────────────────────
    _sec("🌡️ Import Intensity Heatmap — Month × Year")

    heat = total.copy()
    heat['HeatMonth'] = heat['Period Start'].dt.month
    heat['HeatYear']  = heat['Period Start'].dt.year
    pivot = heat.pivot_table(
        index='HeatMonth', columns='HeatYear',
        values='Figures', aggfunc='sum'
    )
    pivot.index = [MONTH_ORDER[i - 1] for i in pivot.index]

    z_vals    = np.round(pivot.values.astype(float), 3)
    text_vals = np.where(np.isnan(z_vals), "", z_vals.astype(str))
    fig6 = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[str(c) for c in pivot.columns],
        y=list(pivot.index),
        colorscale=[[0,'#e8f4fb'],[0.3,'#6bbdd4'],[0.6,'#1a8aaa'],[1,'#005577']],
        showscale=True,
        colorbar=dict(tickfont=dict(color='#333333'), outlinecolor='#cccccc',
                      title_font=dict(color='#333333')),
        hovertemplate='Year: %{x}<br>Month: %{y}<br>%{z:.3f} M Tons<extra></extra>',
        text=text_vals,
        texttemplate='%{text}',
        textfont=dict(size=8, color='#111111'),
    ))
    fig6.update_layout(**PLOT_BG, height=380,
                       title=dict(text='Monthly Import Intensity — Brighter = Higher Volume',
                                  font=dict(color='#444444', size=11)))
    _ax(fig6, side='bottom', xgridcolor='#dddddd', autorange='reversed',
        gridcolor='#dddddd')
    st.plotly_chart(fig6, use_container_width=True)

    # ── 7. Bulk vs General Monthly Bars (2 cols) ────────────────────────────────
    _sec("🔍 Dry Cargo Deep Dive — Bulk vs General Monthly")

    c5, c6 = st.columns(2)
    with c5:
        fig7a = go.Figure(go.Bar(
            x=bulk['Period Start'], y=bulk['Figures'],
            marker_color=C['bulk'], opacity=0.85,
            hovertemplate='%{x|%b %Y}<br>Bulk: %{y:.3f} M Tons<extra></extra>'
        ))
        fig7a.update_layout(**PLOT_BG, height=300,
                            title=dict(text='Bulk Cargo Imports — Monthly Bar',
                                       font=dict(color='#444444', size=12)))
        _ax(fig7a, ytitle='Million Tons')
        st.plotly_chart(fig7a, use_container_width=True)

    with c6:
        fig7b = go.Figure(go.Bar(
            x=general['Period Start'], y=general['Figures'],
            marker_color=C['general'], opacity=0.85,
            hovertemplate='%{x|%b %Y}<br>General: %{y:.3f} M Tons<extra></extra>'
        ))
        fig7b.update_layout(**PLOT_BG, height=300,
                            title=dict(text='General Cargo Imports — Monthly Bar',
                                       font=dict(color='#444444', size=12)))
        _ax(fig7b, ytitle='Million Tons')
        st.plotly_chart(fig7b, use_container_width=True)

    # ── 8. Pie + Donut (2 cols) ─────────────────────────────────────────────────
    _sec("🥧 Overall Cargo Share — Pie & Donut")

    share_df = imp[imp['Cargo'].isin(['Bulk Cargo','General Cargo','Total Liquid Cargo'])]
    sg       = share_df.groupby('Cargo')['Figures'].sum().reset_index()
    lbls     = sg['Cargo'].tolist()
    vals     = sg['Figures'].tolist()
    clrs     = [C['bulk'], C['general'], C['liquid']]

    c7, c8 = st.columns(2)
    with c7:
        fig8a = go.Figure(go.Pie(
            labels=lbls, values=vals,
            marker=dict(colors=clrs, line=dict(color='#ffffff', width=2)),
            textinfo='label+percent', textfont=dict(size=11, color='#222222'),
            hovertemplate='%{label}<br>%{value:.2f} M Tons (%{percent})<extra></extra>'
        ))
        fig8a.update_layout(**PLOT_BG, height=300, showlegend=False,
                            title=dict(text='Import Share by Cargo Type',
                                       font=dict(color='#444444', size=12)))
        st.plotly_chart(fig8a, use_container_width=True)

    with c8:
        fig8b = go.Figure(go.Pie(
            labels=lbls, values=vals, hole=0.55,
            marker=dict(colors=clrs, line=dict(color='#ffffff', width=2)),
            textinfo='label+percent', textfont=dict(size=11, color='#222222'),
            hovertemplate='%{label}<br>%{value:.2f} M Tons (%{percent})<extra></extra>'
        ))
        fig8b.update_layout(**PLOT_BG, height=300, showlegend=False,
                            title=dict(text='Cargo Share — Donut View',
                                       font=dict(color='#444444', size=12)))
        st.plotly_chart(fig8b, use_container_width=True)

    # ── 9. Seasonal Average by Month ────────────────────────────────────────────
    _sec("📆 Seasonal Pattern — Average Imports by Month")

    seas = total.groupby('MonthName')['Figures'].mean().reindex(MONTH_ORDER).reset_index()
    seas.columns = ['MonthName', 'AvgFigures']
    overall_avg  = seas['AvgFigures'].mean()

    fig9 = go.Figure(go.Bar(
        x=seas['MonthName'],
        y=seas['AvgFigures'],
        marker_color=[C['pos'] if v >= overall_avg else '#aaccdd' for v in seas['AvgFigures']],
        text=seas['AvgFigures'].round(3), textposition='outside',
        textfont=dict(color='#444444', size=9),
        hovertemplate='%{x}<br>Avg: %{y:.3f} M Tons<extra></extra>'
    ))
    fig9.add_hline(
        y=overall_avg, line_dash='dot',
        line_color=C['avg'], line_width=1.5,
        annotation_text=f'Overall Avg: {overall_avg:.3f}',
        annotation_font_color=C['avg'], annotation_font_size=10,
        annotation_position='top right'
    )
    fig9.update_layout(**PLOT_BG, height=300,
                       title=dict(text='Average Monthly Import Volume — Seasonal Pattern',
                                  font=dict(color='#444444', size=12)))
    _ax(fig9, ytitle='Avg Million Tons',
        categoryorder='array', categoryarray=MONTH_ORDER)
    st.plotly_chart(fig9, use_container_width=True)

    # ── 10. YoY Growth Rate ─────────────────────────────────────────────────────
    _sec("📉 Year-over-Year Growth Rate")

    yoy = total.groupby('Year')['Figures'].sum().reset_index()
    yoy['Growth'] = yoy['Figures'].pct_change() * 100
    yoy_v = yoy.dropna(subset=['Growth']).copy()

    fig10 = go.Figure(go.Bar(
        x=yoy_v['Year'],
        y=yoy_v['Growth'],
        marker_color=[C['pos'] if v >= 0 else C['neg'] for v in yoy_v['Growth']],
        text=[f"{v:+.1f}%" for v in yoy_v['Growth']],
        textposition='outside',
        textfont=dict(color='#444444', size=10),
        hovertemplate='%{x}<br>YoY Growth: %{y:+.2f}%<extra></extra>'
    ))
    fig10.add_hline(y=0, line_color='#aaaaaa', line_width=1)
    fig10.update_layout(**PLOT_BG, height=300,
                        title=dict(text='Year-over-Year Import Growth Rate (%)',
                                   font=dict(color='#444444', size=12)))
    _ax(fig10, ytitle='Growth %', tickmode='linear', dtick=1)
    st.plotly_chart(fig10, use_container_width=True)

    # ── 11. Month-over-Month Change ─────────────────────────────────────────────
    _sec("🔄 Month-over-Month Change — Total Imports")

    mom   = total.copy().sort_values('Period Start')
    mom['MoM'] = mom['Figures'].diff()
    mom_v = mom.dropna(subset=['MoM']).copy()

    fig11 = go.Figure(go.Bar(
        x=mom_v['Period Start'],
        y=mom_v['MoM'],
        marker_color=[C['pos'] if v >= 0 else C['neg'] for v in mom_v['MoM']],
        hovertemplate='%{x|%b %Y}<br>Change: %{y:+.3f} M Tons<extra></extra>'
    ))
    fig11.add_hline(y=0, line_color='#aaaaaa', line_width=1)
    fig11.update_layout(**PLOT_BG, height=280,
                        title=dict(text='Month-over-Month Import Change (Blue = Growth, Red = Decline)',
                                   font=dict(color='#444444', size=12)))
    _ax(fig11, ytitle='Δ Million Tons')
    st.plotly_chart(fig11, use_container_width=True)

    # ── 12. Stacked Bar — Yearly Composition ────────────────────────────────────
    _sec("📦 Yearly Cargo Composition — Stacked Bar")

    sb  = imp[imp['Cargo'].isin(['Bulk Cargo','General Cargo','Total Liquid Cargo'])]
    sb  = sb.groupby(['Year','Cargo'])['Figures'].sum().reset_index()

    fig12 = go.Figure()
    for cargo, color in [
        ('Bulk Cargo',         C['bulk']),
        ('General Cargo',      C['general']),
        ('Total Liquid Cargo', C['liquid']),
    ]:
        d = sb[sb['Cargo'] == cargo]
        fig12.add_trace(go.Bar(
            x=d['Year'], y=d['Figures'], name=cargo,
            marker_color=color, opacity=0.9,
            hovertemplate=f'{cargo}<br>%{{x}}: %{{y:.2f}} M Tons<extra></extra>'
        ))
    fig12.update_layout(**PLOT_BG, height=320, barmode='stack',
                        title=dict(text='Yearly Import Composition — Stacked (Bulk + General + Liquid)',
                                   font=dict(color='#444444', size=12)))
    _ax(fig12, ytitle='Million Tons', tickmode='linear', dtick=1)
    st.plotly_chart(fig12, use_container_width=True)

    # ── 13. Top 10 Highest & Lowest Import Months (2 cols) ──────────────────────
    _sec("🏆 Top 10 Highest & Lowest Import Months")

    top10    = total.nlargest(10, 'Figures').sort_values('Figures', ascending=True)
    bottom10 = total.nsmallest(10, 'Figures').sort_values('Figures', ascending=False)

    c9, c10 = st.columns(2)
    with c9:
        fig13a = go.Figure(go.Bar(
            x=top10['Figures'],
            y=top10['MonthLabel'],
            orientation='h',
            marker_color=C['pos'],
            marker_line_color='rgba(0,119,170,0.4)', marker_line_width=1,
            text=top10['Figures'].round(3), textposition='outside',
            textfont=dict(color='#444444', size=9),
            hovertemplate='%{y}<br>%{x:.3f} M Tons<extra></extra>'
        ))
        fig13a.update_layout(**PLOT_BG, height=380,
                            title=dict(text='Top 10 Highest Import Months',
                                        font=dict(color='#444444', size=12)))
        fig13a.update_layout(margin=dict(l=90, r=30, t=44, b=10))
        fig13a.update_xaxes(**_AXIS, title=dict(text='Million Tons',
                                                font=dict(color='#333333')))
        fig13a.update_yaxes(**_AXIS)
        st.plotly_chart(fig13a, use_container_width=True)

    with c10:
        fig13b = go.Figure(go.Bar(
            x=bottom10['Figures'],
            y=bottom10['MonthLabel'],
            orientation='h',
            marker_color=C['neg'],
            marker_line_color='rgba(221,51,51,0.4)', marker_line_width=1,
            text=bottom10['Figures'].round(3), textposition='outside',
            textfont=dict(color='#444444', size=9),
            hovertemplate='%{y}<br>%{x:.3f} M Tons<extra></extra>'
        ))
        fig13b.update_layout(**PLOT_BG, height=380,
                            title=dict(text='Top 10 Lowest Import Months',
                                        font=dict(color='#444444', size=12)))
        fig13b.update_layout(margin=dict(l=90, r=30, t=44, b=10))
        fig13b.update_xaxes(**_AXIS, title=dict(text='Million Tons',
                                                font=dict(color='#333333')))
        fig13b.update_yaxes(**_AXIS)
        st.plotly_chart(fig13b, use_container_width=True)

    # ── Footer ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;color:#888888;font-size:10px;letter-spacing:2px;
        margin-top:40px;padding-top:16px;border-top:1px solid #dddddd;">
        IMPORT ANALYSIS · KARACHI PORT TRUST · ALL FIGURES IN MILLION TONS
    </div>""", unsafe_allow_html=True)