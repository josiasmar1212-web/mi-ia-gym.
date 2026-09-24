# =================================================================
# PROJECT: MORPHAI NEURAL PERFORMANCE OS (v19.0 - APEX EDITION / DARK-ENERGY)
# AUTHOR: JOSIAS MARTINEZ & AI CO-ARCHITECT
# =================================================================
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import base64
import time
import hashlib
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
    page_title="MorphAI OS v19.0 | Apex Edition",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. BASE DE DATOS (PERSISTENCIA REAL AMPLIADA) ---
DB_PATH = "morphai.db"

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    # Tabla de usuarios (login / cuentas)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            weight REAL, height REAL, age INTEGER
        )
    """)
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
    # Tabla de Neural Readiness (Sueño, Fatiga, HRV)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readiness (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT, fecha TEXT, sueno_hrs REAL, calidad_sueno INTEGER,
            doms INTEGER, estres INTEGER, hrv INTEGER, score REAL, nota TEXT
        )
    """)
    # Tabla de Nutrición e Hidratación
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

# --- FUNCIONES DE CUENTA (LOGIN / REGISTRO) ---
def hash_pw(pw):
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def create_user(username, password, weight=75.0, height=175, age=25):
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, weight, height, age) VALUES (?,?,?,?,?)",
            (username, hash_pw(password), weight, height, age)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def check_user(username, password):
    row = conn.execute(
        "SELECT password_hash, weight, height, age FROM users WHERE username=?",
        (username,)
    ).fetchone()
    if row and row[0] == hash_pw(password):
        return {"weight": row[1], "height": row[2], "age": row[3]}
    return None

# --- 3. MOTOR ESTÉTICO (CSS) — Sistema "Dossier de Rendimiento" (Blanco / Azul) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap');
:root {
    --bg-0: #0a0f1a;
    --bg-1: #10182a;
    --panel: #131c2f;
    --line: rgba(45, 212, 191, 0.18);
    --signal: #2dd4bf;
    --signal-soft: rgba(45, 212, 191, 0.14);
    --success: #34d399;
    --success-soft: rgba(52, 211, 153, 0.14);
    --amber: #fbbf24;
    --amber-soft: rgba(251, 191, 36, 0.14);
    --red: #fb7185;
    --red-soft: rgba(251, 113, 133, 0.14);
    --ink: #0a0f1a;
    --text-hi: #f1f5f9;
    --text-mid: #94a3b8;
    --text-low: #64748b;
}
.stApp { background: var(--bg-0); color: var(--text-hi); font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }
.hero-card {
    background: linear-gradient(160deg, var(--bg-1) 0%, var(--panel) 100%);
    border: 1px solid var(--line); border-radius: 16px; padding: 28px 32px;
    margin-bottom: 28px; display: flex; justify-content: space-between;
    align-items: center; flex-wrap: wrap; gap: 16px;
    box-shadow: 0 4px 18px rgba(45, 212, 191, 0.10);
}
.hero-eyebrow { font-family: 'JetBrains Mono', monospace; color: var(--signal); font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 6px; }
.hero-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.9rem; font-weight: 700; color: var(--text-hi); margin: 0; }
.hero-sub { color: var(--text-mid); font-size: 0.92rem; margin-top: 4px; }
.hero-badge {
    font-family: 'JetBrains Mono', monospace; background: var(--success-soft); border: 1px solid var(--line);
    color: var(--success); padding: 10px 16px; border-radius: 10px; font-size: 0.8rem; text-align: right; line-height: 1.5;
}
.live-dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--success);
    margin-right:6px; box-shadow: 0 0 0 rgba(22,163,74,0.5); animation: pulseDot 1.6s infinite; }
