"""
MorphAI Performance OS
=======================
App de seguimiento deportivo y coaching con IA (Claude), construida con Streamlit.

Ejecutar localmente:
    streamlit run app.py

Configuración de la IA (recomendado para producción):
    Crea un archivo .streamlit/secrets.toml con:
        ANTHROPIC_API_KEY = "sk-ant-..."
    Así ningún usuario final necesita tener ni pegar su propia API key.
    Si no hay secrets configurados, la app pedirá la key manualmente
    en la barra lateral (modo desarrollo/demo).
"""

from __future__ import annotations

import base64
import re
import sqlite3
import time
from datetime import date, datetime, timedelta
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================

APP_NAME = "MorphAI Performance OS"
APP_VERSION = "19.0"
DB_PATH = "morphai.db"
AI_MODEL = "claude-sonnet-4-5-20250929"  # revisa docs.claude.com/docs/about-claude/models si cambias de versión
AI_MAX_TOKENS = 1600

MODULES = [
    "🧠 Neural Readiness & Sueño",
    "🏋️ Entrenamiento de Fuerza",
    "🏃 Running Telemetry",
    "🥊 Combate & Explosividad",
    "🧘 Movilidad & Recuperación",
    "🍎 Nutrición & Macros",
    "🔥 AI Warm-up & Form Coach",
    "📚 Biblioteca de Ejercicios",
    "🎯 Objetivos & Racha",
    "🤖 AI Routine Coach",
    "🗞️ Resumen Semanal IA",
    "📊 Analítica Global",
    "🛠️ Gestión de Datos & Backup",
]

st.set_page_config(
    page_title=f"{APP_NAME} | v{APP_VERSION}",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# BASE DE DATOS
# ============================================================

@st.cache_resource
def get_connection() -> sqlite3.Connection:
    """Crea (o reutiliza) la conexión a la base de datos SQLite. No crea tablas aquí:
    si esta función queda cacheada de una versión anterior del código, las tablas nuevas
    (como 'users') nunca se crearían. Ver ensure_schema()."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    # Modo WAL: permite lecturas y escrituras concurrentes sin que se bloqueen entre sí.
    # Es el modo recomendado cuando varias sesiones de Streamlit comparten un mismo archivo
    # SQLite (evita el típico "database is locked").
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=30000;")
    return conn


def ensure_schema() -> None:
    """Se llama en cada carga de la app (no está cacheada). CREATE TABLE IF NOT EXISTS es
    barato e idempotente, así que esto garantiza que el esquema esté siempre al día aunque
    get_connection() venga de una versión anterior cacheada del proceso."""
    try:
        _create_tables(get_connection())
    except sqlite3.OperationalError as exc:
        st.error(f"⚠️ No se pudo preparar la base de datos: {exc}")
        st.stop()


def _create_tables(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT, fecha TEXT, tipo TEXT, actividad TEXT,
            valor REAL, meta TEXT, extra TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT, fecha TEXT, peso REAL, grasa REAL, nota TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readiness (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT, fecha TEXT, sueno_hrs REAL, calidad_sueno INTEGER,
            doms INTEGER, estres INTEGER, hrv INTEGER, score REAL, nota TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nutrition (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT, fecha TEXT, calorias INTEGER, proteina INTEGER,
            carbs INTEGER, grasa INTEGER, agua_l REAL
        )
    """)
    conn.commit()


def save_entry(user: str, tipo: str, actividad: str, valor: float, meta: str, extra: str) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO entries (user, fecha, tipo, actividad, valor, meta, extra) VALUES (?,?,?,?,?,?,?)",
        (user, datetime.now().strftime("%Y-%m-%d %H:%M"), tipo, actividad, valor, meta, extra),
    )
    conn.commit()


def load_entries(user: str) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql_query("SELECT * FROM entries WHERE user=? ORDER BY id DESC", conn, params=(user,))


def save_metric(user: str, peso: float, grasa: float, nota: str) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO metrics (user, fecha, peso, grasa, nota) VALUES (?,?,?,?,?)",
        (user, datetime.now().strftime("%Y-%m-%d %H:%M"), peso, grasa, nota),
    )
    conn.commit()


def load_metrics(user: str) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql_query("SELECT * FROM metrics WHERE user=? ORDER BY id", conn, params=(user,))


def save_readiness(user: str, sueno: float, calidad: int, doms: int, estres: int,
                    hrv: int, score: float, nota: str) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO readiness (user, fecha, sueno_hrs, calidad_sueno, doms, estres, hrv, score, nota) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (user, datetime.now().strftime("%Y-%m-%d %H:%M"), sueno, calidad, doms, estres, hrv, score, nota),
    )
    conn.commit()


def load_readiness(user: str) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql_query("SELECT * FROM readiness WHERE user=? ORDER BY id DESC", conn, params=(user,))


def save_nutrition(user: str, cal: int, prot: int, carbs: int, grasa: int, agua: float) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO nutrition (user, fecha, calorias, proteina, carbs, grasa, agua_l) VALUES (?,?,?,?,?,?,?)",
        (user, datetime.now().strftime("%Y-%m-%d %H:%M"), cal, prot, carbs, grasa, agua),
    )
    conn.commit()


def load_nutrition(user: str) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql_query("SELECT * FROM nutrition WHERE user=? ORDER BY id DESC", conn, params=(user,))


def delete_record(table: str, record_id: int, user: str) -> None:
    conn = get_connection()
    conn.execute(f"DELETE FROM {table} WHERE id=? AND user=?", (record_id, user))
    conn.commit()


# ============================================================
# DATOS DE EJERCICIOS
# ============================================================

DB_EXERCISES: dict[str, list[str]] = {
    "Pecho": ["Press Banca Plano", "Press Banca Inclinado", "Press Banca Declinado", "Press Mancuernas Plano",
              "Press Mancuernas Inclinado", "Aperturas Polea", "Aperturas Mancuerna", "Fondos en Paralelas",
              "Pull-over con Mancuerna", "Cruces en Polea Alta"],
    "Espalda": ["Dominadas Pro", "Dominadas Lastradas", "Remo Pendlay", "Remo con Mancuerna", "Remo en T",
                "Remo Gironda", "Jalón al Pecho", "Jalón Agarre Cerrado", "Peso Muerto Convencional",
                "Hiperextensiones"],
    "Piernas": ["Sentadilla Barra", "Sentadilla Frontal", "Sentadilla Búlgara", "Peso Muerto Sumó",
                "Peso Muerto Rumano", "Prensa 45°", "Zancadas Búlgaras", "Step Up con Carga",
                "Curl Femoral", "Extensión Cuádriceps", "Sissy Squat"],
    "Glúteos": ["Hip Thrust", "Patada de Glúteo en Polea", "Peso Muerto a una Pierna", "Puente de Glúteo",
                "Abducción de Cadera en Máquina", "Sentadilla Sumó con Mancuerna"],
    "Pantorrillas": ["Elevación de Talones de Pie", "Elevación de Talones Sentado", "Elevación de Talones en Prensa"],
    "Hombros": ["Press Militar", "Press Arnold", "Press Landmine", "Elevaciones Laterales",
                "Elevaciones Frontales", "Pájaros Posteriores", "Remo al Mentón", "Face Pull"],
    "Brazos": ["Curl Barra Z", "Curl Martillo", "Curl Predicador", "Curl Concentrado",
               "Press Francés", "Fondos Tríceps en Banco", "Extensión de Tríceps en Polea", "Curl 21s"],
    "Antebrazos": ["Curl de Muñeca", "Curl de Muñeca Invertido", "Farmer's Walk", "Dead Hang en Barra"],
    "Core": ["Plancha Frontal", "Plancha Lateral", "Rueda Abdominal", "Elevación de Piernas Colgado",
             "Russian Twist", "Dead Bug", "Hollow Body Hold", "Crunch en Polea Alta"],
    "Explosividad": ["Saltos al Cajón", "Broad Jump", "Landmine Punch", "Medball Slam", "Burpee Pliométrico",
                      "Snatch con Mancuerna", "Clean and Press", "Sprints Potencia", "Kettlebell Swing"],
    "Calistenia": ["Muscle Up", "Pistol Squat", "Handstand Push-up", "Front Lever (progresión)",
                    "Archer Pull-up", "L-sit", "Human Flag (progresión)"],
    "Running": ["Carrera Continua", "Series VO2 Max", "Fartlek Neural", "Umbral Lactato",
                "Trote Regenerativo", "Cuestas Cortas", "Series de 400m"],
    "Movilidad": ["Movilidad de Cadera", "Movilidad Torácica", "Movilidad de Tobillo",
                  "Estiramiento Isquiotibiales", "Foam Rolling Espalda", "Foam Rolling Cuádriceps",
                  "Movilidad de Hombro", "Respiración Diafragmática"],
}

