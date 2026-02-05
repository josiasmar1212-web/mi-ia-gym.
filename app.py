import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go

# =================================================================
# SYSTEM ARCHITECTURE: MORPHAI PERFORMANCE OS v12.5
# DEVELOPER: JOSIAS MARTINEZ
# MODULE: HYBRID ATHLETE INTEGRATION (STRENGTH / ENDURANCE / COMBAT)
# =================================================================

st.set_page_config(
    page_title="MorphAI Beta | Enterprise Athlete System",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED STYLING (NEON UI DESIGN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@300;400;600&display=swap');
    
    :root {
        --neon-green: #00ff88;
        --dark-bg: #050505;
        --card-bg: rgba(255, 255, 255, 0.05);
    }

    .stApp { background-color: var(--dark-bg); color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    .header-container {
        padding: 2rem;
        background: linear-gradient(180deg, rgba(0,255,136,0.1) 0%, rgba(0,0,0,0) 100%);
        border-radius: 0 0 50px 50px;
        margin-bottom: 2rem;
    }

    .main-title { 
        font-family: 'Orbitron', sans-serif; 
        color: var(--neon-green); 
        text-align: center; 
        font-size: 3.5rem; 
        letter-spacing: 15px; 
        text-shadow: 0px 0px 25px rgba(0, 255, 136, 0.5);
    }

    /* Timer Style */
    .timer-card {
        background: rgba(20, 20, 20, 0.9);
        border: 2px solid #ff4b4b;
        border-radius: 30px;
        padding: 40px;
        text-align: center;
        box-shadow: 0 0 30px rgba(255, 75, 75, 0.2);
    }
    .timer-text { font-family: 'Orbitron'; font-size: 6rem; color: #ff4b4b; }
    .work-active { border-color: var(--neon-green) !important; color: var(--neon-green) !important; }

    /* Metrics Display */
    .metric-box {
        background: var(--card-bg);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        transition: 0.3s;
    }
    .metric-box:hover { border-color: var(--neon-green); background: rgba(0,255,136,0.05); }

    .rm-giant { font-family: 'Orbitron'; font-size: 5.5rem; color: var(--neon-green); margin: 0; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE & DATABASE INITIALIZATION ---
if 'db' not in st.session_state:
    st.session_state['db'] = []
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = {"name": "JOSIAS MARTINEZ", "weight": 80.0, "height": 180, "age": 25}

# --- SIDEBAR: ATLETA & CONFIG ---
with st.sidebar:
    st.markdown(f'<h1 style="color:#00ff88; font-family:Orbitron;">MORPHAI V12.5</h1>', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/847/847969.png", width=100)
    
    st.subheader("👤 Perfil del Atleta")
    st.session_state.user_profile["name"] = st.text_input("Nombre", st.session_state.user_profile["name"])
    st.session_state.user_profile["weight"] = st.number_input("Peso (kg)", 40.0, 200.0, st.session_state.user_profile["weight"])
    st.session_state.user_profile["height"] = st.number_input("Altura (cm)", 100, 250, st.session_state.user_profile["height"])
    
    st.divider()
    modo = st.selectbox("🎯 Módulo de Sistema", ["POWER & STRENGTH", "ENDURANCE TECH", "COMBAT & EXPLOSIVITY"])
    
    if st.session_state['db']:
        st.divider()
        df_export = pd.DataFrame(st.session_state['db'])
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button("📂 Exportar Data RAW", data=csv, file_name=f"MorphAI_{datetime.now().strftime('%Y%m%d')}.csv", mime='text/csv')

# --- HEADER SECTION ---
st.markdown('<div class="header-container">', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">MORPHAI SYSTEM</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; opacity:0.6;">OPERADOR: {st.session_state.user_profile["name"]} | STATUS: BETA ACTIVA</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🚀 WORKOUT", "📈 ANALYTICS", "⚡ 1RM ENGINE", "🧬 BIO-DATA"])

# --- TAB 1: WORKOUT ENGINE ---
with tab1:
    if modo == "POWER & STRENGTH":
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("### 🛠️ Log de Cargas")
            with st.form("gym_form", clear_on_submit=True):
                ejer = st.selectbox("Ejercicio Ejercicio", ["Press Banca Barra", "Sentadilla High Bar", "Peso Muerto", "Press Militar", "Dominadas Lastradas", "Remo con Barra"])
                peso = st.number_input("Peso (kg)", 0.0, 500.0, 100.0)
                reps = st.number_input("Reps", 1, 30, 5)
                rpe = st.select_slider("Esfuerzo (RPE)", options=[6, 7, 8, 8.5, 9, 9.5, 10])
                tempo = st.text_input("Tempo (Ej: 3-1-1-0)", "2-0-1-0")
                if st.form_submit_button("REGISTRAR SET"):
                    st.session_state['db'].append({
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Category": "Fuerza", "Exercise": ejer, "Metric": peso, 
                        "Reps": reps, "Volume": peso * reps, "Intensidad": rpe, "Extra": tempo
                    })
        with c2:
            st.markdown("### 📋 Sesión Actual")
            if st.session_state['db']:
                temp_df = pd.DataFrame(st.session_state['db']).tail(5)
                st.table(temp_df[["Exercise", "Metric", "Reps", "Intensidad"]])

    elif modo == "ENDURANCE TECH":
        c1, c2 = st.columns(2)
        with c1:
            with st.form("run_form"):
                dist = st.number_input("Distancia (km)", 0.1, 100.0, 5.0)
                t_m = st.number_input("Minutos", 0, 500, 25)
                t_s = st.number_input("Segundos", 0, 59, 0)
                hr = st.slider("FC Media (BPM)", 100, 210, 150)
                if st.form_submit_button("REGISTRAR CARRERA"):
                    total_time = t_m + (t_s/60)
                    pace = total_time / dist
                    st.session_state['db'].append({
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Category": "Resistencia", "Exercise": "Running", "Metric": dist,
                        "Reps": 1, "Volume": dist, "Intensidad": hr, "Extra": f"Pace: {int(pace)}:{int((pace%1)*60):02d}"
                    })
        with c2:
            st.info("💡 Tip: Mantén tu FC en Zona 2 para optimizar la oxidación de grasas.")

    elif modo == "COMBAT & EXPLOSIVITY":
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            st.markdown("### ⏱️ Combat Timer")
            rds = st.number_input("Rounds", 1, 12, 3)
            w_t = st.number_input("Trabajo (min)", 1, 5, 3)
            r_t = st.number_input("Descanso (seg)", 10, 60, 30)
            if st.button("🔔 INICIAR COMBATE"):
                t_placeholder = st.empty()
                for r in range(1, rds + 1):
                    # Trabajo
                    for t in range(w_t * 60, 0, -1):
                        t_placeholder.markdown(f'<div class="timer-card work-active"><p>ROUND {r}</p><p class="timer-text" style="color:#00ff88">{t//60:02d}:{t%60:02d}</p></div>', unsafe_allow_html=True)
                        time.sleep(1)
                    # Descanso
                    if r < rds:
                        for t in range(r_t, 0, -1):
                            t_placeholder.markdown(f'<div class="timer-card"><p>BREAK</p><p class="timer-text">{t//60:02d}:{t%60:02d}</p></div>', unsafe_allow_html=True)
                            time.sleep(1)
                t_placeholder.success("✅ SESIÓN FINALIZADA")

# --- TAB 2: ANALYTICS (DEEP DATA) ---
with tab2:
    if st.session_state['db']:
        df = pd.DataFrame(st.session_state['db'])
        st.markdown("### 📊 Business Intelligence Performance")
        
        # Gráfico 1: Volumen Total Acumulado
        fig1 = px.area(df, x="Timestamp", y="Volume", color="Category", 
                      title="Volumen de Trabajo Acumulado (Métrica de Fatiga)",
                      template="plotly_dark", color_discrete_sequence=['#00ff88', '#00aaff'])
        st.plotly_chart(fig1, use_container_width=True)
        
        c_an1, c_an2 = st.columns(2)
        # Gráfico 2: Composición del Atleta
        fig2 = px.pie(df, names='Category', hole=0.6, title="Distribución de Cargas",
                     color_discrete_sequence=['#00ff88', '#00aaff', '#ff4b4b'])
        c_an1.plotly_chart(fig2)
        
        # Gráfico 3: Intensidad Relativa
        fig3 = px.scatter(df, x="Timestamp", y="Intensidad", size="Volume", color="Category",
                         title="Relación Intensidad vs Volumen")
        c_an2.plotly_chart(fig3)
    else:
        st.warning("⚠️ No hay datos suficientes para generar telemetría avanzada.")

# --- TAB 3: 1RM ENGINE ---
with tab3:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.markdown("### 🧮 Algoritmo de Estimación Brzycki")
    c_rm1, c_rm2 = st.columns(2)
    p_in = c_rm1.number_input("Carga Real (kg)", 1.0, 500.0, 100.0, key="rm_p")
    r_in = c_rm2.number_input("Reps al fallo técnico", 1, 12, 5, key="rm_r")
    
    # Formula Brzycki
    rm_final = p_in / (1.0278 - (0.0278 * r_in))
    st.markdown(f'<p class="rm-giant">{round(rm_final, 1)} KG</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Tabla de Porcentajes de Entrenamiento
    st.markdown("### 📈 Programación de Intensidades Sugerida")
    pcts = [1.0, 0.95, 0.90, 0.85, 0.80, 0.75, 0.70]
    labels = ["Max (100%)", "Fuerza (95%)", "Fuerza (90%)", "Power (85%)", "Hipertrofia (80%)", "Hipertrofia (75%)", "Velocidad (70%)"]
    st.columns(len(pcts))
    cols = st.columns(len(pcts))
    for i, p in enumerate(pcts):
        cols[i].metric(labels[i], f"{round(rm_final*p, 1)}kg")

# --- TAB 4: BIO-DATA (EL VALOR AÑADIDO) ---
with tab4:
    st.markdown("### 🧬 Análisis Biométrico")
    w = st.session_state.user_profile["weight"]
    h = st.session_state.user_profile["height"] / 100
    imc = w / (h**2)
    
    col_b1, col_b2, col_b3 = st.columns(3)
    col_b1.metric("Índice de Masa Corporal", round(imc, 2))
    # TMB Harris-Benedict simplificada
    tmb = (10 * w) + (6.25 * h * 100) - (5 * 25) + 5 
    col_b2.metric("Gasto Basal Est. (TMB)", f"{int(tmb)} kcal")
    col_b3.metric("Status de Hidratación", "Óptimo", delta="0.5L")

# --- FOOTER ---
st.markdown("---")
st.markdown(f"**MORPHAI ENTERPRISE OS v12.5** | © 2026 Developed by **Josías Martínez** | [Streamlit Cloud Deployment]")
