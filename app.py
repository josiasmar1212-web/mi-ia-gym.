
"""
MorphAI Performance OS — V2.0
Dashboard fitness con IA, entrenamiento, progresión, readiness, nutrición,
running, recuperación, analítica, objetivos y exportación.

Ejecutar:
    pip install -r requirements.txt
    streamlit run app.py

IA opcional:
    .streamlit/secrets.toml
    ANTHROPIC_API_KEY = "sk-ant-..."
"""

from __future__ import annotations

import base64
import io
import json
import sqlite3
import time
from datetime import date, datetime, timedelta
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


# ============================================================
# CONFIG
# ============================================================

APP_NAME = "MorphAI"
APP_VERSION = "20.0"
DB_PATH = "morphai.db"
AI_MODEL = "claude-sonnet-4-5-20250929"
AI_MAX_TOKENS = 2200

MODULES = [
    "🏠 Dashboard",
    "🏋️ Entrenamiento",
    "📈 Progreso",
    "🧠 Readiness",
    "🍎 Nutrición",
    "🏃 Running",
    "🧘 Recuperación",
    "🤖 AI Coach",
    "📚 Ejercicios",
    "🎯 Objetivos",
    "📊 Analítica",
    "⚙️ Datos",
]

EXERCISES = {
    "Pecho": [
        "Press Banca Plano", "Press Banca Inclinado", "Press Mancuernas",
        "Aperturas Polea", "Fondos en Paralelas", "Press Declinado"
    ],
    "Espalda": [
        "Dominadas", "Remo Pendlay", "Remo con Mancuerna", "Jalón al Pecho",
        "Peso Muerto Convencional", "Remo en T"
    ],
    "Piernas": [
        "Sentadilla Barra", "Peso Muerto Sumo", "Prensa 45°", "Zancadas Búlgaras",
        "Curl Femoral", "Extensión Cuádriceps", "Hip Thrust"
    ],
    "Hombros": [
        "Press Militar", "Elevaciones Laterales", "Pájaros Posteriores",
        "Press Arnold", "Face Pull"
    ],
    "Brazos": [
        "Curl Barra Z", "Curl Martillo", "Press Francés",
        "Fondos Tríceps", "Curl Predicador"
    ],
    "Core": [
        "Plancha Frontal", "Rueda Abdominal", "Elevación de Piernas",
        "Russian Twist", "Plancha Lateral"
    ],
}

EXERCISE_INFO = {
    "Press Banca Plano": ("Pecho · tríceps · deltoide anterior",
                          "Escápulas estables, pies firmes y recorrido controlado."),
    "Press Banca Inclinado": ("Pecho superior · tríceps",
                              "Mantén el hombro estable y evita perder tensión."),
    "Sentadilla Barra": ("Cuádriceps · glúteos · core",
                         "Rodillas acompañan la dirección de los pies y torso estable."),
    "Peso Muerto Convencional": ("Cadena posterior",
                                 "Barra cercana al cuerpo y columna neutra."),
    "Peso Muerto Sumo": ("Glúteos · aductores · isquios",
                         "Base amplia y empuje del suelo."),
    "Dominadas": ("Dorsal · bíceps",
                  "Inicia con las escápulas y lleva los codos hacia las costillas."),
    "Remo Pendlay": ("Espalda media · dorsal",
                     "Torso estable y barra hacia la zona baja del torso."),
    "Hip Thrust": ("Glúteo mayor",
                   "Extiende la cadera sin hiperextender la zona lumbar."),
    "Press Militar": ("Hombro · tríceps · core",
                      "Glúteos y abdomen activos, evitando compensaciones."),
    "Elevaciones Laterales": ("Deltoide lateral",
                              "Movimiento controlado sin convertirlo en un balanceo."),
}


# ============================================================
# PAGE + CSS
# ============================================================

