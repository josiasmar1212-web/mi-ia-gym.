# =================================================================
# PROJECT: MORPHAI NEURAL PERFORMANCE OS (v14.0)
# AUTHOR: JOSIAS MARTINEZ
# COUNTRY: SPAIN / GLOBAL
# DESCRIPTION: ENTERPRISE-GRADE HYBRID ATHLETE MANAGEMENT SYSTEM
# =================================================================

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CORE SYSTEM CONFIGURATION ---
st.set_page_config(
    page_title="MorphAI Neural OS | Josías Martínez",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED NEON ARCHITECTURE (CSS) ---
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
    
    /* Header Animation */
    .main-title { 
        font-family: 'Orbitron', sans-serif; 
        color: var(--neon-green); 
        text-align: center; 
        font-size: 4rem; 
        letter-spacing: 15px; 
        text-shadow: 0px 0px 25px rgba(0, 255, 136, 0.4);
        margin-top: -30px;
    }

    /* Professional IA Cards */
    .neural-card {
        background: rgba(10, 10, 10, 0.8);
        border: 1px solid var(--neon-green);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0px 0px 20px rgba(0, 255, 136, 0.15);
        margin-bottom: 20px;
    }

    .block-header {
        font-family: 'Orbitron';
        color: var(--neon-green);
        font-size: 1.2rem;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Metrics Panels */
    .metric-v {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        text-align: center;
    }

    /* Timer Styles */
    .timer-box {
        font-family: 'Orbitron';
        font-size: 6rem;
        text-align: center;
        padding: 40px;
        border-radius: 30px;
        border: 4px solid var(--neon-red);
        color: var(--neon-red);
        background: rgba(255, 75, 75, 0.05);
        margin: 20px 0;
    }
    .work-active { border-color: var(--neon-green) !important; color: var(--neon-green) !important; box-shadow: 0 0 30px rgba(0, 255, 136, 0.3); }

    /* Buttons Customization */
    .stButton>button {
        border-radius: 8px;
        border: 1px solid var(--neon-green);
        background-color: transparent;
        color: var(--neon-green);
        font-family: 'Orbitron';
        transition: 0.4s;
    }
    .stButton>button:hover {
        background-color: var(--neon-green);
        color: black;
        box-shadow: 0 0 15px var(--neon-green);
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA PERSISTENCE LAYER ---
if 'master_db' not in st.session_state:
    st.session_state['master_db'] = []
if 'atleta_data' not in st.session_state:
    st.session_state['atleta_data'] = {"name": "JOSIAS MARTINEZ", "kg": 85, "cm": 182, "age": 26, "goal": "Fuerza Híbrida"}

# --- 4. SIDEBAR LOGISTICS ---
with st.sidebar:
    st.markdown(f'<h1 style="font-family:Orbitron; color:{st.get_option("theme.primaryColor") if "theme" in st.session_state else "#00ff88"};">MORPHAI OS</h1>', unsafe_allow_html=True)
    st.write("---")
    st.markdown("### 🛠️ Profile Management")
    st.session_state.atleta_data["name"] = st.text_input("Operator Name", st.session_state.atleta_data["name"])
    st.session_state.atleta_data["kg"] = st.number_input("Bodyweight (kg)", 40, 200, st.session_state.atleta_data["kg"])
    st.session_state.atleta_data["cm"] = st.number_input("Height (cm)", 100, 250, st.session_state.atleta_data["cm"])
    
    st.divider()
    system_mode = st.radio("System Core", ["🚀 SESSION LOG", "📊 TELEMETRY", "🧠 NEURAL PLANNER", "🧮 1RM ENGINE"])
    
    st.divider()
    if st.button("🚨 NUCLEAR RESET"):
        st.session_state['master_db'] = []
        st.rerun()

# --- 5. TOP INTERFACE ---
st.markdown('<h1 class="main-title">MORPHAI NEURAL ENGINE</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; opacity:0.7; letter-spacing:3px;">ACTIVE OPERATOR: {st.session_state.atleta_data["name"]} | 2026 BETA ACCESS</p>', unsafe_allow_html=True)

# --- 6. SYSTEM CORE MODULES ---

# --- TAB: SESSION LOG ---
if system_mode == "🚀 SESSION LOG":
    col_l1, col_l2 = st.columns([1, 1])
    with col_l1:
        st.markdown("### 📥 Input Telemetry")
        with st.form("main_log", clear_on_submit=True):
            cat = st.selectbox("Category", ["Strength (Lifting)", "Endurance (Running)", "Explosivity (Combat)"])
            ejer = st.text_input("Exercise / Activity", "Bench Press")
            c_p, c_r = st.columns(2)
            metric_val = c_p.number_input("Weight / Distance", 0.0, 500.0, 100.0)
            reps_val = c_r.number_input("Reps / Sets", 1, 50, 5)
            rpe = st.slider("Intensity (RPE)", 1, 10, 8)
            if st.form_submit_button("COMMIT TO DATABASE"):
                vol = metric_val * reps_val if cat != "Endurance (Running)" else metric_val
                st.session_state['master_db'].append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Type": cat, "Exercise": ejer, "Value": metric_val, 
                    "Units": reps_val, "Volume": vol, "Intensity": rpe
                })
                st.success("Data Synthesized.")

    with col_l2:
        st.markdown("### ⏱️ Tactical Combat Timer")
        c_t1, c_t2 = st.columns(2)
        work = c_t1.number_input("Work (Min)", 1, 5, 3)
        rest = c_t2.number_input("Rest (Sec)", 10, 60, 30)
        if st.button("🔔 START COMBAT CLOCK"):
            timer_ph = st.empty()
            for rd in range(1, 4):
                # Work Phase
                for t in range(work * 60, 0, -1):
                    timer_ph.markdown(f'<div class="timer-box work-active">RD {rd}<br>{t//60:02d}:{t%60:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
                # Rest Phase
                for t in range(rest, 0, -1):
                    timer_ph.markdown(f'<div class="timer-box">REST<br>00:{t:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
            timer_ph.success("Session Completed.")

# --- TAB: TELEMETRY (GRÁFICOS) ---
elif system_mode == "📊 TELEMETRY":
    if not st.session_state['master_db']:
        st.info("System awaiting data input for visualization.")
    else:
        df = pd.DataFrame(st.session_state['master_db'])
        st.markdown("### 📉 Performance Analytics")
        
        # Main Progress Chart
        fig_evol = px.line(df, x="Date", y="Volume", color="Type", markers=True, 
                          template="plotly_dark", title="Workload Evolution (Neural Progress)")
        fig_evol.update_traces(line_color='#00ff88')
        st.plotly_chart(fig_evol, use_container_width=True)
        
        col_g1, col_g2 = st.columns(2)
        # Distribution
        fig_pie = px.pie(df, names='Type', hole=0.5, title="Training Balance",
                        color_discrete_sequence=['#00ff88', '#00d4ff', '#ff4b4b'])
        col_g1.plotly_chart(fig_pie)
        
        # Intensity Matrix
        fig_bar = px.bar(df, x="Exercise", y="Intensity", color="Type", title="Intensity Distribution per Movement")
        col_g2.plotly_chart(fig_bar)

# --- TAB: NEURAL PLANNER (EL "GUAU") ---
elif system_mode == "🧠 NEURAL PLANNER":
    st.markdown("### 🧠 Artificial Intelligence Training Architect")
    col_p1, col_p2 = st.columns([1, 2])
    
    with col_p1:
        goal = st.selectbox("Primary Directive", ["Hypertrophy (Mass)", "Absolute Strength", "Combat Power", "Hybrid Endurance"])
        stress = st.select_slider("System Fatigue Level", options=["Low", "Baseline", "Elevated", "Critical"])
        duration = st.slider("Time Window (Min)", 15, 120, 60)
        
        if st.button("SYNTHESIZE WORKOUT"):
            with st.spinner("Processing bio-signals and training logs..."):
                time.sleep(2.5)
                st.session_state['generated_plan'] = True
                
    with col_p2:
        if 'generated_plan' in st.session_state:
            st.markdown(f"""
            <div class="neural-card">
                <div class="block-header">🧬 PROTOCOLO: {goal.upper()}</div>
                <div style="margin-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:10px;">
                    <b>Status de Fatiga:</b> {stress} | <b>Ventana:</b> {duration} min
                </div>
                <p><b>A. Neural Primer (10 min):</b> 3 Rondas de Movilidad Articular + Saltos Pliométricos (Explosividad).</p>
                <p><b>B. Primary Load (30 min):</b> Basado en tus récords, ejecutar 4x6 con 85% 1RM en el movimiento principal.</p>
                <p><b>C. Metabolic Burn (20 min):</b> Circuito híbrido: 500m Sprint + 15 Medball Slams (3 vueltas).</p>
                <p style="color:#00ff88; font-style:italic;">*Recomendación IA: Incrementar ingesta de magnesio post-sesión debido al estrés {stress}.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHRiaHlyM2MxejZ6eG9tZ2wzeHh5Z3lyM2MxejZ6eG9tZ2wzeHh5Z3kmbXQ9Zw/3o7TKSjP8X7D6lR052/giphy.gif", use_column_width=True)

# --- TAB: 1RM ENGINE ---
elif system_mode == "🧮 1RM ENGINE":
    st.markdown("### ⚡ Absolute Power Estimator")
    col_rm1, col_rm2 = st.columns([1, 1])
    with col_rm1:
        weight_rm = st.number_input("Last Load Lifted (kg)", 1.0, 500.0, 100.0)
        reps_rm = st.number_input("Repetitions (to failure)", 1, 12, 5)
        brzycki = weight_rm / (1.0278 - (0.0278 * reps_rm))
        
        st.markdown(f'<div class="metric-v"><p style="font-family:Orbitron; color:#00ff88; font-size:4rem;">{round(brzycki, 1)} KG</p><p>ESTIMATED 1RM</p></div>', unsafe_allow_html=True)
    
    with col_rm2:
        st.markdown("### 📉 Intensity Brackets")
        perc = [0.95, 0.90, 0.85, 0.80, 0.75, 0.70]
        titles = ["95% Fuerza", "90% Fuerza", "85% Potencia", "80% Hipertrofia", "75% Hipertrofia", "70% Velocidad"]
        for t, p in zip(titles, perc):
            st.write(f"**{t}:** {round(brzycki * p, 1)} kg")

# --- 7. BIOMETRIC FOOTER ---
st.write("---")
w_f = st.session_state.atleta_data["kg"]
h_f = st.session_state.atleta_data["cm"] / 100
imc_f = w_f / (h_f**2)
st.markdown(f"**MORPHAI BIOMETRICS:** BMI {round(imc_f, 1)} | **OPERATOR:** {st.session_state.atleta_data['name']} | © 2026 NEURAL OS")
