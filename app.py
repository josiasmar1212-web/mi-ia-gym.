import streamlit as st
import pandas as pd
from datetime import datetime
import time
import plotly.express as px

# --- 1. CONFIGURACIÓN DE VANGUARDIA Y ESTÉTICA ---
st.set_page_config(page_title="MorphAI Social Pro v11.0", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    .stApp { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; color: #00ff88; text-align: center; font-size: 3.5rem; letter-spacing: 12px; text-shadow: 0px 0px 20px rgba(0, 255, 136, 0.4); margin-bottom:0px; }
    .quote-style { font-style: italic; text-align: center; color: #00ff88; font-size: 1.1rem; opacity: 0.8; margin-bottom: 30px; }
    
    /* Estilos de Temporizador */
    .timer-display { font-size: 6rem; text-align: center; font-family: 'Orbitron'; border-radius: 25px; padding: 35px; border: 4px solid #ff4b4b; color: #ff4b4b; background: rgba(255, 75, 75, 0.05); }
    .work-mode { border-color: #00ff88 !important; color: #00ff88 !important; box-shadow: 0px 0px 40px rgba(0, 255, 136, 0.4); background: rgba(0, 255, 136, 0.05); }
    
    /* Estilo Panel 1RM */
    .rm-display { background: rgba(0, 255, 136, 0.1); border: 2px solid #00ff88; padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 30px; }
    .rm-val { font-family: 'Orbitron', sans-serif; color: #00ff88; font-size: 5rem; margin: 0; text-shadow: 0px 0px 15px rgba(0, 255, 136, 0.5); }
    
    /* Cards de Planificación */
    .routine-box { background: rgba(255, 255, 255, 0.03); border-left: 5px solid #00ff88; padding: 20px; border-radius: 10px; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# --- 2. BASE DE DATOS E HISTORIAL ---
if 'db_full' not in st.session_state:
    st.session_state['db_full'] = []

DB_PESAS = {
    "Pecho": ["Press Banca Plano Barra", "Press Inclinado Mancuernas", "Aperturas Cable", "Fondos Lastrados"],
    "Espalda": ["Dominadas Pro", "Remo Pendlay", "Remo Unilateral", "Peso Muerto Convencional"],
    "Piernas": ["Sentadilla High Bar", "Prensa 45°", "Peso Muerto Rumano", "Sentadilla Búlgara"],
    "Hombros/Brazos": ["Press Militar", "Elevaciones Laterales", "Curl Barra Z", "Press Francés"]
}

DB_EXPLOSIVIDAD = {
    "Pliometría": ["Saltos al Cajón", "Broad Jumps", "Sentadilla Explosiva"],
    "Impacto": ["Flexiones Pliométricas", "Landmine Punch", "Medball Slam"],
    "Torque": ["Woodchoppers Cable", "Rotación Landmine", "Russian Twist Pesado"]
}

# --- 3. NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.markdown('<h1 style="color:#00ff88; font-family:Orbitron;">MORPHAI</h1>', unsafe_allow_html=True)
    atleta = st.text_input("ID ATLETA:", value="JOSIAS_MARTINEZ").upper()
    st.divider()
    modo = st.radio("MÓDULO ACTIVO:", ["🏋️ Pesas Pro", "🏃 Running Tech", "🥊 Contacto & Power"])
    st.divider()
    if st.button("🚨 RESET TOTAL"):
        st.session_state['db_full'] = []
        st.rerun()

# --- 4. CABECERA ---
st.markdown('<h1 class="main-title">MORPHAI SYSTEM</h1>', unsafe_allow_html=True)
st.markdown('<p class="quote-style">"Disciplina sobre motivación. Siempre."</p>', unsafe_allow_html=True)

tabs = st.tabs(["⚡ ENTRENAR", "📊 ANALYTICS", "🧮 1RM MAESTRO", "🧠 IA PLANNER"])

# --- TAB 1: ENTRENAR (TODO INCLUIDO) ---
with tabs[0]:
    if modo == "🏋️ Pesas Pro":
        with st.form("f_gym", clear_on_submit=True):
            c1, c2 = st.columns(2)
            grupo = c1.selectbox("Grupo Muscular", list(DB_PESAS.keys()))
            ejer = c2.selectbox("Ejercicio", DB_PESAS[grupo])
            c3, c4, c5 = st.columns(3)
            p = c3.number_input("Carga (kg)", 0.0, 500.0, 60.0)
            r = c4.number_input("Reps", 1, 50, 10)
            rpe = c5.slider("Intensidad (RPE)", 1, 10, 8)
            tempo = st.text_input("Tempo (Excéntrica-Isométrica-Concéntrica)", "2-0-1-0")
            if st.form_submit_button("REGISTRAR SET"):
                st.session_state['db_full'].append({
                    "Fecha": datetime.now().strftime("%H:%M"), "Tipo": "Pesas",
                    "Actividad": ejer, "Dato": f"{p}kg x {r}", "Valor": p * r, "Extra": f"Tempo {tempo} | RPE {rpe}"
                })

    elif modo == "🏃 Running Tech":
        with st.form("f_run", clear_on_submit=True):
            c1, c2 = st.columns(2)
            dist = c1.number_input("Distancia (km)", 0.1, 100.0, 5.0)
            tipo_r = c2.selectbox("Estímulo", ["Fondo Aeróbico", "Series VO2 Max", "Umbral Lactato"])
            c3, c4, c5 = st.columns(3)
            m = c3.number_input("Minutos", 0, 500, 25)
            s = c4.number_input("Segundos", 0, 59, 0)
            bpm = c5.number_input("BPM Medio", 60, 220, 145)
            if st.form_submit_button("GUARDAR SESIÓN"):
                t_total = m + (s/60)
                pace = t_total / dist
                ritmo_str = f"{int(pace)}:{int((pace%1)*60):02d}"
                st.session_state['db_full'].append({
                    "Fecha": datetime.now().strftime("%d/%m"), "Tipo": "Running",
                    "Actividad": f"Run ({tipo_r})", "Dato": f"{dist}km @ {ritmo_str}", "Valor": dist, "Extra": f"{bpm} BPM"
                })

    elif modo == "🥊 Contacto & Power":
        st.subheader("⏱️ Temporizador de Combate")
        tc1, tc2, tc3 = st.columns(3)
        rds = tc1.number_input("Rounds", 1, 15, 3)
        tw = tc2.number_input("Trabajo (min)", 1, 5, 3)
        tr = tc3.number_input("Descanso (seg)", 10, 60, 30)
        
        if st.button("🔔 INICIAR ROUNDS"):
            ph = st.empty()
            for r in range(1, rds + 1):
                for t in range(tw * 60, 0, -1):
                    ph.markdown(f'<div class="timer-display work-mode">ROUND {r}<br>{t//60:02d}:{t%60:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
                if r < rds:
                    for t in range(tr, 0, -1):
                        ph.markdown(f'<div class="timer-display">DESCANSAR<br>00:{t:02d}</div>', unsafe_allow_html=True)
                        time.sleep(1)
            ph.success("COMBATE FINALIZADO")

        st.divider()
        st.subheader("⚡ Explosividad y Potencia")
        with st.form("f_explosive", clear_on_submit=True):
            cat = st.selectbox("Categoría", list(DB_EXPLOSIVIDAD.keys()))
            ej_ex = st.selectbox("Ejercicio", DB_EXPLOSIVIDAD[cat])
            c_p, c_r = st.columns(2)
            p_ex = c_p.number_input("Peso/Lastre (kg)", 0, 150, 0)
            r_ex = c_r.number_input("Reps Explosivas", 1, 30, 5)
            if st.form_submit_button("REGISTRAR POTENCIA"):
                st.session_state['db_full'].append({
                    "Fecha": datetime.now().strftime("%H:%M"), "Tipo": "Contacto",
                    "Actividad": ej_ex, "Dato": f"{p_ex}kg x {r_ex}", "Valor": r_ex if p_ex == 0 else p_ex, "Extra": "Foco Potencia"
                })

    if st.session_state['db_full']:
        st.table(pd.DataFrame(st.session_state['db_full']).tail(5))

# --- TAB 2: ANALYTICS (GRÁFICOS COMPLETOS) ---
with tabs[1]:
    st.subheader("📊 Centro de Telemetría")
    if st.session_state['db_full']:
        df_ana = pd.DataFrame(st.session_state['db_full'])
        
        # Gráfico de Evolución
        fig_line = px.line(df_ana, x="Fecha", y="Valor", color="Tipo", title="Evolución de Rendimiento", template="plotly_dark")
        fig_line.update_traces(line_color='#00ff88', marker=dict(size=10))
        st.plotly_chart(fig_line, use_container_width=True)
        
        col_g1, col_g2 = st.columns(2)
        # Distribución de Modalidades
        fig_pie = px.pie(df_ana, names='Tipo', title='Balance de Entrenamiento', hole=0.4, color_discrete_sequence=['#00ff88', '#0088ff', '#ff4b4b'])
        col_g1.plotly_chart(fig_pie)
        
        # Volumen por Actividad
        fig_bar = px.bar(df_ana, x='Actividad', y='Valor', color='Tipo', title='Volumen por Ejercicio/Actividad')
        col_g2.plotly_chart(fig_bar)
    else:
        st.info("Esperando datos para generar telemetría...")

# --- TAB 3: 1RM MAESTRO ---
with tabs[2]:
    st.markdown('<div class="rm-display">', unsafe_allow_html=True)
    st.markdown('<p style="color:#00ff88; letter-spacing:5px;">MAX POTENTIAL ESTIMATOR</p>', unsafe_allow_html=True)
    c_rm1, c_rm2 = st.columns(2)
    p_rm = c_rm1.number_input("Carga Levantada (kg)", 1.0, 600.0, 100.0)
    r_rm = c_rm2.number_input("Reps Realizadas", 1, 12, 5)
    rm_calc = p_rm / (1.0278 - (0.0278 * r_rm))
    st.markdown(f'<h1 class="rm-val">{round(rm_calc, 1)} KG</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("📈 Zonas de Entrenamiento")
    z1, z2, z3, z4 = st.columns(4)
    z1.metric("FUERZA (90%)", f"{round(rm_calc*0.9, 1)} kg")
    z2.metric("MASA (80%)", f"{round(rm_calc*0.8, 1)} kg")
    z3.metric("POTENCIA (70%)", f"{round(rm_calc*0.7, 1)} kg")
    z4.metric("FONDO (60%)", f"{round(rm_calc*0.6, 1)} kg")

# --- TAB 4: IA PLANNER ---
with tabs[3]:
    st.subheader("🧬 Generador de Ciclos")
    objetivo = st.selectbox("Meta Principal:", ["Hipertrofia", "Fuerza Absoluta", "Potencia Explosiva"])
    if st.button("DISEÑAR"):
        planes = {"Hipertrofia": "4x10 (Tempo 3-0-1-0)", "Fuerza Absoluta": "5x3 (RPE 9)", "Potencia Explosiva": "3x6 (Máxima Velocidad)"}
        st.markdown(f'<div class="routine-box"><b>MÉTODO:</b> {planes[objetivo]}</div>', unsafe_allow_html=True)

# --- PIE DE PÁGINA PROFESIONAL ---
st.markdown("---")
st.markdown(f"© 2026 MorphAI System | Desarrollado por **Josías Martínez** | Propiedad Intelectual")
