# =================================================================
# PROJECT: MORPHAI NEURAL PERFORMANCE OS (v17.0 - PERSISTENT + IA EDITION)
# AUTHOR: JOSIAS MARTINEZ
# =================================================================

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import base64
import time
from datetime import datetime
import plotly.express as px

try:
    import anthropic
    ANTHROPIC_OK = True
except ImportError:
    ANTHROPIC_OK = False

# --- 1. CONFIGURACIÓN DE NÚCLEO ---
st.set_page_config(
    page_title="MorphAI OS v17.0 | Professional Edition",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. BASE DE DATOS (PERSISTENCIA REAL) ---
DB_PATH = "morphai.db"

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            fecha TEXT,
            tipo TEXT,
            actividad TEXT,
            valor REAL,
            meta TEXT,
            extra TEXT
        )
    """)
    conn.commit()
    return conn

conn = init_db()

def save_entry(user, tipo, actividad, valor, meta, extra):
    conn.execute(
        "INSERT INTO entries (user, fecha, tipo, actividad, valor, meta, extra) VALUES (?,?,?,?,?,?,?)",
        (user, datetime.now().strftime("%Y-%m-%d %H:%M"), tipo, actividad, valor, meta, extra)
    )
    conn.commit()

def load_entries(user):
    df = pd.read_sql_query("SELECT * FROM entries WHERE user=? ORDER BY id DESC", conn, params=(user,))
    return df

# --- 3. MOTOR ESTÉTICO (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    :root { --neon-green: #00ff88; --neon-blue: #00d4ff; --neon-red: #ff4b4b; --bg-black: #050505; }
    .stApp { background-color: var(--bg-black); color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; color: var(--neon-green); text-align: center;
        font-size: 3.5rem; letter-spacing: 12px; text-shadow: 0px 0px 30px rgba(0, 255, 136, 0.4); }
    .module-container { background: rgba(20, 20, 20, 0.8); border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 20px; padding: 30px; margin-bottom: 25px; }
    .timer-display { font-family: 'Orbitron'; font-size: 6.5rem; text-align: center; padding: 45px;
        border-radius: 35px; border: 5px solid var(--neon-red); color: var(--neon-red);
        background: rgba(255, 75, 75, 0.05); text-shadow: 0 0 20px rgba(255, 75, 75, 0.3); }
    .work-active { border-color: var(--neon-green) !important; color: var(--neon-green) !important;
        box-shadow: 0 0 50px rgba(0, 255, 136, 0.3); text-shadow: 0 0 20px rgba(0, 255, 136, 0.5); }
    .ia-card { background: linear-gradient(135deg, rgba(0,255,136,0.15) 0%, rgba(0,0,0,1) 100%);
        border: 1px solid var(--neon-green); border-radius: 20px; padding: 30px; white-space: pre-wrap; }
    .ia-tag { color: var(--neon-green); font-family: 'Orbitron'; font-size: 1.3rem;
        border-bottom: 1px solid rgba(0,255,136,0.3); margin-bottom: 15px; padding-bottom: 10px; }
    .rm-giant { font-family: 'Orbitron'; font-size: 5rem; color: var(--neon-green); text-align: center; margin: 0; }
    </style>
""", unsafe_allow_html=True)

DB_EXERCISES = {
    "Fuerza": ["Press Banca", "Sentadilla Barra", "Peso Muerto Sumó", "Press Militar", "Dominadas Pro", "Remo Pendlay"],
    "Explosividad": ["Saltos al Cajón", "Landmine Punch", "Medball Slam", "Burpee Pliométrico", "Snatch con Mancuerna", "Sprints Potencia"],
    "Running": ["Carrera Continua", "Series VO2 Max", "Fartlek Neural", "Umbral Lactato"]
}