DB_EXERCISE_INFO: dict[str, tuple[str, str]] = {
    "Sentadilla Barra": ("Cuádriceps, glúteos, core",
                          "Barra libre en espalda alta, baja controlando la rodilla en línea con el pie."),
    "Peso Muerto Sumó": ("Glúteos, isquiotibiales, espalda baja",
                         "Postura ancha, espalda neutra, empuja el piso con los talones."),
    "Peso Muerto Convencional": ("Cadena posterior completa",
                                  "Barra pegada a la tibia, cadera arriba antes que el pecho."),
    "Press Banca Plano": ("Pectoral, tríceps, hombro anterior",
                           "Escápulas retraídas, barra baja al esternón con control."),
    "Dominadas Pro": ("Dorsal ancho, bíceps", "Agarre prono, tira con el codo hacia la cadera."),
    "Press Militar": ("Hombro, tríceps, core", "De pie, evita arquear la espalda baja al empujar."),
    "Hip Thrust": ("Glúteo mayor", "Espalda apoyada en banco, empuje con talones, aprieta glúteo arriba."),
    "Muscle Up": ("Dorsal, tríceps, core",
                  "Transición explosiva de dominada a fondo, requiere buena base de fuerza en ambos."),
    "Kettlebell Swing": ("Cadena posterior, potencia de cadera", "El impulso viene de la cadera, no de los brazos."),
    "Plancha Frontal": ("Core, estabilidad lumbar", "Cuerpo en línea recta, glúteos y abdomen activos."),
    "Movilidad de Cadera": ("Flexores de cadera, rotadores", "Series de 90/90 y círculos controlados, sin rebotes."),
    "Press Banca Inclinado": ("Pectoral superior, hombro anterior",
                               "Banco a 30-45°, controla el descenso hasta rozar la parte alta del pecho."),
    "Remo Pendlay": ("Dorsal, romboides, espalda media",
                      "La barra parte del suelo en cada repetición, tirón explosivo con el torso paralelo al piso."),
    "Sentadilla Frontal": ("Cuádriceps, core, espalda alta",
                            "Barra sobre los deltoides anteriores, torso más vertical que en la sentadilla trasera."),
    "Peso Muerto Rumano": ("Isquiotibiales, glúteo",
                            "Rodilla semi-flexionada fija, la cadera se dobla hacia atrás con la barra pegada a la pierna."),
    "Sentadilla Búlgara": ("Cuádriceps, glúteo unilateral",
                            "Pie trasero elevado en banco, desciende controlando que la rodilla delantera no se desvíe."),
    "Elevación de Talones de Pie": ("Gemelo (gastrocnemio)", "Rango completo, pausa 1s arriba en máxima contracción."),
    "Press Arnold": ("Deltoides completo", "Rotación de muñeca durante el empuje: de mancuernas al frente a arriba."),
    "Fondos Tríceps en Banco": ("Tríceps", "Manos apoyadas detrás del cuerpo, codos hacia atrás, no hacia los lados."),
    "Farmer's Walk": ("Antebrazo, core, trapecio", "Carga pesada en cada mano, camina con postura erguida y pasos cortos."),
    "Rueda Abdominal": ("Core completo",
                         "Extiende desde rodillas o de pie manteniendo la zona lumbar neutra, sin arquear."),
    "Dead Bug": ("Core, estabilidad lumbar", "Espalda pegada al piso, extiende brazo y pierna opuestos de forma controlada."),
    "Broad Jump": ("Potencia de piernas", "Salto horizontal máximo, aterriza con las rodillas semi-flexionadas."),
    "Clean and Press": ("Cuerpo completo, potencia", "Tirón explosivo desde el suelo a los hombros, luego press sobre la cabeza."),
    "Pistol Squat": ("Cuádriceps unilateral, equilibrio", "Sentadilla a una pierna, la otra se mantiene extendida al frente."),
    "Front Lever (progresión)": ("Dorsal, core", "Cuerpo horizontal colgado de la barra; progresa desde tuck hasta extendido."),
    "Movilidad de Tobillo": ("Flexores dorsales de tobillo",
                              "Rodilla avanza sobre el pie sin levantar el talón, series controladas."),
    "Umbral Lactato": ("Sistema aeróbico-anaeróbico", "Ritmo sostenido cercano a tu umbral, 20-30 min continuos o en bloques."),
}


# ============================================================
# MANIQUÍ MUSCULAR (diagrama simplificado, no anatómico)
# ============================================================

MUSCLE_REGION_MAP: dict[str, list[str]] = {
    "Pecho": ["chest"],
    "Espalda": ["chest", "shoulders"],
    "Piernas": ["thigh_l", "thigh_r"],
    "Glúteos": ["hips"],
    "Pantorrillas": ["calf_l", "calf_r"],
    "Hombros": ["shoulders"],
    "Brazos": ["arm_l", "arm_r"],
    "Antebrazos": ["forearm_l", "forearm_r"],
    "Core": ["abs"],
    "Calistenia": ["chest", "arm_l", "arm_r", "abs", "shoulders"],
}


def render_body_diagram(grupo: str) -> None:
    """Dibuja un maniquí simplificado resaltando la zona trabajada. No es un diagrama anatómico preciso,
    solo una guía visual rápida."""
    highlight = set(MUSCLE_REGION_MAP.get(grupo, []))

    def fill(region_id: str) -> str:
        return "var(--signal)" if region_id in highlight else "#2a332e"

    def op(region_id: str) -> str:
        return "1" if region_id in highlight else "0.5"

    svg = f'''
    <div style="display:flex; justify-content:center; padding:10px 0;">
    <svg viewBox="0 0 200 380" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:190px;">
      <circle cx="100" cy="34" r="23" fill="#2a332e" stroke="var(--line)" stroke-width="2" opacity="0.7"/>
      <rect x="90" y="53" width="20" height="14" fill="#2a332e" opacity="0.7"/>
      <circle cx="58" cy="76" r="15" fill="{fill('shoulders')}" opacity="{op('shoulders')}"/>
      <circle cx="142" cy="76" r="15" fill="{fill('shoulders')}" opacity="{op('shoulders')}"/>
      <rect x="63" y="68" width="74" height="55" rx="14" fill="{fill('chest')}" opacity="{op('chest')}"/>
      <rect x="68" y="124" width="64" height="48" rx="10" fill="{fill('abs')}" opacity="{op('abs')}"/>
      <rect x="63" y="173" width="74" height="30" rx="12" fill="{fill('hips')}" opacity="{op('hips')}"/>
      <rect x="30" y="70" width="26" height="68" rx="12" fill="{fill('arm_l')}" opacity="{op('arm_l')}"/>
      <rect x="144" y="70" width="26" height="68" rx="12" fill="{fill('arm_r')}" opacity="{op('arm_r')}"/>
      <rect x="26" y="139" width="22" height="55" rx="10" fill="{fill('forearm_l')}" opacity="{op('forearm_l')}"/>
      <rect x="152" y="139" width="22" height="55" rx="10" fill="{fill('forearm_r')}" opacity="{op('forearm_r')}"/>
      <rect x="66" y="202" width="28" height="85" rx="12" fill="{fill('thigh_l')}" opacity="{op('thigh_l')}"/>
      <rect x="106" y="202" width="28" height="85" rx="12" fill="{fill('thigh_r')}" opacity="{op('thigh_r')}"/>
      <rect x="68" y="287" width="24" height="75" rx="10" fill="{fill('calf_l')}" opacity="{op('calf_l')}"/>
      <rect x="108" y="287" width="24" height="75" rx="10" fill="{fill('calf_r')}" opacity="{op('calf_r')}"/>
    </svg>
    </div>
    '''
    st.markdown(svg, unsafe_allow_html=True)
    st.caption(f"🟢 Zona destacada: **{grupo}** · diagrama orientativo, no anatómico exacto.")


# ============================================================
# ESTILOS (CSS)
# ============================================================