@keyframes pulseDot { 0% { box-shadow: 0 0 0 0 rgba(22,163,74,0.5); } 70% { box-shadow: 0 0 0 7px rgba(22,163,74,0); } 100% { box-shadow: 0 0 0 0 rgba(22,163,74,0); } }
.module-container { background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 26px; margin-bottom: 22px; box-shadow: 0 2px 10px rgba(45,212,191,0.08); }
.timer-display {
    font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 5.5rem;
    text-align: center; padding: 40px; border-radius: 18px; border: 2px solid var(--amber);
    color: var(--amber); background: var(--amber-soft); letter-spacing: 4px;
}
.work-active { border-color: var(--success) !important; color: var(--success) !important; background: var(--success-soft) !important; }
.ia-card { background: var(--panel); border: 1px solid var(--line); border-left: 3px solid var(--signal); border-radius: 14px; padding: 26px; white-space: pre-wrap; color: var(--text-hi); line-height: 1.6; }
.ia-tag { color: var(--signal); font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; letter-spacing: 1.5px; text-transform: uppercase; border-bottom: 1px solid var(--line); margin-bottom: 14px; padding-bottom: 10px; }
.rm-giant { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 3.6rem; color: var(--signal); text-align: center; margin: 0; }
.readiness-box { padding: 20px; border-radius: 12px; text-align: center; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 2rem; margin-bottom: 15px; }
.readiness-high { background: var(--success-soft); color: var(--success); border: 1px solid var(--success); }
.readiness-mid { background: var(--amber-soft); color: var(--amber); border: 1px solid var(--amber); }
.readiness-low { background: var(--red-soft); color: var(--red); border: 1px solid var(--red); }
section[data-testid="stSidebar"] { background: var(--bg-1); border-right: 1px solid var(--line); border-right-width: 2px; box-shadow: 2px 0 12px rgba(11,18,32,0.04); }
.sidebar-title-pill { display:inline-block; background: var(--panel); color: var(--text-hi); padding: 8px 16px; border-radius: 10px;
    border: 1px solid var(--line); border-left: 4px solid var(--signal);
    font-family:'Space Grotesk',sans-serif; letter-spacing:2px; font-size:1.15rem; font-weight:700; }
.auth-card { max-width: 420px; margin: 40px auto; background: var(--panel); border: 1px solid var(--line);
    border-radius: 18px; padding: 34px; box-shadow: 0 8px 30px rgba(45,212,191,0.14); }

/* --- LEGIBILIDAD: forzar texto claro y de alto contraste sobre el fondo oscuro en TODA la app --- */
:root { --text-color: #f1f5f9; --background-color: #0a0f1a; --secondary-background-color: #131c2f; }
.stApp, .stApp p, .stApp span, .stApp label, .stApp li, .stApp div,
.stMarkdown, .stCaption, .stText, .stAlert, .stTabs, .stRadio, .stSelectbox,
h1, h2, h3, h4, h5, h6 { color: var(--text-hi); }
section[data-testid="stSidebar"] * { color: var(--text-hi); }
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input {
    background-color: var(--panel) !important; color: var(--text-hi) !important;
    border: 1px solid var(--line) !important;
}
div[data-baseweb="select"] > div, div[data-baseweb="select"] span {
    background-color: var(--panel) !important; color: var(--text-hi) !important;
}
div[data-baseweb="popover"] li, div[data-baseweb="menu"] li,
div[data-baseweb="popover"] *, ul[role="listbox"] * {
    background-color: var(--panel) !important; color: var(--text-hi) !important;
}
div[data-testid*="Alert"], div[data-testid*="Notification"], .stAlert {
    background-color: var(--panel) !important; border: 1px solid var(--line) !important;
}
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    background-color: var(--signal); color: var(--ink) !important;
    border: 1.5px solid var(--signal); font-weight: 700;
}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
    background-color: var(--panel); color: var(--signal) !important; border-color: var(--signal);
}
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

# --- MANIQUÍ ANIMADO (cuerpo humano continuo, sin "piezas de robot") ---
def _mezclar(hexcolor, factor, hacia_blanco=True):
    """Aclara (hacia_blanco=True) u oscurece un color hex un factor 0-1, para simular volumen 3D."""
    h = hexcolor.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    if hacia_blanco:
        r, g, b = [min(255, int(v + (255 - v) * factor)) for v in (r, g, b)]
    else:
        r, g, b = [max(0, int(v * (1 - factor))) for v in (r, g, b)]
    return f"#{r:02x}{g:02x}{b:02x}"