if 'user' not in st.session_state:
    st.session_state['user'] = {"name": "JOSIAS MARTINEZ", "weight": 80, "height": 180}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown('<h1 style="font-family:Orbitron; color:#00ff88; letter-spacing:3px;">MORPHAI OS</h1>', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/847/847969.png", width=90)
    st.session_state.user["name"] = st.text_input("OPERADOR:", st.session_state.user["name"]).upper()

    st.divider()
    system_mode = st.radio("SISTEMA:", [
        "🏋️ FUERZA & LOGÍSTICA",
        "🏃 RUNNING TELEMETRY",
        "🥊 COMBATE & EXPLOSIVIDAD",
        "🤖 AI ROUTINE COACH",
        "📊 ANALÍTICA GLOBAL"
    ])

    st.divider()
    st.caption("Tus datos ahora se guardan de forma permanente (SQLite) por usuario/operador.")

USER = st.session_state.user["name"]

# --- 5. INTERFAZ PRINCIPAL ---
st.markdown('<h1 class="main-title">MORPHAI NEURAL ENGINE</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; opacity:0.6; letter-spacing:4px;">ACTIVE OPERATOR: {USER} | v17.0</p>', unsafe_allow_html=True)

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
                save_entry(USER, "Fuerza", ejer, peso * reps, f"{peso}kg x {reps}", f"RPE {rpe}")
                st.success("Set guardado permanentemente.")
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
                save_entry(USER, "Running", tipo_r, dist, pace_str, f"{hr} BPM")
                st.success("Carrera guardada permanentemente.")
    with c_run2:
        st.info("Pace estimado calculado automáticamente. (Imagen decorativa retirada por enlace roto.)")

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
            save_entry(USER, "Combate", ej_ex, reps_ex, f"{reps_ex} reps", f"{lastre}kg Lastre")
            st.success("Registro guardado permanentemente.")

# --- MÓDULO: AI ROUTINE COACH (IA REAL) ---
elif system_mode == "🤖 AI ROUTINE COACH":
    st.markdown("### 🤖 AI Routine Coach")
    st.caption("Describe tu rutina actual en texto y/o sube una foto (de tu cuaderno, una app, o una pizarra del gym). La IA la analiza y te propone una versión mejorada.")

    if not ANTHROPIC_OK:
        st.error("Falta instalar el paquete `anthropic`. Agrega `anthropic` a tu requirements.txt.")

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        help="Consíguela en console.anthropic.com. No se guarda ni se envía a ningún lado excepto a la API de Anthropic."
    )

    objetivo = st.selectbox("Objetivo principal", ["Hipertrofia", "Fuerza máxima", "Pérdida de grasa", "Resistencia / Híbrido"])
    nivel = st.select_slider("Nivel", options=["Principiante", "Intermedio", "Avanzado"])
    rutina_texto = st.text_area("Describe tu rutina actual (días, ejercicios, series/reps)", height=150)
    foto = st.file_uploader("O sube una foto de tu rutina", type=["png", "jpg", "jpeg"])

    if st.button("🧠 ANALIZAR Y MEJORAR CON IA"):
        if not api_key:
            st.warning("Ingresa tu API key para continuar.")
        elif not rutina_texto and not foto:
            st.warning("Describe tu rutina en texto o sube una foto.")
        else:
            with st.spinner("Analizando rutina..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    content = []
                    if foto is not None:
                        img_bytes = foto.read()
                        b64 = base64.b64encode(img_bytes).decode("utf-8")
                        media_type = "image/png" if foto.type == "image/png" else "image/jpeg"
                        content.append({
                            "type": "image",
                            "source": {"type": "base64", "media_type": media_type, "data": b64}
                        })
                    prompt = (
                        f"Soy un atleta de nivel {nivel}, mi objetivo es {objetivo}. "
                        f"Esta es mi rutina actual (texto y/o imagen adjunta): {rutina_texto or '(ver imagen)'}. "
                        "Analiza la rutina, señala 2-3 puntos débiles concretos, y propón una versión mejorada "
                        "organizada por día, con series, reps e intensidad sugerida. Sé específico y breve."
                    )
                    content.append({"type": "text", "text": prompt})

                    response = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=1000,
                        messages=[{"role": "user", "content": content}]
                    )
                    resultado = "".join(block.text for block in response.content if block.type == "text")
                    st.session_state["ultimo_plan_ia"] = resultado
                except Exception as e:
                    st.error(f"Error llamando a la IA: {e}")

    if "ultimo_plan_ia" in st.session_state:
        st.markdown(f'<div class="ia-card"><div class="ia-tag">🧬 PLAN MEJORADO POR IA</div>{st.session_state["ultimo_plan_ia"]}</div>', unsafe_allow_html=True)
        if st.button("💾 Guardar este plan en mi historial"):
            save_entry(USER, "IA-Plan", objetivo, 0, nivel, "Plan generado por IA")
            st.success("Plan guardado en tu historial.")

# --- MÓDULO: ANALÍTICA ---
elif system_mode == "📊 ANALÍTICA GLOBAL":
    df = load_entries(USER)
    if not df.empty:
        st.markdown("### 📈 Performance Telemetry")
        fig1 = px.line(df.sort_values("id"), x="fecha", y="valor", color="tipo", markers=True,
                        template="plotly_dark", title="Evolución de Carga")
        fig1.update_traces(line_color='#00ff88')
        st.plotly_chart(fig1, use_container_width=True)

        c_a1, c_a2 = st.columns(2)
        fig2 = px.pie(df, names='tipo', hole=0.6, title="Balance del Atleta",
                      color_discrete_sequence=['#00ff88', '#00d4ff', '#ff4b4b', '#ffaa00'])
        c_a1.plotly_chart(fig2)

        fig3 = px.bar(df, x="actividad", y="valor", color="tipo", title="Volumen Acumulado por Ejercicio")
        c_a2.plotly_chart(fig3)

        st.divider()
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Aún no hay datos guardados para este operador.")

# --- FOOTER ---
st.markdown("---")
st.markdown(f"**MORPHAI NEURAL PERFORMANCE OS** | Operador: **{USER}** | © 2026 Josías Martínez")
