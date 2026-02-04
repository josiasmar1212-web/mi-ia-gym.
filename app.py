import streamlit as st
import pandas as pd
from datetime import datetime
import time
import plotly.express as px

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="MorphAI Social Pro v7", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    .stApp { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; color: #00ff88; text-align: center; font-size: 3.5rem; letter-spacing: 12px; margin-bottom: 0px; text-shadow: 0px 0px 20px rgba(0, 255, 136, 0.4); }
    .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; margin-bottom: 20px; }
    .timer-display { font-size: 6rem; text-align: center; font-family: 'Orbitron'; border-radius: 20px; padding: 30px; border: 4px solid #ff4b4b; color: #ff4b4b; margin: 20px 0; }
    .work-mode { border-color: #00ff88 !important; color: #00ff88 !important; box-shadow: 0px 0px 40px rgba(0, 255, 136, 0.4); }
    .routine-box { background: rgba(0, 255, 136, 0.05); border-left: 5px solid #00ff88; padding: 20px; margin: 15px 0; border-radius: 10px; }
    .quote-style { font-style: italic; text-align: center; color: #00ff88; font-size: 1.2rem; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. BIBLIOTECAS COMPLETAS ---
BIBLIOTECA_GYM = {
    "Pecho": ["Press Banca Plano", "Press Inclinado", "Aperturas Polea", "Fondos Lastrados", "Chest Press Machine"],
    "Espalda": ["Dominadas Pro", "Remo con Barra Pendlay", "Jalón al Pecho", "Remo Unilateral", "Pull-over Cuerda"],
    "Piernas": ["Sentadilla Libre", "Prensa 45°", "Peso Muerto Rumano", "Sentadilla Búlgara", "Extensiones"],
    "Hombros": ["Press Militar Barra", "Elevaciones Laterales", "Face Pulls", "Press Arnold"],
    "Brazos": ["Curl Barra Z", "Press Francés", "Martillo con Cuerda", "Tríceps Polea Alta"]
}

EJER_EXPLOSIVOS = {
    "Potencia Inferior": ["Saltos al Cajón", "Broad Jumps", "Sentadilla Explosiva", "Kettlebell Swings"],
    "Impacto Superior": ["Flexiones Pliométricas", "Lanzamiento Balón Pared", "Landmine Press (Punch)"],
    "Rotación Combat": ["Woodchoppers Cable", "Rotación Landmine", "Lanzamiento Lateral Medball"]
}

# --- 3. MEMORIA ---
if 'historial_sesion' not in st.session_state: st.session_state['historial_sesion'] = []
if 'records_social' not in st.session_state: st.session_state['records_social'] = {}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown('<h1 style="color:#00ff88; font-family:Orbitron;">PERFIL</h1>', unsafe_allow_html=True)
    usuario = st.text_input("Atleta:", value="Atleta_Alpha").strip()
    st.divider()
    modalidad = st.radio("MODALIDAD:", ["🏋️ Pesas Pro", "🏃 Running Tech", "🥊 Contacto & Power"])
    st.divider()
    if st.button("🗑️ REINICIAR"):
        st.session_state['historial_sesion'] = []
        st.rerun()

# --- 5. CABECERA ---
st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)
st.markdown('<p class="quote-style">"No cuentes los días, haz que los días cuenten."</p>', unsafe_allow_html=True)

tabs = st.tabs(["⚡ ENTRENAR", "🧠 PLANIFICAR", "🏆 RÉCORDS", "📊 ANALYTICS", "🧮 1RM"])

# --- TAB 1: ENTRENAR (CORREGIDO) ---
with tabs[0]:
    if modalidad == "🏋️ Pesas Pro":
        with st.form("gym_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            grupo_sel = col1.selectbox("Grupo Muscular", list(BIBLIOTECA_GYM.keys()))
            # ESTO ES LO QUE PEDISTE: El segundo selectbox depende del primero
            ejer_sel = col2.selectbox("Ejercicio", BIBLIOTECA_GYM[grupo_sel])
            
            c3, c4 = st.columns(2)
            peso = c3.number_input("Peso (kg)", 0.0, 500.0, 60.0)
            reps = c4.number_input("Reps", 1, 50, 10)
            
            if st.form_submit_button("REGISTRAR SERIE"):
                st.session_state['historial_sesion'].append({
                    "Usuario": usuario, "Fecha": datetime.now().strftime("%H:%M"), 
                    "Actividad": ejer_sel, "Dato": f"{peso}kg x {reps}", "Valor": peso
                })

    elif modalidad == "🏃 Running Tech":
        with st.form("run_form", clear_on_submit=True):
            c_r1, c_r2 = st.columns(2)
            km = c_r1.number_input("Distancia (km)", 0.1, 100.0, 5.0)
            tipo_r = c_r2.selectbox("Periodo", ["Fondo", "Series", "Recuperación", "Tirada Larga"])
            
            c_r3, c_r4 = st.columns(2)
            mins = c_r3.number_input("Minutos", 1, 600, 25)
            segs = c_r4.number_input("Segundos", 0, 59, 0)
            
            if st.form_submit_button("GUARDAR RUN"):
                t_total = mins + (segs/60)
                ritmo = t_total / km
                ritmo_str = f"{int(ritmo)}:{int((ritmo%1)*60):02d} min/km"
                st.session_state['historial_sesion'].append({
                    "Usuario": usuario, "Fecha": datetime.now().strftime("%d/%m"), 
                    "Actividad": f"Running ({tipo_r})", "Dato": f"{km}km a {ritmo_str}", "Valor": km
                })

    elif modalidad == "🥊 Contacto & Power":
        st.subheader("⏱️ Temporizador Verde (Go!)")
        ct1, ct2, ct3 = st.columns(3)
        rounds = ct1.number_input("Rounds", 1, 15, 3)
        m_work = ct2.number_input("Min Round", 1, 5, 3)
        s_rest = ct3.number_input("Seg Descanso", 10, 60, 30)
        
        if st.button("🔔 EMPEZAR ROUNDS"):
            ph = st.empty()
            for r in range(1, rounds + 1):
                # TRABAJO EN VERDE
                for t in range(m_work * 60, 0, -1):
                    ph.markdown(f'<div class="timer-display work-mode">ROUND {r}<br>{t//60:02d}:{t%60:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
                # DESCANSO EN ROJO
                if r < rounds:
                    for t in range(s_rest, 0, -1):
                        ph.markdown(f'<div class="timer-display">DESCANSO<br>00:{t:02d}</div>', unsafe_allow_html=True)
                        time.sleep(1)
            ph.success("¡Combate finalizado!")

        st.divider()
        st.subheader("🔥 Biblioteca de Explosividad")
        with st.form("ex_form", clear_on_submit=True):
            cat_ex = st.selectbox("Categoría de Potencia", list(EJER_EXPLOSIVOS.keys()))
            ejer_ex = st.selectbox("Ejercicio", EJER_EXPLOSIVOS[cat_ex])
            p_ex = st.number_input("Carga (kg)", 0, 150, 10)
            if st.form_submit_button("REGISTRAR POTENCIA"):
                st.session_state['historial_sesion'].append({
                    "Usuario": usuario, "Fecha": datetime.now().strftime("%H:%M"), 
                    "Actividad": ejer_ex, "Dato": f"Explosivo {p_ex}kg", "Valor": p_ex
                })

    # TABLA DE PROGRESO SIEMPRE VISIBLE ABAJO DE ENTRENAR
    if st.session_state['historial_sesion']:
        st.markdown("### 📋 Tabla de Progreso de la Sesión")
        st.table(pd.DataFrame(st.session_state['historial_sesion']).tail(10))

# --- TAB 2: PLANIFICAR (CON GENERADOR) ---
with tabs[1]:
    st.subheader("🧬 Generador de Rutina IA")
    meta = st.selectbox("¿Qué buscas hoy?", ["Hipertrofia", "Fuerza Máxima", "Potencia Explosiva"])
    if st.button("GENERAR PLAN"):
        params = {
            "Hipertrofia": {"s": "4", "r": "10-12", "d": "90s", "f": "Controlado"},
            "Fuerza Máxima": {"s": "5", "r": "3-5", "d": "3 min", "f": "Explosivo en subida"},
            "Potencia Explosiva": {"s": "3", "r": "6", "d": "2 min", "f": "Máxima Velocidad"}
        }
        p = params[meta]
        st.markdown(f"""
        <div class="routine-box">
            <b>PLAN GENERADO: {meta.upper()}</b><br>
            • Series: {p['s']} | Reps: {p['r']} | Descanso: {p['d']}<br>
            • Enfoque: {p['f']}
        </div>
        """, unsafe_allow_html=True)

# --- TAB 4: ANALYTICS ---
with tabs[3]:
    if st.session_state['historial_sesion']:
        df = pd.DataFrame(st.session_state['historial_sesion'])
        fig = px.line(df, x="Fecha", y="Valor", color="Actividad", template="plotly_dark", title="Tu Evolución")
        fig.update_traces(line_color='#00ff88')
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 5: 1RM ---
with tabs[4]:
    st.subheader("Calculadora 1RM")
    c_rm1, c_rm2 = st.columns(2)
    p_rm = c_rm1.number_input("Peso", 1, 500, 100)
    r_rm = c_rm2.number_input("Reps", 1, 12, 5)
    rm_calc = p_rm * (1 + 0.0333 * r_rm)
    st.metric("Tu 1RM es de:", f"{round(rm_calc, 1)} kg")
