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

# --- 3. MOTOR ESTÉTICO (CSS) — Sistema "Dossier de Rendimiento" ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap');

    :root {
        --bg-0: #0b0f0d;
        --bg-1: #121714;
        --panel: #161d19;
        --line: rgba(150, 255, 200, 0.12);
        --signal: #35d68c;
        --signal-soft: rgba(53, 214, 140, 0.12);
        --amber: #f5a623;
        --amber-soft: rgba(245, 166, 35, 0.10);
        --text-hi: #eef2f0;
        --text-mid: #9aa8a2;
        --text-low: #5e6b66;
    }

    .stApp { background: var(--bg-0); color: var(--text-hi); font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }

    /* Cabecera de bienvenida */
    .hero-card {
        background: linear-gradient(160deg, var(--bg-1) 0%, var(--panel) 100%);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 28px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }
    .hero-eyebrow {
        font-family: 'JetBrains Mono', monospace;
        color: var(--signal);
        font-size: 0.75rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.9rem;
        font-weight: 700;
        color: var(--text-hi);
        margin: 0;
    }
    .hero-sub { color: var(--text-mid); font-size: 0.92rem; margin-top: 4px; }
    .hero-badge {
        font-family: 'JetBrains Mono', monospace;
        background: var(--signal-soft);
        border: 1px solid var(--line);
        color: var(--signal);
        padding: 10px 16px;
        border-radius: 10px;
        font-size: 0.8rem;
        text-align: right;
        line-height: 1.5;
    }

    /* Contenedores de módulo */
    .module-container {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 26px;
        margin-bottom: 22px;
    }

    /* Temporizador táctico */
    .timer-display {
        font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 5.5rem;
        text-align: center; padding: 40px; border-radius: 18px; border: 2px solid var(--amber);
        color: var(--amber); background: var(--amber-soft); letter-spacing: 4px;
    }
    .work-active {
        border-color: var(--signal) !important; color: var(--signal) !important;
        background: var(--signal-soft) !important;
    }

    /* Tarjeta de IA */
    .ia-card {
        background: var(--panel); border: 1px solid var(--line); border-left: 3px solid var(--signal);
        border-radius: 14px; padding: 26px; white-space: pre-wrap; color: var(--text-hi); line-height: 1.6;
    }
    .ia-tag {
        color: var(--signal); font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;
        letter-spacing: 1.5px; text-transform: uppercase; border-bottom: 1px solid var(--line);
        margin-bottom: 14px; padding-bottom: 10px;
    }

    .rm-giant {
        font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 3.6rem;
        color: var(--signal); text-align: center; margin: 0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] { background: var(--bg-1); border-right: 1px solid var(--line); }
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
    st.caption("🔒 Tus datos se guardan de forma permanente y separados por operador.")

USER = st.session_state.user["name"]

# --- 5. CABECERA / BIENVENIDA ---
_df_home = load_entries(USER)
_total = len(_df_home)
_ultima = _df_home.iloc[0]["fecha"] if _total > 0 else "Sin registros aún"

st.markdown(f"""
<div class="hero-card">
    <div>
        <div class="hero-eyebrow">MorphAI · Panel de rendimiento</div>
        <p class="hero-title">Hola, {USER.title()} 👋</p>
        <p class="hero-sub">Elige un módulo en el menú lateral — registra un set, corre el reloj de rounds, o pide a la IA que mejore tu rutina. Todo se guarda solo.</p>
    </div>
    <div class="hero-badge">SESIONES REGISTRADAS: {_total}<br>ÚLTIMA ACTIVIDAD: {_ultima}</div>
</div>
""", unsafe_allow_html=True)

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
        st.info("Todavía no hay datos que graficar. Registra tu primer set en '🏋️ Fuerza & Logística' o tu primera carrera en '🏃 Running Telemetry' — aparecerá aquí al instante.")

# --- FOOTER ---
st.markdown("---")
st.markdown(f"**MORPHAI NEURAL PERFORMANCE OS** | Operador: **{USER}** | © 2026 Josías Martínez")