def apply_custom_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    :root {
        --bg-0: #05080a; --bg-1: #0e1512; --panel: #131a17; --panel-2: #171f1b;
        --line: rgba(150, 255, 200, 0.14);
        --signal: #35d68c; --signal-2: #00e5ff; --signal-soft: rgba(53, 214, 140, 0.14);
        --amber: #f5a623; --amber-soft: rgba(245, 166, 35, 0.12);
        --red: #ff4b4b; --red-soft: rgba(255, 75, 75, 0.14);
        --violet: #a86bff;
        --text-hi: #f3f7f5; --text-mid: #9fb0a9; --text-low: #5e6b66;
    }

    * { scrollbar-width: thin; scrollbar-color: var(--signal) var(--bg-1); }
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-1); }
    ::-webkit-scrollbar-thumb { background: var(--signal); border-radius: 8px; }

    .stApp {
        background:
            radial-gradient(circle at 10% 10%, rgba(53,214,140,0.10) 0%, transparent 45%),
            radial-gradient(circle at 90% 20%, rgba(0,229,255,0.08) 0%, transparent 40%),
            radial-gradient(circle at 50% 100%, rgba(168,107,255,0.08) 0%, transparent 45%),
            var(--bg-0);
        color: var(--text-hi); font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif; }

    /* HERO */
    .hero-card {
        position: relative; overflow: hidden;
        background: linear-gradient(160deg, rgba(19,26,23,0.92) 0%, rgba(14,21,18,0.96) 100%);
        border: 1px solid var(--line); border-radius: 20px; padding: 32px 36px;
        margin-bottom: 28px; display: flex; justify-content: space-between;
        align-items: center; flex-wrap: wrap; gap: 20px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.04);
    }
    .hero-card::before {
        content: ""; position: absolute; top: -60%; right: -15%; width: 420px; height: 420px;
        background: radial-gradient(circle, rgba(53,214,140,0.18) 0%, transparent 70%);
        animation: floatGlow 8s ease-in-out infinite alternate; pointer-events: none;
    }
    @keyframes floatGlow { from { transform: translate(0,0) scale(1); } to { transform: translate(-30px, 30px) scale(1.15); } }

    .hero-eyebrow { font-family: 'JetBrains Mono', monospace; color: var(--signal); font-size: 0.75rem;
                    letter-spacing: 3px; text-transform: uppercase; margin-bottom: 8px; }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif; font-size: 2.1rem; font-weight: 800; margin: 0;
        background: linear-gradient(90deg, #eef2f0 40%, var(--signal) 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }
    .hero-sub { color: var(--text-mid); font-size: 0.94rem; margin-top: 6px; max-width: 480px; }
    .hero-stats { display: flex; gap: 12px; flex-wrap: wrap; z-index: 1; }
    .stat-chip {
        font-family: 'JetBrains Mono', monospace; background: rgba(255,255,255,0.03);
        border: 1px solid var(--line); padding: 10px 18px; border-radius: 12px;
        text-align: center; min-width: 100px; transition: all 0.2s ease;
    }
    .stat-chip:hover { border-color: var(--signal); transform: translateY(-2px); box-shadow: 0 6px 18px rgba(53,214,140,0.15); }
    .stat-chip .num { font-size: 1.3rem; font-weight: 700; color: var(--signal); display: block; }
    .stat-chip .lbl { font-size: 0.65rem; color: var(--text-mid); letter-spacing: 1px; text-transform: uppercase; }

    /* SECCIONES */
    .module-container { background: var(--panel); border: 1px solid var(--line); border-radius: 16px;
                         padding: 26px; margin-bottom: 22px; box-shadow: 0 6px 20px rgba(0,0,0,0.2); }
    .section-title {
        display: flex; align-items: center; gap: 10px; font-family: 'Space Grotesk', sans-serif;
        font-size: 1.15rem; font-weight: 700; color: var(--text-hi); margin: 4px 0 18px 0;
        padding-bottom: 10px; border-bottom: 1px solid var(--line);
    }

    /* TIMER */
    .timer-display {
        font-family: 'JetBrains Mono', monospace; font-weight: 800; font-size: 5.5rem;
        text-align: center; padding: 44px; border-radius: 22px; border: 2px solid var(--amber);
        color: var(--amber); background: radial-gradient(circle at 50% 0%, var(--amber-soft), transparent 70%);
        letter-spacing: 4px; animation: pulseGlow 1.4s ease-in-out infinite;
    }
    .work-active { border-color: var(--signal) !important; color: var(--signal) !important;
                    background: radial-gradient(circle at 50% 0%, var(--signal-soft), transparent 70%) !important; }
    @keyframes pulseGlow { 0%,100% { box-shadow: 0 0 25px rgba(245,166,35,0.12); } 50% { box-shadow: 0 0 45px rgba(245,166,35,0.28); } }

    /* IA CARD */
    .ia-card { background: linear-gradient(160deg, var(--panel) 0%, var(--panel-2) 100%);
               border: 1px solid var(--line); border-left: 4px solid var(--signal);
               border-radius: 16px; padding: 28px; white-space: pre-wrap; color: var(--text-hi);
               line-height: 1.7; box-shadow: 0 8px 26px rgba(0,0,0,0.25); }
    .ia-tag { color: var(--signal); font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;
              letter-spacing: 1.5px; text-transform: uppercase; border-bottom: 1px solid var(--line);
              margin-bottom: 16px; padding-bottom: 12px; }

    /* 1RM GIGANTE */
    .rm-giant { font-family: 'JetBrains Mono', monospace; font-weight: 800; font-size: 3.8rem;
                text-align: center; margin: 0; background: linear-gradient(90deg, var(--signal), var(--signal-2));
                -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }

    /* ANILLO DE READINESS */
    .readiness-wrap { display: flex; align-items: center; gap: 26px; margin-bottom: 10px; flex-wrap: wrap; }
    .readiness-ring {
        width: 140px; height: 140px; border-radius: 50%; display: flex; align-items: center;
        justify-content: center; position: relative; flex-shrink: 0;
    }
    .readiness-high { background: conic-gradient(var(--signal) calc(var(--pct) * 1%), rgba(255,255,255,0.06) 0); }
    .readiness-mid { background: conic-gradient(var(--amber) calc(var(--pct) * 1%), rgba(255,255,255,0.06) 0); }
    .readiness-low { background: conic-gradient(var(--red) calc(var(--pct) * 1%), rgba(255,255,255,0.06) 0); }
    .readiness-ring::after { content: ""; position: absolute; width: 112px; height: 112px; border-radius: 50%; background: var(--panel); }
    .readiness-ring .val { font-family: 'JetBrains Mono', monospace; font-weight: 800; font-size: 1.8rem; z-index: 1; }
    .readiness-status { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.05rem; }

    /* SIDEBAR */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, var(--bg-1) 0%, #080c0a 100%);
                                        border-right: 1px solid var(--line); }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        border-radius: 10px; padding: 6px 10px; margin-bottom: 2px; transition: all 0.15s ease;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: rgba(53,214,140,0.08); }

    /* BOTONES */
    .stButton>button { border-radius: 12px; font-weight: 700; transition: all 0.18s ease;
                        border: 1px solid var(--line); }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(53,214,140,0.18);
                              border-color: var(--signal); }

    /* MÉTRICAS Y CHAT */
    div[data-testid="stMetric"] { background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
                                   padding: 14px 18px; box-shadow: 0 4px 14px rgba(0,0,0,0.2); }
    div[data-testid="stChatMessage"] { border-radius: 14px; border: 1px solid var(--line); }

    /* VARIANTES DE COLOR */
    .stat-chip.chip-cyan { border-color: rgba(0,229,255,0.35); }
    .stat-chip.chip-cyan .num { color: var(--signal-2); }
    .stat-chip.chip-amber { border-color: rgba(245,166,35,0.35); }
    .stat-chip.chip-amber .num { color: var(--amber); }
    .stat-chip.chip-violet { border-color: rgba(168,107,255,0.35); }
    .stat-chip.chip-violet .num { color: var(--violet); }

    .ia-card.ia-amber { border-left-color: var(--amber); }
    .ia-card.ia-amber .ia-tag { color: var(--amber); }
    .ia-card.ia-cyan { border-left-color: var(--signal-2); }
    .ia-card.ia-cyan .ia-tag { color: var(--signal-2); }

    /* LOGIN */
    div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px !important; border-color: var(--line) !important;
    }

    /* MÓVIL: la app está pensada para usarse principalmente desde el teléfono */
    @media (max-width: 640px) {
        .hero-card { flex-direction: column; align-items: flex-start; padding: 22px 20px; }
        .hero-title { font-size: 1.5rem; }
        .hero-sub { max-width: 100%; }
        .hero-stats { width: 100%; }
        .stat-chip { flex: 1; min-width: 0; padding: 8px 6px; }
        .stat-chip .num { font-size: 1.05rem; }
        .timer-display { font-size: 2.8rem; padding: 26px 16px; }
        .rm-giant { font-size: 2.4rem; }
        .module-container { padding: 16px; }
        .section-title { font-size: 1rem; }
        .readiness-wrap { flex-direction: column; align-items: flex-start; gap: 14px; }
        .ia-card { padding: 18px; }
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# INTEGRACIÓN CON IA (Claude)
# ============================================================

def _get_secret_api_key() -> Optional[str]:
    """Lee la API key desde .streamlit/secrets.toml si existe. Nunca lanza excepción."""
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return None


def get_ai_client() -> Optional["anthropic.Anthropic"]:
    """
    Devuelve un cliente de Anthropic listo para usar, o None si no hay key disponible.
    Prioridad: secrets.toml (producción) > key manual introducida en la sesión (demo/desarrollo).
    """
    if not ANTHROPIC_AVAILABLE:
        return None

    api_key = _get_secret_api_key() or st.session_state.get("manual_api_key")
    if not api_key:
        return None

    return anthropic.Anthropic(api_key=api_key)


def call_ai(client: "anthropic.Anthropic", prompt: str, *, system: Optional[str] = None,
            image_b64: Optional[str] = None, media_type: str = "image/jpeg") -> Optional[str]:
    """Llama al modelo y devuelve el texto de respuesta, o None si hubo un error (ya mostrado con st.error)."""
    content = []
    if image_b64:
        content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_b64}})
    content.append({"type": "text", "text": prompt})

    kwargs = dict(model=AI_MODEL, max_tokens=AI_MAX_TOKENS, messages=[{"role": "user", "content": content}])
    if system:
        kwargs["system"] = system

    try:
        with st.spinner("Consultando a tu entrenador IA..."):
            response = client.messages.create(**kwargs)
        return "".join(block.text for block in response.content if block.type == "text")
    except Exception as exc:
        st.error(f"Error al comunicarse con la IA: {exc}")
        return None


# ============================================================
# UTILIDADES COMPARTIDAS
# ============================================================

def compute_streak(df_all: pd.DataFrame) -> int:
    """Calcula la racha de días consecutivos con al menos un registro, terminando hoy."""
    if df_all.empty:
        return 0
    fechas = set(pd.to_datetime(df_all["fecha"]).dt.date.unique())
    racha = 0
    dia = datetime.now().date()
    while dia in fechas:
        racha += 1
        dia = date.fromordinal(dia.toordinal() - 1)
    return racha