st.set_page_config(
    page_title=f"{APP_NAME} Performance OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

def css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --bg:#070b09;
        --panel:#0d1411;
        --panel2:#111b16;
        --line:rgba(119,255,185,.13);
        --green:#45e695;
        --green2:#9bffc7;
        --text:#f2f6f4;
        --muted:#87968e;
        --orange:#ffb454;
        --red:#ff6d78;
        --blue:#65b8ff;
    }

    .stApp {
        background:
          radial-gradient(circle at 85% 0%, rgba(69,230,149,.07), transparent 30%),
          radial-gradient(circle at 0% 25%, rgba(101,184,255,.035), transparent 25%),
          var(--bg);
        color:var(--text);
        font-family:'DM Sans',sans-serif;
    }

    h1,h2,h3,h4 { font-family:'Space Grotesk',sans-serif !important; }
    [data-testid="stSidebar"] {
        background:linear-gradient(180deg,#09100d,#070b09);
        border-right:1px solid var(--line);
    }
    [data-testid="stSidebar"] * { font-family:'DM Sans',sans-serif; }

    .brand {
        padding:4px 0 18px;
        border-bottom:1px solid var(--line);
        margin-bottom:18px;
    }
    .brand-name {
        color:var(--green);
        font-family:'Space Grotesk',sans-serif;
        font-weight:700;
        font-size:1.65rem;
        letter-spacing:1.5px;
    }
    .brand-sub {
        color:var(--muted);
        font-size:.76rem;
        letter-spacing:1px;
        text-transform:uppercase;
    }

    .hero {
        position:relative;
        overflow:hidden;
        border:1px solid var(--line);
        background:
          linear-gradient(135deg,rgba(69,230,149,.09),transparent 45%),
          linear-gradient(160deg,#111a15,#0b110e);
        border-radius:22px;
        padding:30px;
        margin-bottom:22px;
        box-shadow:0 18px 50px rgba(0,0,0,.22);
    }
    .hero:after {
        content:"";
        position:absolute;
        width:230px;height:230px;
        right:-100px;top:-100px;
        border-radius:50%;
        border:1px solid rgba(69,230,149,.18);
        box-shadow:0 0 0 35px rgba(69,230,149,.025),0 0 0 70px rgba(69,230,149,.015);
    }
    .eyebrow {
        color:var(--green);
        font-size:.72rem;
        font-weight:700;
        letter-spacing:2px;
        text-transform:uppercase;
    }
    .hero-title {
        font-family:'Space Grotesk',sans-serif;
        font-size:2.25rem;
        font-weight:700;
        margin:5px 0;
    }
    .hero-text { color:var(--muted); max-width:720px; }
    .hero-badge {
        display:inline-block;
        margin-top:12px;
        padding:8px 12px;
        border:1px solid var(--line);
        border-radius:999px;
        color:var(--green2);
        background:rgba(69,230,149,.06);
        font-size:.78rem;
    }

    .card {
        background:linear-gradient(145deg,#101813,#0c120f);
        border:1px solid var(--line);
        border-radius:18px;
        padding:20px;
        min-height:112px;
        box-shadow:0 10px 30px rgba(0,0,0,.15);
    }
    .card-label {
        color:var(--muted);
        font-size:.73rem;
        text-transform:uppercase;
        letter-spacing:1.2px;
    }
    .card-value {
        font-family:'Space Grotesk',sans-serif;
        font-size:1.85rem;
        font-weight:700;
        margin-top:5px;
    }
    .card-note { color:var(--muted); font-size:.78rem; margin-top:3px; }

    .section {
        border:1px solid var(--line);
        background:rgba(13,20,17,.86);
        border-radius:18px;
        padding:22px;
        margin:10px 0 20px;
    }
    .section-title {
        font-family:'Space Grotesk',sans-serif;
        font-weight:700;
        font-size:1.1rem;
        margin-bottom:2px;
    }
    .section-sub { color:var(--muted); font-size:.82rem; margin-bottom:15px; }

    .score {
        text-align:center;
        border-radius:18px;
        padding:24px 12px;
        border:1px solid var(--line);
        background:linear-gradient(145deg,rgba(69,230,149,.09),rgba(69,230,149,.025));
    }
    .score-number {
        font-family:'Space Grotesk',sans-serif;
        font-size:3.8rem;
        font-weight:700;
        color:var(--green);
        line-height:1;
    }
    .score-label { color:var(--muted); margin-top:7px; }

    .coach {
        border-left:3px solid var(--green);
        border-top:1px solid var(--line);
        border-right:1px solid var(--line);
        border-bottom:1px solid var(--line);
        border-radius:14px;
        padding:18px;
        background:rgba(69,230,149,.035);
        white-space:pre-wrap;
        line-height:1.55;
    }

    .pill {
        display:inline-block;
        border-radius:999px;
        padding:5px 9px;
        font-size:.72rem;
        border:1px solid var(--line);
        color:var(--green2);
        background:rgba(69,230,149,.05);
        margin-right:5px;
    }

    .tip {
        padding:13px 15px;
        border-radius:12px;
        background:rgba(101,184,255,.05);
        border:1px solid rgba(101,184,255,.15);
        color:#cfe9ff;
    }

    .stButton > button {
        border-radius:11px !important;
        font-weight:700 !important;
        min-height:42px;
    }
    .stProgress > div > div > div > div { background:var(--green); }
    div[data-testid="stMetric"] {
        background:rgba(17,27,22,.72);
        border:1px solid var(--line);
        border-radius:14px;
        padding:12px;
    }
    .block-container { padding-top:1.5rem; padding-bottom:4rem; }
    footer { visibility:hidden; }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# DATABASE
# ============================================================

@st.cache_resource
def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            fecha TEXT NOT NULL,
            tipo TEXT NOT NULL,
            actividad TEXT NOT NULL,
            valor REAL DEFAULT 0,
            meta TEXT DEFAULT '',
            extra TEXT DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metrics(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            fecha TEXT NOT NULL,
            peso REAL,
            grasa REAL,
            cintura REAL DEFAULT 0,
            brazo REAL DEFAULT 0,
            nota TEXT DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readiness(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            fecha TEXT NOT NULL,
            sueno REAL,
            calidad INTEGER,
            doms INTEGER,
            estres INTEGER,
            hrv REAL,
            score REAL,
            nota TEXT DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nutrition(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            fecha TEXT NOT NULL,
            calorias INTEGER,
            proteina REAL,
            carbs REAL,
            grasa REAL,
            agua REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS goals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            nombre TEXT NOT NULL,
            objetivo REAL,
            actual REAL DEFAULT 0,
            unidad TEXT DEFAULT '',
            deadline TEXT DEFAULT ''
        )
    """)
    conn.commit()
    return conn


def q(sql: str, params=()) -> pd.DataFrame:
    return pd.read_sql_query(sql, db(), params=params)


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def add_entry(user, tipo, actividad, valor=0, meta="", extra=""):
    db().execute(
        "INSERT INTO entries(user,fecha,tipo,actividad,valor,meta,extra) VALUES(?,?,?,?,?,?,?)",
        (user, now_str(), tipo, actividad, valor, meta, extra)
    )
    db().commit()


def entries(user):
    return q("SELECT * FROM entries WHERE user=? ORDER BY id DESC", (user,))


def save_metric(user, peso, grasa, cintura, brazo, nota):
    db().execute(
        "INSERT INTO metrics(user,fecha,peso,grasa,cintura,brazo,nota) VALUES(?,?,?,?,?,?,?)",
        (user, now_str(), peso, grasa, cintura, brazo, nota)
    )
    db().commit()


def metrics(user):
    return q("SELECT * FROM metrics WHERE user=? ORDER BY id", (user,))


def save_readiness(user, sueno, calidad, doms, estres, hrv, score, nota):
    db().execute(
        "INSERT INTO readiness(user,fecha,sueno,calidad,doms,estres,hrv,score,nota) VALUES(?,?,?,?,?,?,?,?,?)",
        (user, now_str(), sueno, calidad, doms, estres, hrv, score, nota)
    )
    db().commit()


def readiness(user):
    return q("SELECT * FROM readiness WHERE user=? ORDER BY id DESC", (user,))


def save_nutrition(user, cal, prot, carbs, grasa, agua):
    db().execute(
        "INSERT INTO nutrition(user,fecha,calorias,proteina,carbs,grasa,agua) VALUES(?,?,?,?,?,?,?)",
        (user, now_str(), cal, prot, carbs, grasa, agua)
    )
    db().commit()


def nutrition(user):
    return q("SELECT * FROM nutrition WHERE user=? ORDER BY id DESC", (user,))


# ============================================================
# MATH / ANALYTICS
# ============================================================

def e1rm(weight: float, reps: int) -> float:
    if reps <= 1:
        return weight
    if reps >= 37:
        return weight
    return weight / (1.0278 - 0.0278 * reps)


def pace_text(minutes: float, km: float) -> str:
    if km <= 0:
        return "--"
    pace = minutes / km
    mins = int(pace)
    secs = int(round((pace - mins) * 60))
    if secs == 60:
        mins += 1
        secs = 0
    return f"{mins}:{secs:02d} /km"


def readiness_score(sleep, quality, doms, stress, hrv):
    # Score de disposición basado en los datos introducidos; no diagnostica fatiga.
    base = min(sleep / 8, 1.15) * 32
    base += quality * 3.0
    base += (11 - doms) * 2.3
    base += (11 - stress) * 1.7
    if hrv > 0:
        base = base * .82 + min(hrv / 80 * 18, 18)
    return round(max(10, min(100, base)), 1)


def current_streak(df):
    if df.empty:
        return 0
    days = set(pd.to_datetime(df["fecha"]).dt.date)
    d = date.today()
    streak = 0
    while d in days:
        streak += 1
        d -= timedelta(days=1)
    return streak


def weekly_sessions(df):
    if df.empty:
        return 0
    days = set(pd.to_datetime(df["fecha"]).dt.date)
    return sum((date.today() - d).days < 7 for d in days)


def strength_df(df, exercise=None):
    if df.empty:
        return df
    x = df[df["tipo"].str.startswith("Fuerza", na=False)].copy()
    if exercise:
        x = x[x["actividad"] == exercise]
    if x.empty:
        return x
    def parse_weight(s):
        try:
            return float(str(s).split("kg")[0])
        except Exception:
            return 0
    def parse_reps(s):
        try:
            return int(str(s).split("x")[1].split()[0])
        except Exception:
            return 0
    x["peso"] = x["meta"].apply(parse_weight)
    x["reps"] = x["meta"].apply(parse_reps)
    x["e1rm"] = x.apply(lambda r: e1rm(r["peso"], int(r["reps"])), axis=1)
    x["volumen"] = x["peso"] * x["reps"]
    return x


# ============================================================
# AI
# ============================================================

def secret_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return None


def ai_client():
    if not ANTHROPIC_AVAILABLE:
        return None
    key = secret_key() or st.session_state.get("manual_api_key")
    return anthropic.Anthropic(api_key=key) if key else None


def call_ai(client, prompt, system=None, image_b64=None, media_type="image/jpeg"):
    content = []
    if image_b64:
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": image_b64}
        })
    content.append({"type": "text", "text": prompt})
    try:
        response = client.messages.create(
            model=AI_MODEL,
            max_tokens=AI_MAX_TOKENS,
            system=system or "Eres MorphAI, un coach de fitness prudente, claro y práctico.",
            messages=[{"role": "user", "content": content}],
        )
        return "".join(x.text for x in response.content if x.type == "text")
    except Exception as exc:
        st.error(f"Error de IA: {exc}")
        return None


# ============================================================
# UI HELPERS
# ============================================================

def card(label, value, note=""):
    st.markdown(
        f'<div class="card"><div class="card-label">{label}</div>'
        f'<div class="card-value">{value}</div>'
        f'<div class="card-note">{note}</div></div>',
        unsafe_allow_html=True
    )


def title(text, sub=""):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="section-sub">{sub}</div>', unsafe_allow_html=True)


def chart_layout(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=45, b=10),
        font=dict(family="DM Sans"),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    return fig


# ============================================================
# SIDEBAR
# ============================================================

def sidebar():
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "name": "ATLETA", "weight": 80.0, "height": 180,
            "age": 20, "goal": "Hipertrofia"
        }

    with st.sidebar:
        st.markdown(
            '<div class="brand"><div class="brand-name">MORPHAI</div>'
            '<div class="brand-sub">Performance OS · V20</div></div>',
            unsafe_allow_html=True
        )

        name = st.text_input("Atleta", st.session_state.profile["name"])
        st.session_state.profile["name"] = name.strip().upper() or "ATLETA"

        st.session_state.profile["weight"] = st.number_input(
            "Peso (kg)", 30.0, 250.0, float(st.session_state.profile["weight"]), 0.5
        )
        st.session_state.profile["goal"] = st.selectbox(
            "Objetivo",
            ["Hipertrofia", "Fuerza", "Pérdida de grasa", "Rendimiento híbrido"],
            index=["Hipertrofia", "Fuerza", "Pérdida de grasa", "Rendimiento híbrido"].index(
                st.session_state.profile["goal"]
            )
        )

        st.divider()

        if secret_key():
            st.success("● IA conectada")
        else:
            with st.expander("🔑 Conectar IA"):
                st.caption("La clave manual permanece en la sesión.")
                key = st.text_input(
                    "Anthropic API Key",
                    type="password",
                    value=st.session_state.get("manual_api_key", "")
                )
                if key:
                    st.session_state.manual_api_key = key

        st.divider()
        module = st.radio("Navegación", MODULES, label_visibility="collapsed")

        st.divider()
        st.caption("SQLite local · Datos persistentes")
        return st.session_state.profile["name"], module


# ============================================================
# HERO
# ============================================================

def hero(user):
    df = entries(user)
    rd = readiness(user)
    score = f"{rd.iloc[0].score:.0f}" if not rd.empty else "--"
    st.markdown(
        f'<div class="hero">'
        f'<div class="eyebrow">MORPHAI · PERFORMANCE OS · V{APP_VERSION}</div>'
        f'<div class="hero-title">Hola, {user.title()} 👋</div>'
        f'<div class="hero-text">Tu centro de entrenamiento: rendimiento, recuperación, progreso y coaching con IA en un solo lugar.</div>'
        f'<span class="hero-badge">READINESS {score}% · {len(df)} REGISTROS</span>'
        f'</div>',
        unsafe_allow_html=True
    )


# ============================================================
# DASHBOARD
# ============================================================

def dashboard(user):
    df = entries(user)
    rd = readiness(user)
    nut = nutrition(user)
    met = metrics(user)

    score = float(rd.iloc[0]["score"]) if not rd.empty else 0
    streak = current_streak(df)
    sessions = weekly_sessions(df)

    st.markdown("## 🏠 Dashboard")
    st.caption("Una vista rápida de lo que está pasando con tu entrenamiento.")

    a,b,c,d = st.columns(4)
    with a: card("Readiness", f"{score:.0f}%" if score else "--", "Último check-in")
    with b: card("Racha", f"{streak} días", "Días consecutivos con actividad")
    with c: card("Semana", f"{sessions}", "Días activos · últimos 7 días")
    with d: card("Peso", f"{met.iloc[-1]['peso']:.1f} kg" if not met.empty else "--", "Última medición")

    st.markdown('<div class="section">', unsafe_allow_html=True)
    title("⚡ Panel de acción", "Tres cosas que puedes hacer ahora.")
    p1,p2,p3 = st.columns(3)
    with p1:
        st.markdown("**🏋️ Entrenar**")
        st.caption("Registra sets, RIR, carga y reps para alimentar tu progresión.")
    with p2:
        st.markdown("**🧠 Comprobar estado**")
        st.caption("Registra sueño, estrés, DOMS y HRV si lo tienes.")
    with p3:
        st.markdown("**🤖 Consultar IA**")
        st.caption("Pide una rutina, análisis o recomendación contextual.")
    st.markdown('</div>', unsafe_allow_html=True)

    left,right = st.columns([1,1])
    with left:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("🧠 Estado actual", "Tu último check-in, sin convertirlo en un diagnóstico.")
        if rd.empty:
            st.info("Haz tu primer check-in en Readiness.")
        else:
            cls = "🟢 Buen estado" if score >= 80 else ("🟡 Intermedio" if score >= 60 else "🔴 Bajo")
            st.markdown(
                f'<div class="score"><div class="score-number">{score:.0f}</div>'
                f'<div class="score-label">READINESS · {cls}</div></div>',
                unsafe_allow_html=True
            )
            st.progress(score / 100)
            st.caption(f"Sueño: {rd.iloc[0]['sueno']:.1f} h · Calidad: {rd.iloc[0]['calidad']}/10 · "
                       f"DOMS: {rd.iloc[0]['doms']}/10 · Estrés: {rd.iloc[0]['estres']}/10")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("📈 Actividad reciente")
        if df.empty:
            st.info("Todavía no hay actividad.")
        else:
            recent = df.head(8)[["fecha","tipo","actividad","valor"]].copy()
            recent.columns = ["Fecha","Módulo","Actividad","Valor"]
            st.dataframe(recent, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if not df.empty:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("📊 Actividad acumulada", "Carga/volumen registrado por tipo.")
        tmp = df.copy()
        tmp["fecha"] = pd.to_datetime(tmp["fecha"])
        daily = tmp.groupby(tmp["fecha"].dt.date)["valor"].sum().reset_index()
        daily.columns = ["fecha","valor"]
        fig = px.area(daily, x="fecha", y="valor")
        st.plotly_chart(chart_layout(fig), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# STRENGTH
# ============================================================

def strength(user):
    st.markdown("## 🏋️ Entrenamiento")
    st.caption("Registra cada set. MorphAI transforma tus datos en progresión.")

    df = entries(user)
    s = strength_df(df)
    exercises = [e for values in EXERCISES.values() for e in values]

    left,right = st.columns([1.05,.95])
    with left:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("Registrar set", "Guarda carga, repeticiones y esfuerzo percibido.")
        group = st.selectbox("Grupo muscular", list(EXERCISES.keys()))
        exercise = st.selectbox("Ejercicio", EXERCISES[group])
        c1,c2,c3 = st.columns(3)
        weight = c1.number_input("Carga (kg)", 0.0, 500.0, 40.0, 0.5)
        reps = c2.number_input("Reps", 1, 50, 8)
        rir = c3.number_input("RIR", 0, 5, 2)
        notes = st.text_input("Nota del set", placeholder="Ej. técnica limpia")
        if st.button("＋ Guardar set", use_container_width=True, type="primary"):
            volume = weight * reps
            est = e1rm(weight, reps)
            add_entry(
                user, f"Fuerza-{group}", exercise, volume,
                f"{weight:g}kg x {reps}", f"RIR {rir} · e1RM {est:.1f} kg · {notes}"
            )
            st.success(f"{exercise}: {weight:g} kg × {reps} guardado.")
            st.rerun()

        info = EXERCISE_INFO.get(exercise)
        if info:
            st.markdown(f'<div class="tip">💡 <b>Enfoque:</b> {info[0]}<br>{info[1]}</div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("🧮 Calculadora e1RM", "Estimación Brzycki para cargas de referencia.")
        p = st.number_input("Peso", 1.0, 500.0, 80.0, 0.5, key="calc_p")
        r = st.number_input("Repeticiones", 1, 12, 5, key="calc_r")
        rm = e1rm(p,r)
        st.markdown(f'<div class="score"><div class="score-number">{rm:.1f}</div>'
                    f'<div class="score-label">e1RM · KG</div></div>', unsafe_allow_html=True)
        x1,x2,x3 = st.columns(3)
        x1.metric("70%", f"{rm*.70:.1f} kg")
        x2.metric("80%", f"{rm*.80:.1f} kg")
        x3.metric("90%", f"{rm*.90:.1f} kg")
        st.markdown("**Calentamiento orientativo**")
        for pct,reps_w in [(0.40,8),(0.60,5),(0.75,3),(0.85,1)]:
            st.write(f"• {rm*pct:.1f} kg × {reps_w}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">', unsafe_allow_html=True)
    title("🏆 Rendimiento por ejercicio")
    if s.empty:
        st.info("Registra un set para empezar a construir tu historial.")
    else:
        selected = st.selectbox("Ejercicio a analizar", sorted(s["actividad"].unique()))
        ex = s[s["actividad"] == selected].sort_values("fecha")
        best = ex["e1rm"].max()
        max_weight = ex["peso"].max()
        total_vol = ex["volumen"].sum()
        c1,c2,c3 = st.columns(3)
        c1.metric("Mejor e1RM", f"{best:.1f} kg")
        c2.metric("Mayor carga", f"{max_weight:.1f} kg")
        c3.metric("Volumen", f"{total_vol:,.0f} kg")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ex["fecha"], y=ex["e1rm"], mode="lines+markers", name="e1RM"))
        fig = chart_layout(fig)
        fig.update_layout(title="Evolución estimada de fuerza", yaxis_title="e1RM (kg)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            ex[["fecha","peso","reps","e1rm","volumen","extra"]].tail(12),
            use_container_width=True, hide_index=True
        )
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# PROGRESS
# ============================================================

def progress(user):
    st.markdown("## 📈 Progreso")
    st.caption("No mires solamente el peso: mira fuerza, volumen y tendencia.")

    df = entries(user)
    met = metrics(user)
    s = strength_df(df)

    if s.empty and met.empty:
        st.info("Todavía no hay suficientes datos. Registra entrenamientos o mediciones.")
        return

    if not s.empty:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("Fuerza estimada")
        exercises = sorted(s["actividad"].unique())
        selected = st.multiselect("Ejercicios", exercises, default=exercises[:3])
        if selected:
            fig = go.Figure()
            for ex in selected:
                x = s[s["actividad"] == ex].sort_values("fecha")
                fig.add_trace(go.Scatter(x=x["fecha"], y=x["e1rm"], mode="lines+markers", name=ex))
            fig = chart_layout(fig)
            fig.update_layout(yaxis_title="e1RM (kg)", title="Tendencia de fuerza")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if not met.empty:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("Peso y composición")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=met["fecha"], y=met["peso"], mode="lines+markers", name="Peso"))
        if met["grasa"].fillna(0).max() > 0:
            fig.add_trace(go.Scatter(x=met["fecha"], y=met["grasa"], mode="lines+markers", name="% grasa",
                                     yaxis="y2"))
        fig.update_layout(
            title="Evolución corporal",
            yaxis_title="Peso (kg)",
            yaxis2=dict(title="% grasa", overlaying="y", side="right")
        )
        st.plotly_chart(chart_layout(fig), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# READINESS
# ============================================================

def readiness_page(user):
    st.markdown("## 🧠 Readiness")
    st.caption("Un check-in diario para contextualizar tu entrenamiento. No es una herramienta médica.")

    left,right = st.columns([1,1])
    with left:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("Check-in de hoy")
        sleep = st.number_input("Horas de sueño", 1.0, 14.0, 7.5, .5)
        quality = st.slider("Calidad del sueño", 1, 10, 8)
        doms = st.slider("DOMS / agujetas", 1, 10, 3)
        stress = st.slider("Estrés", 1, 10, 4)
        hrv = st.number_input("HRV (opcional)", 0.0, 250.0, 0.0, 1.0)
        note = st.text_input("Cómo te sientes hoy", "Normal")
        score = readiness_score(sleep,quality,doms,stress,hrv)
        st.metric("Readiness estimado", f"{score:.0f}/100")
        if st.button("Guardar check-in", use_container_width=True, type="primary"):
            save_readiness(user,sleep,quality,doms,stress,hrv,score,note)
            st.success("Check-in guardado.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("Interpretación")
        if score >= 80:
            msg = "🟢 Datos compatibles con una buena disposición para la sesión."
        elif score >= 60:
            msg = "🟡 Datos intermedios. Mantén flexibilidad y controla el esfuerzo."
        else:
            msg = "🔴 Datos bajos. Considera reducir carga/volumen si también te sientes fatigado."
        st.markdown(f'<div class="score"><div class="score-number">{score:.0f}</div>'
                    f'<div class="score-label">{msg}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    hist = readiness(user)
    if not hist.empty:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("Tendencia de readiness")
        x = hist.head(30).sort_values("fecha")
        fig = px.line(x, x="fecha", y="score", markers=True)
        st.plotly_chart(chart_layout(fig), use_container_width=True)
        st.dataframe(hist.head(14), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# NUTRITION
# ============================================================

def nutrition_page(user):
    st.markdown("## 🍎 Nutrición")
    st.caption("Estimaciones orientativas para organizar calorías, macros e hidratación.")

    p = st.session_state.profile
    c1,c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("TDEE y macros")
        weight = st.number_input("Peso", 30.0, 250.0, float(p["weight"]), .5)
        height = st.number_input("Altura", 120, 230, int(p["height"]), 1)
        age = st.number_input("Edad", 15, 90, int(p["age"]), 1)
        sex = st.selectbox("Fórmula Mifflin", ["Hombre","Mujer"])
        activity = st.selectbox("Actividad", [
            "Sedentario","Ligero","Moderado","Alto","Muy alto"
        ])
        mult = {"Sedentario":1.2,"Ligero":1.375,"Moderado":1.55,"Alto":1.725,"Muy alto":1.9}[activity]
        sgn = 5 if sex == "Hombre" else -161
        bmr = 10*weight + 6.25*height - 5*age + sgn
        tdee = bmr * mult
        goal = st.selectbox("Objetivo calórico", ["Mantenimiento","Déficit moderado","Superávit moderado"])
        target = tdee + {"Mantenimiento":0,"Déficit moderado":-350,"Superávit moderado":250}[goal]
        protein = weight * 1.8
        fat = weight * .8
        carbs = max(0,(target - protein*4 - fat*9)/4)
        x1,x2 = st.columns(2)
        x1.metric("TDEE", f"{tdee:.0f} kcal")
        x2.metric("Objetivo", f"{target:.0f} kcal")
        st.write(f"**Proteína:** {protein:.0f} g · **Grasa:** {fat:.0f} g · **Carbohidratos:** {carbs:.0f} g")
        st.caption("Las necesidades reales varían. Usa el cambio de peso y rendimiento para ajustar.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("Registrar día")
        with st.form("nutrition_form"):
            cal = st.number_input("Calorías", 0, 10000, int(target//50*50), 50)
            prot = st.number_input("Proteína (g)", 0.0, 500.0, float(protein), 5.0)
            carbs_in = st.number_input("Carbohidratos (g)", 0.0, 1000.0, float(carbs), 5.0)
            fat_in = st.number_input("Grasa (g)", 0.0, 400.0, float(fat), 5.0)
            water = st.number_input("Agua (L)", 0.0, 12.0, 2.5, .25)
            if st.form_submit_button("Guardar nutrición", use_container_width=True):
                save_nutrition(user,cal,prot,carbs_in,fat_in,water)
                st.success("Registro guardado.")
                st.rerun()
        n = nutrition(user)
        if not n.empty:
            st.dataframe(n.head(7), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# RUNNING
# ============================================================

def running(user):
    st.markdown("## 🏃 Running")
    st.caption("Registra distancia, tiempo y frecuencia cardiaca para construir tu tendencia.")

    df = entries(user)
    left,right = st.columns(2)
    with left:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("Nueva carrera")
        kind = st.selectbox("Sesión", ["Carrera fácil","Tempo","Series","Fartlek","Umbral","Recuperación"])
        km = st.number_input("Distancia (km)", .1, 100., 5., .1)
        mins = st.number_input("Tiempo (min)", 1., 600., 30., .5)
        hr = st.number_input("FC media", 40, 230, 145)
        if st.button("Guardar carrera", use_container_width=True, type="primary"):
            add_entry(user,"Running",kind,km,pace_text(mins,km),f"{hr} BPM · {mins:.1f} min")
            st.success(f"Guardado · {pace_text(mins,km)}")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("Referencia 5K")
        pb = st.number_input("Mejor 5K (min)", 10., 90., 25., .5)
        pace = pb/5
        st.metric("Ritmo 5K", pace_text(pb,5))
        st.write(f"Rodaje fácil orientativo: {pace*1.25:.2f} min/km")
        st.write(f"Tempo orientativo: {pace*1.10:.2f} min/km")
        st.write(f"Intervalos rápidos: {pace*.95:.2f} min/km")
        st.markdown('</div>', unsafe_allow_html=True)

    runs = df[df["tipo"]=="Running"] if not df.empty else df
    if not runs.empty:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("Historial")
        runs = runs.copy()
        runs["fecha"] = pd.to_datetime(runs["fecha"])
        fig = px.line(runs.sort_values("fecha"),x="fecha",y="valor",markers=True)
        fig.update_layout(yaxis_title="Distancia (km)")
        st.plotly_chart(chart_layout(fig), use_container_width=True)
        st.dataframe(runs.head(15), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# RECOVERY
# ============================================================

def recovery(user):
    st.markdown("## 🧘 Recuperación")
    st.caption("Movilidad, respiración y recuperación activa.")

    routines = {
        "Cadera": ["90/90 · 45s/lado","Estocada con extensión · 45s/lado","Respiración · 60s"],
        "Hombros": ["Rotación externa suave · 60s","Wall slides · 10 reps","Respiración · 60s"],
        "Espalda": ["Cat-cow · 10 reps","Rotación torácica · 45s/lado","Respiración · 90s"],
        "General": ["Cadera · 60s","Torácica · 60s","Hombros · 60s","Respiración · 120s"],
    }

    focus = st.selectbox("Zona", list(routines.keys()))
    st.markdown('<div class="section">', unsafe_allow_html=True)
    title("Rutina rápida · 5 minutos")
    for i,item in enumerate(routines[focus],1):
        st.write(f"**{i}.** {item}")
    if st.button("Registrar recuperación", type="primary"):
        add_entry(user,"Recuperación",focus,5,"5 min","Rutina guiada")
        st.success("Sesión registrada.")
    st.markdown('</div>', unsafe_allow_html=True)

    df = entries(user)
    rec = df[df["tipo"]=="Recuperación"] if not df.empty else df
    if not rec.empty:
        st.metric("Sesiones de recuperación", len(rec))
        st.dataframe(rec.head(10),use_container_width=True,hide_index=True)


# ============================================================
# AI COACH
# ============================================================

def ai_coach(user):
    st.markdown("## 🤖 AI Coach")
    st.caption("Coach contextual para entrenamiento, progresión, nutrición y planificación.")

    client = ai_client()
    if client is None:
        st.warning("Conecta una API key de Anthropic en la barra lateral para activar el coach.")

    df = entries(user)
    rd = readiness(user)
    profile = st.session_state.profile
    context = {
        "objetivo": profile["goal"],
        "peso": profile["weight"],
        "registros": len(df),
        "readiness": float(rd.iloc[0]["score"]) if not rd.empty else None,
        "actividad_reciente": df.head(8)[["tipo","actividad","valor","meta","extra"]].to_dict("records")
            if not df.empty else []
    }

    left,right = st.columns([1,1])
    with left:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("⚡ Acciones rápidas")
        action = st.selectbox("Qué quieres que haga", [
            "Crear entrenamiento para hoy",
            "Analizar mi progresión",
            "Optimizar mi rutina semanal",
            "Analizar recuperación",
            "Ayudarme con nutrición",
        ])
        extra = st.text_area("Contexto adicional", placeholder="Ej. hoy quiero entrenar pecho y espalda...")
        if st.button("Generar con IA", disabled=client is None, use_container_width=True, type="primary"):
            prompt = f"""
Usuario: {user}
Contexto real disponible:
{json.dumps(context, ensure_ascii=False, default=str, indent=2)}

Petición: {action}
Información adicional: {extra}

Responde en español. Sé práctico. Si propones entrenamiento, incluye ejercicios,
series, repeticiones, RIR y descansos. No diagnostiques lesiones ni prometas resultados.
Distingue entre datos registrados y recomendaciones.
"""
            result = call_ai(client,prompt)
            if result:
                st.session_state["ai_result"] = result
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        title("🧬 Resultado")
        if st.session_state.get("ai_result"):
            st.markdown(f'<div class="coach">{st.session_state["ai_result"]}</div>',
                        unsafe_allow_html=True)
        else:
            st.info("Tu próxima recomendación aparecerá aquí.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">', unsafe_allow_html=True)
    title("💬 Pregunta libre")
    if "chat" not in st.session_state:
        st.session_state.chat = []
    for role,msg in st.session_state.chat[-8:]:
        with st.chat_message(role):
            st.write(msg)
    question = st.chat_input("Ej. ¿Cómo progresaría en press banca?")
    if question:
        st.session_state.chat.append(("user",question))
        if client:
            prompt = f"Perfil: {json.dumps(context,ensure_ascii=False,default=str)}\nPregunta: {question}"
            answer = call_ai(client,prompt) or "No pude responder ahora."
        else:
            answer = "Conecta la IA para utilizar el chat."
        st.session_state.chat.append(("assistant",answer))
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# EXERCISE LIBRARY
# ============================================================

def library():
    st.markdown("## 📚 Biblioteca")
    st.caption("Ejercicios disponibles y guía técnica básica.")

    all_rows = []
    for group, items in EXERCISES.items():
        for ex in items:
            info = EXERCISE_INFO.get(ex,("—","Descripción pendiente."))
            all_rows.append({"Grupo":group,"Ejercicio":ex,"Músculos":info[0],"Técnica":info[1]})
    lib = pd.DataFrame(all_rows)
    c1,c2 = st.columns([1,2])
    group = c1.selectbox("Grupo",["Todos"]+list(EXERCISES.keys()))
    search = c2.text_input("🔎 Buscar")
    if group != "Todos":
        lib = lib[lib["Grupo"]==group]
    if search:
        lib = lib[lib["Ejercicio"].str.contains(search,case=False,na=False)]
    st.dataframe(lib,use_container_width=True,hide_index=True)


# ============================================================
# GOALS
# ============================================================

def goals(user):
    st.markdown("## 🎯 Objetivos")
    df = entries(user)
    streak = current_streak(df)
    week = weekly_sessions(df)

    a,b,c = st.columns(3)
    a.metric("Racha",f"{streak} días")
    b.metric("Días activos",f"{week}/7")
    c.metric("Registros",len(df))

    st.markdown('<div class="section">',unsafe_allow_html=True)
    title("🏅 Hitos")
    milestones = [
        ("Primer registro",1,len(df)),
        ("Constancia",7,week),
        ("25 registros",25,len(df)),
        ("100 registros",100,len(df)),
    ]
    for name,target,current in milestones:
        pct=min(current/target,1)
        st.write(f"**{name}** · {current}/{target}")
        st.progress(pct)
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="section">',unsafe_allow_html=True)
    title("⚖️ Medición corporal")
    with st.form("body_form"):
        c1,c2,c3,c4 = st.columns(4)
        weight = c1.number_input("Peso",30.,250.,float(st.session_state.profile["weight"]),.1)
        fat = c2.number_input("% grasa",0.,60.,15.,.5)
        waist = c3.number_input("Cintura",0.,200.,80.,.5)
        arm = c4.number_input("Brazo",0.,80.,35.,.5)
        note = st.text_input("Nota")
        if st.form_submit_button("Guardar medición",use_container_width=True):
            save_metric(user,weight,fat,waist,arm,note)
            st.session_state.profile["weight"]=weight
            st.success("Medición guardada.")
            st.rerun()
    m = metrics(user)
    if not m.empty:
        st.dataframe(m.tail(12),use_container_width=True,hide_index=True)
    st.markdown('</div>',unsafe_allow_html=True)


# ============================================================
# ANALYTICS
# ============================================================

def analytics(user):
    st.markdown("## 📊 Analítica")
    st.caption("Datos sin adornos: volumen, frecuencia y distribución.")

    df = entries(user)
    if df.empty:
        st.info("Necesitas registrar actividad.")
        return

    df["fecha_dt"] = pd.to_datetime(df["fecha"])
    total = df["valor"].sum()
    days = df["fecha_dt"].dt.date.nunique()
    avg = total/days if days else 0

    a,b,c,d = st.columns(4)
    a.metric("Valor acumulado",f"{total:,.0f}")
    b.metric("Días activos",days)
    c.metric("Promedio/día",f"{avg:,.0f}")
    d.metric("Módulos",df["tipo"].nunique())

    st.markdown('<div class="section">',unsafe_allow_html=True)
    title("Actividad por día")
    daily = df.groupby(df["fecha_dt"].dt.date)["valor"].sum().reset_index()
    fig = px.bar(daily,x="fecha_dt",y="valor")
    st.plotly_chart(chart_layout(fig),use_container_width=True)
    st.markdown('</div>',unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        fig = px.pie(df,names="tipo",values="valor",hole=.62)
        st.plotly_chart(chart_layout(fig),use_container_width=True)
    with c2:
        top = df.groupby("actividad")["valor"].sum().nlargest(10).reset_index()
        fig = px.bar(top,x="valor",y="actividad",orientation="h")
        st.plotly_chart(chart_layout(fig),use_container_width=True)

    s = strength_df(df)
    if not s.empty:
        st.markdown('<div class="section">',unsafe_allow_html=True)
        title("🏆 Mejores e1RM")
        prs = s.groupby("actividad")["e1rm"].max().sort_values(ascending=False).head(12).reset_index()
        prs.columns=["Ejercicio","e1RM"]
        st.dataframe(prs,use_container_width=True,hide_index=True)
        st.markdown('</div>',unsafe_allow_html=True)


# ============================================================
# DATA
# ============================================================

def data_page(user):
    st.markdown("## ⚙️ Datos")
    st.caption("Exporta tu historial y elimina registros concretos.")

    df = entries(user)
    m = metrics(user)
    r = readiness(user)
    n = nutrition(user)

    tabs = st.tabs(["📥 Exportar","🗑️ Registros","🧾 Resumen"])

    with tabs[0]:
        if df.empty:
            st.info("No hay entrenamientos para exportar.")
        else:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Descargar entrenamientos CSV",csv,
                file_name=f"morphai_{user.lower()}_{date.today()}.csv",
                mime="text/csv",use_container_width=True
            )
        bundle = {
            "entries": df.to_dict("records"),
            "metrics": m.to_dict("records"),
            "readiness": r.to_dict("records"),
            "nutrition": n.to_dict("records"),
            "exported_at": now_str()
        }
        st.download_button(
            "Descargar backup JSON completo",
            json.dumps(bundle,ensure_ascii=False,default=str,indent=2).encode("utf-8"),
            file_name=f"morphai_backup_{date.today()}.json",
            mime="application/json",use_container_width=True
        )

    with tabs[1]:
        if df.empty:
            st.info("No hay registros.")
        else:
            st.dataframe(df.head(50),use_container_width=True,hide_index=True)
            record_id = st.number_input("ID",1,int(df["id"].max()),1)
            if st.button("Eliminar registro",type="primary"):
                db().execute("DELETE FROM entries WHERE id=? AND user=?",(int(record_id),user))
                db().commit()
                st.success("Registro eliminado.")
                st.rerun()

    with tabs[2]:
        a,b,c,d = st.columns(4)
        a.metric("Entrenamientos",len(df))
        b.metric("Readiness",len(r))
        c.metric("Nutrición",len(n))
        d.metric("Mediciones",len(m))
        st.json({"usuario":user,"version":APP_VERSION,"base_de_datos":DB_PATH})


# ============================================================
# ROUTER
# ============================================================

def main():
    css()
    user,module = sidebar()
    hero(user)

    handlers = {
        "🏠 Dashboard": dashboard,
        "🏋️ Entrenamiento": strength,
        "📈 Progreso": progress,
        "🧠 Readiness": readiness_page,
        "🍎 Nutrición": nutrition_page,
        "🏃 Running": running,
        "🧘 Recuperación": recovery,
        "🤖 AI Coach": ai_coach,
        "📚 Ejercicios": lambda _: library(),
        "🎯 Objetivos": goals,
        "📊 Analítica": analytics,
        "⚙️ Datos": data_page,
    }
    handlers[module](user)

    st.markdown("---")
    st.caption(f"MORPHAI PERFORMANCE OS · V{APP_VERSION} · SQLite local · © 2026")


if __name__ == "__main__":
    main()
