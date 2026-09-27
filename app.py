"""
ANALIZADOR MULTI-TEMPORAL DINÁMICO
Configuración Libre de Temporalidades (W1 / D1 / H4 / H1 / M30 / M15 / M5 / M1)
MA30/50/100/200 · RSI · MACD
© 2026 JC TRADER ANALYSIS
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io

# ── Config página ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Analizador Multi-Temporal Dinámico",
    page_icon="📊",
    layout="wide",
)

# ── MAPEO GENERAL DE TEMPORALIDADES ───────────────────────────────────────────
TIMEFRAMES = {
    "W1": {"label": "📅 W1 — Semanal",  "interval": "1wk", "period": "5y"},
    "D1": {"label": "📅 D1 — Diario",   "interval": "1d",  "period": "2y"},
    "H4": {"label": "🕓 H4 — 4 Horas",  "interval": "1h",  "period": "730d"}, # Resampled de 1h
    "H1": {"label": "🕐 H1 — Horario",  "interval": "1h",  "period": "60d"},
    "M30": {"label": "⏱ M30 — 30 min",  "interval": "30m", "period": "30d"},
    "M15": {"label": "⚡ M15 — 15 min",  "interval": "15m", "period": "15d"},
    "M5":  {"label": "⚡ M5 — 5 min",   "interval": "5m",  "period": "5d"},
    "M1":  {"label": "🚀 M1 — 1 min",   "interval": "1m",  "period": "1d"}
}

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Analizador Técnico")
    st.markdown('<center style="font-size: 13px; color: #8b949e; margin-bottom: 12px;">Multitemporal Personalizable · MA · RSI · MACD</center>', unsafe_allow_html=True)
    st.divider()

    sym_input = st.text_input("🔎 Ticker", value="F", placeholder="TSLA · AAPL · F · BTC-USD")
    cargar = st.button("▶ Cargar ticker", type="primary", use_container_width=True)

    if cargar:
        st.session_state["sym"] = sym_input.upper().strip()
        st.cache_data.clear()
        st.rerun()

    if "sym" not in st.session_state:
        st.session_state["sym"] = "F"

    st.divider()

    asset_type = st.selectbox("📦 Tipo de activo", ["Acción (Stock)", "Cripto", "Forex", "Índice", "Commodity"])

    # --- SECCIÓN MULTITEMPORAL DINÁMICA ---
    st.markdown("### 🎛️ Configuración Multitemporal")
    
    tf_list = list(TIMEFRAMES.keys())
    
    # 1. Macro Trend (Por defecto H4 o D1)
    macro_tf = st.selectbox(
        "1. MACRO TREND (Tendencia):",
        options=tf_list,
        index=2 # H4
    )
    
    # 2. Estructura / Confirmación (Por defecto H1)
    struct_tf = st.selectbox(
        "2. ESTRUCTURA (Confirmación):",
        options=tf_list,
        index=3 # H1
    )
    
    # 3. Gatillo / Entrada (Por defecto M5)
    trigger_tf = st.selectbox(
        "3. GATILLO (Entrada / Scalp):",
        options=tf_list,
        index=6 # M5
    )

    st.divider()
    
    # Selector de visualización en el gráfico
    tf_key = st.radio(
        "📈 Mostrar Gráfico en:",
        [macro_tf, struct_tf, trigger_tf],
        format_func=lambda x: TIMEFRAMES[x]["label"]
    )

    st.divider()
    st.markdown("**📉 Medias móviles**")
    show_ma = {
        30:  st.checkbox("MA 30",  value=True),
        50:  st.checkbox("MA 50",  value=True),
        100: st.checkbox("MA 100", value=True),
        200: st.checkbox("MA 200", value=True),
    }

    st.divider()
    dark_mode = st.radio("🎨 Tema Gráfico", ["Oscuro", "Claro"], horizontal=True) == "Oscuro"

    st.divider()
    st.markdown("**📌 Acceso Rápido (Watchlist)**")
    quick_list = ["F", "TSLA", "AAPL", "MSFT", "NVDA", "SPY", "QQQ", "BTC-USD"]
    
    for q_sym in quick_list:
        if st.button(f"▪ {q_sym}", key=f"btn_{q_sym}", use_container_width=True):
            st.session_state["sym"] = q_sym
            st.cache_data.clear()
            st.rerun()

    st.divider()
    st.markdown('<center style="font-size: 12px; color: #8b949e;">⚠ Datos vía Yahoo Finance</center>', unsafe_allow_html=True) 
    st.markdown('<center style="font-size: 13px; color: #8b949e; margin-top: 4px;">© 2026 JC TRADER ANALYSIS</center>', unsafe_allow_html=True)
    st.divider()


# Variables de color para las tarjetas HTML
CARD_BG = "#161b22" if dark_mode else "#f0f2f6"
TEXT_COLOR = "#c9d1d9" if dark_mode else "#1f2937"
BORDER_COLOR = "#30363d" if dark_mode else "#e5e7eb"

# ── CSS LIMPIO ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
.block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; }}
.card {{
    background: {CARD_BG}; border: 1px solid {BORDER_COLOR};
    border-radius: 10px; padding: 14px 16px; margin-bottom: 4px; color: {TEXT_COLOR} !important;
}}
.card-lbl {{ font-size: 10px; font-weight: 700; color: #8b949e; text-transform: uppercase; letter-spacing: .6px; margin-bottom: 6px; }}
.card-val {{ font-size: 18px; font-weight: 700; color: #FFE066; }}
.card-sub {{ font-size: 11px; color: #8b949e; margin-top: 3px; }}
.tf-card  {{ background: {CARD_BG}; border: 1px solid {BORDER_COLOR}; border-radius: 10px; padding: 16px; color: {TEXT_COLOR} !important; }}
.tf-lbl   {{ font-size: 10px; font-weight: 700; color: #8b949e; text-transform: uppercase; letter-spacing: .6px; margin-bottom: 8px; }}
.tf-trend {{ font-size: 15px; font-weight: 700; margin-bottom: 8px; }}
.bull {{ color: #22D991; }} .bear {{ color: #FF5252; }} .lat {{ color: #FFB830; }}
.tf-body  {{ font-size: 12px; line-height: 1.65; }}
.dec-buy  {{ background:#0d2818; border:1px solid #22D991; border-radius:10px; padding:16px 20px; }}
.dec-sell {{ background:#2d0f0f; border:1px solid #FF5252; border-radius:10px; padding:16px 20px; }}
.dec-wait {{ background:#2d2000; border:1px solid #FFB830; border-radius:10px; padding:16px 20px; }}
.dec-title{{ font-size:15px; font-weight:700; margin-bottom:8px; }}
.dec-body {{ font-size:12px; line-height:1.7; color:#c9d1d9; }}
.dec-buy .dec-title {{ color:#22D991; }} .dec-sell .dec-title {{ color:#FF5252; }} .dec-wait .dec-title {{ color:#FFB830; }}
.slbl {{ font-size:11px; font-weight:700; color:#8b949e; text-transform:uppercase; letter-spacing:.6px;
        border-bottom:1px solid {BORDER_COLOR}; padding-bottom:5px; margin-bottom:12px; }}
</style>
""", unsafe_allow_html=True)