def suggest_progressive_overload(df_ejer: pd.DataFrame) -> Optional[str]:
    """Analiza el último set registrado de un ejercicio (peso, reps, RIR) y sugiere el
    siguiente objetivo siguiendo el principio clásico de sobrecarga progresiva."""
    if df_ejer.empty:
        return None

    match = re.match(r"([\d.]+)kg x (\d+) \(RIR (\d+)\)", str(df_ejer.iloc[0]["meta"]))
    if not match:
        return None

    peso_last = float(match.group(1))
    reps_last = int(match.group(2))
    rir_last = int(match.group(3))

    if rir_last <= 1:
        return (f"💪 **Sube el peso:** la última vez llegaste casi al fallo (RIR {rir_last}). "
                f"Hoy prueba **{peso_last + 2.5:.1f} kg × {reps_last} reps**.")
    if rir_last >= 4:
        return (f"⚡ **Te sobró margen** (RIR {rir_last}). Sube directo a "
                f"**{peso_last + 5:.1f} kg × {reps_last} reps**, o añade una serie extra hoy.")
    return (f"🎯 **Progresión en reps:** buen margen (RIR {rir_last}). Antes de subir peso, "
            f"intenta **{peso_last:.1f} kg × {reps_last + 1} reps**.")


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> tuple[str, str]:
    with st.sidebar:
        st.markdown(
            f'<h1 style="font-family:Space Grotesk, sans-serif; color:#35d68c; '
            f'letter-spacing:2px; font-size:1.5rem; margin-bottom:0;">{APP_NAME.split()[0].upper()} OS</h1>',
            unsafe_allow_html=True,
        )
        st.caption(f"v{APP_VERSION} · Apex Edition")
        st.divider()

        st.markdown(f"👤 **{st.session_state.user['name']}**", unsafe_allow_html=True)
        if st.button("🔓 Cerrar sesión", use_container_width=True):
            st.session_state["logged_in"] = False
            st.rerun()

        st.divider()

        if _get_secret_api_key() is None:
            with st.expander("🔑 Configurar entrenador IA", expanded=not bool(st.session_state.get("manual_api_key"))):
                st.caption("Tu key solo vive en esta sesión de navegador, no se guarda en ningún servidor.")
                key_input = st.text_input(
                    "Anthropic API Key", type="password",
                    value=st.session_state.get("manual_api_key", ""),
                    help="Consíguela en console.anthropic.com",
                )
                if key_input:
                    st.session_state["manual_api_key"] = key_input
        else:
            st.success("🟢 Entrenador IA activo")

        st.divider()
        modulo = st.radio("Sistema:", MODULES, label_visibility="collapsed")
        st.divider()
        st.caption("🔒 Cada operador ve solo su propio historial.")

    return st.session_state.user["id"], modulo


# ============================================================
# MÓDULO: NEURAL READINESS
# ============================================================

