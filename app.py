# =================================================================
# PROJECT: MORPHAI NEURAL PERFORMANCE OS (v18.0 - APEX EDITION)
# AUTHOR: JOSIAS MARTINEZ & AI CO-ARCHITECT
# =================================================================

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import base64
import time
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

try:
    import anthropic
    ANTHROPIC_OK = True
except ImportError:
    ANTHROPIC_OK = False

# --- 1. CONFIGURACIÓN DE NÚCLEO ---
st.set_page_config(
    page_title="MorphAI OS v18.0 | Apex Edition",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. BASE DE DATOS (PERSISTENCIA REAL AMPLIADA) ---
DB_PATH = "morphai.db"

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    # Tabla de entrenamientos y actividad
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT, fecha TEXT, tipo TEXT, actividad TEXT,
            valor REAL, meta TEXT, extra TEXT
        )
    """)
    # Tabla de composición corporal
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT, fecha TEXT, peso REAL, grasa REAL, nota TEXT
        )
    """)
    # NUEVO: Tabla de Neural Readiness (Sueño, Fatiga, HRV)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readiness (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT, fecha TEXT, sueno_hrs REAL, calidad_sueno INTEGER,
            doms INTEGER, estres INTEGER, hrv INTEGER, score REAL, nota TEXT
        )
    """)
    # NUEVO: Tabla de Nutrición e Hidratación
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nutrition (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT, fecha TEXT, calorias INTEGER, proteina INTEGER,
            carbs INTEGER, grasa INTEGER, agua_l REAL
        )
    """)
    conn.commit()
    return conn

conn = init_db()

# --- FUNCIONES DE ACCESO A DATOS ---
def save_metric(user, peso, grasa, nota):
    conn.execute("INSERT INTO metrics (user, fecha, peso, grasa, nota) VALUES (?,?,?,?,?)",
                 (user, datetime.now().strftime("%Y-%m-%d %H:%M"), peso, grasa, nota))
    conn.commit()

def load_metrics(user):
    return pd.read_sql_query("SELECT * FROM metrics WHERE user=? ORDER BY id", conn, params=(user,))

def save_entry(user, tipo, actividad, valor, meta, extra):
    conn.execute("INSERT INTO entries (user, fecha, tipo, actividad, valor, meta, extra) VALUES (?,?,?,?,?,?,?)",
                 (user, datetime.now().strftime("%Y-%m-%d %H:%M"), tipo, actividad, valor, meta, extra))
    conn.commit()

def load_entries(user):
    return pd.read_sql_query("SELECT * FROM entries WHERE user=? ORDER BY id DESC", conn, params=(user,))

def save_readiness(user, sueno, calidad, doms, estres, hrv, score, nota):
    conn.execute("INSERT INTO readiness (user, fecha, sueno_hrs, calidad_sueno, doms, estres, hrv, score, nota) VALUES (?,?,?,?,?,?,?,?,?)",
                 (user, datetime.now().strftime("%Y-%m-%d %H:%M"), sueno, calidad, doms, estres, hrv, score, nota))
    conn.commit()

def load_readiness(user):
    return pd.read_sql_query("SELECT * FROM readiness WHERE user=? ORDER BY id DESC", conn, params=(user,))

def save_nutrition(user, cal, prot, carbs, grasa, agua):
    conn.execute("INSERT INTO nutrition (user, fecha, calorias, proteina, carbs, grasa, agua_l) VALUES (?,?,?,?,?,?,?)",
                 (user, datetime.now().strftime("%Y-%m-%d %H:%M"), cal, prot, carbs, grasa, agua))
    conn.commit()

def load_nutrition(user):
    return pd.read_sql_query("SELECT * FROM nutrition WHERE user=? ORDER BY id DESC", conn, params=(user,))

def delete_record(table, record_id, user):
    conn.execute(f"DELETE FROM {table} WHERE id=? AND user=?", (record_id, user))
    conn.commit()

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
        --red: #ff4b4b;
        --red-soft: rgba(255, 75, 75, 0.12);
        --text-hi: #eef2f0;
        --text-mid: #9aa8a2;
        --text-low: #5e6b66;
    }

    .stApp { background: var(--bg-0); color: var(--text-hi); font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }

    .hero-card {
        background: linear-gradient(160deg, var(--bg-1) 0%, var(--panel) 100%);
        border: 1px solid var(--line); border-radius: 16px; padding: 28px 32px;
        margin-bottom: 28px; display: flex; justify-content: space-between;
        align-items: center; flex-wrap: wrap; gap: 16px;
    }
    .hero-eyebrow { font-family: 'JetBrains Mono', monospace; color: var(--signal); font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 6px; }
    .hero-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.9rem; font-weight: 700; color: var(--text-hi); margin: 0; }
    .hero-sub { color: var(--text-mid); font-size: 0.92rem; margin-top: 4px; }
    .hero-badge {
        font-family: 'JetBrains Mono', monospace; background: var(--signal-soft); border: 1px solid var(--line);
        color: var(--signal); padding: 10px 16px; border-radius: 10px; font-size: 0.8rem; text-align: right; line-height: 1.5;
    }

    .module-container { background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 26px; margin-bottom: 22px; }

    .timer-display {
        font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 5.5rem;
        text-align: center; padding: 40px; border-radius: 18px; border: 2px solid var(--amber);
        color: var(--amber); background: var(--amber-soft); letter-spacing: 4px;
    }
    .work-active { border-color: var(--signal) !important; color: var(--signal) !important; background: var(--signal-soft) !important; }

    .ia-card { background: var(--panel); border: 1px solid var(--line); border-left: 3px solid var(--signal); border-radius: 14px; padding: 26px; white-space: pre-wrap; color: var(--text-hi); line-height: 1.6; }
    .ia-tag { color: var(--signal); font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; letter-spacing: 1.5px; text-transform: uppercase; border-bottom: 1px solid var(--line); margin-bottom: 14px; padding-bottom: 10px; }
    .rm-giant { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 3.6rem; color: var(--signal); text-align: center; margin: 0; }
    
    .readiness-box { padding: 20px; border-radius: 12px; text-align: center; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 2rem; margin-bottom: 15px; }
    .readiness-high { background: var(--signal-soft); color: var(--signal); border: 1px solid var(--signal); }
    .readiness-mid { background: var(--amber-soft); color: var(--amber); border: 1px solid var(--amber); }
    .readiness-low { background: var(--red-soft); color: var(--red); border: 1px solid var(--red); }

    section[data-testid="stSidebar"] { background: var(--bg-1); border-right: 1px solid var(--line); }
    </style>