def render_mannequin(grupo, key="m"):
    """SVG de un maniquí con las extremidades realmente fundidas en una silueta continua
    (filtro 'goo'), más un halo de energía detrás del grupo muscular activo."""
    grupo_map = {
        "Pecho": "chest", "Espalda": "back", "Hombros": "shoulders",
        "Brazos": "arms", "Piernas": "legs", "Core": "core",
        "Running": "legs", "Movilidad": "full", "Explosividad": "full",
        "Calistenia": "full",
    }
    activo = grupo_map.get(grupo, "full")
    ACTIVO = "#2dd4bf"
    ACERO = "#374357"   # tono base "en reposo", visible sobre el panel oscuro
    TINTA = "#f1f5f9"

    def activo_aqui(part):
        return activo in (part, "full")

    def c(part):
        return f"url(#{key}-gA)" if activo_aqui(part) else f"url(#{key}-gP)"

    ac_luz, ac_som = _mezclar(ACTIVO, 0.35), _mezclar(ACTIVO, 0.35, hacia_blanco=False)
    ac2_luz, ac2_som = _mezclar(ACERO, 0.45), _mezclar(ACERO, 0.25, hacia_blanco=False)

    anim_arms = "swingArms 1.3s ease-in-out infinite" if activo in ("chest", "back", "shoulders", "arms", "full") else "none"
    anim_legs = "swingLegs 1.3s ease-in-out infinite" if activo in ("legs", "full") else "none"
    anim_core = "pulseCore 1.1s ease-in-out infinite" if activo == "core" else "none"
    nota_back = "<p style='text-align:center;color:#94a3b8;font-size:0.7rem;'>Vista frontal simplificada (dorsales laterales)</p>" if grupo == "Espalda" else ""

    halo_geo = {
        "chest": (110, 96, 52, 50), "back": (110, 96, 52, 50),
        "shoulders": (110, 74, 62, 42), "arms": (110, 140, 95, 78),
        "legs": (110, 235, 55, 105), "core": (110, 128, 42, 42),
        "full": (110, 175, 100, 160),
    }
    hx, hy, hrx, hry = halo_geo.get(activo, halo_geo["full"])

    html = f"""
    <div style="display:flex;justify-content:center;padding:6px 0 0 0;">
    <style>
    @keyframes swingArms {{ 0%,100% {{ transform: rotate(-8deg); }} 50% {{ transform: rotate(12deg); }} }}
    @keyframes swingLegs {{ 0%,100% {{ transform: rotate(6deg); }} 50% {{ transform: rotate(-10deg); }} }}
    @keyframes pulseCore {{ 0%,100% {{ transform: scale(1); opacity:1; }} 50% {{ transform: scale(1.08); opacity:0.85; }} }}
    @keyframes pulseGlow {{ 0%,100% {{ opacity:0.5; }} 50% {{ opacity:1; }} }}
    @keyframes pulseHalo {{ 0%,100% {{ opacity:0.30; }} 50% {{ opacity:0.55; }} }}
    .{key}-larm {{ transform-box: view-box; transform-origin: 66px 74px; animation: {anim_arms}; }}
    .{key}-rarm {{ transform-box: view-box; transform-origin: 154px 74px; animation: {anim_arms}; }}
    .{key}-lleg {{ transform-box: view-box; transform-origin: 92px 178px; animation: {anim_legs}; }}
    .{key}-rleg {{ transform-box: view-box; transform-origin: 128px 178px; animation: {anim_legs}; }}
    .{key}-core {{ transform-box: view-box; transform-origin: 110px 127px; animation: {anim_core}; }}
    .{key}-dot {{ animation: pulseGlow 1.1s ease-in-out infinite; }}
    .{key}-halo {{ animation: pulseHalo 2.4s ease-in-out infinite; }}
    </style>
    <svg viewBox="0 0 220 340" width="150" height="232">
      <defs>
        <linearGradient id="{key}-gA" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="{ac_luz}"/><stop offset="100%" stop-color="{ac_som}"/>
        </linearGradient>
        <linearGradient id="{key}-gP" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="{ac2_luz}"/><stop offset="100%" stop-color="{ac2_som}"/>
        </linearGradient>
        <radialGradient id="{key}-halo-grad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="{ACTIVO}" stop-opacity="0.55"/>
          <stop offset="100%" stop-color="{ACTIVO}" stop-opacity="0"/>
        </radialGradient>
        <filter id="{key}-goo" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur"/>
          <feColorMatrix in="blur" mode="matrix"
            values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -10" result="goo"/>
          <feComposite in="SourceGraphic" in2="goo" operator="atop"/>
        </filter>
        <filter id="{key}-blur" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation="14"/>
        </filter>
        <filter id="{key}-sombra" x="-30%" y="-10%" width="160%" height="130%">
          <feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>
        </filter>
      </defs>

      <!-- líneas de escaneo (ambiente "neural") -->
      <g opacity="0.10" stroke="{TINTA}" stroke-width="1">
        <line x1="20" y1="60" x2="200" y2="60"/>
        <line x1="20" y1="150" x2="200" y2="150"/>
        <line x1="20" y1="240" x2="200" y2="240"/>
      </g>

      <!-- halo de energía detrás del grupo activo -->
      <ellipse class="{key}-halo" cx="{hx}" cy="{hy}" rx="{hrx}" ry="{hry}"
               fill="url(#{key}-halo-grad)" filter="url(#{key}-blur)"/>

      <g filter="url(#{key}-sombra)">
        <!-- dorsales (asoman levemente por detrás del torso, fundidas entre sí) -->
        <g filter="url(#{key}-goo)" opacity="0.9">
          <ellipse cx="73" cy="92" rx="11" ry="30" fill="{c('back')}"/>
          <ellipse cx="147" cy="92" rx="11" ry="30" fill="{c('back')}"/>
        </g>

        <!-- piernas: muslo + gemelo + pie fundidos en una silueta continua -->
        <g class="{key}-lleg">
          <g filter="url(#{key}-goo)">
            <ellipse cx="91" cy="203" rx="17" ry="36" fill="{c('legs')}"/>
            <ellipse cx="86" cy="254" rx="13" ry="34" fill="{c('legs')}"/>
            <ellipse cx="79" cy="292" rx="17" ry="11" fill="{c('legs')}"/>
          </g>
        </g>
        <g class="{key}-rleg">
          <g filter="url(#{key}-goo)">
            <ellipse cx="129" cy="203" rx="17" ry="36" fill="{c('legs')}"/>
            <ellipse cx="134" cy="254" rx="13" ry="34" fill="{c('legs')}"/>
            <ellipse cx="141" cy="292" rx="17" ry="11" fill="{c('legs')}"/>
          </g>
        </g>
        <!-- cadera: conecta ambas piernas -->
        <rect x="78" y="148" width="64" height="40" rx="22" fill="{c('legs')}"/>

        <!-- brazos: hombro + bíceps + antebrazo + mano fundidos en una silueta continua -->
        <g class="{key}-larm">
          <g filter="url(#{key}-goo)">
            <ellipse cx="61" cy="90" rx="17" ry="32" fill="{c('arms')}"/>
            <ellipse cx="46" cy="149" rx="13" ry="31" fill="{c('arms')}"/>
            <ellipse cx="39" cy="199" rx="11" ry="15" fill="{c('arms')}"/>
          </g>
        </g>
        <g class="{key}-rarm">
          <g filter="url(#{key}-goo)">
            <ellipse cx="159" cy="90" rx="17" ry="32" fill="{c('arms')}"/>
            <ellipse cx="174" cy="149" rx="13" ry="31" fill="{c('arms')}"/>
            <ellipse cx="181" cy="199" rx="11" ry="15" fill="{c('arms')}"/>
          </g>
        </g>

        <!-- tronco: hombros + pecho/abdomen fundidos en una sola silueta continua -->
        <g filter="url(#{key}-goo)">
          <circle cx="72" cy="68" r="19" fill="{c('shoulders')}"/>
          <circle cx="148" cy="68" r="19" fill="{c('shoulders')}"/>
          <path d="M 77,62 Q 77,55 90,55 L 130,55 Q 143,55 143,62
                   L 141,112 Q 139,152 126,160 L 94,160 Q 81,152 79,112 Z"
                fill="{c('chest')}"/>
        </g>
        <ellipse cx="110" cy="128" rx="27" ry="27" fill="{c('core')}" opacity="0.6" class="{key}-core"/>

        <!-- cuello y cabeza (silueta limpia, sin fundir, para un perfil facial nítido) -->
        <rect x="101" y="44" width="18" height="18" rx="7" fill="{c('shoulders')}"/>
        <circle cx="110" cy="30" r="20" fill="url(#{key}-gP)" stroke="{TINTA}" stroke-width="1.2" stroke-opacity="0.3"/>
      </g>

      <!-- indicador "en marcha" -->
      <circle cx="198" cy="24" r="6" fill="{ACTIVO}" class="{key}-dot"/>
    </svg>
    </div>
    <p style="text-align:center;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:{ACTIVO};letter-spacing:1px;text-transform:uppercase;margin-top:2px;">
    <span style="color:{ACTIVO};">●</span> Zona activa: {grupo}
    </p>
    {nota_back}
    """
    return html