# ── INDICADORES MATEMÁTICOS ───────────────────────────────────────────────────
def ma(s, p):   return s.rolling(p).mean()
def ema(s, p):  return s.ewm(span=p, adjust=False).mean()

def rsi(s, p=14):
    d = s.diff()
    g = d.clip(lower=0).rolling(p).mean()
    l = (-d.clip(upper=0)).rolling(p).mean()
    return 100 - 100 / (1 + g / l.replace(0, np.nan))

def macd(s):
    m = ema(s, 12) - ema(s, 26)
    sig = ema(m, 9)
    return m, sig, m - sig

def atr(h, l, c, p=14):
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(p).mean()


# ── DESCARGA Y PROCESAMIENTO DINÁMICO DE DATOS ────────────────────────────────
@st.cache_data(ttl=15, show_spinner=False)
def get_df(sym, key):
    cfg = TIMEFRAMES[key]
    interval = cfg["interval"]
    period = cfg["period"]
    
    try:
        df = yf.download(sym, interval=interval, period=period, auto_adjust=True, progress=False)
        if df is not None and not df.empty and len(df) > 5:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            df.columns = [str(c).strip().capitalize() for c in df.columns]
            df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
            df = df.astype(float)
            
            # Procesar H4 de forma especial resampleando de 1h
            if key == "H4":
                df = df.resample('4h').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()
                
            return df, interval, period
    except:
        pass
    return None, None, None

