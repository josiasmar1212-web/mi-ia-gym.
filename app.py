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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            fecha TEXT,
            peso REAL,
            grasa REAL,
            nota TEXT
        )
    """)
    conn.commit()
    return conn

conn = init_db()

def save_metric(user, peso, grasa, nota):
    conn.execute(
        "INSERT INTO metrics (user, fecha, peso, grasa, nota) VALUES (?,?,?,?,?)",
        (user, datetime.now().strftime("%Y-%m-%d %H:%M"), peso, grasa, nota)
    )
    conn.commit()

def load_metrics(user):
    return pd.read_sql_query("SELECT * FROM metrics WHERE user=? ORDER BY id", conn, params=(user,))

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

# Grupos musculares principales por categoría (para la biblioteca de ejercicios)
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
    st.session_state['user'] = {"name": "JOSIAS MARTINEZ", "weight": 80, "height": 180}
if 'metrics' not in st.session_state:
    st.session_state['metrics'] = []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown('<h1 style="font-family:Space Grotesk; color:#35d68c; letter-spacing:2px; font-size:1.6rem;">MORPHAI OS</h1>', unsafe_allow_html=True)
    st.session_state.user["name"] = st.text_input("OPERADOR:", st.session_state.user["name"]).upper()

    st.divider()
    system_mode = st.radio("SISTEMA:", [
        "🏋️ ENTRENAMIENTO DE FUERZA",
        "🏃 RUNNING TELEMETRY",
        "🥊 COMBATE & EXPLOSIVIDAD",
        "🧘 MOVILIDAD & RECUPERACIÓN",
        "📚 BIBLIOTECA DE EJERCICIOS",
        "🎯 OBJETIVOS & RACHA",
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

# --- MÓDULO: FUERZA (todos los grupos musculares) ---
if system_mode == "🏋️ ENTRENAMIENTO DE FUERZA":
    grupos_fuerza = ["Pecho", "Espalda", "Piernas", "Hombros", "Brazos", "Core", "Calistenia"]
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("### 📥 Registro de Set")
        grupo = st.selectbox("Grupo muscular", grupos_fuerza)
        with st.form("f_gym", clear_on_submit=True):
            ejer = st.selectbox("Ejercicio", DB_EXERCISES[grupo])
            c_p, c_r = st.columns(2)
            peso = c_p.number_input("Carga (kg)", 0.0, 500.0, 40.0)
            reps = c_r.number_input("Reps", 1, 50, 10)
            rpe = st.slider("Intensidad (RPE)", 1, 10, 8)
            if st.form_submit_button("REGISTRAR SET"):
                save_entry(USER, f"Fuerza-{grupo}", ejer, peso * reps, f"{peso}kg x {reps}", f"RPE {rpe}")
                st.success(f"Set de {ejer} guardado.")
        info = DB_EXERCISE_INFO.get(ejer)
        if info:
            st.caption(f"💡 **Trabaja:** {info[0]} — {info[1]}")
    with c2:
        st.markdown("### 🧮 Estimación 1RM (Algoritmo Brzycki)")
        p_rm = st.number_input("Peso para cálculo", 1.0, 500.0, 100.0)
        r_rm = st.number_input("Reps para cálculo", 1, 12, 5)
        res_rm = p_rm / (1.0278 - (0.0278 * r_rm))
        st.markdown(f'<p class="rm-giant">{round(res_rm, 1)} KG</p>', unsafe_allow_html=True)
        st.divider()
        st.write("**Zonas de intensidad sugeridas:**")
        st.write(f"🔴 95% (Máxima): {round(res_rm*0.95,1)}kg · 🟠 85% (Fuerza): {round(res_rm*0.85,1)}kg · 🟢 70% (Hipertrofia): {round(res_rm*0.7,1)}kg")

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

# --- MÓDULO: MOVILIDAD & RECUPERACIÓN ---
elif system_mode == "🧘 MOVILIDAD & RECUPERACIÓN":
    st.markdown("### 🧘 Sesión de Movilidad")
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
        if info:
            st.caption(f"💡 **Enfoque:** {info[0]} — {info[1]}")
    with c2:
        st.markdown("#### 🔄 Rutina rápida sugerida (5 min)")
        st.write("1. Movilidad de Cadera — 60s por lado")
        st.write("2. Movilidad Torácica — 60s")
        st.write("3. Estiramiento Isquiotibiales — 60s por lado")
        st.write("4. Movilidad de Hombro — 60s")
        st.write("5. Respiración Diafragmática — 60s")
        st.info("Ideal antes de entrenar o como cierre de un día de descanso.")

# --- MÓDULO: BIBLIOTECA DE EJERCICIOS ---
elif system_mode == "📚 BIBLIOTECA DE EJERCICIOS":
    st.markdown("### 📚 Biblioteca de Ejercicios")
    st.caption("Consulta técnica y grupo muscular de cada ejercicio disponible en la app.")
    categorias = list(DB_EXERCISES.keys())
    cat_sel = st.selectbox("Categoría", categorias)
    busqueda = st.text_input("🔍 Buscar ejercicio por nombre")

    lista = DB_EXERCISES[cat_sel]
    if busqueda:
        lista = [e for e in lista if busqueda.lower() in e.lower()]

    if not lista:
        st.info("No se encontraron ejercicios con ese nombre en esta categoría.")
    for ej in lista:
        info = DB_EXERCISE_INFO.get(ej, ("Consulta con tu entrenador", "Aún no hay descripción técnica cargada para este ejercicio."))
        with st.container():
            st.markdown(f"**{ej}**")
            st.caption(f"🎯 Grupo: {info[0]}")
            st.caption(f"📝 Técnica: {info[1]}")
            st.divider()

# --- MÓDULO: OBJETIVOS & RACHA ---
elif system_mode == "🎯 OBJETIVOS & RACHA":
    st.markdown("### 🎯 Objetivos & Racha")
    df_all = load_entries(USER)

    fechas = pd.to_datetime(df_all["fecha"]).dt.date.unique() if not df_all.empty else []
    racha = 0
    if len(fechas) > 0:
        dia = datetime.now().date()
        fechas_set = set(fechas)
        while dia in fechas_set:
            racha += 1
            dia = dia.fromordinal(dia.toordinal() - 1)

    c1, c2, c3 = st.columns(3)
    c1.metric("🔥 Racha actual", f"{racha} días")
    c2.metric("📦 Sesiones totales", len(df_all))
    meta_semanal = st.number_input("Meta semanal (sesiones)", 1, 14, 4)
    hoy = datetime.now().date()
    semana = [d for d in fechas if (hoy - d).days < 7]
    c3.metric("✅ Esta semana", f"{len(semana)}/{meta_semanal}")

    st.divider()
    st.markdown("### ⚖️ Registro corporal")
    with st.form("f_metric", clear_on_submit=True):
        cm1, cm2, cm3 = st.columns(3)
        peso_m = cm1.number_input("Peso (kg)", 30.0, 250.0, float(st.session_state.user["weight"]))
        grasa_m = cm2.number_input("% Grasa corporal (opcional)", 0.0, 60.0, 0.0)
        nota_m = cm3.text_input("Nota", "")
        if st.form_submit_button("GUARDAR MEDICIÓN"):
            save_metric(USER, peso_m, grasa_m, nota_m)
            st.success("Medición guardada.")

    df_metrics = load_metrics(USER)
    if not df_metrics.empty:
        fig_m = px.line(df_metrics, x="fecha", y="peso", markers=True, template="plotly_dark", title="Evolución de peso corporal")
        fig_m.update_traces(line_color="#35d68c")
        st.plotly_chart(fig_m, use_container_width=True)
    else:
        st.info("Registra tu primera medición para ver tu evolución de peso aquí.")

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