def render_readiness(user: str) -> None:
    st.markdown('<div class="section-title">🧠 Evaluación Diaria del Sistema Nervioso (Readiness)</div>', unsafe_allow_html=True)
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

            if st.form_submit_button("Calcular y guardar readiness"):
                score = (sueno / 8.0 * 30) + (calidad * 3) + ((11 - doms) * 2.5) + ((11 - estres) * 1.5)
                if hrv > 0:
                    score = (score * 0.8) + min(hrv / 80.0 * 20, 20)
                score = min(max(score, 10), 100)
                save_readiness(user, sueno, calidad, doms, estres, hrv, score, nota_r)
                st.success(f"Readiness registrado: {score:.1f}%")
                st.rerun()

    with c2:
        df_r = load_readiness(user)
        if df_r.empty:
            st.info("Registra tu primer check-in matutino para calibrar tu algoritmo de entrenamiento.")
            return

        last_score = df_r.iloc[0]["score"]
        if last_score >= 80:
            ring_class, status, advice = ("readiness-high", "🟢 ÓPTIMO PARA ROMPER PRs",
                "Tu sistema nervioso está fresco. Es el día perfecto para máxima intensidad (RPE 9-10) o cargas pesadas.")
        elif last_score >= 60:
            ring_class, status, advice = ("readiness-mid", "🟡 ESTADO NEUTRO / NORMAL",
                "Entrena según lo planificado. Mantén el volumen de trabajo habitual (RPE 7-8). Escucha a tu cuerpo.")
        else:
            ring_class, status, advice = ("readiness-low", "🔴 ALERTA: FATIGA CENTRAL",
                "Altas probabilidades de sobreentrenamiento o lesión. Se recomienda movilidad, cardio suave Z1 o descanso.")

        st.markdown(
            f'<div class="readiness-wrap">'
            f'<div class="readiness-ring {ring_class}" style="--pct:{last_score:.0f}">'
            f'<span class="val">{last_score:.0f}%</span></div>'
            f'<div><div class="readiness-status">{status}</div>'
            f'<p style="color:var(--text-mid); margin-top:8px; max-width:320px;">{advice}</p></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.divider()

        fig_r = px.line(df_r.head(14).sort_values("id"), x="fecha", y="score", markers=True,
                         template="plotly_dark", title="Tendencia de Readiness (últimos 14 registros)")
        fig_r.update_traces(line_color="#35d68c")
        st.plotly_chart(fig_r, use_container_width=True)


# ============================================================
# MÓDULO: FUERZA
# ============================================================

def render_strength(user: str) -> None:
    st.markdown('<div class="section-title">🏋️ Entrenamiento de Fuerza</div>', unsafe_allow_html=True)
    grupos_fuerza = ["Pecho", "Espalda", "Piernas", "Glúteos", "Pantorrillas", "Hombros",
                      "Brazos", "Antebrazos", "Core", "Calistenia"]
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown('<div class="section-title">📥 Registro de Set</div>', unsafe_allow_html=True)
        grupo = st.selectbox("Grupo muscular", grupos_fuerza)
        render_body_diagram(grupo)

        with st.form("f_gym", clear_on_submit=True):
            ejer = st.selectbox("Ejercicio", DB_EXERCISES[grupo])
            c_p, c_r, c_rir = st.columns(3)
            peso = c_p.number_input("Carga (kg)", 0.0, 500.0, 40.0, 2.5)
            reps = c_r.number_input("Reps", 1, 50, 10)
            rir = c_rir.number_input("RIR (reserva)", 0, 5, 2,
                                      help="Repeticiones que sentiste que podías haber hecho antes del fallo.")
            rpe = 10 - rir

            if st.form_submit_button("Registrar set"):
                tonelaje = peso * reps
                save_entry(user, f"Fuerza-{grupo}", ejer, tonelaje, f"{peso}kg x {reps} (RIR {rir})", f"RPE {rpe}")
                st.session_state["ultimo_peso"] = peso
                st.session_state["ultimas_reps"] = reps
                st.success(f"Set de {ejer} guardado. Tonelaje: {tonelaje:.0f} kg.")

        info = DB_EXERCISE_INFO.get(ejer)
        if info:
            st.caption(f"💡 **Trabaja:** {info[0]} — {info[1]}")

        st.divider()
        st.markdown(f"#### 📜 Historial — {ejer}")
        df_ejer = load_entries(user)
        df_ejer = df_ejer[df_ejer["actividad"] == ejer] if not df_ejer.empty else df_ejer

        if not df_ejer.empty:
            pr = df_ejer["valor"].max()
            pr_row = df_ejer[df_ejer["valor"] == pr].iloc[0]
            st.metric("🏆 Récord de tonelaje (carga × reps)", f"{pr:.0f} kg", help=f"Logrado el {pr_row['fecha']}")

            sugerencia = suggest_progressive_overload(df_ejer)
            if sugerencia:
                st.info(sugerencia)

            st.dataframe(df_ejer[["fecha", "meta", "extra"]].head(5), use_container_width=True, hide_index=True)
        else:
            st.caption("Aún no tienes sets registrados de este ejercicio. Este será tu primer PR.")

    with c2:
        st.markdown('<div class="section-title">🧮 Estimación 1RM (Algoritmo Brzycki)</div>', unsafe_allow_html=True)
        p_rm = st.number_input("Peso para cálculo", 1.0, 500.0,
                                float(st.session_state.get("ultimo_peso", 100.0)))
        r_rm = st.number_input("Reps para cálculo", 1, 12,
                                int(st.session_state.get("ultimas_reps", 5)))
        res_rm = p_rm / (1.0278 - (0.0278 * r_rm)) if r_rm < 37 else p_rm

        st.markdown(f'<p class="rm-giant">{round(res_rm, 1)} KG</p>', unsafe_allow_html=True)
        st.divider()
        st.write("**Zonas de intensidad sugeridas:**")
        st.write(f"🔴 **95% (Máxima fuerza):** {round(res_rm*0.95, 1)} kg · "
                  f"🟠 **85% (Fuerza):** {round(res_rm*0.85, 1)} kg · "
                  f"🟢 **70% (Hipertrofia):** {round(res_rm*0.7, 1)} kg")
        st.divider()
        st.markdown("#### 🔥 Series de calentamiento sugeridas")
        st.write("1. Barra vacía / ligero × 12 reps (movilidad y activación)")
        st.write(f"2. {round(res_rm*0.4, 1)} kg × 8 reps (aproximación)")
        st.write(f"3. {round(res_rm*0.6, 1)} kg × 4 reps (preparación del SNC)")
        st.write(f"4. {round(res_rm*0.8, 1)} kg × 1 rep (potenciación post-tetánica)")
        st.caption("¿Quieres un calentamiento más completo y personalizado? Ve al módulo 🔥 AI Warm-up & Form Coach.")

    st.divider()
    st.markdown('<div class="section-title">⚖️ Balance Muscular Acumulado</div>', unsafe_allow_html=True)
    df_fuerza = load_entries(user)
    df_fuerza = df_fuerza[df_fuerza["tipo"].str.startswith("Fuerza-")] if not df_fuerza.empty else df_fuerza
    if not df_fuerza.empty:
        df_fuerza = df_fuerza.copy()
        df_fuerza["grupo"] = df_fuerza["tipo"].str.replace("Fuerza-", "", regex=False)
        balance = df_fuerza.groupby("grupo")["valor"].sum().sort_values(ascending=False).reset_index()
        fig_bal = px.bar(balance, x="grupo", y="valor", template="plotly_dark",
                          title="Tonelaje total (carga × reps) por grupo muscular",
                          color="grupo", color_discrete_sequence=px.colors.qualitative.Set2)
        fig_bal.update_layout(showlegend=False)
        st.plotly_chart(fig_bal, use_container_width=True)
        top_grupo = balance.iloc[0]["grupo"]
        bajo_grupo = balance.iloc[-1]["grupo"]
        if len(balance) > 1:
            st.caption(f"💡 Estás priorizando **{top_grupo}**. Si tu objetivo es un físico equilibrado, "
                       f"vigila que **{bajo_grupo}** no se quede muy rezagado.")
    else:
        st.caption("Registra tus primeros sets de fuerza para ver aquí tu balance muscular.")


# ============================================================
# MÓDULO: RUNNING
# ============================================================

def render_running(user: str) -> None:
    c_run1, c_run2 = st.columns(2)

    with c_run1:
        st.markdown('<div class="section-title">🏃 Registro de Resistencia</div>', unsafe_allow_html=True)
        with st.form("f_run", clear_on_submit=True):
            tipo_r = st.selectbox("Tipo de estímulo", DB_EXERCISES["Running"])
            dist = st.number_input("Distancia (km)", 0.1, 100.0, 5.0, 0.5)
            m_r = st.number_input("Minutos", 1, 500, 25)
            hr = st.slider("BPM medio", 60, 220, 145)

            if st.form_submit_button("Guardar run"):
                pace = m_r / dist
                pace_str = f"{int(pace)}:{int((pace % 1) * 60):02d} min/km"
                save_entry(user, "Running", tipo_r, dist, pace_str, f"{hr} BPM")
                st.session_state["ultima_dist"] = dist
                st.success("Carrera guardada permanentemente.")

        st.divider()
        st.markdown("#### 📜 Últimas carreras")
        df_run = load_entries(user)
        df_run = df_run[df_run["tipo"] == "Running"] if not df_run.empty else df_run
        if not df_run.empty:
            st.dataframe(
                df_run[["fecha", "actividad", "valor", "meta", "extra"]].head(5)
                    .rename(columns={"valor": "km", "meta": "pace", "extra": "BPM"}),
                use_container_width=True, hide_index=True,
            )
        else:
            st.caption("Aún no registras carreras. La primera aparecerá aquí.")

    with c_run2:
        st.markdown('<div class="section-title">📐 Zonas de ritmo (Karvonen simplificado)</div>', unsafe_allow_html=True)
        pb_min = st.number_input("Tu mejor tiempo en 5K (minutos)", 10.0, 60.0, 25.0, 0.5)
        pb_pace = pb_min / 5.0
        st.write(f"**Pace de referencia (5K):** {int(pb_pace)}:{int((pb_pace % 1) * 60):02d} min/km")
        st.divider()

        zonas = {
            "🟢 Z1 Recuperación": pb_pace * 1.4,
            "🔵 Z2 Base aeróbica": pb_pace * 1.25,
            "🟡 Z3 Tempo": pb_pace * 1.1,
            "🟠 Z4 Umbral": pb_pace * 1.03,
            "🔴 Z5 VO2 Max": pb_pace * 0.95,
        }
        for zona, p in zonas.items():
            st.write(f"**{zona}:** {int(p)}:{int((p % 1) * 60):02d} min/km")

        st.divider()
        peso_run = st.session_state.user.get("weight", 75)
        dist_ref = st.session_state.get("ultima_dist", 0)
        cal = round(dist_ref * peso_run * 1.036)
        st.metric("🔥 Calorías estimadas (última carrera)", f"{cal} kcal")
        st.caption("Estimación metabólica aproximada (MET running ≈ 1.036 kcal/kg/km).")


# ============================================================
# MÓDULO: COMBATE Y EXPLOSIVIDAD
# ============================================================

def render_combat(user: str) -> None:
    st.subheader("⏱️ Temporizador Táctico de Combate")
    preset = st.radio(
        "Preset rápido",
        ["Personalizado", "Tabata Clásico (8x20/10)", "Boxeo Amateur (3x180/60)", "HIIT Largo (5x240/60)"],
        horizontal=True,
    )
    presets_map = {
        "Tabata Clásico (8x20/10)": (8, 20 / 60, 10),
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

    if st.button("🔔 Iniciar rounds"):
        ph = st.empty()
        for r in range(1, rds + 1):
            for t in range(int(w_t * 60), 0, -1):
                ph.markdown(f'<div class="timer-display work-active">ROUND {r}<br>{t//60:02d}:{t%60:02d}</div>',
                            unsafe_allow_html=True)
                time.sleep(1)
            if r < rds:
                for t in range(r_t, 0, -1):
                    ph.markdown(f'<div class="timer-display">REST<br>00:{t:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
        ph.success("🔥 Combate finalizado con éxito")
        save_entry(user, "Combate-Rounds", preset, rds, f"{rds} rounds", f"{w_t}min trabajo / {r_t}s desc.")

    st.divider()
    st.subheader("⚡ Biblioteca de Explosividad y Potencia")
    with st.form("f_ex", clear_on_submit=True):
        ej_ex = st.selectbox("Ejercicio de potencia", DB_EXERCISES["Explosividad"])
        reps_ex = st.slider("Reps explosivas", 1, 30, 6)
        lastre = st.number_input("Lastre extra (kg)", 0, 100, 0)
        if st.form_submit_button("Registrar potencia"):
            save_entry(user, "Combate", ej_ex, reps_ex, f"{reps_ex} reps", f"{lastre}kg lastre")
            st.success("Registro guardado permanentemente.")

    df_comb = load_entries(user)
    df_comb = df_comb[df_comb["tipo"].str.startswith("Combate")] if not df_comb.empty else df_comb
    if not df_comb.empty:
        st.markdown("#### 📜 Historial reciente")
        st.dataframe(df_comb[["fecha", "actividad", "meta", "extra"]].head(5), use_container_width=True, hide_index=True)


# ============================================================
# MÓDULO: MOVILIDAD
# ============================================================

def render_mobility(user: str) -> None:
    st.markdown('<div class="section-title">🧘 Sesión de Movilidad y Regeneración</div>', unsafe_allow_html=True)
    st.caption("La recuperación también es entrenamiento. Registra tus sesiones de movilidad y recuperación activa.")

    c1, c2 = st.columns([1, 1])
    with c1:
        with st.form("f_mov", clear_on_submit=True):
            mov = st.selectbox("Ejercicio de movilidad", DB_EXERCISES["Movilidad"])
            dur = st.slider("Duración (minutos)", 1, 60, 10)
            sensacion = st.select_slider("Sensación al terminar", options=["Tenso", "Normal", "Suelto", "Óptimo"])
            if st.form_submit_button("Registrar sesión"):
                save_entry(user, "Movilidad", mov, dur, f"{dur} min", sensacion)
                st.success(f"Sesión de {mov} guardada.")

        info = DB_EXERCISE_INFO.get(mov)
        if info:
            st.caption(f"💡 **Enfoque:** {info[0]} — {info[1]}")

    with c2:
        st.markdown("#### 🔄 Rutina rápida sugerida (5 min)")
        st.write("1. **Movilidad de cadera:** 60s por lado")
        st.write("2. **Movilidad torácica:** 60s en rodillas")
        st.write("3. **Estiramiento isquiotibiales:** 60s por lado")
        st.write("4. **Movilidad de hombro:** 60s con banda o pica")
        st.write("5. **Respiración diafragmática:** 60s (downregulation del SNC)")
        st.info("Ideal antes de entrenar o como cierre de un día de descanso.")


# ============================================================
# MÓDULO: NUTRICIÓN
# ============================================================

def render_nutrition(user: str) -> None:
    st.markdown('<div class="section-title">🍎 Motor Metabólico & Gestión de Combustible</div>', unsafe_allow_html=True)
    st.caption("El rendimiento deportivo requiere precisión calórica e hidratación óptima.")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### 🧮 Calculadora TDEE y objetivos")
        peso_act = st.number_input("Tu peso actual (kg)", 40.0, 160.0, float(st.session_state.user["weight"]))
        altura_act = st.number_input("Altura (cm)", 140, 220, int(st.session_state.user["height"]))
        edad_act = st.number_input("Edad", 15, 80, int(st.session_state.user["age"]))
        actividad = st.selectbox("Nivel de actividad física", [
            "Sedentario (poco o ningún ejercicio)",
            "Ligero (1-3 días/semana)",
            "Moderado (3-5 días/semana)",
            "Intenso (6-7 días/semana)",
            "Atleta de élite (dobles sesiones)",
        ], index=2)

        mult_map = {
            "Sedentario (poco o ningún ejercicio)": 1.2,
            "Ligero (1-3 días/semana)": 1.375,
            "Moderado (3-5 días/semana)": 1.55,
            "Intenso (6-7 días/semana)": 1.725,
            "Atleta de élite (dobles sesiones)": 1.9,
        }

        tmb = 10 * peso_act + 6.25 * altura_act - 5 * edad_act + 5
        tdee = tmb * mult_map[actividad]

        st.metric("🔥 Calorías de mantenimiento (TDEE)", f"{tdee:.0f} kcal/día")
        st.write(f"📉 **Déficit (perder grasa):** {tdee-500:.0f} kcal | 📈 **Superávit (ganar masa):** {tdee+300:.0f} kcal")
        st.write(f"💧 **Meta de hidratación recomendada:** {(peso_act * 0.04):.1f} litros/día")

    with c2:
        st.markdown("#### 📥 Registro diario de ingesta")
        with st.form("f_nutricion", clear_on_submit=True):
            cal_in = st.number_input("Calorías totales ingeridas", 0, 10000, 2500, 50)
            prot_in = st.number_input("Proteínas (g)", 0, 500, 160, 5)
            carb_in = st.number_input("Carbohidratos (g)", 0, 1000, 250, 10)
            fat_in = st.number_input("Grasas (g)", 0, 300, 70, 5)
            agua_in = st.number_input("Agua consumida (litros)", 0.0, 10.0, 3.0, 0.25)
            if st.form_submit_button("Guardar macros del día"):
                save_nutrition(user, cal_in, prot_in, carb_in, fat_in, agua_in)
                st.success("Ingesta registrada en el historial metabólico.")

        df_nut = load_nutrition(user)
        if not df_nut.empty:
            st.markdown("#### 📜 Historial nutricional reciente")
            st.dataframe(
                df_nut[["fecha", "calorias", "proteina", "carbs", "grasa", "agua_l"]].head(5)
                    .rename(columns={"calorias": "Kcal", "proteina": "Prot(g)", "carbs": "Carbs(g)",
                                      "grasa": "Grasa(g)", "agua_l": "Agua(L)"}),
                use_container_width=True, hide_index=True,
            )


# ============================================================
# MÓDULO: AI WARM-UP & FORM COACH (NUEVO)
# ============================================================

def render_ai_warmup(user: str) -> None:
    st.markdown('<div class="section-title">🔥 AI Warm-up & Form Coach</div>', unsafe_allow_html=True)
    st.caption("Genera un calentamiento personalizado antes de entrenar y resuelve dudas de técnica al instante.")

    client = get_ai_client()
    if client is None:
        st.warning("Configura el entrenador IA en la barra lateral (🔑 Configurar entrenador IA) para usar este módulo.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 🌡️ Generador de calentamiento")
        grupo_focus = st.selectbox("¿Qué vas a entrenar hoy?", list(DB_EXERCISES.keys()))
        render_body_diagram(grupo_focus)
        duracion = st.slider("Minutos disponibles para calentar", 3, 20, 8)
        molestia = st.selectbox("¿Alguna molestia hoy?",
                                 ["Ninguna", "Hombro", "Rodilla", "Espalda baja", "Cadera", "Otra"])
        intensidad = st.select_slider("Intensidad de la sesión de hoy", options=["Suave", "Moderada", "Alta", "Máxima"])

        if st.button("🔥 Generar calentamiento", use_container_width=True):
            if client is None:
                st.warning("Configura el entrenador IA en la barra lateral (🔑 Configurar entrenador IA) primero.")
            else:
                prompt = (
                    f"Soy un atleta que va a entrenar '{grupo_focus}' hoy, con intensidad {intensidad.lower()}. "
                    f"Tengo {duracion} minutos disponibles para calentar. Molestia física a considerar: {molestia}. "
                    "Actúa como preparador físico experto. Dame un calentamiento progresivo en tres bloques "
                    "(movilidad general, activación específica del grupo muscular, y potenciación previa al trabajo "
                    "principal), en formato de lista numerada con tiempos o repeticiones aproximadas en cada ejercicio. "
                    "Sé breve, concreto y responde en español."
                )
                resultado = call_ai(client, prompt)
                if resultado:
                    st.session_state["ultimo_calentamiento"] = resultado
                    st.session_state["ultimo_calentamiento_meta"] = (grupo_focus, intensidad, molestia)

        if "ultimo_calentamiento" in st.session_state:
            st.markdown(
                f'<div class="ia-card ia-amber"><div class="ia-tag">🔥 Calentamiento sugerido</div>'
                f'{st.session_state["ultimo_calentamiento"]}</div>',
                unsafe_allow_html=True,
            )
            if st.button("💾 Guardar en mi historial"):
                g, i, m = st.session_state.get("ultimo_calentamiento_meta", (grupo_focus, intensidad, molestia))
                save_entry(user, "IA-Calentamiento", g, 0, i, m)
                st.success("Calentamiento guardado en tu historial.")

    with col2:
        st.markdown("#### 💬 Pregúntale a tu entrenador IA")
        st.caption("Dudas de técnica, dolor durante el ejercicio, sustituciones de ejercicios, etc.")

        if "chat_coach" not in st.session_state:
            st.session_state["chat_coach"] = []

        chat_box = st.container(height=320)
        with chat_box:
            for rol, msg in st.session_state["chat_coach"]:
                with st.chat_message(rol):
                    st.write(msg)

        pregunta = st.chat_input("Ej: ¿Cómo evito que me duela la muñeca en press banca?")
        if pregunta:
            st.session_state["chat_coach"].append(("user", pregunta))

            if client is None:
                respuesta = ("⚠️ Configura tu entrenador IA en la barra lateral "
                             "(🔑 Configurar entrenador IA) para que pueda responderte.")
            else:
                system = (
                    "Eres un entrenador personal y fisioterapeuta deportivo experto. Respondes en español, "
                    "de forma breve, clara y práctica, priorizando siempre la seguridad. Si detectas una posible "
                    "lesión seria, recomienda consultar a un profesional de la salud de forma presencial."
                )
                respuesta = call_ai(client, pregunta, system=system) or \
                    "No pude generar una respuesta, inténtalo de nuevo."
            st.session_state["chat_coach"].append(("assistant", respuesta))
            st.rerun()


# ============================================================
# MÓDULO: BIBLIOTECA DE EJERCICIOS
# ============================================================

def render_library() -> None:
    st.markdown('<div class="section-title">📚 Biblioteca de Ejercicios y Biomecánica</div>', unsafe_allow_html=True)
    total_ejercicios = sum(len(v) for v in DB_EXERCISES.values())
    st.caption(f"Consulta técnica y grupo muscular de cada ejercicio disponible en la app · "
               f"**{total_ejercicios} ejercicios** en {len(DB_EXERCISES)} categorías.")

    if "favoritos" not in st.session_state:
        st.session_state["favoritos"] = set()

    cat_sel = st.selectbox("Categoría", list(DB_EXERCISES.keys()))
    busqueda = st.text_input("🔍 Buscar ejercicio por nombre")
    solo_fav = st.checkbox("⭐ Mostrar solo favoritos")

    lista = DB_EXERCISES[cat_sel]
    if busqueda:
        lista = [e for e in lista if busqueda.lower() in e.lower()]
    if solo_fav:
        lista = [e for e in lista if e in st.session_state["favoritos"]]

    if not lista:
        st.info("No se encontraron ejercicios con esos filtros.")

    for ej in lista:
        info = DB_EXERCISE_INFO.get(ej, ("Consulta con tu entrenador", "Aún no hay descripción técnica cargada."))
        col_a, col_b = st.columns([6, 1])
        with col_a:
            st.markdown(f"**{ej}**")
            st.caption(f"🎯 Grupo: {info[0]}")
            st.caption(f"📝 Técnica: {info[1]}")
        with col_b:
            es_fav = ej in st.session_state["favoritos"]
            if st.button("⭐" if es_fav else "☆", key=f"fav_{ej}"):
                if es_fav:
                    st.session_state["favoritos"].discard(ej)
                else:
                    st.session_state["favoritos"].add(ej)
                st.rerun()
        st.divider()


# ============================================================
# MÓDULO: OBJETIVOS Y RACHA
# ============================================================

def render_goals(user: str) -> None:
    st.markdown('<div class="section-title">🎯 Objetivos, Racha y Medallas</div>', unsafe_allow_html=True)
    df_all = load_entries(user)
    fechas = pd.to_datetime(df_all["fecha"]).dt.date.unique() if not df_all.empty else []
    racha = compute_streak(df_all)

    c1, c2, c3 = st.columns(3)
    c1.metric("🔥 Racha actual", f"{racha} días")
    c2.metric("📦 Sesiones totales", len(df_all))
    meta_semanal = st.number_input("Meta semanal (sesiones)", 1, 14, 4)

    hoy = datetime.now().date()
    semana = [d for d in fechas if (hoy - d).days < 7]
    c3.metric("✅ Esta semana", f"{len(semana)}/{meta_semanal}")
    st.progress(min(len(semana) / meta_semanal, 1.0))

    st.divider()
    st.markdown('<div class="section-title">🏅 Sistema de Logros del Operador</div>', unsafe_allow_html=True)

    badges = [
        ("🏆", "Iniciado", 1, len(df_all), "Registra tu primera sesión"),
        ("🔥", "Constante", 3, racha, "Alcanza una racha de 3 días"),
        ("🌙", "Disciplina Total", 7, racha, "Alcanza una racha de 7 días"),
        ("⚡", "Imparable", 25, len(df_all), "Acumula 25 sesiones"),
        ("🧬", "Atleta Élite", 100, len(df_all), "Acumula 100 sesiones"),
        ("💎", "Leyenda MorphAI", 250, len(df_all), "Acumula 250 sesiones"),
    ]
    cols_badges = st.columns(3)
    for i, (icon, nombre, meta_b, actual_b, descr) in enumerate(badges):
        with cols_badges[i % 3]:
            desbloqueado = actual_b >= meta_b
            st.markdown(f"**{icon} {nombre}** {'✅' if desbloqueado else ''}")
            st.progress(min(actual_b / meta_b, 1.0))
            st.caption(f"{min(actual_b, meta_b)}/{meta_b} · {descr}")

    st.divider()
    st.markdown('<div class="section-title">⚖️ Registro Corporal</div>', unsafe_allow_html=True)
    with st.form("f_metric", clear_on_submit=True):
        cm1, cm2, cm3, cm4 = st.columns(4)
        peso_m = cm1.number_input("Peso (kg)", 30.0, 250.0, float(st.session_state.user["weight"]), 0.1)
        grasa_m = cm2.number_input("% Grasa (opcional)", 0.0, 60.0, 15.0, 0.5)
        cintura_m = cm3.number_input("Cintura (cm, opcional)", 0.0, 200.0, 80.0, 0.5)
        brazo_m = cm4.number_input("Brazo (cm, opcional)", 0.0, 80.0, 38.0, 0.5)
        nota_m = st.text_input("Nota", "")

        if st.form_submit_button("Guardar medición"):
            nota_completa = f"{nota_m} | Cintura:{cintura_m}cm Brazo:{brazo_m}cm".strip(" |")
            save_metric(user, peso_m, grasa_m, nota_completa)
            st.session_state.user["weight"] = peso_m
            st.success("Medición guardada.")

    df_metrics = load_metrics(user)
    if not df_metrics.empty:
        fig_m = px.line(df_metrics, x="fecha", y="peso", markers=True, template="plotly_dark",
                         title="Evolución de peso corporal (kg)")
        fig_m.update_traces(line_color="#35d68c")
        st.plotly_chart(fig_m, use_container_width=True)
        with st.expander("Ver historial completo de mediciones"):
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)
    else:
        st.info("Registra tu primera medición para ver tu evolución de peso aquí.")


# ============================================================
# MÓDULO: AI ROUTINE COACH
# ============================================================

def render_ai_routine_coach(user: str) -> None:
    st.markdown('<div class="section-title">🤖 AI Routine Coach</div>', unsafe_allow_html=True)
    st.caption("Describe tu rutina actual en texto y/o sube una foto. La IA la analizará biomecánicamente "
               "y propondrá una versión mejorada.")

    client = get_ai_client()
    if client is None:
        st.warning("Configura el entrenador IA en la barra lateral (🔑 Configurar entrenador IA) para usar este módulo.")

    objetivo = st.selectbox("Objetivo principal", ["Hipertrofia", "Fuerza máxima", "Pérdida de grasa",
                                                      "Resistencia / Híbrido"])
    nivel = st.select_slider("Nivel", options=["Principiante", "Intermedio", "Avanzado"])
    dias_disp = st.slider("Días disponibles por semana", 1, 7, 4)

    st.markdown("**Preguntas rápidas de contexto:**")
    qc1, qc2, qc3 = st.columns(3)
    lesion = qc1.selectbox("¿Alguna molestia/lesión?", ["Ninguna", "Hombro", "Rodilla", "Espalda baja", "Otra"])
    equipo = qc2.selectbox("Equipo disponible", ["Gym completo", "Mancuernas/casa", "Solo peso corporal"])
    tiempo_sesion = qc3.selectbox("Tiempo por sesión", ["30 min", "45 min", "60 min", "90+ min"])

    rutina_texto = st.text_area("Describe tu rutina actual (días, ejercicios, series/reps)", height=150)
    foto = st.file_uploader("O sube una foto de tu rutina o pizarra", type=["png", "jpg", "jpeg"])

    if st.button("🧠 Analizar y mejorar con IA"):
        if client is None:
            st.warning("Configura el entrenador IA en la barra lateral (🔑 Configurar entrenador IA) primero.")
        elif not rutina_texto and not foto:
            st.warning("Describe tu rutina en texto o sube una foto para poder analizarla.")
        else:
            image_b64, media_type = None, "image/jpeg"
            if foto is not None:
                image_b64 = base64.b64encode(foto.read()).decode("utf-8")
                media_type = "image/png" if foto.type == "image/png" else "image/jpeg"

            prompt = (
                f"Soy un atleta de nivel {nivel}, mi objetivo es {objetivo}. "
                f"Dispongo de {dias_disp} días por semana, sesiones de {tiempo_sesion}, equipo: {equipo}. "
                f"Molestia física a considerar: {lesion}. "
                f"Esta es mi rutina actual: {rutina_texto or '(ver imagen adjunta)'}. "
                "Actúa como fisiólogo del ejercicio y entrenador de élite. Analiza la rutina, señala 2-3 puntos "
                "débiles concretos (ej. balance de empuje/tirón, volumen basura o selección de ejercicios), y "
                "propón una versión mejorada organizada por día, indicando series, reps, RIR sugerido y tiempos "
                "de descanso. Sé riguroso y breve. Responde en español."
            )
            resultado = call_ai(client, prompt, image_b64=image_b64, media_type=media_type)
            if resultado:
                st.session_state["ultimo_plan_ia"] = resultado
                st.session_state["ultimo_plan_meta"] = (objetivo, nivel)

    if "ultimo_plan_ia" in st.session_state:
        st.markdown(
            f'<div class="ia-card"><div class="ia-tag">🧬 Plan mejorado por IA</div>'
            f'{st.session_state["ultimo_plan_ia"]}</div>',
            unsafe_allow_html=True,
        )
        if st.button("💾 Guardar este plan en mi historial"):
            obj, niv = st.session_state.get("ultimo_plan_meta", (objetivo, nivel))
            save_entry(user, "IA-Plan", obj, 0, niv, "Plan generado por IA")
            st.success("Plan guardado en tu historial exitosamente.")

    df_planes = load_entries(user)
    df_planes = df_planes[df_planes["tipo"] == "IA-Plan"] if not df_planes.empty else df_planes
    if not df_planes.empty:
        with st.expander(f"📁 Historial de planes generados ({len(df_planes)})"):
            st.dataframe(
                df_planes[["fecha", "actividad", "meta"]].rename(columns={"actividad": "objetivo", "meta": "nivel"}),
                use_container_width=True, hide_index=True,
            )


# ============================================================
# MÓDULO: RESUMEN SEMANAL IA
# ============================================================

def render_ai_weekly_report(user: str) -> None:
    st.markdown('<div class="section-title">🗞️ Resumen Semanal IA</div>', unsafe_allow_html=True)
    st.caption("Tu entrenador IA analiza los últimos 7 días de entrenamiento, readiness y nutrición, y te dice "
               "qué funcionó, qué vigilar y en qué enfocarte la semana que viene.")

    client = get_ai_client()
    if client is None:
        st.warning("Configura el entrenador IA en la barra lateral (🔑 Configurar entrenador IA) para generar el resumen.")

    limite = datetime.now().date() - timedelta(days=7)

    df_e = load_entries(user)
    df_e = df_e[pd.to_datetime(df_e["fecha"]).dt.date >= limite] if not df_e.empty else df_e

    df_r = load_readiness(user)
    df_r = df_r[pd.to_datetime(df_r["fecha"]).dt.date >= limite] if not df_r.empty else df_r

    df_n = load_nutrition(user)
    df_n = df_n[pd.to_datetime(df_n["fecha"]).dt.date >= limite] if not df_n.empty else df_n

    readiness_prom = df_r["score"].mean() if not df_r.empty else None
    cal_prom = df_n["calorias"].mean() if not df_n.empty else None

    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Sesiones esta semana", len(df_e))
    c2.metric("🧠 Readiness promedio", f"{readiness_prom:.0f}%" if readiness_prom is not None else "N/A")
    c3.metric("🍎 Calorías promedio/día", f"{cal_prom:.0f}" if cal_prom is not None else "N/A")

    if df_e.empty and df_r.empty and df_n.empty:
        st.info("Todavía no hay datos esta semana. Registra al menos un entrenamiento o check-in "
                "para poder generar tu resumen.")
        return

    st.divider()
    if st.button("🧠 Generar resumen semanal", use_container_width=True):
        if client is None:
            st.warning("Configura el entrenador IA en la barra lateral primero.")
        else:
            resumen_entrenos = (df_e[["fecha", "tipo", "actividad", "meta"]].to_string(index=False)
                                 if not df_e.empty else "Sin entrenamientos registrados esta semana.")
            resumen_readiness = (df_r[["fecha", "score"]].to_string(index=False)
                                  if not df_r.empty else "Sin check-ins de readiness esta semana.")
            resumen_nutricion = (df_n[["fecha", "calorias", "proteina"]].to_string(index=False)
                                  if not df_n.empty else "Sin registros de nutrición esta semana.")

            prompt = (
                "Eres un entrenador de élite haciendo el check-in semanal de un atleta. Estos son sus datos "
                f"de los últimos 7 días:\n\nENTRENAMIENTOS:\n{resumen_entrenos}\n\n"
                f"READINESS (0-100%):\n{resumen_readiness}\n\nNUTRICIÓN (calorías y proteína en g):\n{resumen_nutricion}\n\n"
                "Escribe un resumen semanal breve en español con tres secciones tituladas exactamente así: "
                "'✅ Lo que funcionó', '⚠️ Puntos de atención' y '🎯 Foco para la próxima semana'. "
                "Sé directo y concreto, basándote solo en los datos de arriba, sin inventar cifras que no aparezcan."
            )
            resultado = call_ai(client, prompt)
            if resultado:
                st.session_state["ultimo_resumen_semanal"] = resultado

    if "ultimo_resumen_semanal" in st.session_state:
        st.markdown(
            f'<div class="ia-card ia-cyan"><div class="ia-tag">🗞️ Resumen de tu semana</div>'
            f'{st.session_state["ultimo_resumen_semanal"]}</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# MÓDULO: ANALÍTICA GLOBAL
# ============================================================

def render_analytics(user: str) -> None:
    df = load_entries(user)
    if df.empty:
        st.info("Todavía no hay datos que graficar. Registra tus entrenamientos para encender la telemetría.")
        return

    st.markdown('<div class="section-title">📈 Performance Telemetry</div>', unsafe_allow_html=True)
    fig1 = px.line(df.sort_values("id"), x="fecha", y="valor", color="tipo", markers=True,
                   template="plotly_dark", title="Evolución de carga / volumen en el tiempo")
    fig1.update_traces(line_color="#35d68c")
    st.plotly_chart(fig1, use_container_width=True)

    c_a1, c_a2 = st.columns(2)
    fig2 = px.pie(df, names="tipo", hole=0.6, title="Balance del atleta por módulo",
                  color_discrete_sequence=["#35d68c", "#00d4ff", "#ff4b4b", "#f5a623", "#a86bff"])
    c_a1.plotly_chart(fig2, use_container_width=True)

    fig3 = px.bar(df, x="actividad", y="valor", color="tipo", title="Volumen acumulado por ejercicio / actividad")
    c_a2.plotly_chart(fig3, use_container_width=True)

    st.divider()
    st.markdown('<div class="section-title">🏆 Récords Personales (PRs Máximos)</div>', unsafe_allow_html=True)
    prs = df.groupby("actividad")["valor"].max().sort_values(ascending=False).head(10)
    st.dataframe(
        prs.reset_index().rename(columns={"actividad": "Ejercicio/Actividad", "valor": "Mejor marca registrada"}),
        use_container_width=True, hide_index=True,
    )


# ============================================================
# MÓDULO: GESTIÓN DE DATOS Y BACKUP
# ============================================================

def render_data_management(user: str) -> None:
    st.markdown('<div class="section-title">🛠️ Administración de Datos y Copias de Seguridad</div>', unsafe_allow_html=True)
    st.caption("Gestiona tu base de datos local SQLite, exporta reportes para tu entrenador o elimina registros erróneos.")

    tab1, tab2 = st.tabs(["📦 Exportar Datos", "🗑️ Eliminar Registros Erróneos"])

    with tab1:
        st.write("Descarga tu historial completo en formato CSV compatible con Excel, Google Sheets y software de coaching.")
        df_export = load_entries(user)
        if not df_export.empty:
            csv = df_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Descargar historial de entrenamientos (CSV)",
                data=csv,
                file_name=f"morphai_log_{st.session_state.user['name'].lower().replace(' ', '_')}_"
                          f"{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.warning("No hay datos para exportar.")

    with tab2:
        st.write("Si cometiste un error en un registro anterior, búscalo por ID y bórralo de forma permanente.")
        df_all = load_entries(user)
        if not df_all.empty:
            st.dataframe(df_all[["id", "fecha", "tipo", "actividad", "meta", "extra"]],
                         use_container_width=True, hide_index=True)
            id_borrar = st.number_input("ID del registro a eliminar", min_value=1, step=1)
            if st.button("🗑️ Eliminar registro definitivamente", type="primary"):
                delete_record("entries", id_borrar, user)
                st.success(f"Registro ID {id_borrar} eliminado correctamente.")
                time.sleep(1)
                st.rerun()
        else:
            st.info("La base de datos está limpia.")


# ============================================================
# CABECERA
# ============================================================

def render_header(user: str) -> None:
    df_home = load_entries(user)
    total = len(df_home)
    racha = compute_streak(df_home)
    nombre_mostrar = st.session_state.user["name"]

    df_readiness = load_readiness(user)
    readiness_val = f"{df_readiness.iloc[0]['score']:.0f}%" if not df_readiness.empty else "N/A"

    st.markdown(f"""
    <div class="hero-card">
        <div>
            <div class="hero-eyebrow">MorphAI · Telemetría y Rendimiento v{APP_VERSION}</div>
            <p class="hero-title">Hola, {nombre_mostrar} 👋</p>
            <p class="hero-sub">Sistema neural activo. Selecciona un módulo en el menú lateral para gestionar tu día atlético.</p>
        </div>
        <div class="hero-stats">
            <div class="stat-chip"><span class="num">{total}</span><span class="lbl">Sesiones</span></div>
            <div class="stat-chip chip-cyan"><span class="num">{readiness_val}</span><span class="lbl">Readiness</span></div>
            <div class="stat-chip chip-amber"><span class="num">🔥 {racha}</span><span class="lbl">Racha</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# ENRUTADOR PRINCIPAL
# ============================================================

MODULE_HANDLERS = {
    "🧠 Neural Readiness & Sueño": render_readiness,
    "🏋️ Entrenamiento de Fuerza": render_strength,
    "🏃 Running Telemetry": render_running,
    "🥊 Combate & Explosividad": render_combat,
    "🧘 Movilidad & Recuperación": render_mobility,
    "🍎 Nutrición & Macros": render_nutrition,
    "🔥 AI Warm-up & Form Coach": render_ai_warmup,
    "🎯 Objetivos & Racha": render_goals,
    "🤖 AI Routine Coach": render_ai_routine_coach,
    "🗞️ Resumen Semanal IA": render_ai_weekly_report,
    "📊 Analítica Global": render_analytics,
    "🛠️ Gestión de Datos & Backup": render_data_management,
}


# ============================================================
# LOGIN / SELECCIÓN DE OPERADOR
# ============================================================

def render_login_screen() -> None:
    """Pantalla de entrada simple: nombre + apellido identifican al operador (sin correo ni
    contraseña, sin tocar ninguna tabla nueva de la base de datos), y de paso se recogen los
    datos básicos para que el TDEE y el 1RM ya tengan algo con qué calcular desde el primer día."""
    st.markdown("""
    <div style="text-align:center; margin-top:6vh; margin-bottom:26px;">
        <div style="font-size:3.4rem;">🧬</div>
        <p style="font-family:'Space Grotesk',sans-serif; font-size:1.9rem; font-weight:800; margin:8px 0 6px 0;
                   background:linear-gradient(90deg,#eef2f0 25%, var(--signal) 60%, var(--signal-2) 100%);
                   -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
            MorphAI Performance OS
        </p>
        <p style="color:var(--text-mid); font-size:0.95rem;">
            Escribe tus datos para empezar. Cada nombre + apellido tiene su propio historial, aislado del resto.
        </p>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Nombre", placeholder="Ej: Josías", key="perfil_nombre")
            apellido = c2.text_input("Apellido", placeholder="Ej: Martínez", key="perfil_apellido")

            c3, c4, c5 = st.columns(3)
            peso = c3.number_input("Peso (kg)", 30.0, 250.0, 75.0, 0.5, key="perfil_peso")
            altura = c4.number_input("Altura (cm)", 140, 220, 175, key="perfil_altura")
            edad = c5.number_input("Edad", 12, 90, 25, key="perfil_edad")

            if st.button("🚀 Entrar", use_container_width=True, type="primary"):
                if not nombre.strip() or not apellido.strip():
                    st.warning("Escribe al menos tu nombre y apellido.")
                else:
                    operador_id = f"{nombre.strip()}_{apellido.strip()}".lower().replace(" ", "_")
                    st.session_state["user"] = {
                        "id": operador_id,
                        "name": f"{nombre.strip().title()} {apellido.strip().title()}",
                        "weight": peso,
                        "height": altura,
                        "age": edad,
                    }
                    st.session_state["logged_in"] = True
                    st.rerun()


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

def main() -> None:
    apply_custom_css()
    ensure_schema()

    if not st.session_state.get("logged_in"):
        render_login_screen()
        return

    # El identificador único de cada operador es "nombre_apellido"; el nombre completo solo se usa para mostrar.
    operador_id, modulo = render_sidebar()
    render_header(operador_id)

    if modulo == "📚 Biblioteca de Ejercicios":
        render_library()
    else:
        MODULE_HANDLERS[modulo](operador_id)

    nombre_mostrar = st.session_state.user["name"]
    st.markdown("---")
    st.markdown(f"**{APP_NAME.upper()} v{APP_VERSION} APEX** | Operador activo: **{nombre_mostrar}** | © 2026")


if __name__ == "__main__":
    main()