@st.cache_data(ttl=15, show_spinner=False)
def get_info(sym):
    try:
        df1y = yf.download(sym, period="5d", interval="1d", auto_adjust=True, progress=False)
        if df1y.empty:
            return None
        
        if isinstance(df1y.columns, pd.MultiIndex):
            df1y.columns = df1y.columns.get_level_values(0)
        df1y.columns = [str(c).strip().capitalize() for c in df1y.columns]
        
        price  = float(df1y["Close"].iloc[-1])
        prev   = float(df1y["Close"].iloc[-2]) if len(df1y) > 1 else price
        high52 = float(df1y["High"].max())
        low52  = float(df1y["Low"].min())
        
        chg    = (price - prev) / prev * 100 if prev != 0 else 0
        drop   = (price - high52) / high52 * 100 if high52 != 0 else 0
        rng    = (price - low52) / (high52 - low52) * 100 if high52 != low52 else 50
        
        return dict(price=price, prev=prev, high52=high52, low52=low52,
                    chg=chg, drop=drop, rng=rng, name=sym, currency="USD")
    except:
        return None


# ── ANÁLISIS TÉCNICO MULTI-TEMPORAL DINÁMICO ──────────────────────────────────
def analyze(df_macro, df_struct, df_trigger, info, tfs_keys):
    if df_macro is None or len(df_macro) < 5 or info is None:
        return None
        
    c = df_macro["Close"].squeeze()
    h = df_macro["High"].squeeze()
    l = df_macro["Low"].squeeze()
    price = info["price"]

    ma30  = float(ma(c, 30).iloc[-1]) if len(c) >= 30 else float(ma(c, 10).iloc[-1])
    ma50  = float(ma(c, 50).iloc[-1]) if len(c) >= 50 else ma30
    ma100 = float(ma(c, 100).iloc[-1]) if len(c) >= 100 else None
    ma200 = float(ma(c, 200).iloc[-1]) if len(c) >= 200 else None

    r     = rsi(c)
    rv    = float(r.iloc[-1]) if not pd.isna(r.iloc[-1]) else 50.0
    ml, sl_m, hl = macd(c)
    mv    = float(ml.iloc[-1]) if not pd.isna(ml.iloc[-1]) else 0.0
    sv    = float(sl_m.iloc[-1]) if not pd.isna(sl_m.iloc[-1]) else 0.0
    hv    = float(hl.iloc[-1]) if not pd.isna(hl.iloc[-1]) else 0.0
    av    = float(atr(h, l, c).iloc[-1]) if len(c) > 14 else price * 0.01

    sc = 0
    if ma100 and price > ma100: sc += 2
    if ma200 and price > ma200: sc += 2
    if price > ma50:  sc += 1
    if price > ma30:  sc += 1
    if mv > 0:        sc += 1
    if rv > 55:       sc += 1
    t_macro = "Alcista" if sc >= 5 else "Bajista" if sc <= 2 else "Lateral"

    # Análisis Estructura Intermedia
    if df_struct is not None and len(df_struct) > 5:
        c_st = df_struct["Close"].squeeze()
        r_st = rsi(c_st)
        rv_st = float(r_st.iloc[-1]) if not pd.isna(r_st.iloc[-1]) else 50.0
        rec = c_st.tail(5)
        rup = float(rec.iloc[-1]) > float(rec.iloc[0])
        t_struct = "Alcista" if (rup and rv_st > 50) else "Bajista" if (not rup and rv_st < 50) else "Lateral"
    else:
        t_struct = "Lateral"

    sesgo = "Continuación" if t_macro == t_struct and t_macro != "Lateral" else "Corrección" if t_macro != t_struct else "Rango"

    bOK = t_macro == "Alcista" and t_struct == "Alcista" and 45 < rv < 75
    sOK = t_macro == "Bajista" and t_struct == "Bajista" and 25 < rv < 55
    dec = "Comprar" if bOK else "Vender" if sOK else "No entrar"

    zref  = ma50
    zona  = f"${zref*0.999:,.2f} – ${zref*1.001:,.2f}"
    sl_v  = price - av * 2 if dec == "Comprar" else price + av * 2 if dec == "Vender" else None
    tp_v  = price + av * 4 if dec == "Comprar" else price - av * 4 if dec == "Vender" else None

    def vm(v, lbl):
        if not v: return "N/D"
        return f"{'sobre' if price > v else 'bajo'} {lbl} (${v:,.2f})"

    rlbl = "sobrecompra" if rv > 70 else "sobreventa" if rv < 30 else "neutral"
    rtxt = f"RSI {rv:.1f} — {rlbl}."
    mtxt = f"MACD {mv:.3f} histograma {'positivo' if hv > 0 else 'negativo'}."

    return dict(
        td1=t_macro, th1=t_struct, sesgo=sesgo, dec=dec,
        d1=f"Estructura principal en {tfs_keys[0]}. Precio {vm(ma50, 'MA50')} — {t_macro.lower()}. {rtxt}",
        h1=f"Confirmación en {tfs_keys[1]}. {vm(ma30, 'MA30')}. MACD {'positivo.' if mv > sv else 'sin momentum.'}",
        m5=f"Entrada en {tfs_keys[2]} alineada a favor del sesgo {sesgo.lower()}. Esperar confirmación de velas.",
        razon=f"Estructura en {tfs_keys[0]} {t_macro.lower()}: precio {vm(ma30, 'MA30')} y {vm(ma50, 'MA50')}. {rtxt} {mtxt}",
        rv=rv, rlbl=rlbl, mv=mv, sv=sv,
        ma30=ma30, ma50=ma50, ma100=ma100, ma200=ma200,
        zona=zona,
        sl=f"${sl_v:,.2f}" if sl_v else "N/D",
        tp=f"${tp_v:,.2f}" if tp_v else "N/D",
    )


