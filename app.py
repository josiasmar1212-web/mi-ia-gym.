# =================================================================
# PROJECT: MORPHAI NEURAL PERFORMANCE OS (v15.0 - FULL EDITION)
# AUTHOR: JOSIAS MARTINEZ
# COUNTRY: SPAIN / GLOBAL
# MODULES: STRENGTH | RUNNING | COMBAT | NEURAL IA
# =================================================================

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
import plotly.express as px

# --- 1. CONFIGURACIÓN DE INTERFAZ DE ÉLITE ---
st.set_page_config(
    page_title="MorphAI OS v15.0 | Josías Martínez",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ARQUITECTURA VISUAL NEÓN (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    :root {
        --neon-green: #00ff88;
        --neon-blue: #00d4ff;
        --neon-red: #ff4b4b;
        --dark-bg: #050505;
    }

    .stApp { background-color: var(--dark-bg); color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    .main-title { 
        font-family: 'Orbitron', sans-serif; 
        color: var(--neon-green); 
        text-align: center; 
        font-size: 3.8rem; 
        letter-spacing: 12px; 
        text-shadow: 0px 0px 25px rgba(0, 255, 136, 0.4);
        margin-top: -20px;
    }

    /* Tarjetas de Módulo */
    .module-card {
        background: rgba(15, 15, 15, 0.9);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .module-card:hover { border-color: var(--neon-green); box-shadow: 0 0 20px rgba(0, 255, 136, 0.1); }

    /* Temporizador Visual */
    .timer-display {
        font-family: 'Orbitron';
        font-size: 6.5rem;
        text-align: center;
        padding: 40px;
        border-radius: 30px;
        border: 4px solid var(--neon-red);
        color: var(--neon-red);
        background: rgba(255, 75, 75, 0.05);
        margin: 20px 0;
    }
    .work-active { border-color: var(--neon-green) !important; color: var(--neon-green) !important; box-shadow: 0 0 40px rgba(0, 255, 136, 0.3); }

    /* Estilo IA Card */
    .ia-output {
        background: linear-gradient(145deg, rgba(0,255,136,0.1), rgba(0,0,0,1));
        border-left: 5px solid var(--neon-green);
        padding: 25px;
        border-radius: 10px;
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. PERSISTENCIA DE DATOS ---
if 'master_db' not in st.session_state: st.session_state['master_db'] = []
if 'profile' not in st.session_state: st.session_state['profile'] = {"name": "JOSIAS MARTINEZ", "kg": 80}

# --- 4. BARRA LATERAL (CONTROL MAESTRO) ---
with st.sidebar:
    st.markdown(f'<h1 style="font-family:Orbitron; color:#00ff88;">MORPHAI OS</h1>', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/847/847969.png", width=80)
    st.session_state.profile["name"] = st.text_input("Atleta:", st.session_state.profile["name"])
    
    st.divider()
    system_mode = st.radio("SISTEMA:", ["🏋️ FUERZA PRO", "🏃 RUNNING TECH", "🥊 COMBATE & POWER", "🧠 IA NEURAL", "📊 ANALÍTICA"])
    
    st.divider()
    if st.button("🗑️ RESETEAR SISTEMA"):
        st.session_state['master_db'] = []
        st.rerun()
    
    if st.session_state['master_db']:
        csv = pd.DataFrame(st.session_state['master_db']).to_csv(index=False).encode('utf-8')
        st.download_button("📥 EXPORTAR DATA", data=csv, file_name="morphai_data.csv")

# --- 5. CABECERA ---
st.markdown('<h1 class="main-title">MORPHAI PERFORMANCE</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; opacity:0.6;">OPERADOR: {st.session_state.profile["name"]} | STATUS: CONECTADO</p>', unsafe_allow_html=True)

# --- 6. MÓDULOS DEL SISTEMA ---

# --- MÓDULO 1: FUERZA PRO ---
if system_mode == "🏋️ FUERZA PRO":
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 📥 Registro de Cargas")
        with st.form("f_fuerza", clear_on_submit=True):
            ejer = st.selectbox("Ejercicio", ["Press Banca", "Sentadilla", "Peso Muerto", "Press Militar", "Dominadas"])
            c_p, c_r = st.columns(2)
            peso = c_p.number_input("Peso (kg)", 0.0, 500.0, 80.0)
            reps = c_r.number_input("Reps", 1, 30, 8)
            rpe = st.slider("Intensidad (RPE)", 1, 10, 8)
            tempo = st.text_input("Tempo (Ej: 3-0-1-0)", "2-0-1-0")
            if st.form_submit_button("REGISTRAR SET"):
                st.session_state['master_db'].append({
                    "Fecha": datetime.now().strftime("%H:%M"), "Tipo": "Fuerza",
                    "Actividad": ejer, "Valor": peso * reps, "Meta": f"{peso}kg x {reps}", "Extra": f"RPE {rpe} | {tempo}"
                })
                st.success("Set Guardado.")

    with col2:
        st.markdown("### 🧮 Estimador 1RM")
        p_rm = st.number_input("Peso Levantado", 1.0, 500.0, 100.0)
        r_rm = st.number_input("Reps realizadas", 1, 12, 5)
        rm_calc = p_rm / (1.0278 - (0.0278 * r_rm))
        st.markdown(f'<h1 style="color:#00ff88; font-family:Orbitron; font-size:4rem; text-align:center;">{round(rm_calc, 1)} KG</h1>', unsafe_allow_html=True)
        st.caption("Cálculo basado en el algoritmo de Brzycki para alta precisión.")

# --- MÓDULO 2: RUNNING TECH ---
elif system_mode == "🏃 RUNNING TECH":
    col_r1, col_r2 = st.columns([1, 1])
    with col_r1:
        st.markdown("### 🏃 Telemetría de Carrera")
        with st.form("f_run", clear_on_submit=True):
            dist = st.number_input("Distancia (km)", 0.1, 100.0, 5.0)
            c_m, c_s = st.columns(2)
            mins = c_m.number_input("Minutos", 0, 500, 25)
            secs = c_s.number_input("Segundos", 0, 59, 0)
            hr = st.slider("Frecuencia Cardíaca Media (BPM)", 60, 220, 150)
            if st.form_submit_button("REGISTRAR CARRERA"):
                t_total = mins + (secs/60)
                pace = t_total / dist
                pace_str = f"{int(pace)}:{int((pace%1)*60):02d} min/km"
                st.session_state['master_db'].append({
                    "Fecha": datetime.now().strftime("%d/%m"), "Tipo": "Running",
                    "Actividad": "Carrera", "Valor": dist, "Meta": pace_str, "Extra": f"{hr} BPM"
                })
                st.success("Sesión de Resistencia Guardada.")
    with col_r2:
        st.info("💡 El entrenamiento en Zona 2 (BPM bajo) mejora la eficiencia mitocondrial.")
        st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHJidm91Z3o5YnZ5Z3Y5Z3Y5Z3Y5Z3Y5Z3Y5Z3Y5Z3Y5Z3YmZXA9YnYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxof4T9I4H6/giphy.gif")

# --- MÓDULO 3: COMBATE & POWER ---
elif system_mode == "🥊 COMBATE & POWER":
    st.markdown("### ⏱️ Temporizador Táctico de Rounds")
    c_t1, c_t2, c_t3 = st.columns(3)
    rds = c_t1.number_input("Rounds", 1, 15, 3)
    t_w = c_t2.number_input("Trabajo (min)", 1, 5, 3)
    t_r = c_t3.number_input("Descanso (seg)", 10, 60, 30)
    
    if st.button("🔔 INICIAR COMBATE"):
        t_ph = st.empty()
        for r in range(1, rds + 1):
            # Fase Trabajo
            for t in range(t_w * 60, 0, -1):
                t_ph.markdown(f'<div class="timer-display work-active">RD {r}<br>{t//60:02d}:{t%60:02d}</div>', unsafe_allow_html=True)
                time.sleep(1)
            # Fase Descanso
            if r < rds:
                for t in range(t_r, 0, -1):
                    t_ph.markdown(f'<div class="timer-display">DESCANSAR<br>00:{t:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
        t_ph.success("🥊 ¡FINAL DEL COMBATE!")
    
    st.divider()
    st.markdown("### ⚡ Registro de Explosividad")
    with st.form("f_power"):
        ej_ex = st.selectbox("Ejercicio de Potencia", ["Saltos al Cajón", "Landmine Punch", "Medball Slam", "Burpee Explosivo"])
        reps_ex = st.slider("Reps Explosivas", 1, 30, 5)
        if st.form_submit_button("REGISTRAR POTENCIA"):
            st.session_state['master_db'].append({
                "Fecha": datetime.now().strftime("%H:%M"), "Tipo": "Combate",
                "Actividad": ej_ex, "Valor": reps_ex, "Meta": f"{reps_ex} reps", "Extra": "Foco Explosivo"
            })

# --- MÓDULO 4: IA NEURAL ---
elif system_mode == "🧠 IA NEURAL":
    st.markdown("### 🧠 MorphAI Neural Planner")
    col_ia1, col_ia2 = st.columns([1, 2])
    with col_ia1:
        meta = st.selectbox("Objetivo IA", ["Fuerza Híbrida", "Potencia Explosiva", "Resistencia Táctica"])
        fatiga = st.select_slider("Nivel de Fatiga", options=["Baja", "Normal", "Alta"])
        if st.button("GENERAR PLAN NEURAL"):
            with st.spinner("Procesando algoritmos..."):
                time.sleep(2)
                st.session_state['ia_plan'] = f"Protocolo {meta.upper()} activado. Fatiga {fatiga}. Enfoque en volumen moderado y alta velocidad concéntrica."

    with col_ia2:
        if 'ia_plan' in st.session_state:
            st.markdown(f"""
            <div class="ia-output">
                <h4 style="color:#00ff88; font-family:Orbitron;">🧬 SESIÓN SUGERIDA</h4>
                <p><b>1. Calentamiento:</b> 10' Movilidad + 3x5 Saltos Verticales.</p>
                <p><b>2. Bloque Principal:</b> 4x6 Sentadilla (RPE 8) + 4x4 Landmine Punch.</p>
                <p><b>3. Finisher:</b> 3 Rounds de 500m Run + 20 Medball Slams.</p>
                <p style="font-size:0.9rem; opacity:0.7;"><i>*IA Note: Recuperación estimada 24h. Hidratación recomendada: 1L extra.</i></p>
            </div>
            """, unsafe_allow_html=True)

# --- MÓDULO 5: ANALÍTICA ---
elif system_mode == "📊 ANALÍTICA":
    if st.session_state['master_db']:
        df = pd.DataFrame(st.session_state['master_db'])
        st.markdown("### 📈 Visualización de Telemetría")
        
        fig_line = px.line(df, x="Fecha", y="Valor", color="Tipo", markers=True, template="plotly_dark", title="Evolución de Rendimiento")
        fig_line.update_traces(line_color='#00ff88')
        st.plotly_chart(fig_line, use_container_width=True)
        
        c_an1, c_an2 = st.columns(2)
        fig_pie = px.pie(df, names='Tipo', hole=0.5, title="Distribución de Atleta", color_discrete_sequence=['#00ff88', '#00d4ff', '#ff4b4b'])
        c_an1.plotly_chart(fig_pie)
        
        fig_bar = px.bar(df, x="Actividad", y="Valor", color="Tipo", title="Volumen por Actividad")
        c_an2.plotly_chart(fig_bar)
    else:
        st.warning("Sin datos para analizar.")

# --- PIE DE PÁGINA ---
st.markdown("---")
st.markdown("© 2026 **MorphAI Neural OS** | Propiedad de **Josías Martínez** | BETA INTERNACIONAL")
