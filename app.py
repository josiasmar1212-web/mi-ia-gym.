# =================================================================
# PROJECT: MORPHAI NEURAL PERFORMANCE OS (v16.0 - COLOSSUS EDITION)
# AUTHOR: JOSIAS MARTINEZ
# ARCHITECTURE: HYBRID ATHLETE INTEGRATION (STRENGTH / RUN / COMBAT)
# =================================================================

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN DE NÚCLEO ---
st.set_page_config(
    page_title="MorphAI OS v16.0 | Professional Edition",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. MOTOR ESTÉTICO (CSS AVANZADO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    :root {
        --neon-green: #00ff88;
        --neon-blue: #00d4ff;
        --neon-red: #ff4b4b;
        --bg-black: #050505;
    }

    .stApp { background-color: var(--bg-black); color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    .main-title { 
        font-family: 'Orbitron', sans-serif; color: var(--neon-green); text-align: center; 
        font-size: 3.5rem; letter-spacing: 12px; text-shadow: 0px 0px 30px rgba(0, 255, 136, 0.4);
    }

    /* Contenedores de Módulo */
    .module-container {
        background: rgba(20, 20, 20, 0.8);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
    }

    /* Temporizador Táctico */
    .timer-display {
        font-family: 'Orbitron'; font-size: 6.5rem; text-align: center; padding: 45px;
        border-radius: 35px; border: 5px solid var(--neon-red); color: var(--neon-red);
        background: rgba(255, 75, 75, 0.05); text-shadow: 0 0 20px rgba(255, 75, 75, 0.3);
    }
    .work-active { 
        border-color: var(--neon-green) !important; color: var(--neon-green) !important; 
        box-shadow: 0 0 50px rgba(0, 255, 136, 0.3); text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
    }

    /* IA Card Style */
    .ia-card {
        background: linear-gradient(135deg, rgba(0,255,136,0.15) 0%, rgba(0,0,0,1) 100%);
        border: 1px solid var(--neon-green); border-radius: 20px; padding: 30px;
    }
    .ia-tag { color: var(--neon-green); font-family: 'Orbitron'; font-size: 1.3rem; border-bottom: 1px solid rgba(0,255,136,0.3); margin-bottom: 15px; padding-bottom: 10px; }
    
    /* Metrics Area */
    .rm-giant { font-family: 'Orbitron'; font-size: 5rem; color: var(--neon-green); text-align: center; margin: 0; }
    </style>
""", unsafe_allow_html=True)

# --- 3. GESTIÓN DE BASES DE DATOS ---
if 'db' not in st.session_state: st.session_state['db'] = []
if 'user' not in st.session_state: st.session_state['user'] = {"name": "JOSIAS MARTINEZ", "weight": 80, "height": 180}

DB_EXERCISES = {
    "Fuerza": ["Press Banca", "Sentadilla Barra", "Peso Muerto Sumó", "Press Militar", "Dominadas Pro", "Remo Pendlay"],
    "Explosividad": ["Saltos al Cajón", "Landmine Punch", "Medball Slam", "Burpee Pliométrico", "Snatch con Mancuerna", "Sprints Potencia"],
    "Running": ["Carrera Continua", "Series VO2 Max", "Fartlek Neural", "Umbral Lactato"]
}

# --- 4. BARRA LATERAL (CENTRO DE MANDO) ---
with st.sidebar:
    st.markdown('<h1 style="font-family:Orbitron; color:#00ff88; letter-spacing:3px;">MORPHAI OS</h1>', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/847/847969.png", width=90)
    st.session_state.user["name"] = st.text_input("OPERADOR:", st.session_state.user["name"]).upper()
    
    st.divider()
    system_mode = st.radio("SISTEMA:", [
        "🏋️ FUERZA & LOGÍSTICA", 
        "🏃 RUNNING TELEMETRY", 
        "🥊 COMBATE & EXPLOSIVIDAD", 
        "🧠 NEURAL IA PLANNER", 
        "📊 ANALÍTICA GLOBAL"
    ])
    
    st.divider()
    if st.button("🚨 NUCLEAR RESET"):
        st.session_state['db'] = []
        st.rerun()

# --- 5. INTERFAZ PRINCIPAL ---
st.markdown('<h1 class="main-title">MORPHAI NEURAL ENGINE</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; opacity:0.6; letter-spacing:4px;">ACTIVE OPERATOR: {st.session_state.user["name"]} | BETA v16.0</p>', unsafe_allow_html=True)

# --- MÓDULO: FUERZA ---
if system_mode == "🏋️ FUERZA & LOGÍSTICA":
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("### 📥 Registro de Carga")
        with st.form("f_gym", clear_on_submit=True):
            ejer = st.selectbox("Ejercicio", DB_EXERCISES["Fuerza"])
            c_p, c_r = st.columns(2)
            peso = c_p.number_input("Carga (kg)", 0.0, 500.0, 100.0)
            reps = c_r.number_input("Reps", 1, 50, 5)
            rpe = st.slider("Intensidad (RPE)", 1, 10, 8)
            if st.form_submit_button("REGISTRAR SET"):
                st.session_state['db'].append({
                    "Fecha": datetime.now().strftime("%H:%M"), "Tipo": "Fuerza",
                    "Actividad": ejer, "Valor": peso * reps, "Meta": f"{peso}kg x {reps}", "Extra": f"RPE {rpe}"
                })
    with c2:
        st.markdown("### 🧮 Estimación 1RM (Algoritmo Brzycki)")
        p_rm = st.number_input("Peso para cálculo", 1.0, 500.0, 100.0)
        r_rm = st.number_input("Reps para cálculo", 1, 12, 5)
        res_rm = p_rm / (1.0278 - (0.0278 * r_rm))
        st.markdown(f'<p class="rm-giant">{round(res_rm, 1)} KG</p>', unsafe_allow_html=True)
        st.divider()
        st.write("**Zonas de Poder:**")
        st.write(f"90% (Fuerza): {round(res_rm*0.9, 1)}kg | 80% (Masa): {round(res_rm*0.8, 1)}kg")

# --- MÓDULO: RUNNING ---
elif system_mode == "🏃 RUNNING TELEMETRY":
    c_run1, c_run2 = st.columns(2)
    with c_run1:
        st.markdown("### 🏃 Registro de Resistencia")
        with st.form("f_run", clear_on_submit=True):
            tipo_r = st.selectbox("Tipo de Estímulo", DB_EXERCISES["Running"])
            dist = st.number_input("Distancia (km)", 0.1, 100.0, 5.0)
            m_r = st.number_input("Minutos", 1, 500, 25)
            hr = st.slider("BPM Medio", 60, 220, 145)
            if st.form_submit_button("GUARDAR RUN"):
                pace = m_r / dist
                pace_str = f"{int(pace)}:{int((pace%1)*60):02d} min/km"
                st.session_state['db'].append({
                    "Fecha": datetime.now().strftime("%d/%m"), "Tipo": "Running",
                    "Actividad": tipo_r, "Valor": dist, "Meta": pace_str, "Extra": f"{hr} BPM"
                })
    with c_run2:
        st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHJidm91Z3o5YnZ5Z3Y5Z3Y5Z3Y5Z3Y5Z3Y5Z3Y5Z3Y5Z3YmZXA9YnYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxof4T9I4H6/giphy.gif")
        st.info("Pace estimado calculado automáticamente.")

# --- MÓDULO: COMBATE & EXPLOSIVIDAD ---
elif system_mode == "🥊 COMBATE & EXPLOSIVIDAD":
    st.subheader("⏱️ Temporizador Táctico")
    t_c1, t_c2, t_c3 = st.columns(3)
    rds = t_c1.number_input("Rounds", 1, 15, 3)
    w_t = t_c2.number_input("Trabajo (min)", 1, 5, 3)
    r_t = t_c3.number_input("Descanso (seg)", 10, 60, 30)
    
    if st.button("🔔 INICIAR ROUNDS"):
        ph = st.empty()
        for r in range(1, rds + 1):
            for t in range(w_t * 60, 0, -1):
                ph.markdown(f'<div class="timer-display work-active">ROUND {r}<br>{t//60:02d}:{t%60:02d}</div>', unsafe_allow_html=True)
                time.sleep(1)
            if r < rds:
                for t in range(r_t, 0, -1):
                    ph.markdown(f'<div class="timer-display">REST<br>00:{t:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
        ph.success("COMBATE FINALIZADO")

    st.divider()
    st.subheader("⚡ Biblioteca de Explosividad")
    with st.form("f_ex", clear_on_submit=True):
        ej_ex = st.selectbox("Ejercicio de Potencia", DB_EXERCISES["Explosividad"])
        reps_ex = st.slider("Reps Explosivas", 1, 30, 6)
        lastre = st.number_input("Lastre Extra (kg)", 0, 100, 0)
        if st.form_submit_button("REGISTRAR POTENCIA"):
            st.session_state['db'].append({
                "Fecha": datetime.now().strftime("%H:%M"), "Tipo": "Combate",
                "Actividad": ej_ex, "Valor": reps_ex, "Meta": f"{reps_ex} reps", "Extra": f"{lastre}kg Lastre"
            })

# --- MÓDULO: IA NEURAL (DISEÑO GENERAL) ---
elif system_mode == "🧠 NEURAL IA PLANNER":
    st.markdown("### 🧠 Neural IA Architecture")
    col_ia1, col_ia2 = st.columns([1, 2])
    with col_ia1:
        st.write("Configuración de Algoritmo:")
        obj = st.selectbox("Meta del Ciclo", ["Híbrido Total", "Powerlifting", "Fuerza de Combate", "Resistencia Elite"])
        fat = st.select_slider("Estado del SNC", options=["Fresco", "Cargado", "Fatigado"])
        if st.button("DISEÑAR PLAN NEURAL"):
            with st.spinner("Sincronizando con bases de datos deportivas..."):
                time.sleep(2)
                st.session_state['ia_plan'] = True

    with col_ia2:
        if 'ia_plan' in st.session_state:
            st.markdown(f"""
            <div class="ia-card">
                <div class="ia-tag">🧬 PROTOCOLO: {obj.upper()}</div>
                <p><b>1. BLOQUE DE FUERZA:</b> 5x5 Sentadilla (80% 1RM) + 4x6 Press Militar.</p>
                <p><b>2. BLOQUE EXPLOSIVO:</b> 4 Rondas de 8 Medball Slams + 8 Saltos al cajón (Máxima velocidad).</p>
                <p><b>3. BLOQUE CARDIO:</b> 25 min Carrera Tempo (Pace sostenido Zona 3).</p>
                <p style="color:#00ff88; font-size:0.9rem;"><i>*Nota Neural: Mantener hidratación alta. Recuperación sugerida: 36 horas.</i></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHRiaHlyM2MxejZ6eG9tZ2wzeHh5Z3lyM2MxejZ6eG9tZ2wzeHh5Z3kmbXQ9Zw/3o7TKSjP8X7D6lR052/giphy.gif")

# --- MÓDULO: ANALÍTICA ---
elif system_mode == "📊 ANALÍTICA GLOBAL":
    if st.session_state['db']:
        df = pd.DataFrame(st.session_state['db'])
        st.markdown("### 📈 Performance Telemetry")
        
        # Gráfico Lineal de Volumen
        fig1 = px.line(df, x="Fecha", y="Valor", color="Tipo", markers=True, template="plotly_dark", title="Evolución de Carga")
        fig1.update_traces(line_color='#00ff88')
        st.plotly_chart(fig1, use_container_width=True)
        
        c_a1, c_a2 = st.columns(2)
        # Distribución de Módulos
        fig2 = px.pie(df, names='Tipo', hole=0.6, title="Balance del Atleta", color_discrete_sequence=['#00ff88', '#00d4ff', '#ff4b4b'])
        c_a1.plotly_chart(fig2)
        
        # Volumen por Actividad
        fig3 = px.bar(df, x="Actividad", y="Valor", color="Tipo", title="Volumen Acumulado por Ejercicio")
        c_a2.plotly_chart(fig3)
        
        st.divider()
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Aún no hay datos en el sistema central.")

# --- FOOTER ---
st.markdown("---")
st.markdown(f"**MORPHAI NEURAL PERFORMANCE OS** | Operador: **{st.session_state.user['name']}** | © 2026 Josías Martínez")