# ── CONSTRUCCIÓN DEL GRÁFICO SEGURO DE PLOTLY ─────────────────────────────────
MAC = {30: "#60AAFF", 50: "#FFB830", 100: "#FF6B9D", 200: "#B09FFF"}

def make_chart(df, sym, tf_key, used_interval, show_ma, dark=True):
    idx = df.index
    c   = df["Close"].values
    
    bg   = "#0a0c10" if dark else "#ffffff"
    bg2  = "#111318" if dark else "#f8f9fa"
    grid = "rgba(255,255,255,0.06)" if dark else "rgba(0,0,0,0.06)"
    
    title_color = "#60AAFF" if dark else "#0052cc"
    tc   = "rgba(220,225,255,0.85)" if dark else "rgba(20,30,55,0.85)"
    
    up_c = "#22D991"; dn_c = "#FF5252"
    pcol = up_c if c[-1] >= c[0] else dn_c

    fig = make_subplots(rows=3, cols=1, row_heights=[0.58, 0.21, 0.21],
                        shared_xaxes=True, vertical_spacing=0.04)

    fig.add_trace(go.Scatter(x=idx, y=c, name="Precio",
        line=dict(color=pcol, width=2), hovertemplate="$%{y:,.2f}<extra>Precio</extra>"),
        row=1, col=1)

    c_series = df["Close"]
    for p, col in MAC.items():
        if show_ma.get(p) and len(c_series) >= p:
            fig.add_trace(go.Scatter(x=idx, y=ma(c_series, p).values, name=f"MA{p}",
                line=dict(color=col, width=1.5),
                hovertemplate=f"MA{p}: $%{{y:,.2f}}<extra></extra>"),
                row=1, col=1)

    rv_arr = rsi(c_series).values
    fig.add_trace(go.Scatter(x=idx, y=rv_arr, name="RSI",
        line=dict(color="#60AAFF", width=1.5),
        hovertemplate="RSI: %{y:.1f}<extra></extra>"), row=2, col=1)
    
    line_col_50 = "rgba(255,255,255,0.15)" if dark else "rgba(0,0,0,0.15)"
    for lvl, col in [(70, "rgba(255,82,82,0.4)"), (50, line_col_50), (30, "rgba(34,217,145,0.4)")]:
        fig.add_hline(y=lvl, line_dash="dot", line_color=col, row=2, col=1)

    _, _, hist_s = macd(c_series)
    hist_arr = hist_s.values
    bar_c = [up_c if v >= 0 else dn_c for v in hist_arr]
    fig.add_trace(go.Bar(x=idx, y=hist_arr, name="MACD Hist",
        marker_color=bar_c, opacity=0.75,
        hovertemplate="Hist: %{y:.4f}<extra></extra>"), row=3, col=1)

    fig.update_layout(
        template="plotly_dark" if dark else "plotly_white",
        title=dict(
            text=f"<b>{sym}</b> · {tf_key} ({used_interval})", 
            x=0.01,
            font=dict(color=title_color, size=16)
        ),
        paper_bgcolor=bg, plot_bgcolor=bg2,
        height=550, margin=dict(l=10, r=50, t=40, b=10),
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", font=dict(color=tc)),
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        xaxis2_rangeslider_visible=False,
        xaxis3_rangeslider_visible=False,
    )
    axis_style = dict(gridcolor=grid, zeroline=False, side="right", tickfont=dict(color=tc))
    fig.update_xaxes(gridcolor=grid, zeroline=False, tickfont=dict(color=tc))
    fig.update_yaxes(**axis_style)
    return fig


