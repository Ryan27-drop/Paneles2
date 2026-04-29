import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io

from modelo import resolver_todas, PANELES, HORAS_SOL, DIAS_MES

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Optimización Solar — LP Solver",
    page_icon="☀️",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #0f2027 0%, #1a4a2e 50%, #0d3b1e 100%);
    padding: 1.6rem 2rem; border-radius: 14px; margin-bottom: 1.5rem;
    border: 1px solid #2a7a4a; position: relative; overflow: hidden;
}
.main-header::before {
    content: "☀️"; position: absolute; right: 2rem; top: 50%;
    transform: translateY(-50%); font-size: 4rem; opacity: 0.15;
}
.main-header h1 { margin: 0; font-size: 1.75rem; color: #e8f5e9; font-weight: 700; }
.main-header p  { margin: 0.4rem 0 0; color: #81c784; font-size: 0.88rem; }

.kpi-box {
    background: linear-gradient(135deg, #0d2818 0%, #1a3a28 100%);
    border: 1px solid #2e7d52; border-left: 4px solid #4caf7d;
    padding: 1rem 1.2rem; border-radius: 10px; margin-bottom: 0.7rem;
}
.kpi-box .label { font-size: 0.72rem; color: #81c784; text-transform: uppercase;
                   letter-spacing: 0.08em; font-weight: 600; }
.kpi-box .val   { font-size: 2rem; font-weight: 700; color: #e8f5e9; font-family: 'DM Mono', monospace; }
.kpi-box .unit  { font-size: 0.78rem; color: #a5d6a7; margin-top: 0.1rem; }

.sec {
    color: #81c784; border-bottom: 2px solid #2e7d52;
    padding-bottom: 0.35rem; margin-top: 1.4rem; margin-bottom: 0.9rem;
    font-size: 1.05rem; font-weight: 600; letter-spacing: 0.02em;
}

.house-card {
    background: linear-gradient(135deg, #0d2818 0%, #152a1e 100%);
    border: 1px solid #2e7d52; border-radius: 12px;
    padding: 1.2rem 1.4rem; margin-bottom: 1rem;
}
.house-card h4 { color: #a5d6a7; margin: 0 0 0.8rem; font-size: 1rem; }

.badge-optimo    { background: #1b5e20; color: #a5d6a7; padding: 0.2rem 0.7rem;
                   border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
.badge-infact    { background: #7f1d1d; color: #fca5a5; padding: 0.2rem 0.7rem;
                   border-radius: 20px; font-size: 0.78rem; font-weight: 600; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1f12 0%, #0d2818 100%);
    border-right: 1px solid #2e7d52;
}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown p {
    color: #a5d6a7 !important;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #81c784 !important; }

.stTabs [data-baseweb="tab-list"] { gap: 0.4rem; }
.stTabs [data-baseweb="tab"] {
    background: #0d2818; color: #81c784; border-radius: 8px 8px 0 0;
    border: 1px solid #2e7d52; padding: 0.5rem 1.2rem;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1b5e20, #2e7d52) !important;
    color: #e8f5e9 !important;
}

.stDataFrame { border: 1px solid #2e7d52 !important; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>☀️ Optimización de Paneles Solares</h1>
    <p>Minimización de inversión · Programación Lineal Entera (ILP) · Curso II-1122 UCR Alajuela</p>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR — PARÁMETROS EDITABLES ───────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Parámetros del Modelo")

    with st.expander("☀️ Condiciones Solares", expanded=False):
        horas_sol = st.number_input(
            "Horas pico solares / día", value=float(HORAS_SOL),
            min_value=1.0, max_value=10.0, step=0.5
        )
        dias_mes = st.number_input(
            "Días por mes", value=int(DIAS_MES),
            min_value=28, max_value=31, step=1
        )

    st.markdown("---")
    st.markdown("### 🏠 Casa 1")
    c1_consumo = st.number_input("Consumo mensual (kWh)", value=355.0, min_value=10.0, step=10.0, key="c1_cons")
    c1_area    = st.number_input("Área de techo (m²)",   value=40.0,  min_value=5.0,  step=5.0,  key="c1_area")

    st.markdown("### 🏠 Casa 2")
    c2_consumo = st.number_input("Consumo mensual (kWh)", value=342.0, min_value=10.0, step=10.0, key="c2_cons")
    c2_area    = st.number_input("Área de techo (m²)",   value=40.0,  min_value=5.0,  step=5.0,  key="c2_area")

    st.markdown("### 🏠 Casa 3")
    c3_consumo = st.number_input("Consumo mensual (kWh)", value=302.0, min_value=10.0, step=10.0, key="c3_cons")
    c3_area    = st.number_input("Área de techo (m²)",   value=176.0, min_value=5.0,  step=5.0,  key="c3_area")

    st.markdown("---")
    resolver_btn = st.button("🚀 Resolver Optimización", type="primary", use_container_width=True)

# ─── RESOLVER ─────────────────────────────────────────────────────────────────
casas_input = [
    {'nombre': 'Casa 1', 'consumo_mensual_kwh': c1_consumo, 'area_techo_m2': c1_area},
    {'nombre': 'Casa 2', 'consumo_mensual_kwh': c2_consumo, 'area_techo_m2': c2_area},
    {'nombre': 'Casa 3', 'consumo_mensual_kwh': c3_consumo, 'area_techo_m2': c3_area},
]

if resolver_btn:
    resultados = resolver_todas(casas_input)
    st.session_state['resultados'] = resultados
    st.session_state['casas_input'] = casas_input

resultados  = st.session_state.get('resultados', None)
casas_input_saved = st.session_state.get('casas_input', casas_input)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📐 Modelo Matemático",
    "✅ Solución Óptima",
    "📊 Análisis Comparativo",
    "📥 Exportar",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MODELO MATEMÁTICO
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<h3 class="sec">Formulación General del Modelo ILP</h3>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Variables de Decisión** (enteras ≥ 0)")
        st.markdown("""
| Variable | Descripción |
|----------|-------------|
| $A_i$ | Cantidad de paneles tipo A en casa $i$ |
| $B_i$ | Cantidad de paneles tipo B en casa $i$ |
| $C_i$ | Cantidad de paneles tipo C en casa $i$ |
""")
        st.markdown("**Especificaciones de Paneles**")
        df_paneles = pd.DataFrame({
            'Tipo': list(PANELES.keys()),
            'Potencia (W)': [p['watts'] for p in PANELES.values()],
            'Área (m²)': [p['area'] for p in PANELES.values()],
            'Costo ($)': [p['costo'] for p in PANELES.values()],
        })
        st.dataframe(df_paneles, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**Función Objetivo (Minimizar inversión total)**")
        st.latex(r"""
\min \quad Z = \sum_{i=1}^{3} \left(190A_i + 205B_i + 255C_i\right)
""")
        st.markdown("**Restricciones por casa $i$**")
        st.latex(r"""
\begin{aligned}
(1)\;&(400A_i + 450B_i + 550C_i)\cdot\frac{h_s}{1000} \geq D_i \\[4pt]
(2)\;&(400A_i + 450B_i + 550C_i)\cdot\frac{h_s \cdot 30}{1000} \geq M_i \\[4pt]
(3)\;&1.9A_i + 2.1B_i + 2.5C_i \leq T_i \\[4pt]
(4)\;&400A_i + 450B_i + 550C_i \geq \frac{D_i}{h_s}\cdot 1000 \\[4pt]
&A_i, B_i, C_i \in \mathbb{Z}^+
\end{aligned}
""")
        st.markdown("""
> **Donde:**  
> $h_s$ = horas pico solares/día · $D_i$ = consumo diario (kWh) · $M_i$ = consumo mensual (kWh) · $T_i$ = área de techo (m²)
""")

    st.markdown('<h3 class="sec">Datos de Entrada Actuales</h3>', unsafe_allow_html=True)
    df_input = pd.DataFrame([{
        'Casa': c['nombre'],
        'Consumo mensual (kWh)': c['consumo_mensual_kwh'],
        'Consumo diario (kWh)': round(c['consumo_mensual_kwh'] / dias_mes, 3),
        'Potencia mín. (kW)': round(c['consumo_mensual_kwh'] / dias_mes / horas_sol, 3),
        'Área techo (m²)': c['area_techo_m2'],
    } for c in casas_input])
    st.dataframe(df_input, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SOLUCIÓN ÓPTIMA
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    if resultados is None:
        st.info("👈 Ajusta los parámetros en el panel lateral y presiona **Resolver Optimización**.")
    else:
        costo_global = resultados['__global__']['costo_total']

        # KPIs globales
        st.markdown('<h3 class="sec">Resumen Global</h3>', unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        casas_names = ['Casa 1', 'Casa 2', 'Casa 3']
        total_paneles = sum(
            sum(resultados[c]['paneles'].values())
            for c in casas_names if c in resultados
        )
        total_kwh_mes = sum(
            resultados[c]['produccion_mensual_kwh']
            for c in casas_names if c in resultados
        )
        with k1:
            st.markdown(f'''
<div class="kpi-box">
  <div class="label">Inversión Total Óptima</div>
  <div class="val">${costo_global:,.0f}</div>
  <div class="unit">dólares</div>
</div>''', unsafe_allow_html=True)
        with k2:
            st.markdown(f'''
<div class="kpi-box">
  <div class="label">Paneles Totales</div>
  <div class="val">{total_paneles}</div>
  <div class="unit">unidades</div>
</div>''', unsafe_allow_html=True)
        with k3:
            st.markdown(f'''
<div class="kpi-box">
  <div class="label">Producción Total / Mes</div>
  <div class="val">{total_kwh_mes:,.1f}</div>
  <div class="unit">kWh/mes</div>
</div>''', unsafe_allow_html=True)

        # Resultados por casa
        st.markdown('<h3 class="sec">Detalle por Casa</h3>', unsafe_allow_html=True)
        for i, casa in enumerate(casas_input_saved):
            nombre = casa['nombre']
            res = resultados.get(nombre, {})
            estado = res.get('estado', 'Error')
            badge = f'<span class="badge-optimo">✅ {estado}</span>' if estado == 'Óptimo' \
                    else f'<span class="badge-infact">❌ {estado}</span>'

            with st.expander(f"🏠 {nombre} — ${res.get('costo_total', 0):,.0f}  {badge}", expanded=True):
                if estado != 'Óptimo':
                    st.error(f"No se encontró solución óptima: {estado}. Revisa los parámetros (área del techo podría ser insuficiente).")
                    continue

                ca, cb, cc = st.columns(3)
                with ca:
                    st.markdown(f'''
<div class="kpi-box">
  <div class="label">Costo de inversión</div>
  <div class="val">${res["costo_total"]:,.0f}</div>
  <div class="unit">dólares</div>
</div>''', unsafe_allow_html=True)
                with cb:
                    st.markdown(f'''
<div class="kpi-box">
  <div class="label">Producción mensual</div>
  <div class="val">{res["produccion_mensual_kwh"]:,.1f}</div>
  <div class="unit">kWh/mes (necesario: {casa["consumo_mensual_kwh"]} kWh)</div>
</div>''', unsafe_allow_html=True)
                with cc:
                    st.markdown(f'''
<div class="kpi-box">
  <div class="label">Área utilizada</div>
  <div class="val">{res["area_usada_m2"]:.1f}</div>
  <div class="unit">m² de {casa["area_techo_m2"]} m² disponibles</div>
</div>''', unsafe_allow_html=True)

                if res['detalle']:
                    df_det = pd.DataFrame(res['detalle'])
                    st.dataframe(df_det, use_container_width=True, hide_index=True)
                else:
                    # mostrar todos los tipos aunque sean 0
                    st.info("Sin paneles asignados.")

        # Tabla resumen comparativa
        st.markdown('<h3 class="sec">Tabla Comparativa</h3>', unsafe_allow_html=True)
        rows = []
        for casa in casas_input_saved:
            nombre = casa['nombre']
            res = resultados.get(nombre, {})
            if res.get('estado') == 'Óptimo':
                cant = res['paneles']
                rows.append({
                    'Casa': nombre,
                    'Panel A': cant.get('A', 0),
                    'Panel B': cant.get('B', 0),
                    'Panel C': cant.get('C', 0),
                    'Total Paneles': sum(cant.values()),
                    'Costo ($)': res['costo_total'],
                    'Prod. Diaria (kWh)': res['produccion_diaria_kwh'],
                    'Prod. Mensual (kWh)': res['produccion_mensual_kwh'],
                    'Área Usada (m²)': res['area_usada_m2'],
                })
        if rows:
            df_comp = pd.DataFrame(rows)
            st.dataframe(df_comp, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANÁLISIS COMPARATIVO
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    if resultados is None:
        st.info("👈 Resuelve el modelo primero.")
    else:
        VERDE   = "#4caf7d"
        VERDE2  = "#2e7d52"
        VERDE3  = "#81c784"
        DARK    = "#0d2818"
        BLANCO  = "#e8f5e9"
        AMARILLO = "#ffd54f"
        AZUL    = "#4fc3f7"

        casas_validas = [
            c for c in casas_input_saved
            if resultados.get(c['nombre'], {}).get('estado') == 'Óptimo'
        ]
        nombres   = [c['nombre'] for c in casas_validas]
        costos    = [resultados[c['nombre']]['costo_total'] for c in casas_validas]
        prod_mes  = [resultados[c['nombre']]['produccion_mensual_kwh'] for c in casas_validas]
        cons_mes  = [c['consumo_mensual_kwh'] for c in casas_validas]
        areas_us  = [resultados[c['nombre']]['area_usada_m2'] for c in casas_validas]
        areas_tot = [c['area_techo_m2'] for c in casas_validas]
        n_paneles_tipo = {
            t: [resultados[c['nombre']]['paneles'].get(t, 0) for c in casas_validas]
            for t in PANELES
        }

        fig, axes = plt.subplots(2, 2, figsize=(13, 9))
        fig.patch.set_facecolor(DARK)
        for ax in axes.flat:
            ax.set_facecolor('#152a1e')
            ax.tick_params(colors=BLANCO)
            for spine in ax.spines.values():
                spine.set_edgecolor('#2e7d52')

        # ── Gráfica 1: Costo total por casa ──────────────────────────────────
        ax = axes[0, 0]
        colors_bars = [VERDE, VERDE2, AMARILLO][:len(nombres)]
        bars = ax.bar(nombres, costos, color=colors_bars,
                      width=0.5, edgecolor='#0d2818', linewidth=1.5)
        for b in bars:
            ax.text(b.get_x() + b.get_width()/2, b.get_height() + 10,
                    f"${b.get_height():,.0f}", ha='center', color=BLANCO, fontsize=10, fontweight='bold')
        ax.set_title("Inversión por Casa ($)", color=BLANCO, fontweight='bold', pad=10)
        ax.set_ylabel("Dólares ($)", color=VERDE3)
        ax.set_ylim(0, max(costos) * 1.25 if costos else 1)

        # ── Gráfica 2: Producción vs Consumo ─────────────────────────────────
        ax = axes[0, 1]
        x = range(len(nombres))
        width = 0.35
        b1 = ax.bar([xi - width/2 for xi in x], cons_mes, width, label='Consumo', color=AZUL, alpha=0.85)
        b2 = ax.bar([xi + width/2 for xi in x], prod_mes, width, label='Producción', color=VERDE, alpha=0.85)
        ax.set_xticks(list(x)); ax.set_xticklabels(nombres, color=BLANCO)
        ax.set_title("Producción vs Consumo Mensual (kWh)", color=BLANCO, fontweight='bold', pad=10)
        ax.set_ylabel("kWh/mes", color=VERDE3)
        ax.legend(facecolor='#0d2818', labelcolor=BLANCO, edgecolor='#2e7d52')
        for b in list(b1) + list(b2):
            ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1,
                    f"{b.get_height():.0f}", ha='center', color=BLANCO, fontsize=8)

        # ── Gráfica 3: Área usada vs disponible ──────────────────────────────
        ax = axes[1, 0]
        b1 = ax.bar([xi - width/2 for xi in x], areas_tot, width, label='Área techo', color='#455a64', alpha=0.9)
        b2 = ax.bar([xi + width/2 for xi in x], areas_us, width, label='Área usada', color=AMARILLO, alpha=0.9)
        ax.set_xticks(list(x)); ax.set_xticklabels(nombres, color=BLANCO)
        ax.set_title("Área Usada vs Disponible (m²)", color=BLANCO, fontweight='bold', pad=10)
        ax.set_ylabel("m²", color=VERDE3)
        ax.legend(facecolor='#0d2818', labelcolor=BLANCO, edgecolor='#2e7d52')

        # ── Gráfica 4: Composición de paneles (stacked bar) ──────────────────
        ax = axes[1, 1]
        colores_paneles = {'A': VERDE, 'B': AMARILLO, 'C': AZUL}
        bottom = [0] * len(nombres)
        for tipo, vals in n_paneles_tipo.items():
            if any(v > 0 for v in vals):
                bars_s = ax.bar(nombres, vals, bottom=bottom,
                                label=f'Panel {tipo}', color=colores_paneles[tipo],
                                alpha=0.9, edgecolor=DARK, linewidth=0.8)
                for b, v, bot in zip(bars_s, vals, bottom):
                    if v > 0:
                        ax.text(b.get_x() + b.get_width()/2, bot + v/2,
                                str(v), ha='center', color=DARK, fontsize=11, fontweight='bold')
                bottom = [b + v for b, v in zip(bottom, vals)]
        ax.set_title("Composición de Paneles por Casa", color=BLANCO, fontweight='bold', pad=10)
        ax.set_ylabel("Cantidad de paneles", color=VERDE3)
        ax.legend(facecolor='#0d2818', labelcolor=BLANCO, edgecolor='#2e7d52')

        plt.tight_layout(pad=2.5)
        st.pyplot(fig)
        plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — EXPORTAR
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    if resultados is None:
        st.info("👈 Resuelve el modelo primero para exportar resultados.")
    else:
        st.markdown('<h3 class="sec">Exportar Resultados a Excel</h3>', unsafe_allow_html=True)

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            # Hoja resumen global
            resumen_rows = []
            for casa in casas_input_saved:
                nombre = casa['nombre']
                res = resultados.get(nombre, {})
                if res.get('estado') == 'Óptimo':
                    cant = res['paneles']
                    resumen_rows.append({
                        'Casa': nombre,
                        'Consumo mensual (kWh)': casa['consumo_mensual_kwh'],
                        'Área techo (m²)': casa['area_techo_m2'],
                        'Panel A': cant.get('A', 0),
                        'Panel B': cant.get('B', 0),
                        'Panel C': cant.get('C', 0),
                        'Total paneles': sum(cant.values()),
                        'Costo total ($)': res['costo_total'],
                        'Prod. diaria (kWh)': res['produccion_diaria_kwh'],
                        'Prod. mensual (kWh)': res['produccion_mensual_kwh'],
                        'Área usada (m²)': res['area_usada_m2'],
                    })
            if resumen_rows:
                pd.DataFrame(resumen_rows).to_excel(writer, sheet_name='Resumen', index=False)

            # Hoja de detalle por casa
            for casa in casas_input_saved:
                nombre = casa['nombre']
                res = resultados.get(nombre, {})
                if res.get('estado') == 'Óptimo' and res['detalle']:
                    pd.DataFrame(res['detalle']).to_excel(
                        writer, sheet_name=nombre.replace(' ', '_'), index=False
                    )

            # Hoja de parámetros de paneles
            pd.DataFrame([
                {'Tipo': t, 'Watts': d['watts'], 'Área (m²)': d['area'], 'Costo ($)': d['costo']}
                for t, d in PANELES.items()
            ]).to_excel(writer, sheet_name='Paneles', index=False)

        buf.seek(0)
        st.download_button(
            label="📥 Descargar Excel",
            data=buf,
            file_name="optimizacion_paneles_solares.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        if resumen_rows:
            st.markdown("**Vista previa — Resumen Global:**")
            st.dataframe(pd.DataFrame(resumen_rows), use_container_width=True, hide_index=True)