# =================================================================
# PUERTA DE ACCESO: INICIAR SESIÓN / CREAR CUENTA
# =================================================================
if "auth_user" not in st.session_state:
    st.markdown("""
    <div class="hero-card" style="justify-content:center; text-align:center;">
        <div>
            <div class="hero-eyebrow">MorphAI · Neural Performance OS</div>
            <p class="hero-title">🧬 Bienvenido a MorphAI</p>
            <p class="hero-sub">Inicia sesión o crea tu cuenta para acceder a tu telemetría de entrenamiento.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    tab_login, tab_signup = st.tabs(["🔑 Iniciar sesión", "🆕 Crear cuenta"])

    with tab_login:
        with st.form("f_login"):
            u_login = st.text_input("Usuario")
            p_login = st.text_input("Contraseña", type="password")
            if st.form_submit_button("ENTRAR"):
                perfil = check_user(u_login.strip(), p_login)
                if perfil:
                    st.session_state["auth_user"] = u_login.strip()
                    st.session_state["user"] = {
                        "name": u_login.strip().upper(),
                        "weight": perfil["weight"], "height": perfil["height"], "age": perfil["age"]
                    }
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

    with tab_signup:
        with st.form("f_signup"):
            u_new = st.text_input("Elige un usuario")
            p_new = st.text_input("Elige una contraseña", type="password")
            p_new2 = st.text_input("Repite la contraseña", type="password")
            cs1, cs2, cs3 = st.columns(3)
            w_new = cs1.number_input("Peso (kg)", 30.0, 250.0, 75.0)
            h_new = cs2.number_input("Altura (cm)", 130, 220, 175)
            a_new = cs3.number_input("Edad", 12, 90, 25)
            if st.form_submit_button("CREAR CUENTA"):
                if not u_new or not p_new:
                    st.warning("Completa usuario y contraseña.")
                elif p_new != p_new2:
                    st.warning("Las contraseñas no coinciden.")
                elif create_user(u_new.strip(), p_new, w_new, h_new, a_new):
                    st.success("Cuenta creada. Ahora inicia sesión en la otra pestaña.")
                else:
                    st.error("Ese nombre de usuario ya existe. Elige otro.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- A partir de aquí, el usuario ya inició sesión ---
if "user" not in st.session_state:
    st.session_state["user"] = {"name": st.session_state["auth_user"].upper(), "weight": 75, "height": 175, "age": 25}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown('<span class="sidebar-title-pill">🧬 MORPHAI OS</span>', unsafe_allow_html=True)
    st.write("")
    st.caption(f"👤 Sesión de **{st.session_state.user['name'].title()}**")
    if st.button("🚪 Cerrar sesión"):
        del st.session_state["auth_user"]
        del st.session_state["user"]
        st.rerun()
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
    st.caption("🔒 v19.0 Apex | Cuentas y persistencia nativa SQLite activa.")

USER = st.session_state.user["name"]

# --- 5. CABECERA / BIENVENIDA ---
_df_home = load_entries(USER)
_total = len(_df_home)
_ultima = _df_home.iloc[0]["fecha"] if _total > 0 else "Sin registros aún"

_df_readiness = load_readiness(USER)
_readiness_val = f"{_df_readiness.iloc[0]['score']:.0f}%" if not _df_readiness.empty else "N/A"

st.markdown(f"""
<div class="hero-card">
<div>
<div class="hero-eyebrow">MorphAI · Telemetría y Rendimiento v19.0</div>
<p class="hero-title">Hola, {USER.title()} 👋</p>
<p class="hero-sub">Sistema Neural Activo. Selecciona un módulo en el menú lateral para gestionar tu día atlético.</p>
</div>
<div class="hero-badge"><span class="live-dot"></span>SESIONES: {_total} | READINESS: {_readiness_val}<br>ÚLTIMA ACTIVIDAD: {_ultima}</div>
</div>
""", unsafe_allow_html=True)

# =================================================================
# MÓDULO 1: NEURAL READINESS & SUEÑO
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
            fig_r.update_traces(line_color="#2ecc71")
            st.plotly_chart(fig_r, use_container_width=True)
        else:
            st.info("Registra tu primer check-in matutino para calibrar tu algoritmo de entrenamiento.")

# =================================================================
# MÓDULO 2: ENTRENAMIENTO DE FUERZA (CON MANIQUÍ ANIMADO)
# =================================================================
elif system_mode == "🏋️ ENTRENAMIENTO DE FUERZA":
    grupos_fuerza = ["Pecho", "Espalda", "Piernas", "Hombros", "Brazos", "Core", "Calistenia"]
    c1, c2, c3 = st.columns([1, 1, 0.8])
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

        st.markdown("##### ⏱️ Descanso entre series")
        dcol1, dcol2 = st.columns([1, 1])
        seg_descanso = dcol1.selectbox("Duración", [60, 90, 120, 180], index=1, format_func=lambda s: f"{s}s")
        if dcol2.button("▶️ Iniciar descanso"):
            ph_d = st.empty()
            for t in range(seg_descanso, 0, -1):
                ph_d.markdown(f'<div class="timer-display work-active" style="font-size:2.6rem;padding:16px;">DESCANSO<br>{t//60:02d}:{t%60:02d}</div>', unsafe_allow_html=True)
                time.sleep(1)
            ph_d.success("✅ Descanso terminado. ¡A por la siguiente serie!")

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
    with c3:
        st.markdown("### 🧍 Maniquí")
        st.markdown(render_mannequin(grupo, key="fuerza"), unsafe_allow_html=True)

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
        st.markdown(render_mannequin("Piernas", key="run"), unsafe_allow_html=True)
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
# MÓDULO 5: MOVILIDAD & RECUPERACIÓN (CON MANIQUÍ ANIMADO)
# =================================================================
elif system_mode == "🧘 MOVILIDAD & RECUPERACIÓN":
    st.markdown("### 🧘 Sesión de Movilidad y Regeneración")
    st.caption("La recuperación también es entrenamiento. Registra tus sesiones de movilidad y recuperación activa.")
    c1, c2, c3 = st.columns([1, 1, 0.8])
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
    with c3:
        st.markdown("### 🧍 Maniquí")
        st.markdown(render_mannequin("Movilidad", key="mov"), unsafe_allow_html=True)

# =================================================================
# MÓDULO 6: NUTRICIÓN & MACROS
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
# MÓDULO 7: BIBLIOTECA DE EJERCICIOS (CON MANIQUÍ ANIMADO)
# =================================================================
elif system_mode == "📚 BIBLIOTECA DE EJERCICIOS":
    st.markdown("### 📚 Biblioteca de Ejercicios y Biomecánica")
    total_ejercicios = sum(len(v) for v in DB_EXERCISES.values())
    st.caption(f"Consulta técnica y grupo muscular de cada ejercicio disponible en la app · **{total_ejercicios} ejercicios** en {len(DB_EXERCISES)} categorías.")
    if 'favoritos' not in st.session_state:
        st.session_state['favoritos'] = set()
    col_lib, col_man = st.columns([2.3, 1])
    with col_lib:
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
    with col_man:
        st.markdown("### 🧍 Maniquí")
        st.markdown(render_mannequin(cat_sel, key="lib"), unsafe_allow_html=True)

# =================================================================
# MÓDULO 8: OBJETIVOS & RACHA
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
        fig_m.update_traces(line_color="#ff7a45")
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
        st.plotly_chart(fig1, use_container_width=True)
        c_a1, c_a2 = st.columns(2)
        fig2 = px.pie(df, names='tipo', hole=0.6, title="Balance del Atleta por Módulo",
                      color_discrete_sequence=['#ff7a45', '#2ecc71', '#22d3ee', '#ffb020', '#ff5470', '#7c3aed'])
        fig2.update_layout(template="plotly_dark")
        c_a1.plotly_chart(fig2)
        fig3 = px.bar(df, x="actividad", y="valor", color="tipo", title="Volumen Acumulado por Ejercicio / Actividad",
                      color_discrete_sequence=['#ff7a45', '#2ecc71', '#22d3ee', '#ffb020', '#ff5470', '#7c3aed'])
        fig3.update_layout(template="plotly_dark")
        c_a2.plotly_chart(fig3)
        st.divider()
        st.markdown("### 🏆 Récords Personales (PRs Máximos)")
        prs = df.groupby("actividad")["valor"].max().sort_values(ascending=False).head(10)
        st.dataframe(prs.reset_index().rename(columns={"actividad": "Ejercicio/Actividad", "valor": "Mejor marca registrada"}),
                     use_container_width=True, hide_index=True)
    else:
        st.info("Todavía no hay datos que graficar. Registra tus entrenamientos para encender la telemetría.")

# =================================================================
# MÓDULO 11: GESTIÓN DE DATOS & BACKUP
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
st.markdown(f"**MORPHAI NEURAL PERFORMANCE OS v19.0 APEX** | Operador Activo: **{USER}** | © 2026 Josías Martínez")
