import streamlit as st
import pandas as pd
from datetime import datetime
import time
import plotly.express as px

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO ---
st.set_page_config(page_title="MorphAI Social Pro v7", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    .stApp { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; color: #00ff88; text-align: center; font-size: 3.5rem; letter-spacing: 12px; margin-bottom: 0px; text-shadow: 0px 0px 20px rgba(0, 255, 136, 0.4); }
    .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; margin-bottom: 20px; }
    .timer-display { font-size: 6rem; text-align: center; font-family: 'Orbitron'; border-radius: 20px; padding: 30px; border: 4px solid #ff4b4b; color: #ff4b4b; margin: 20px 0; }
    .work-mode { border-color: #00ff88 !important; color: #00ff88 !important; box-shadow: 0px 0px 40px rgba(0, 255, 136, 0.4); }
    .routine-box { background: rgba(0, 255, 136, 0.05); border-left: 5px solid #00ff88; padding: 20px; margin: 15px 0; border-radius: 10px; border-top: 1px solid rgba(0,255,136,0.2); }
    .record-card { background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 136, 255, 0.1)); border: 1px solid #00ff88; border-radius: 12px; padding: 15px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 2. MOTOR DE DATOS (SESSION STATE) ---
if 'historial_sesion' not in st.session_state:
    st.session_state['historial_sesion'] = []
if 'records_social' not in st.session_state:
    st.session_state['records_social'] = {}
if 'plan_activo' not in st.session_state:
    st.session_state['plan_activo'] = "No seleccionado"

# --- 3. BIBLIOTECAS DE EJERCICIOS ---
BIBLIOTECA_GYM = {
    "Pecho": ["Press Banca Plano", "Press Inclinado Mancuernas", "Aperturas Polea", "Fondos Lastrados", "Chest Press Machine", "Push-ups Diamante"],
    "Espalda": ["Dominadas Pro", "Remo con Barra Pendlay", "Jalón al Pecho", "Remo Unilateral Máquina", "Pull-over Cuerda", "Peso Muerto Convencional"],
    "Piernas": ["Sentadilla Libre", "Prensa 45°", "Peso Muerto Rumano", "Sentadilla Búlgara", "Extensiones Cuádriceps", "Curl Femoral Tumbado"],
    "Hombros": ["Press Militar Barra", "Elevaciones Laterales Cable", "Face Pulls", "Pájaros con Mancuerna", "Press Arnold"],
    "Brazos": ["Curl Barra Z", "Press Francés", "Martillo con Cuerda", "Tríceps Polea Alta", "Curl Concentrado"]
}

EJER_EXPLOSIVOS = {
    "Potencia Inferior": ["Saltos al Cajón (Box Jumps)", "Broad Jumps", "Sentadilla Explosiva", "Kettlebell Swings", "Zancadas con Salto"],
    "Impacto Superior": ["Flexiones Pliométricas", "Lanzamiento Balón Pared", "Landmine Press (Punch)", "Slam Ball (Impacto Suelo)"],
    "Rotación Combat": ["Woodchoppers Cable", "Rotación Landmine", "Lanzamiento Lateral Medball", "Rusa Twist Explosivo"]
}

# --- 4. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown('<h1 style="color:#00ff88; font-family:Orbitron;">PERFIL</h1>', unsafe_allow_html=True)
    usuario = st.text_input("Nombre del Atleta:", value="Atleta_Alpha").strip()
    st.divider()
    modalidad = st.radio("MODALIDAD ACTIVA:", ["🏋️ Pesas Pro", "🏃 Running Tech", "🥊 Contacto & Power"])
    st.divider()
    st.info(f"Usuario: {usuario}\nPlan: {st.session_state['plan_activo']}")
    if st.button("🗑️ REINICIAR TODO"):
        st.session_state['historial_sesion'] = []
        st.session_state['records_social'] = {}
        st.rerun()

# --- 5. CABECERA ---
st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; color:#888;">SISTEMA OPERATIVO DE ALTO RENDIMIENTO | BIENVENIDO {usuario.upper()}</p>', unsafe_allow_html=True)

tabs = st.tabs(["⚡ ENTRENAR", "🧠 PLANIFICAR", "🏆 RÉCORDS", "📊 ANALYTICS", "🧮 1RM"])

# --- TAB 1: ENTRENAR ---
with tabs[0]:
    if modalidad == "🥊 Contacto & Power":
        st.subheader("⏱️ Temporizador de Rounds (Green Mode)")
        c1, c2, c3 = st.columns(3)
        n_rounds = c1.number_input("Rounds", 1, 15, 3)
        t_work = c2.number_input("Minutos Round", 1, 5, 3)
        t_rest = c3.number_input("Segundos Descanso", 10, 60, 30)
        
        if st.button("🥊 INICIAR CAMPANA"):
            ph = st.empty()
            for r in range(1, n_rounds + 1):
                # Fase Trabajo (VERDE)
                for t in range(t_work * 60, 0, -1):
                    ph.markdown(f'<div class="timer-display work-mode">ROUND {r}<br>{t//60:02d}:{t%60:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
                
                # Fase Descanso (ROJO)
                if r < n_rounds:
                    st.toast(f"¡Descanso Round {r}!")
                    for t in range(t_rest, 0, -1):
                        ph.markdown(f'<div class="timer-display">DESCANSO<br>00:{t:02d}</div>', unsafe_allow_html=True)
                        time.sleep(1)
            ph.success("✅ ENTRENAMIENTO COMPLETADO")
            st.balloons()

        st.divider()
        st.subheader("🔥 Registro de Potencia Explosiva")
        with st.form("form_ex", clear_on_submit=True):
            cat = st.selectbox("Categoría de Potencia", list(EJER_EXPLOSIVOS.keys()))
            ejer = st.selectbox("Ejercicio", EJER_EXPLOSIVOS[cat])
            c_p, c_r = st.columns(2)
            peso_ex = c_p.number_input("Carga (kg)", 0, 150, 20)
            reps_ex = c_r.number_input("Reps (Velocidad Máxima)", 1, 20, 5)
            if st.form_submit_button("REGISTRAR POTENCIA"):
                st.session_state['historial_sesion'].append({"Usuario": usuario, "Fecha": datetime.now().strftime("%d/%m"), "Actividad": ejer, "Dato": f"{peso_ex}kg x {reps_ex}", "Valor": peso_ex})

    elif modalidad == "🏋️ Pesas Pro":
        with st.form("gym_master_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            grupo = col1.selectbox("Grupo Muscular", list(BIBLIOTECA_GYM.keys()))
            ejer = col2.selectbox("Ejercicio Seleccionado", BIBLIOTECA_GYM[grupo])
            c3, c4 = st.columns(2)
            p = c3.number_input("Peso (kg)", 0.0, 600.0, 60.0)
            r = c4.number_input("Repeticiones", 1, 100, 10)
            if st.form_submit_button("GUARDAR SERIE"):
                key = f"{usuario}_{ejer}"
                if key not in st.session_state['records_social'] or p > st.session_state['records_social'][key]:
                    st.session_state['records_social'][key] = p
                st.session_state['historial_sesion'].append({"Usuario": usuario, "Fecha": datetime.now().strftime("%d/%m"), "Actividad": ejer, "Dato": f"{p}kg x {r}", "Valor": p})

    if st.session_state['historial_sesion']:
        st.markdown("### 📋 Log de la Sesión")
        st.table(pd.DataFrame(st.session_state['historial_sesion']).tail(5))

# --- TAB 2: PLANIFICAR (GENERADOR IA) ---
with tabs[1]:
    st.subheader("🧬 Generador de Rutinas Personalizadas")
    c_p1, c_p2 = st.columns(2)
    meta = c_p1.selectbox("¿Cuál es tu objetivo?", ["Hipertrofia (Masa Muscular)", "Fuerza Bruta", "Potencia para Combate"])
    nivel = c_p2.select_slider("Nivel de Intensidad", options=["Bajo", "Moderado", "Élite"])
    
    if st.button("🪄 GENERAR ESTRATEGIA"):
        st.session_state['plan_activo'] = meta
        config = {
            "Hipertrofia (Masa Muscular)": {"s": "4", "r": "8-12", "d": "90 seg", "tipo": "Control Excétrico"},
            "Fuerza Bruta": {"s": "5", "r": "1-5", "d": "3-5 min", "tipo": "Carga Máxima"},
            "Potencia para Combate": {"s": "3", "r": "5-8", "d": "2 min", "tipo": "Máxima Velocidad"}
        }
        plan = config[meta]
        st.success(f"Plan '{meta}' activado para {usuario}")
        
        cols = st.columns(3)
        for i in range(1, 4):
            cols[i-1].markdown(f"""
            <div class="routine-box">
                <h4>BLOQUE {i}</h4>
                • <b>Series:</b> {plan['s']}<br>
                • <b>Reps:</b> {plan['r']}<br>
                • <b>Descanso:</b> {plan['d']}<br>
                • <b>Foco:</b> {plan['tipo']}
            </div>
            """, unsafe_allow_html=True)

# --- TAB 3: RÉCORDS ---
with tabs[2]:
    st.subheader("🥇 Hall of Fame Personal")
    recs = {k.split('_')[1]: v for k, v in st.session_state['records_social'].items() if k.startswith(usuario)}
    if recs:
        c_rec = st.columns(len(recs) if len(recs) < 5 else 4)
        for i, (ej, p) in enumerate(recs.items()):
            c_rec[i % 4].markdown(f'<div class="record-card"><small>{ej}</small><h2>{p} kg</h2></div>', unsafe_allow_html=True)
    else:
        st.info("Aún no has registrado récords. ¡A trabajar!")

# --- TAB 4: ANALYTICS ---
with tabs[3]:
    st.subheader("📈 Curva de Progreso")
    if st.session_state['historial_sesion']:
        df_an = pd.DataFrame(st.session_state['historial_sesion'])
        df_u = df_an[df_an["Usuario"] == usuario]
        if not df_u.empty:
            fig = px.line(df_u, x=df_u.index, y="Valor", color="Actividad", markers=True, template="plotly_dark")
            fig.update_traces(line_color='#00ff88')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sin datos acumulados.")

# --- TAB 5: 1RM ---
with tabs[4]:
    st.subheader("🧮 Calculadora Científica 1RM")
    c_rm1, c_rm2 = st.columns(2)
    p_rm = c_rm1.number_input("Peso Levantado (kg)", 1.0, 600.0, 100.0)
    r_rm = c_rm2.number_input("Repeticiones Logradas", 1, 12, 5)
    
    # Fórmula de Brzycki
    one_rm = p_rm / (1.0278 - (0.0278 * r_rm))
    
    st.markdown(f'<div class="timer-display work-mode" style="font-size:4rem;">{round(one_rm, 1)} kg</div>', unsafe_allow_html=True)
    
    st.markdown("### 📊 Zonas de Entrenamiento")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("ZONA FUERZA (90%)", f"{round(one_rm*0.9, 1)} kg")
    col_b.metric("ZONA HIPERTROFIA (80%)", f"{round(one_rm*0.8, 1)} kg")
    col_c.metric("ZONA POTENCIA (70%)", f"{round(one_rm*0.7, 1)} kg")