# ── MAIN RENDER ───────────────────────────────────────────────────────────────
SYM = st.session_state["sym"]

st.title("📊 JC TRADER ANALYSIS")
st.info(f"Matriz Activa: **Macro ({macro_tf})** ➔ **Estructura ({struct_tf})** ➔ **Gatillo ({trigger_tf})** &nbsp;|&nbsp; Activo: **{SYM}**")
st.divider()

# Renderizado de gráfico
st.markdown(f'<div class="slbl">📈 Gráfico Dinámico {SYM} — {tf_key}</div>', unsafe_allow_html=True)

with st.spinner(f"Descargando datos de {SYM}..."):
    df, used_int, used_per = get_df(SYM, tf_key)

if df is not None and not df.empty:
    chart_fig = make_chart(df, SYM, tf_key, used_int, show_ma, dark_mode)
    st.plotly_chart(chart_fig, use_container_width=True)

    buf = io.StringIO()
    buf.write(f"# {SYM} — {tf_key} ({used_int})\n")
    df.round(4).to_csv(buf)
    st.download_button("⬇ Descargar data en CSV", buf.getvalue().encode(), f"{SYM}_{tf_key}.csv", "text/csv")
else:
    st.warning(f"No se pudieron cargar datos para {SYM} en {tf_key}. Prueba cambiar la temporalidad o seleccionar otro activo.")

st.divider()

# ── REPORTE AUTOMATIZADO ──────────────────────────────────────────────────────
st.markdown(f'<div class="slbl">🤖 Reporte Multi-Temporal ({macro_tf} / {struct_tf} / {trigger_tf})</div>', unsafe_allow_html=True)