""", unsafe_allow_html=True)

DB_EXERCISES = {
    "Pecho": ["Press Banca Plano", "Press Banca Inclinado", "Press Mancuernas", "Aperturas Polea", "Fondos en Paralelas", "Press Declinado"],
    "Espalda": ["Dominadas Pro", "Remo Pendlay", "Remo con Mancuerna", "Jalón al Pecho", "Peso Muerto Convencional", "Remo en T"],
    "Piernas": ["Sentadilla Barra", "Peso Muerto Sumó", "Prensa 45°", "Zancadas Búlgaras", "Curl Femoral", "Extensión Cuádriceps", "Hip Thrust"],
    "Hombros": ["Press Militar", "Elevaciones Laterales", "Pájaros Posteriores", "Press Arnold", "Face Pull"],
    "Brazos": ["Curl Barra Z", "Curl Martillo", "Press Francés", "Fondos Tríceps", "Curl Predicador"],
    "Core": ["Plancha Frontal", "Rueda Abdominal", "Elevación de Piernas", "Russian Twist", "Plancha Lateral"],
    "Explosividad": ["Saltos al Cajón", "Landmine Punch", "Medball Slam", "Burpee Pliométrico", "Snatch con Mancuerna", "Sprints Potencia", "Kettlebell Swing"],
    "Calistenia": ["Muscle Up", "Pistol Squat", "Handstand Push-up", "Front Lever (progresión)", "Human Flag (progresión)"],
    "Running": ["Carrera Continua", "Series VO2 Max", "Fartlek Neural", "Umbral Lactato", "Trote Regenerativo", "Cuestas Cortas"],
    "Movilidad": ["Movilidad de Cadera", "Movilidad Torácica", "Estiramiento Isquiotibiales", "Foam Rolling Espalda", "Movilidad de Hombro", "Respiración Diafragmática"]
}

DB_EXERCISE_INFO = {
    "Sentadilla Barra": ("Cuádriceps, glúteos, core", "Barra libre en espalda alta, baja controlando la rodilla en línea con el pie."),
    "Peso Muerto Sumó": ("Glúteos, isquiotibiales, espalda baja", "Postura ancha, espalda neutra, empuja el piso con los talones."),
    "Peso Muerto Convencional": ("Cadena posterior completa", "Barra pegada a la tibia, cadera arriba antes que el pecho."),
    "Press Banca Plano": ("Pectoral, tríceps, hombro anterior", "Escápulas retraídas, barra baja al esternón con control."),
    "Dominadas Pro": ("Dorsal ancho, bíceps", "Agarre prono, tira con el codo hacia la cadera."),
    "Press Militar": ("Hombro, tríceps, core", "De pie, evita arquear la espalda baja al empujar."),
    "Hip Thrust": ("Glúteo mayor", "Espalda apoyada en banco, empuje con talones, aprieta glúteo arriba."),
    "Muscle Up": ("Dorsal, tríceps, core", "Transición explosiva de dominada a fondo, requiere buena base de fuerza en ambos."),
    "Kettlebell Swing": ("Cadena posterior, potencia de cadera", "El impulso viene de la cadera, no de los brazos."),
    "Plancha Frontal": ("Core, estabilidad lumbar", "Cuerpo en línea recta, glúteos y abdomen activos."),
    "Movilidad de Cadera": ("Flexores de cadera, rotadores", "Series de 90/90 y círculos controlados, sin rebotes."),
}

if 'user' not in st.session_state:
    st.session_state['user'] = {"name": "JOSIAS MARTINEZ", "weight": 80, "height": 180, "age": 28}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown('<h1 style="font-family:Space Grotesk; color:#35d68c; letter-spacing:2px; font-size:1.6rem;">MORPHAI OS</h1>', unsafe_allow_html=True)
    st.session_state.user["name"] = st.text_input("OPERADOR:", st.session_state.user["name"]).upper()

    st.divider()
    system_mode = st.radio("SISTEMA:", [
        "🧠 NEURAL READINESS & SUEÑO",
        "🏋️ ENTRENAMIENTO DE FUERZA",
        "🏃 RUNNING TELEMETRY",
        "🥊 COMBATE & EXPLOSIVIDAD",
        "🧘 MOVILIDAD & RECUPERACIÓN",
        "🍎 NUTRICIÓN & MACROS",
        "📚 BIBLIOTECA DE EJERCICIOS",
        "🎯 OBJETIVOS & RACHA",
        "🤖 AI ROUTINE COACH",
        "📊 ANALÍTICA GLOBAL",
        "🛠️ GESTIÓN DE DATOS & BACKUP"
    ])

    st.divider()
    st.caption("🔒 v18.0 Apex | Encriptación y persistencia nativa SQLite activa.")

USER = st.session_state.user["name"]

# --- 5. CABECERA / BIENVENIDA ---
_df_home = load_entries(USER)
_total = len(_df_home)
_ultima = _df_home.iloc[0]["fecha"] if _total > 0 else "Sin registros aún"

# Calcular Readiness actual para mostrar en el Header
_df_readiness = load_readiness(USER)
_readiness_val = f"{_df_readiness.iloc[0]['score']:.0f}%" if not _df_readiness.empty else "N/A"

st.markdown(f"""
<div class="hero-card">
    <div>
        <div class="hero-eyebrow">MorphAI · Telemetría y Rendimiento v18.0</div>
        <p class="hero-title">Hola, {USER.title()} 👋</p>
        <p class="hero-sub">Sistema Neural Activo. Selecciona un módulo en el menú lateral para gestionar tu día atlético.</p>
    </div>
    <div class="hero-badge">SESIONES: {_total} | READINESS: {_readiness_val}<br>ÚLTIMA ACTIVIDAD: {_ultima}</div>
