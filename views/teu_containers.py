# views/teu_containers.py  —  TEU Container Analysis  (13 charts)
# Called from app.py as:  mod.render(df)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ── Theme ───────────────────────────────────────────────────────────────────────
BASE_LAYOUT = dict(
    paper_bgcolor='#ffffff',
    plot_bgcolor='#ffffff',
    font=dict(color='#333333', size=11),
    legend=dict(bgcolor='#f9f9f9', bordercolor='#e0e0e0', borderwidth=1,
                font=dict(color='#222222')),
    margin=dict(l=10, r=10, t=40, b=10),
    hoverlabel=dict(bgcolor='#ffffff', bordercolor='#cccccc', font_color='#333'),
)

GRID = dict(
    gridcolor='#dddddd', linecolor='#bbbbbb', zeroline=False,
    tickfont=dict(color='#333333'), title_font=dict(color='#333333')
)

C_IMP  = '#0077aa'
C_EXP  = '#cc3333'
C_TOT  = '#1a9e5c'
C_POS  = '#0077aa'
C_NEG  = '#cc3333'
C_GOLD = '#c8880a'

MONTH_ORDER = ['Jan','Feb','Mar','Apr','May','Jun',
               'Jul','Aug','Sep','Oct','Nov','Dec']

def _sec(title):
    st.markdown(f"""
    <div style="font-size:12px;font-weight:700;color:#111111;letter-spacing:2px;
        text-transform:uppercase;border-bottom:1px solid #0077aa33;
        padding-bottom:8px;margin:32px 0 16px 0;">{title}</div>
    """, unsafe_allow_html=True)

def _ax(fig, ytitle=None, xtitle=None, tickmode=None, dtick=None,
        categoryorder=None, categoryarray=None, autorange=None,
        side=None, xgridcolor=None, ygridcolor=None):
    xcfg = {**GRID}
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

    ycfg = {**GRID}
    if ytitle:
        ycfg['title'] = dict(text=ytitle, font=dict(color='#333333'))
    if autorange:
        ycfg['autorange'] = autorange
    if ygridcolor:
        ycfg['gridcolor'] = ygridcolor
    fig.update_yaxes(**ycfg)