if st.button("🔍 Ejecutar Análisis Avanzado", type="primary"):
    with st.spinner("Analizando temporalidades..."):
        df_macro, _, _ = get_df(SYM, macro_tf)
        df_struct, _, _ = get_df(SYM, struct_tf)
        df_trigger, _, _ = get_df(SYM, trigger_tf)
        inf_a = get_info(SYM)
        
        r = analyze(df_macro, df_struct, df_trigger, inf_a, [macro_tf, struct_tf, trigger_tf])

    if not r:
        st.error("Datos históricos insuficientes para calcular las métricas en las temporalidades seleccionadas.")
    else:
        price  = inf_a["price"]
        chg    = inf_a["chg"]
        drop   = inf_a["drop"]
        high52 = inf_a["high52"]
        rng52  = inf_a["rng"]

        cc = "#22D991" if chg >= 0 else "#FF5252"
        st.markdown(f"""
        <div style="background:{CARD_BG};border:1px solid {BORDER_COLOR};border-radius:10px;
                    padding:12px 18px;margin-bottom:16px;display:flex;align-items:center;gap:16px">
          <span style="font-size:18px;font-weight:700;color:#60AAFF">{SYM}</span>
          <span style="font-size:20px;font-weight:700;color:#FFE066">${price:,.2f}</span>
          <span style="font-size:14px;font-weight:700;color:{cc}">{chg:+.2f}%</span>
        </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        for col, key, lbl, txt in [
            (c1, r["td1"], f"📅 {macro_tf} — Tendencia Principal", r["d1"]),
            (c2, r["th1"], f"🕐 {struct_tf} — Confirmación",        r["h1"]),
            (c3, r["sesgo"], f"⚡ {trigger_tf} — Entrada Técnica",      r["m5"]),
        ]:
            with col:
                st.markdown(f"""
                <div class="tf-card">
                  <div class="tf-lbl">{lbl}</div>
                  <div class="tf-trend">{key}</div>
                  <div class="tf-body">{txt}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Indicadores Clave
        st.markdown('<div class="slbl">Indicadores Técnicos clave</div>', unsafe_allow_html=True)
        i1, i2, i3, i4 = st.columns(4)
        rc = "#FF5252" if r["rv"] > 70 else "#22D991" if r["rv"] < 30 else "#FFE066"
        mc = "#22D991" if r["mv"] > 0 else "#FF5252"

        for col, lbl, val, sub, vc in [
            (i1, "RSI(14)",       f"{r['rv']:.1f}", r["rlbl"],     rc),
            (i2, "MACD",          f"{r['mv']:.3f}", f"Señal: {r['sv']:.3f}", mc),
            (i3, "Caída Máx 52W", f"{drop:.2f}%",   f"-${high52-price:,.2f}", "#FF5252"),
            (i4, "Posición Rango", f"{rng52:.1f}%",  "Zona Activa", "#FFE066"),
        ]:
            with col:
                st.markdown(f"""<div class="card">
                  <div class="card-lbl">{lbl}</div>
                  <div class="card-val" style="color:{vc}">{val}</div>
                  <div class="card-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Parámetros sugeridos
        st.markdown('<div class="slbl">Parámetros Operativos de Referencia</div>', unsafe_allow_html=True)
        n1, n2, n3 = st.columns(3)
        for col, lbl, val, vc in [
            (n1, "Gatillo de entrada óptimo", r["zona"], "#FFE066"),
            (n2, "Stop Loss Sugerido (ATR)", r["sl"],   "#FF5252"),
            (n3, "Take Profit Sugerido (1:2)", r["tp"],   "#22D991"),
        ]:
            with col:
                st.markdown(f"""<div class="card">
                  <div class="card-lbl" style="color:{vc}">{lbl}</div>
                  <div class="card-val" style="color:{vc};font-size:14px">{val}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        dc = {"Comprar": "dec-buy", "Vender": "dec-sell"}.get(r["dec"], "dec-wait")
        st.markdown(f"""
        <div class="{dc}">
          <div class="dec-title">Acción Recomendada: {r['dec']} &nbsp;·&nbsp; Sesgo: {r['sesgo']}</div>
          <div class="dec-body">{r['razon']}</div>
        </div>""", unsafe_allow_html=True)
