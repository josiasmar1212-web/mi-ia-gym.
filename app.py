import streamlit as st
import pandas as pd
from datetime import datetime
import time
import plotly.express as px

# --- 1. CONFIGURACIÓN Y ESTÉTICA NEÓN ---
st.set_page_config(page_title="MorphAI Social Pro v9.5", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    .stApp { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; color: #00ff88; text-align: center; font-size: 3.5rem; letter-spacing: 12px; text-shadow: 0px 0px 20px rgba(0, 255, 136, 0.4); margin-bottom:0px; }
    .quote-style { font-style: italic; text-align: center; color: #00ff88; font-size: 1.1rem; opacity: 0.8; margin-bottom: 30px; }
    
    /* Timer Estilo Dinámico */
    .timer-display { font-size: 6rem; text-align: center; font-family: 'Orbitron'; border-radius: 25px; padding: 35px; border: 4px solid #ff4b4b; color: #ff4b4b; background: rgba(255, 75, 75, 0.05); }
    .work-mode { border-color: #00ff88 !important; color: #00ff88 !important; box-shadow: 0px 0px 40px rgba(0, 255, 136, 0.4); background: rgba(0, 255, 136, 0.05); }
    
    /* Panel 1RM Neón */
    .rm-display { background: rgba(0, 255, 136, 0.1); border: 2px solid #00ff88; padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 30px; box-shadow: 0px 0px 20px rgba(0, 255, 136, 0.2); }
    .rm-val { font-family: 'Orbitron', sans-serif; color: #00ff88; font-size: 5rem; margin: 0; text-shadow: 0px 0px 15px rgba(0, 255, 136, 0.5); }
    
    /* Tarjetas de Planificación */
    .routine-box { background: rgba(255, 255, 255, 0.03); border-left: 5px solid #00ff88; padding: 20px; border-radius: 10px; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# --- 2. BASE DE DATOS DE EJERCICIOS ---
if 'historial_completo' not in st.session_state:
    st.session_state['historial_completo'] = []

DB_PESAS = {
    "Pecho": ["Press Banca Plano Barra", "Press Inclinado Mancuernas", "Aperturas Cable", "Fondos Lastrados", "Chest Press"],
    "Espalda": ["Dominadas Pro", "Remo Pendlay", "Remo Unilateral Máquina", "Jalón al Pecho", "Peso Muerto Convencional"],
    "Piernas": ["Sentadilla High Bar", "Prensa 45°", "Peso Muerto Rumano", "Sentadilla Búlgara", "Extensiones Cuádriceps"],
    "Hombros": ["Press Militar", "Elevaciones Laterales", "Face Pulls", "Press Arnold", "Pájaros"],
    "Brazos": ["Curl Barra Z", "Press Francés", "Martillo con Cuerda", "Tríceps Polea Alta", "Curl Concentrado"]
}

DB_COMBAT = {
    "Potencia Inferior (Pliometría)": ["Saltos al Cajón", "Broad Jumps", "Sentadilla Explosiva", "Kettlebell Swings", "Burpees Pliométricos"],
    "Impacto Superior (Punch Power)": ["Flexiones Pliométricas", "Lanzamiento Balón Pared", "Landmine Punch", "Medball Slam"],
    "Core Rotativo (Torque)": ["Woodchoppers Cable", "Rotación Landmine", "Russian Twist Pesado", "Lanzamiento Lateral Medball"]
}

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.markdown('<h1 style="color:#00ff88; font-family:Orbitron;">MORPHAI</h1>', unsafe_allow_html=True)
    atleta = st.text_input("ID ATLETA:", value="OPERADOR_ALPHA").upper()
    st.divider()
    modo = st.radio("SELECCIONAR MÓDULO:", ["🏋️ Pesas Pro", "🏃 Running Tech", "🥊 Contacto & Power"])
    st.divider()
    if st.button("🗑️ REINICIAR SISTEMA"):
        st.session_state['historial_completo'] = []
        st.rerun()

# --- 4. CABECERA ---
st.markdown('<h1 class="main-title">MORPHAI SYSTEM</h1>', unsafe_allow_html=True)
st.markdown('<p class="quote-style">"Tu mente es el límite, tu cuerpo es la máquina."</p>', unsafe_allow_html=True)

tabs = st.tabs(["⚡ ENTRENAR", "🧠 IA PLANNER", "📊 ANALYTICS", "🧮 MÓDULO 1RM"])

# --- TAB 1: ENTRENAR ---
with tabs[0]:
    if modo == "🏋️ Pesas Pro":
        with st.form("f_gym", clear_on_submit=True):
            c1, c2 = st.columns(2)
            grupo = c1.selectbox("Grupo Muscular", list(DB_PESAS.keys()))
            ejer = c2.selectbox("Ejercicio Seleccionado", DB_PESAS[grupo])
            c3, c4, c5 = st.columns(3)
            p = c3.number_input("Carga (kg)", 0.0, 500.0, 60.0)
            r = c4.number_input("Reps", 1, 50, 10)
            rpe = c5.slider("Intensidad (RPE)", 1, 10, 8)
            tempo = st.text_input("Tempo (Ej: 3-0-1-0)", "2-0-1-0")
            if st.form_submit_button("REGISTRAR SET"):
                st.session_state['historial_completo'].append({
                    "Fecha": datetime.now().strftime("%H:%M"), "Tipo": "Pesas",
                    "Actividad": ejer, "Dato": f"{p}kg x {r}", "Meta": f"RPE {rpe}",
                    "Extra": f"Tempo: {tempo}", "Valor": p * r
                })

    elif modo == "🏃 Running Tech":
        with st.form("f_run", clear_on_submit=True):
            c1, c2 = st.columns(2)
            dist = c1.number_input("Distancia (km)", 0.1, 100.0, 5.0)
            tipo_r = c2.selectbox("Tipo", ["Fondo", "Series", "VO2 Max", "Umbral"])
            c3, c4, c5 = st.columns(3)
            m = c3.number_input("Min", 0, 500, 25)
            s = c4.number_input("Seg", 0, 59, 0)
            bpm = c5.number_input("BPM Medio", 60, 220, 145)
            if st.form_submit_button("GUARDAR RUN"):
                t_total = m + (s/60)
                pace = t_total / dist
                ritmo_str = f"{int(pace)}:{int((pace%1)*60):02d}"
                st.session_state['historial_completo'].append({
                    "Fecha": datetime.now().strftime("%d/%m"), "Tipo": "Running",
                    "Actividad": f"Run ({tipo_r})", "Dato": f"{dist}km @ {ritmo_str}",
                    "Meta": f"BPM: {bpm}", "Extra": f"Ritmo: {ritmo_str}", "Valor": dist
                })

    elif modo == "🥊 Contacto & Power":
        # PARTE A: EL TEMPORIZADOR
        st.subheader("⏱️ Temporizador de Combate")
        tc1, tc2, tc3 = st.columns(3)
        rds = tc1.number_input("Rounds", 1, 15, 3)
        tw = tc2.number_input("Minutos de Trabajo", 1, 5, 3)
        tr = tc3.number_input("Segundos de Descanso", 10, 120, 30)
        
        if st.button("🔔 INICIAR TEMPORIZADOR"):
            ph = st.empty()
            for r in range(1, rds + 1):
                # TRABAJO (VERDE)
                for t in range(tw * 60, 0, -1):
                    ph.markdown(f'<div class="timer-display work-mode">ROUND {r}<br>{t//60:02d}:{t%60:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
                # DESCANSO (ROJO)
                if r < rds:
                    for t in range(tr, 0, -1):
                        ph.markdown(f'<div class="timer-display">DESCANSAR<br>00:{t:02d}</div>', unsafe_allow_html=True)
                        time.sleep(1)
            ph.success("✅ ENTRENAMIENTO FINALIZADO")

        st.divider()
        # PARTE B: EJERCICIOS DE EXPLOSIVIDAD
        st.subheader("⚡ Biblioteca de Explosividad")
        with st.form("f_combat_ex", clear_on_submit=True):
            cat = st.selectbox("Categoría de Potencia", list(DB_COMBAT.keys()))
            ejer_ex = st.selectbox("Ejercicio", DB_COMBAT[cat])
            c_p, c_r = st.columns(2)
            peso_ex = c_p.number_input("Carga (kg)", 0, 150, 0)
            reps_ex = c_r.number_input("Reps de Potencia", 1, 25, 5)
            if st.form_submit_button("REGISTRAR POTENCIA"):
                st.session_state['historial_completo'].append({
                    "Fecha": datetime.now().strftime("%H:%M"), "Tipo": "Contacto",
                    "Actividad": ejer_ex, "Dato": f"{peso_ex}kg x {reps_ex}",
                    "Meta": "Explosividad", "Extra": f"Cat: {cat}", "Valor": reps_ex if peso_ex == 0 else peso_ex
                })

    # TABLA DE PROGRESO (VISIBILIDAD TOTAL)
    if st.session_state['historial_completo']:
        st.markdown("### 📋 Tabla de Progreso de la Sesión")
        st.table(pd.DataFrame(st.session_state['historial_completo']).tail(10))

# --- TAB 4: MÓDULO 1RM (ESTILO NEÓN + ESTADÍSTICAS) ---
with tabs[3]:
    st.markdown('<div class="rm-display">', unsafe_allow_html=True)
    st.markdown('<p style="color:#00ff88; letter-spacing:5px; margin-bottom:0px;">CÁLCULO DE 1RM ESTIMADO</p>', unsafe_allow_html=True)
    c_rm1, c_rm2 = st.columns(2)
    p_in = c_rm1.number_input("Peso (kg)", 1.0, 500.0, 100.0)
    r_in = c_rm2.number_input("Reps (máx 12)", 1, 12, 5)
    rm = p_in / (1.0278 - (0.0278 * r_in)) # Brzycki
    st.markdown(f'<h1 class="rm-val">{round(rm, 1)} KG</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("📊 Zonas de Entrenamiento Críticas")
    z1, z2, z3, z4 = st.columns(4)
    z1.metric("FUERZA (95%)", f"{round(rm*0.95, 1)} kg", "Power")
    z2.metric("MASA (80%)", f"{round(rm*0.8, 1)} kg", "Muscle")
    z3.metric("VELOCIDAD (70%)", f"{round(rm*0.7, 1)} kg", "Speed")
    z4.metric("FONDO (60%)", f"{round(rm*0.6, 1)} kg", "Endurance")
    
    st.divider()
    st.write("**Desglose de Porcentajes:**")
    perc_df = pd.DataFrame({
        "Intensidad": ["100%", "90%", "80%", "70%", "60%", "50%"],
        "Carga Sugerida (kg)": [f"{round(rm*p, 1)} kg" for p in [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]]
    })
    st.table(perc_df)

# --- TAB 3: ANALYTICS ---
with tabs[2]:
    if st.session_state['historial_completo']:
        df = pd.DataFrame(st.session_state['historial_completo'])
        fig = px.line(df, x="Fecha", y="Valor", color="Actividad", template="plotly_dark", title="Evolución de Volumen/Carga")
        fig.update_traces(line_color='#00ff88')
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: IA PLANNER ---
with tabs[1]:
    st.subheader("🧬 Generador de Rutinas IA")
    meta = st.selectbox("Objetivo hoy:", ["Hipertrofia", "Fuerza Máxima", "Potencia para Combate"])
    if st.button("GENERAR"):
        planes = {
            "Hipertrofia": "4x12 (90s descanso) | Tempo 3-1-1-0",
            "Fuerza Máxima": "5x3 (3-5 min descanso) | Explosividad concéntrica",
            "Potencia para Combate": "3x5 (2 min descanso) | Pliometría técnica"
        }
        st.markdown(f'<div class="routine-box"><b>PLAN RECOMENDADO:</b> {planes[meta]}</div>', unsafe_allow_html=True)