def render(df):

    teu = df[df['Category'] == 'Total TEU(s) in Millions'].copy()
    if teu.empty:
        st.warning("⚠️ No TEU data available for the selected range.")
        return

    if not pd.api.types.is_datetime64_any_dtype(teu['Period Start']):
        teu['Period Start'] = pd.to_datetime(teu['Period Start'], format='mixed', errors='coerce')

    teu['Year']       = teu['Period Start'].dt.year
    teu['MonthName']  = teu['Period Start'].dt.strftime('%b')
    teu['MonthLabel'] = teu['Period Start'].dt.strftime('%b-%Y')

    imp = teu[teu['Cargo'] == 'Imports'].sort_values('Period Start')
    exp = teu[teu['Cargo'] == 'Exports'].sort_values('Period Start')

    merged = imp[['Period Start','Figures']].rename(columns={'Figures':'Imp_TEU'}).merge(
        exp[['Period Start','Figures']].rename(columns={'Figures':'Exp_TEU'}),
        on='Period Start'
    ).sort_values('Period Start')

    merged['Total_TEU']  = merged['Imp_TEU'] + merged['Exp_TEU']
    merged['Balance']    = merged['Imp_TEU'] - merged['Exp_TEU']
    merged['Imp_Cnt']    = (merged['Imp_TEU'] * 1_000_000).round(0).astype(int)
    merged['Exp_Cnt']    = (merged['Exp_TEU'] * 1_000_000).round(0).astype(int)
    merged['Total_Cnt']  = merged['Imp_Cnt'] + merged['Exp_Cnt']
    merged['Year']       = merged['Period Start'].dt.year
    merged['MonthName']  = merged['Period Start'].dt.strftime('%b')
    merged['MonthLabel'] = merged['Period Start'].dt.strftime('%b-%Y')

    # ── Info note ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#eaf4fb;border:1px solid #0077aa33;border-left:3px solid #0077aa;
        border-radius:6px;padding:10px 16px;margin-bottom:20px;font-size:11px;color:#444;">
        <b style="color:#0077aa;">ℹ️ TEU Definition:</b>
        1 TEU = one 20-ft equivalent container. All figures in Millions of TEUs unless
        labelled as Actual Containers.
    </div>""", unsafe_allow_html=True)

    # ── 1. Import vs Export TEU Trend ───────────────────────────────────────────
    _sec("📈 Import vs Export TEU — Monthly Trend")

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=merged['Period Start'], y=merged['Imp_TEU'],
        name='Imports', mode='lines+markers',
        line=dict(color=C_IMP, width=2.5), marker=dict(size=4),
        fill='tozeroy', fillcolor='rgba(0,119,170,0.07)',
        hovertemplate='%{x|%b %Y}<br>Imports: %{y:.4f} M TEUs<extra></extra>'
    ))
    fig1.add_trace(go.Scatter(
        x=merged['Period Start'], y=merged['Exp_TEU'],
        name='Exports', mode='lines+markers',
        line=dict(color=C_EXP, width=2.5), marker=dict(size=4),
        fill='tozeroy', fillcolor='rgba(204,51,51,0.07)',
        hovertemplate='%{x|%b %Y}<br>Exports: %{y:.4f} M TEUs<extra></extra>'
    ))
    fig1.update_layout(**BASE_LAYOUT, height=350,
                       title=dict(text='Monthly TEU Imports vs Exports',
                                  font=dict(color='#444444', size=12)))
    _ax(fig1, ytitle='Million TEUs')
    st.plotly_chart(fig1, use_container_width=True)

    # ── 2. Total Containers Per Month ───────────────────────────────────────────
    _sec("📦 Total Containers Per Month — Actual Count")

    fig2 = go.Figure(go.Bar(
        x=merged['Period Start'],
        y=merged['Total_Cnt'],
        marker_color=C_TOT,
        hovertemplate='%{x|%b %Y}<br>Total: %{y:,} containers<extra></extra>'
    ))
    fig2.update_layout(**BASE_LAYOUT, height=300,
                       title=dict(text='Total Containers Handled Per Month (Import + Export)',
                                  font=dict(color='#444444', size=12)))
    _ax(fig2, ytitle='Number of Containers')
    st.plotly_chart(fig2, use_container_width=True)

    # ── 3. Import vs Export Containers Grouped Bar ──────────────────────────────
    _sec("🔀 Import vs Export Containers — Monthly Grouped Bar")

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=merged['Period Start'], y=merged['Imp_Cnt'],
        name='Import Containers', marker_color=C_IMP, opacity=0.9,
        hovertemplate='%{x|%b %Y}<br>Imports: %{y:,}<extra></extra>'
    ))
    fig3.add_trace(go.Bar(
        x=merged['Period Start'], y=merged['Exp_Cnt'],
        name='Export Containers', marker_color=C_EXP, opacity=0.9,
        hovertemplate='%{x|%b %Y}<br>Exports: %{y:,}<extra></extra>'
    ))
    fig3.update_layout(**BASE_LAYOUT, barmode='group', height=320,
                       title=dict(text='Monthly Import vs Export Container Count',
                                  font=dict(color='#444444', size=12)))
    _ax(fig3, ytitle='Number of Containers')
    st.plotly_chart(fig3, use_container_width=True)

    # ── 4. TEU Trade Balance ─────────────────────────────────────────────────────
    _sec("⚖️ TEU Trade Balance — Imports Minus Exports")

    fig4 = go.Figure(go.Bar(
        x=merged['Period Start'],
        y=merged['Balance'],
        marker_color=[C_POS if v >= 0 else C_NEG for v in merged['Balance']],
        hovertemplate='%{x|%b %Y}<br>Balance: %{y:+.4f} M TEUs<extra></extra>'
    ))
    fig4.add_hline(y=0, line_color='#aaaaaa', line_width=1)
    fig4.update_layout(**BASE_LAYOUT, height=280,
                       title=dict(text='Monthly TEU Balance (Blue = More Imports, Red = More Exports)',
                                  font=dict(color='#444444', size=12)))
    _ax(fig4, ytitle='Balance (M TEUs)')
    st.plotly_chart(fig4, use_container_width=True)

    # ── 5. Total TEU Trend + 6-Month Rolling Avg ────────────────────────────────
    _sec("📊 Total TEU Volume — Monthly Trend with Rolling Average")

    ms = merged.copy()
    ms['Roll6'] = ms['Total_TEU'].rolling(6, min_periods=1).mean()

    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=ms['Period Start'], y=ms['Total_TEU'],
        name='Total TEUs', mode='lines+markers',
        line=dict(color=C_TOT, width=2.5), marker=dict(size=4),
        fill='tozeroy', fillcolor='rgba(26,158,92,0.07)',
        hovertemplate='%{x|%b %Y}<br>Total: %{y:.4f} M TEUs<extra></extra>'
    ))
    fig5.add_trace(go.Scatter(
        x=ms['Period Start'], y=ms['Roll6'],
        name='6-Month Avg', mode='lines',
        line=dict(color=C_GOLD, width=1.5, dash='dot'),
        hovertemplate='%{x|%b %Y}<br>6M Avg: %{y:.4f}<extra></extra>'
    ))
    fig5.update_layout(**BASE_LAYOUT, height=340,
                       title=dict(text='Total Monthly TEUs with 6-Month Rolling Average',
                                  font=dict(color='#444444', size=12)))
    _ax(fig5, ytitle='Million TEUs')
    st.plotly_chart(fig5, use_container_width=True)

    # ── 6. Year-wise Annual Summary (2 cols) ────────────────────────────────────
    _sec("📅 Year-wise Annual TEU Summary")

    c1, c2 = st.columns(2)

    with c1:
        yr_tot = merged.groupby('Year')['Total_TEU'].sum().reset_index()
        fig6a = go.Figure(go.Bar(
            x=yr_tot['Year'], y=yr_tot['Total_TEU'],
            marker_color=C_TOT,
            marker_line_color='rgba(26,158,92,0.4)', marker_line_width=1,
            text=yr_tot['Total_TEU'].round(3), textposition='outside',
            textfont=dict(color='#444444', size=10),
            hovertemplate='%{x}<br>Total: %{y:.3f} M TEUs<extra></extra>'
        ))
        fig6a.update_layout(**BASE_LAYOUT, height=320,
                            title=dict(text='Annual Total TEUs by Year',
                                       font=dict(color='#444444', size=12)))
        _ax(fig6a, ytitle='Million TEUs', tickmode='linear', dtick=1)
        st.plotly_chart(fig6a, use_container_width=True)

    with c2:
        yr_imp = merged.groupby('Year')['Imp_TEU'].sum().reset_index()
        yr_exp = merged.groupby('Year')['Exp_TEU'].sum().reset_index()
        fig6b = go.Figure()
        fig6b.add_trace(go.Bar(
            x=yr_imp['Year'], y=yr_imp['Imp_TEU'],
            name='Import TEUs', marker_color=C_IMP, opacity=0.9,
            hovertemplate='Imports %{x}: %{y:.3f} M TEUs<extra></extra>'
        ))
        fig6b.add_trace(go.Bar(
            x=yr_exp['Year'], y=yr_exp['Exp_TEU'],
            name='Export TEUs', marker_color=C_EXP, opacity=0.9,
            hovertemplate='Exports %{x}: %{y:.3f} M TEUs<extra></extra>'
        ))
        fig6b.update_layout(**BASE_LAYOUT, height=320, barmode='group',
                            title=dict(text='Annual Import vs Export TEUs by Year',
                                       font=dict(color='#444444', size=12)))
        _ax(fig6b, ytitle='Million TEUs', tickmode='linear', dtick=1)
        st.plotly_chart(fig6b, use_container_width=True)

    # ── 7. Heatmap Month × Year ─────────────────────────────────────────────────
    _sec("🌡️ TEU Intensity Heatmap — Month × Year")

    heat = merged.copy()
    heat['HeatMonth'] = heat['Period Start'].dt.month
    heat['HeatYear']  = heat['Period Start'].dt.year
    pivot = heat.pivot_table(
        index='HeatMonth', columns='HeatYear',
        values='Total_TEU', aggfunc='sum'
    )
    pivot.index = [MONTH_ORDER[i - 1] for i in pivot.index]

    z_vals    = np.round(pivot.values.astype(float), 3)
    text_vals = np.where(np.isnan(z_vals), "", z_vals.astype(str))
    fig7 = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[str(c) for c in pivot.columns],
        y=list(pivot.index),
        colorscale=[[0,'#e8f4fb'],[0.3,'#6bbdd4'],[0.6,'#1a8aaa'],[1,'#005577']],
        showscale=True,
        colorbar=dict(tickfont=dict(color='#333333'), outlinecolor='#cccccc',
                      title_font=dict(color='#333333')),
        hovertemplate='Year: %{x}<br>Month: %{y}<br>%{z:.4f} M TEUs<extra></extra>',
        text=text_vals,
        texttemplate='%{text}',
        textfont=dict(size=8, color='#111111'),
    ))
    fig7.update_layout(**BASE_LAYOUT, height=380,
                       title=dict(text='Monthly TEU Intensity — Brighter = Higher Volume',
                                  font=dict(color='#444444', size=11)))
    _ax(fig7, side='bottom', xgridcolor='#dddddd', autorange='reversed',
        ygridcolor='#dddddd')
    st.plotly_chart(fig7, use_container_width=True)

    # ── 8. Seasonal Average by Month ────────────────────────────────────────────
    _sec("📆 Seasonal Pattern — Average TEUs by Month")

    seas = merged.groupby('MonthName')['Total_TEU'].mean().reindex(MONTH_ORDER).reset_index()
    seas.columns = ['MonthName', 'AvgTEU']
    overall_avg  = seas['AvgTEU'].mean()

    fig8 = go.Figure(go.Bar(
        x=seas['MonthName'], y=seas['AvgTEU'],
        marker_color=[C_TOT if v >= overall_avg else '#a8dcc4' for v in seas['AvgTEU']],
        text=seas['AvgTEU'].round(4), textposition='outside',
        textfont=dict(color='#444444', size=9),
        hovertemplate='%{x}<br>Avg: %{y:.4f} M TEUs<extra></extra>'
    ))
    fig8.add_hline(
        y=overall_avg, line_dash='dot',
        line_color=C_GOLD, line_width=1.5,
        annotation_text=f'Overall Avg: {overall_avg:.4f}',
        annotation_font_color=C_GOLD, annotation_font_size=10,
        annotation_position='top right'
    )
    fig8.update_layout(**BASE_LAYOUT, height=300,
                       title=dict(text='Average Monthly TEU Volume — Seasonal Pattern',
                                  font=dict(color='#444444', size=12)))
    _ax(fig8, ytitle='Avg Million TEUs',
        categoryorder='array', categoryarray=MONTH_ORDER)
    st.plotly_chart(fig8, use_container_width=True)

    # ── 9. YoY Growth Rate ──────────────────────────────────────────────────────
    _sec("📉 Year-over-Year TEU Growth Rate")

    yoy = merged.groupby('Year')['Total_TEU'].sum().reset_index()
    yoy['Growth'] = yoy['Total_TEU'].pct_change() * 100
    yoy_v = yoy.dropna(subset=['Growth']).copy()

    fig9 = go.Figure(go.Bar(
        x=yoy_v['Year'], y=yoy_v['Growth'],
        marker_color=[C_POS if v >= 0 else C_NEG for v in yoy_v['Growth']],
        text=[f"{v:+.1f}%" for v in yoy_v['Growth']],
        textposition='outside', textfont=dict(color='#444444', size=10),
        hovertemplate='%{x}<br>YoY Growth: %{y:+.2f}%<extra></extra>'
    ))
    fig9.add_hline(y=0, line_color='#aaaaaa', line_width=1)
    fig9.update_layout(**BASE_LAYOUT, height=300,
                       title=dict(text='Year-over-Year TEU Growth Rate (%)',
                                  font=dict(color='#444444', size=12)))
    _ax(fig9, ytitle='Growth %', tickmode='linear', dtick=1)
    st.plotly_chart(fig9, use_container_width=True)

    # ── 10. Month-over-Month Change ─────────────────────────────────────────────
    _sec("🔄 Month-over-Month TEU Change")

    mom = merged.copy().sort_values('Period Start')
    mom['MoM'] = mom['Total_TEU'].diff()
    mom_v = mom.dropna(subset=['MoM']).copy()

    fig10 = go.Figure(go.Bar(
        x=mom_v['Period Start'], y=mom_v['MoM'],
        marker_color=[C_POS if v >= 0 else C_NEG for v in mom_v['MoM']],
        hovertemplate='%{x|%b %Y}<br>Change: %{y:+.4f} M TEUs<extra></extra>'
    ))
    fig10.add_hline(y=0, line_color='#aaaaaa', line_width=1)
    fig10.update_layout(**BASE_LAYOUT, height=280,
                        title=dict(text='Month-over-Month TEU Change (Blue = Growth, Red = Decline)',
                                   font=dict(color='#444444', size=12)))
    _ax(fig10, ytitle='Δ Million TEUs')
    st.plotly_chart(fig10, use_container_width=True)

    # ── 11. Stacked Bar — Yearly Composition ────────────────────────────────────
    _sec("📦 Yearly TEU Composition — Import vs Export Stacked")

    yr_i = merged.groupby('Year')['Imp_TEU'].sum().reset_index()
    yr_e = merged.groupby('Year')['Exp_TEU'].sum().reset_index()

    fig11 = go.Figure()
    fig11.add_trace(go.Bar(
        x=yr_i['Year'], y=yr_i['Imp_TEU'],
        name='Import TEUs', marker_color=C_IMP, opacity=0.9,
        hovertemplate='Imports %{x}: %{y:.3f} M TEUs<extra></extra>'
    ))
    fig11.add_trace(go.Bar(
        x=yr_e['Year'], y=yr_e['Exp_TEU'],
        name='Export TEUs', marker_color=C_EXP, opacity=0.9,
        hovertemplate='Exports %{x}: %{y:.3f} M TEUs<extra></extra>'
    ))
    fig11.update_layout(**BASE_LAYOUT, height=320, barmode='stack',
                        title=dict(text='Yearly TEU Composition — Import + Export Stacked',
                                   font=dict(color='#444444', size=12)))
    _ax(fig11, ytitle='Million TEUs', tickmode='linear', dtick=1)
    st.plotly_chart(fig11, use_container_width=True)

    # ── 12. Import vs Export Share Donut (2 cols) ────────────────────────────────
    _sec("🥧 Overall TEU Share — Import vs Export")

    total_imp = merged['Imp_TEU'].sum()
    total_exp = merged['Exp_TEU'].sum()

    c3, c4 = st.columns(2)
    with c3:
        fig12a = go.Figure(go.Pie(
            labels=['Import TEUs', 'Export TEUs'],
            values=[total_imp, total_exp],
            marker=dict(colors=[C_IMP, C_EXP],
                        line=dict(color='#ffffff', width=2)),
            textinfo='label+percent', textfont=dict(size=12, color='#222222'),
            hovertemplate='%{label}<br>%{value:.3f} M TEUs (%{percent})<extra></extra>'
        ))
        fig12a.update_layout(**BASE_LAYOUT, height=300, showlegend=False,
                             title=dict(text='Overall Import vs Export TEU Share',
                                        font=dict(color='#444444', size=12)))
        st.plotly_chart(fig12a, use_container_width=True)

    with c4:
        fig12b = go.Figure(go.Pie(
            labels=['Import TEUs', 'Export TEUs'],
            values=[total_imp, total_exp],
            hole=0.55,
            marker=dict(colors=[C_IMP, C_EXP],
                        line=dict(color='#ffffff', width=2)),
            textinfo='label+percent', textfont=dict(size=12, color='#222222'),
            hovertemplate='%{label}<br>%{value:.3f} M TEUs (%{percent})<extra></extra>'
        ))
        fig12b.update_layout(**BASE_LAYOUT, height=300, showlegend=False,
                             title=dict(text='TEU Share — Donut View',
                                        font=dict(color='#444444', size=12)))
        st.plotly_chart(fig12b, use_container_width=True)

    # ── 13. Top 10 Highest & Lowest TEU Months (2 cols) ─────────────────────────
    _sec("🏆 Top 10 Highest & Lowest TEU Months")

    top10    = merged.nlargest(10, 'Total_TEU').sort_values('Total_TEU', ascending=True)
    bottom10 = merged.nsmallest(10, 'Total_TEU').sort_values('Total_TEU', ascending=False)

    c5, c6 = st.columns(2)
    with c5:
        fig13a = go.Figure(go.Bar(
            x=top10['Total_TEU'], y=top10['MonthLabel'],
            orientation='h', marker_color=C_TOT,
            marker_line_color='rgba(26,158,92,0.4)', marker_line_width=1,
            text=top10['Total_TEU'].round(4), textposition='outside',
            textfont=dict(color='#444444', size=9),
            hovertemplate='%{y}<br>%{x:.4f} M TEUs<extra></extra>'
        ))
        fig13a.update_layout(**BASE_LAYOUT, height=380,
                             title=dict(text='Top 10 Highest TEU Months',
                                        font=dict(color='#444444', size=12)))
        fig13a.update_layout(margin=dict(l=90, r=30, t=40, b=10))
        fig13a.update_xaxes(**GRID, title=dict(text='Million TEUs',
                                               font=dict(color='#333333')))
        fig13a.update_yaxes(**GRID)
        st.plotly_chart(fig13a, use_container_width=True)

    with c6:
        fig13b = go.Figure(go.Bar(
            x=bottom10['Total_TEU'], y=bottom10['MonthLabel'],
            orientation='h', marker_color=C_NEG,
            marker_line_color='rgba(204,51,51,0.4)', marker_line_width=1,
            text=bottom10['Total_TEU'].round(4), textposition='outside',
            textfont=dict(color='#444444', size=9),
            hovertemplate='%{y}<br>%{x:.4f} M TEUs<extra></extra>'
        ))
        fig13b.update_layout(**BASE_LAYOUT, height=380,
                             title=dict(text='Top 10 Lowest TEU Months',
                                        font=dict(color='#444444', size=12)))
        fig13b.update_layout(margin=dict(l=90, r=30, t=40, b=10))
        fig13b.update_xaxes(**GRID, title=dict(text='Million TEUs',
                                               font=dict(color='#333333')))
        fig13b.update_yaxes(**GRID)
        st.plotly_chart(fig13b, use_container_width=True)

    # ── Footer ───────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;color:#888888;font-size:10px;letter-spacing:2px;
        margin-top:40px;padding-top:16px;border-top:1px solid #dddddd;">
        TEU CONTAINER ANALYSIS · KARACHI PORT TRUST · FIGURES IN MILLION TEUs
    </div>""", unsafe_allow_html=True)