</div>
""", unsafe_allow_html=True)

# =================================================================
# MÓDULO 1: NEURAL READINESS & SUEÑO (NUEVO)
# =================================================================
if system_mode == "🧠 NEURAL READINESS & SUEÑO":
    st.markdown("### 🧠 Evaluación Diaria del Sistema Nervioso (Readiness)")
    st.caption("El sobreentrenamiento destruye el progreso. Mide tu fatiga y HRV antes de cargar la barra.")
    
    c1, c2 = st.columns([1, 1])
    with c1:
        with st.form("f_readiness", clear_on_submit=True):
            sueno = st.number_input("Horas de sueño anoche", 1.0, 14.0, 7.5, 0.5)
            calidad = st.slider("Calidad del sueño (1: Pésimo, 10: Óptimo)", 1, 10, 8)
            doms = st.slider("Dolor muscular / DOMS (1: Ninguno, 10: Dolor extremo)", 1, 10, 3)
            estres = st.slider("Nivel de estrés general/mental (1: Relajado, 10: Alto estrés)", 1, 10, 4)
            hrv = st.number_input("HRV matutino (ms, opcional, 0 si no lo mides)", 0, 200, 65)
            nota_r = st.text_input("Nota del estado matutino", "Buen descanso")
            
            if st.form_submit_button("CALCULAR & GUARDAR READINESS"):
                # Algoritmo heurístico de disposición neural (0-100%)
                score = (sueno / 8.0 * 30) + (calidad * 3) + ((11 - doms) * 2.5) + ((11 - estres) * 1.5)
                if hrv > 0: score = (score * 0.8) + (min(hrv / 80.0 * 20, 20))
                score = min(max(score, 10), 100)
                
                save_readiness(USER, sueno, calidad, doms, estres, hrv, score, nota_r)
                st.success(f"Readiness registrado: {score:.1f}%")
                st.rerun()

    with c2:
        df_r = load_readiness(USER)
        if not df_r.empty:
            last_score = df_r.iloc[0]['score']
            if last_score >= 80:
                box_class, status, advice = "readiness-high", "🟢 ÓPTIMO PARA RÓMPER PRs", "Tu sistema nervioso está fresco. Es el día perfecto para máxima intensidad (RPE 9-10) o cargas pesadas."
            elif last_score >= 60:
                box_class, status, advice = "readiness-mid", "🟡 ESTADO NEUTRO / NORMAL", "Entrena según lo planificado. Mantén el volumen de trabajo habitual (RPE 7-8). Escucha a tu cuerpo."
            else:
                box_class, status, advice = "readiness-low", "🔴 ALERTA: FATIGA CENTRAL", "Altas probabilidades de sobreentrenamiento o lesión. Se recomienda sesión de movilidad, cardio suave Z1 o descanso total."
            
            st.markdown(f'<div class="readiness-box {box_class}">READINESS: {last_score:.0f}%<br><span style="font-size:1rem;">{status}</span></div>', unsafe_allow_html=True)
            st.info(f"💡 **Recomendación táctica:** {advice}")
            
            st.divider()
            fig_r = px.line(df_r.head(14).sort_values("id"), x="fecha", y="score", markers=True, template="plotly_dark", title="Tendencia de Readiness (Últimos 14 registros)")
            fig_r.update_traces(line_color="#35d68c")
            st.plotly_chart(fig_r, use_container_width=True)
        else:
            st.info("Registra tu primer check-in matutino para calibrar tu algoritmo de entrenamiento.")

# =================================================================
# MÓDULO 2: ENTRENAMIENTO DE FUERZA (MEJORADO CON RIR Y TONELAJE)
# =================================================================
elif system_mode == "🏋️ ENTRENAMIENTO DE FUERZA":
    grupos_fuerza = ["Pecho", "Espalda", "Piernas", "Hombros", "Brazos", "Core", "Calistenia"]
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("### 📥 Registro de Set")
        grupo = st.selectbox("Grupo muscular", grupos_fuerza)
        with st.form("f_gym", clear_on_submit=True):
            ejer = st.selectbox("Ejercicio", DB_EXERCISES[grupo])
            c_p, c_r, c_rir = st.columns(3)
            peso = c_p.number_input("Carga (kg)", 0.0, 500.0, 40.0, 2.5)
            reps = c_r.number_input("Reps", 1, 50, 10)
            rir = c_rir.number_input("RIR (Reserva)", 0, 5, 2, help="Repeticiones que sentiste que podías haber hecho antes del fallo.")
            rpe = 10 - rir
            
            if st.form_submit_button("REGISTRAR SET"):
                tonelaje = peso * reps
                save_entry(USER, f"Fuerza-{grupo}", ejer, tonelaje, f"{peso}kg x {reps} (RIR {rir})", f"RPE {rpe}")
                st.success(f"Set de {ejer} guardado. Tonelaje: {tonelaje} kg.")
                
        info = DB_EXERCISE_INFO.get(ejer)
        if info: st.caption(f"💡 **Trabaja:** {info[0]} — {info[1]}")

        st.divider()
        st.markdown(f"#### 📜 Historial — {ejer}")
        df_ejer = load_entries(USER)
        df_ejer = df_ejer[df_ejer["actividad"] == ejer] if not df_ejer.empty else df_ejer
        if not df_ejer.empty:
            pr = df_ejer["valor"].max()
            pr_row = df_ejer[df_ejer["valor"] == pr].iloc[0]
            st.metric("🏆 Récord de Tonelaje (Carga × Reps)", f"{pr:.0f} kg", help=f"Logrado el {pr_row['fecha']}")
            st.dataframe(df_ejer[["fecha", "meta", "extra"]].head(5), use_container_width=True, hide_index=True)
        else:
            st.caption("Aún no tienes sets registrados de este ejercicio. Este será tu primer PR.")

    with c2:
        st.markdown("### 🧮 Estimación 1RM (Algoritmo Brzycki)")
        p_rm = st.number_input("Peso para cálculo", 1.0, 500.0, float(peso) if 'peso' in locals() else 100.0)
        r_rm = st.number_input("Reps para cálculo", 1, 12, int(reps) if 'reps' in locals() else 5)
        res_rm = p_rm / (1.0278 - (0.0278 * r_rm)) if r_rm < 37 else p_rm
        st.markdown(f'<p class="rm-giant">{round(res_rm, 1)} KG</p>', unsafe_allow_html=True)
        
        st.divider()
        st.write("**Zonas de intensidad sugeridas:**")
        st.write(f"🔴 **95% (Máxima Fuerza):** {round(res_rm*0.95,1)} kg · 🟠 **85% (Fuerza):** {round(res_rm*0.85,1)} kg · 🟢 **70% (Hipertrofia):** {round(res_rm*0.7,1)} kg")

        st.divider()
        st.markdown("#### 🔥 Series de calentamiento sugeridas")
        st.write(f"1. Barra vacía / Ligero × 12 reps (Movilidad y activación)")
        st.write(f"2. {round(res_rm*0.4,1)} kg × 8 reps (Aproximación)")
        st.write(f"3. {round(res_rm*0.6,1)} kg × 4 reps (Preparación del SNC)")
        st.write(f"4. {round(res_rm*0.8,1)} kg × 1 rep (Potenciación Post-Tetánica)")

# =================================================================
# MÓDULO 3: RUNNING TELEMETRY
# =================================================================
elif system_mode == "🏃 RUNNING TELEMETRY":
    c_run1, c_run2 = st.columns(2)
    with c_run1:
        st.markdown("### 🏃 Registro de Resistencia")
        with st.form("f_run", clear_on_submit=True):
            tipo_r = st.selectbox("Tipo de Estímulo", DB_EXERCISES["Running"])
            dist = st.number_input("Distancia (km)", 0.1, 100.0, 5.0, 0.5)
            m_r = st.number_input("Minutos", 1, 500, 25)
            hr = st.slider("BPM Medio", 60, 220, 145)
            peso_run = st.session_state.user.get("weight", 75)
            
            if st.form_submit_button("GUARDAR RUN"):
                pace = m_r / dist
                pace_str = f"{int(pace)}:{int((pace%1)*60):02d} min/km"
                save_entry(USER, "Running", tipo_r, dist, pace_str, f"{hr} BPM")
                st.success("Carrera guardada permanentemente.")

        st.divider()
        st.markdown("#### 📜 Últimas carreras")
        df_run = load_entries(USER)
        df_run = df_run[df_run["tipo"] == "Running"] if not df_run.empty else df_run
        if not df_run.empty:
            st.dataframe(df_run[["fecha", "actividad", "valor", "meta", "extra"]].head(5)
                         .rename(columns={"valor": "km", "meta": "pace", "extra": "BPM"}),
                         use_container_width=True, hide_index=True)
        else:
            st.caption("Aún no registras carreras. La primera aparecerá aquí.")

    with c_run2:
        st.markdown("### 📐 Zonas de ritmo (Karvonen simplificado)")
        pb_min = st.number_input("Tu mejor tiempo en 5K (minutos)", 10.0, 60.0, 25.0, 0.5)
        pb_pace = pb_min / 5.0
        st.write(f"**Pace de referencia (5K):** {int(pb_pace)}:{int((pb_pace%1)*60):02d} min/km")
        st.divider()
        zonas = {
            "🟢 Z1 Recuperación": pb_pace * 1.4,
            "🔵 Z2 Base aeróbica": pb_pace * 1.25,
            "🟡 Z3 Tempo": pb_pace * 1.1,
            "🟠 Z4 Umbral": pb_pace * 1.03,
            "🔴 Z5 VO2 Max": pb_pace * 0.95,
        }
        for zona, p in zonas.items():
            st.write(f"**{zona}:** {int(p)}:{int((p%1)*60):02d} min/km")

        st.divider()
        cal = round(dist * peso_run * 1.036) if 'dist' in locals() else 0
        st.metric("🔥 Calorías estimadas (última carrera)", f"{cal} kcal")
        st.caption("Estimación metabólica aproximada (MET running ≈ 1.036 kcal/kg/km).")

# =================================================================
# MÓDULO 4: COMBATE & EXPLOSIVIDAD
# =================================================================
elif system_mode == "🥊 COMBATE & EXPLOSIVIDAD":
    st.subheader("⏱️ Temporizador Táctico de Combate")

    preset = st.radio("Preset rápido", ["Personalizado", "Tabata Clásico (8x20/10)", "Boxeo Amateur (3x180/60)", "HIIT Largo (5x240/60)"], horizontal=True)
    presets_map = {
        "Tabata Clásico (8x20/10)": (8, 20/60, 10),
        "Boxeo Amateur (3x180/60)": (3, 3, 60),
        "HIIT Largo (5x240/60)": (5, 4, 60),
    }

    t_c1, t_c2, t_c3 = st.columns(3)
    if preset in presets_map:
        d_rds, d_wt, d_rt = presets_map[preset]
        rds = t_c1.number_input("Rounds", 1, 15, d_rds)
        w_t = t_c2.number_input("Trabajo (min)", 0.1, 5.0, float(d_wt))
        r_t = t_c3.number_input("Descanso (seg)", 5, 90, d_rt)
    else:
        rds = t_c1.number_input("Rounds", 1, 15, 3)
        w_t = t_c2.number_input("Trabajo (min)", 0.1, 5.0, 3.0)
        r_t = t_c3.number_input("Descanso (seg)", 5, 90, 30)

    if st.button("🔔 INICIAR ROUNDS"):
        ph = st.empty()
        for r in range(1, rds + 1):
            for t in range(int(w_t * 60), 0, -1):
                ph.markdown(f'<div class="timer-display work-active">ROUND {r}<br>{t//60:02d}:{t%60:02d}</div>', unsafe_allow_html=True)
                time.sleep(1)
            if r < rds:
                for t in range(r_t, 0, -1):
                    ph.markdown(f'<div class="timer-display">REST<br>00:{t:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
        ph.success("🔥 COMBATE FINALIZADO CON ÉXITO")
        save_entry(USER, "Combate-Rounds", preset, rds, f"{rds} rounds", f"{w_t}min trabajo / {r_t}s desc.")

    st.divider()
    st.subheader("⚡ Biblioteca de Explosividad y Potencia")
    with st.form("f_ex", clear_on_submit=True):
        ej_ex = st.selectbox("Ejercicio de Potencia", DB_EXERCISES["Explosividad"])
        reps_ex = st.slider("Reps Explosivas", 1, 30, 6)
        lastre = st.number_input("Lastre Extra (kg)", 0, 100, 0)
        if st.form_submit_button("REGISTRAR POTENCIA"):
            save_entry(USER, "Combate", ej_ex, reps_ex, f"{reps_ex} reps", f"{lastre}kg Lastre")
            st.success("Registro guardado permanentemente.")

    df_comb = load_entries(USER)
    df_comb = df_comb[df_comb["tipo"].str.startswith("Combate")] if not df_comb.empty else df_comb
    if not df_comb.empty:
        st.markdown("#### 📜 Historial reciente")
        st.dataframe(df_comb[["fecha", "actividad", "meta", "extra"]].head(5), use_container_width=True, hide_index=True)

# =================================================================
# MÓDULO 5: MOVILIDAD & RECUPERACIÓN
# =================================================================
elif system_mode == "🧘 MOVILIDAD & RECUPERACIÓN":
    st.markdown("### 🧘 Sesión de Movilidad y Regeneración")
    st.caption("La recuperación también es entrenamiento. Registra tus sesiones de movilidad y recuperación activa.")
    c1, c2 = st.columns([1, 1])
    with c1:
        with st.form("f_mov", clear_on_submit=True):
            mov = st.selectbox("Ejercicio de movilidad", DB_EXERCISES["Movilidad"])
            dur = st.slider("Duración (minutos)", 1, 60, 10)
            sensacion = st.select_slider("Sensación al terminar", options=["Tenso", "Normal", "Suelto", "Óptimo"])
            if st.form_submit_button("REGISTRAR SESIÓN"):
                save_entry(USER, "Movilidad", mov, dur, f"{dur} min", sensacion)
                st.success(f"Sesión de {mov} guardada.")
        info = DB_EXERCISE_INFO.get(mov)
        if info: st.caption(f"💡 **Enfoque:** {info[0]} — {info[1]}")
    with c2:
        st.markdown("#### 🔄 Rutina rápida sugerida (5 min)")
        st.write("1. **Movilidad de Cadera:** 60s por lado")
        st.write("2. **Movilidad Torácica:** 60s en rodillas")
        st.write("3. **Estiramiento Isquiotibiales:** 60s por lado")
        st.write("4. **Movilidad de Hombro:** 60s con banda o pica")
        st.write("5. **Respiración Diafragmática:** 60s (SNC Downregulation)")
        st.info("Ideal antes de entrenar o como cierre de un día de descanso.")

# =================================================================
# MÓDULO 6: NUTRICIÓN & MACROS (NUEVO)
# =================================================================
elif system_mode == "🍎 NUTRICIÓN & MACROS":
    st.markdown("### 🍎 Motor Metabólico & Gestión de Combustible")
    st.caption("El rendimiento deportivo requiere precisión calórica e hidratación óptima.")
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### 🧮 Calculadora TDEE y Objetivos")
        peso_act = st.number_input("Tu peso actual (kg)", 40.0, 160.0, float(st.session_state.user["weight"]))
        altura_act = st.number_input("Altura (cm)", 140, 220, int(st.session_state.user["height"]))
        edad_act = st.number_input("Edad", 15, 80, int(st.session_state.user["age"]))
        actividad = st.selectbox("Nivel de Actividad Física", [
            "Sedentario (Poco o ningún ejercicio)",
            "Ligero (1-3 días/semana)",
            "Moderado (3-5 días/semana)",
            "Intenso (6-7 días/semana)",
            "Atleta de Élite (Dobles sesiones)"
        ], index=2)
        
        mult_map = {
            "Sedentario (Poco o ningún ejercicio)": 1.2,
            "Ligero (1-3 días/semana)": 1.375,
            "Moderado (3-5 días/semana)": 1.55,
            "Intenso (6-7 días/semana)": 1.725,
            "Atleta de Élite (Dobles sesiones)": 1.9
        }
        
        # Harris-Benedict simplificado para hombres/general atleta
        tmb = 10 * peso_act + 6.25 * altura_act - 5 * edad_act + 5
        tdee = tmb * mult_map[actividad]
        
        st.metric("🔥 Calorías de Mantenimiento (TDEE)", f"{tdee:.0f} kcal/día")
        st.write(f"📉 **Déficit (Perder grasa):** {tdee-500:.0f} kcal | 📈 **Superávit (Ganar masa):** {tdee+300:.0f} kcal")
        st.write(f"💧 **Meta de Hidratación Recomendada:** {(peso_act * 0.04):.1f} Litros/día")

    with c2:
        st.markdown("#### 📥 Registro Diario de Ingesta")
        with st.form("f_nutricion", clear_on_submit=True):
            cal_in = st.number_input("Calorías totales ingeridas", 0, 10000, 2500, 50)
            prot_in = st.number_input("Proteínas (g)", 0, 500, 160, 5)
            carb_in = st.number_input("Carbohidratos (g)", 0, 1000, 250, 10)
            fat_in = st.number_input("Grasas (g)", 0, 300, 70, 5)
            agua_in = st.number_input("Agua consumida (Litros)", 0.0, 10.0, 3.0, 0.25)
            
            if st.form_submit_button("GUARDAR MACROS DEL DÍA"):
                save_nutrition(USER, cal_in, prot_in, carb_in, fat_in, agua_in)
                st.success("Ingesta registrada en el historial metabólico.")
                
        df_nut = load_nutrition(USER)
        if not df_nut.empty:
            st.markdown("#### 📜 Historial Nutricional Reciente")
            st.dataframe(df_nut[["fecha", "calorias", "proteina", "carbs", "grasa", "agua_l"]].head(5)
                         .rename(columns={"calorias": "Kcal", "proteina": "Prot(g)", "carbs": "Carbs(g)", "grasa": "Grasa(g)", "agua_l": "Agua(L)"}),
                         use_container_width=True, hide_index=True)

# =================================================================
# MÓDULO 7: BIBLIOTECA DE EJERCICIOS
# =================================================================
elif system_mode == "📚 BIBLIOTECA DE EJERCICIOS":
    st.markdown("### 📚 Biblioteca de Ejercicios y Biomecánica")
    total_ejercicios = sum(len(v) for v in DB_EXERCISES.values())
    st.caption(f"Consulta técnica y grupo muscular de cada ejercicio disponible en la app · **{total_ejercicios} ejercicios** en {len(DB_EXERCISES)} categorías.")

    if 'favoritos' not in st.session_state:
        st.session_state['favoritos'] = set()

    categorias = list(DB_EXERCISES.keys())
    cat_sel = st.selectbox("Categoría", categorias)
    busqueda = st.text_input("🔍 Buscar ejercicio por nombre")
    solo_fav = st.checkbox("⭐ Mostrar solo favoritos")

    lista = DB_EXERCISES[cat_sel]
    if busqueda: lista = [e for e in lista if busqueda.lower() in e.lower()]
    if solo_fav: lista = [e for e in lista if e in st.session_state['favoritos']]

    if not lista: st.info("No se encontraron ejercicios con esos filtros.")
    for ej in lista:
        info = DB_EXERCISE_INFO.get(ej, ("Consulta con tu entrenador", "Aún no hay descripción técnica cargada para este ejercicio."))
        col_a, col_b = st.columns([6, 1])
        with col_a:
            st.markdown(f"**{ej}**")
            st.caption(f"🎯 Grupo: {info[0]}")
            st.caption(f"📝 Técnica: {info[1]}")
        with col_b:
            es_fav = ej in st.session_state['favoritos']
            if st.button("⭐" if es_fav else "☆", key=f"fav_{ej}"):
                if es_fav: st.session_state['favoritos'].discard(ej)
                else: st.session_state['favoritos'].add(ej)
                st.rerun()
        st.divider()

# =================================================================
# MÓDULO 8: OBJETIVOS & RACHA (MEJORADO CON LOGROS)
# =================================================================
elif system_mode == "🎯 OBJETIVOS & RACHA":
    st.markdown("### 🎯 Objetivos, Racha y Medallas")
    df_all = load_entries(USER)

    fechas = pd.to_datetime(df_all["fecha"]).dt.date.unique() if not df_all.empty else []
    racha = 0
    if len(fechas) > 0:
        dia = datetime.now().date()
        fechas_set = set(fechas)
        while dia in fechas_set:
            racha += 1
            dia = date.fromordinal(dia.toordinal() - 1)

    c1, c2, c3 = st.columns(3)
    c1.metric("🔥 Racha actual", f"{racha} días")
    c2.metric("📦 Sesiones totales", len(df_all))
    meta_semanal = st.number_input("Meta semanal (sesiones)", 1, 14, 4)
    hoy = datetime.now().date()
    semana = [d for d in fechas if (hoy - d).days < 7]
    c3.metric("✅ Esta semana", f"{len(semana)}/{meta_semanal}")
    st.progress(min(len(semana) / meta_semanal, 1.0))

    st.divider()
    st.markdown("#### 🏅 Sistema de Logros del Operador")
    b1, b2, b3, b4 = st.columns(4)
    b1.info(f"🏆 **Iniciado**\n\n{'✅ Desbloqueado' if len(df_all) >= 1 else '🔒 Regístrate 1 vez'}")
    b2.info(f"🔥 **Constante**\n\n{'✅ Desbloqueado' if racha >= 3 else f'🔒 Racha de 3 días ({racha}/3)'}")
    b3.info(f"⚡ **Imparable**\n\n{'✅ Desbloqueado' if len(df_all) >= 25 else f'🔒 25 sesiones ({len(df_all)}/25)'}")
    b4.info(f"🧬 **Atleta Élite**\n\n{'✅ Desbloqueado' if len(df_all) >= 100 else f'🔒 100 sesiones ({len(df_all)}/100)'}")

    st.divider()
    st.markdown("### ⚖️ Registro Corporal")
    with st.form("f_metric", clear_on_submit=True):
        cm1, cm2, cm3, cm4 = st.columns(4)
        peso_m = cm1.number_input("Peso (kg)", 30.0, 250.0, float(st.session_state.user["weight"]), 0.1)
        grasa_m = cm2.number_input("% Grasa (opcional)", 0.0, 60.0, 15.0, 0.5)
        cintura_m = cm3.number_input("Cintura (cm, opcional)", 0.0, 200.0, 80.0, 0.5)
        brazo_m = cm4.number_input("Brazo (cm, opcional)", 0.0, 80.0, 38.0, 0.5)
        nota_m = st.text_input("Nota", "")
        if st.form_submit_button("GUARDAR MEDICIÓN"):
            nota_completa = f"{nota_m} | Cintura:{cintura_m}cm Brazo:{brazo_m}cm".strip(" |")
            save_metric(USER, peso_m, grasa_m, nota_completa)
            st.session_state.user["weight"] = peso_m
            st.success("Medición guardada.")

    df_metrics = load_metrics(USER)
    if not df_metrics.empty:
        fig_m = px.line(df_metrics, x="fecha", y="peso", markers=True, template="plotly_dark", title="Evolución de Peso Corporal (kg)")
        fig_m.update_traces(line_color="#35d68c")
        st.plotly_chart(fig_m, use_container_width=True)
        with st.expander("Ver historial completo de mediciones"):
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)
    else:
        st.info("Registra tu primera medición para ver tu evolución de peso aquí.")

# =================================================================
# MÓDULO 9: AI ROUTINE COACH
# =================================================================
elif system_mode == "🤖 AI ROUTINE COACH":
    st.markdown("### 🤖 AI Routine Coach")
    st.caption("Describe tu rutina actual en texto y/o sube una foto. La IA la analizará biomecánicamente y propondrá una versión mejorada.")

    if not ANTHROPIC_OK:
        st.error("Falta instalar el paquete `anthropic`. Agrega `anthropic` a tu requirements.txt.")

    api_key = st.text_input("Anthropic API Key", type="password", help="Consíguela en console.anthropic.com. No se guarda en servidores externos.")

    objetivo = st.selectbox("Objetivo principal", ["Hipertrofia", "Fuerza máxima", "Pérdida de grasa", "Resistencia / Híbrido"])
    nivel = st.select_slider("Nivel", options=["Principiante", "Intermedio", "Avanzado"])
    dias_disp = st.slider("Días disponibles por semana", 1, 7, 4)

    st.markdown("**Preguntas rápidas de contexto:**")
    qc1, qc2, qc3 = st.columns(3)
    lesion = qc1.selectbox("¿Alguna molestia/lesión?", ["Ninguna", "Hombro", "Rodilla", "Espalda baja", "Otra"])
    equipo = qc2.selectbox("Equipo disponible", ["Gym completo", "Mancuernas/casa", "Solo peso corporal"])
    tiempo_sesion = qc3.selectbox("Tiempo por sesión", ["30 min", "45 min", "60 min", "90+ min"])

    rutina_texto = st.text_area("Describe tu rutina actual (días, ejercicios, series/reps)", height=150)
    foto = st.file_uploader("O sube una foto de tu rutina o pizarra", type=["png", "jpg", "jpeg"])

    if st.button("🧠 ANALIZAR Y MEJORAR CON IA"):
        if not api_key:
            st.warning("Ingresa tu API key de Anthropic para continuar.")
        elif not rutina_texto and not foto:
            st.warning("Describe tu rutina en texto o sube una foto para poder analizarla.")
        else:
            with st.spinner("Analizando biomecánica y volumen con Claude AI..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    content = []
                    if foto is not None:
                        img_bytes = foto.read()
                        b64 = base64.b64encode(img_bytes).decode("utf-8")
                        media_type = "image/png" if foto.type == "image/png" else "image/jpeg"
                        content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}})
                    
                    prompt = (
                        f"Soy un atleta de nivel {nivel}, mi objetivo es {objetivo}. "
                        f"Dispongo de {dias_disp} días por semana, sesiones de {tiempo_sesion}, equipo: {equipo}. "
                        f"Molestia física a considerar: {lesion}. "
                        f"Esta es mi rutina actual: {rutina_texto or '(ver imagen adjunta)'}. "
                        "Actúa como un fisiólogo del ejercicio y entrenador de élite. Analiza la rutina, señala 2-3 puntos débiles concretos "
                        "(ej. balance de empuje/tirón, volumen basura o selección de ejercicios), y propón una versión mejorada "
                        "organizada por día, indicando series, reps, RIR sugerido y tiempos de descanso. Sé riguroso y breve."
                    )
                    content.append({"type": "text", "text": prompt})

                    # Usando modelo estándar actual
                    response = client.messages.create(
                        model="claude-3-7-sonnet-20250219",
                        max_tokens=1500,
                        messages=[{"role": "user", "content": content}]
                    )
                    resultado = "".join(block.text for block in response.content if block.type == "text")
                    st.session_state["ultimo_plan_ia"] = resultado
                except Exception as e:
                    st.error(f"Error en la comunicación con la IA: {e}")

    if "ultimo_plan_ia" in st.session_state:
        st.markdown(f'<div class="ia-card"><div class="ia-tag">🧬 PLAN MEJORADO POR IA</div>{st.session_state["ultimo_plan_ia"]}</div>', unsafe_allow_html=True)
        if st.button("💾 Guardar este plan en mi historial"):
            save_entry(USER, "IA-Plan", objetivo, 0, nivel, "Plan generado por IA")
            st.success("Plan guardado en tu historial exitosamente.")

    df_planes = load_entries(USER)
    df_planes = df_planes[df_planes["tipo"] == "IA-Plan"] if not df_planes.empty else df_planes
    if not df_planes.empty:
        with st.expander(f"📁 Historial de planes generados ({len(df_planes)})"):
            st.dataframe(df_planes[["fecha", "actividad", "meta"]].rename(columns={"actividad": "objetivo", "meta": "nivel"}), use_container_width=True, hide_index=True)

# =================================================================
# MÓDULO 10: ANALÍTICA GLOBAL
# =================================================================
elif system_mode == "📊 ANALÍTICA GLOBAL":
    df = load_entries(USER)
    if not df.empty:
        st.markdown("### 📈 Performance Telemetry")
        fig1 = px.line(df.sort_values("id"), x="fecha", y="valor", color="tipo", markers=True,
                       template="plotly_dark", title="Evolución de Carga / Volumen en el Tiempo")
        fig1.update_traces(line_color='#35d68c')
        st.plotly_chart(fig1, use_container_width=True)

        c_a1, c_a2 = st.columns(2)
        fig2 = px.pie(df, names='tipo', hole=0.6, title="Balance del Atleta por Módulo",
                      color_discrete_sequence=['#35d68c', '#00d4ff', '#ff4b4b', '#f5a623', '#a86bff'])
        c_a1.plotly_chart(fig2)

        fig3 = px.bar(df, x="actividad", y="valor", color="tipo", title="Volumen Acumulado por Ejercicio / Actividad")
        c_a2.plotly_chart(fig3)

        st.divider()
        st.markdown("### 🏆 Récords Personales (PRs Máximos)")
        prs = df.groupby("actividad")["valor"].max().sort_values(ascending=False).head(10)
        st.dataframe(prs.reset_index().rename(columns={"actividad": "Ejercicio/Actividad", "valor": "Mejor marca registrada"}),
                     use_container_width=True, hide_index=True)
    else:
        st.info("Todavía no hay datos que graficar. Registra tus entrenamientos para encender la telemetría.")

# =================================================================
# MÓDULO 11: GESTIÓN DE DATOS & BACKUP (NUEVO)
# =================================================================
elif system_mode == "🛠️ GESTIÓN DE DATOS & BACKUP":
    st.markdown("### 🛠️ Administración de Datos y Copias de Seguridad")
    st.caption("Gestiona tu base de datos local SQLite, exporta reportes para tu entrenador o elimina registros erróneos.")
    
    tab1, tab2 = st.tabs(["📦 Exportar Datos", "🗑️ Eliminar Registros Erróneos"])
    
    with tab1:
        st.write("Descarga tu historial completo en formato CSV compatible con Excel, Google Sheets y software de coaching.")
        df_export = load_entries(USER)
        if not df_export.empty:
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Historial de Entrenamientos (CSV)",
                data=csv,
                file_name=f"morphai_log_{USER.lower()}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.warning("No hay datos para exportar.")
            
    with tab2:
        st.write("Si cometiste un error en un registro anterior, búscalo por ID y bórralo de forma permanente.")
        df_all = load_entries(USER)
        if not df_all.empty:
            st.dataframe(df_all[["id", "fecha", "tipo", "actividad", "meta", "extra"]], use_container_width=True, hide_index=True)
            id_borrar = st.number_input("ID del registro a eliminar", min_value=1, step=1)
            if st.button("🗑️ ELIMINAR REGISTRO DEFINITIVAMENTE", type="primary"):
                delete_record("entries", id_borrar, USER)
                st.success(f"Registro ID {id_borrar} eliminado correctamente.")
                time.sleep(1)
                st.rerun()
        else:
            st.info("La base de datos está limpia.")

# --- FOOTER ---
st.markdown("---")
st.markdown(f"**MORPHAI NEURAL PERFORMANCE OS v18.0 APEX** | Operador Activo: **{USER}** | © 2026 Josías Martínez")
