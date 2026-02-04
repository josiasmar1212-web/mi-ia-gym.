import streamlit as st
import pandas as pd
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN DE PÁGINA Y MOTOR VISUAL ---
st.set_page_config(page_title="MorphAI Social Pro v8.0", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    
    /* Fondo y Base */
    .stApp { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    /* Títulos Neón */
    .main-title { font-family: 'Orbitron', sans-serif; color: #00ff88; text-align: center; font-size: 3.8rem; letter-spacing: 15px; margin-bottom: 0px; text-shadow: 0px 0px 25px rgba(0, 255, 136, 0.5); }
    .quote-style { font-style: italic; text-align: center; color: #00ff88; font-size: 1.1rem; opacity: 0.8; margin-bottom: 30px; }
    
    /* Contenedores Pro */
    .glass-card { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8); }
    
    /* Temporizador */
    .timer-display { font-size: 6.5rem; text-align: center; font-family: 'Orbitron'; border-radius: 25px; padding: 40px; border: 5px solid #ff4b4b; color: #ff4b4b; margin: 25px 0; background: rgba(255, 75, 75, 0.05); transition: 0.5s; }
    .work-mode { border-color: #00ff88 !important; color: #00ff88 !important; box-shadow: 0px 0px 50px rgba(0, 255, 136, 0.4); background: rgba(0, 255, 136, 0.05); }
    
    /* Panel 1RM */
    .rm-display { background: linear-gradient(180deg, rgba(0, 255, 136, 0.15) 0%, rgba(0, 255, 136, 0.0) 100%); border: 2px solid #00ff88; padding: 50px; border-radius: 30px; text-align: center; margin-bottom: 40px; }
    .rm-val { font-family: 'Orbitron', sans-serif; color: #00ff88; font-size: 5.5rem; margin: 10px 0; text-shadow: 0px 0px 15px rgba(0, 255, 136, 0.6); }
    .rm-label { color: #00ff88; letter-spacing: 8px; font-weight: bold; font-size: 1.2rem; }
    
    /* Sidebar */
    .stSidebar { background-color: #0a0a0a !important; border-right: 1px solid rgba(0, 255, 136, 0.2); }
    </style>
""", unsafe_allow_html=True)

# --- 2. BASE DE DATOS E INVENTARIO DE EJERCICIOS ---
if 'historial_sesion' not in st.session_state: st.session_state['historial_sesion'] = []
if 'records_social' not in st.session_state: st.session_state['records_social'] = {}

# Biblioteca Expandida 2026
DATA_MASTER = {
    "🏋️ PESAS": {
        "Pecho": ["Press Banca Plano Barra", "Press Inclinado Mancuernas", "Aperturas en Cable", "Fondos Lastrados", "Chest Press (Máquina)", "Push-ups Explosivas"],
        "Espalda": ["Dominadas Pro (Lastre)", "Remo Pendlay", "Remo en Punta", "Jalón al Pecho (Agarre Neutro)", "Peso Muerto Convencional", "Pull-over Cuerda"],
        "Piernas": ["Sentadilla High Bar", "Prensa 45°", "Peso Muerto Rumano", "Sentadilla Búlgara", "Zancadas Caminando", "Extensiones Cuádriceps", "Curl Femoral"],
        "Hombros": ["Press Militar Barra", "Elevaciones Laterales Cable", "Face Pulls Pro", "Press Arnold", "Pájaros Posterior"],
        "Brazos": ["Curl Barra Z", "Press Francés", "Martillo con Cuerda", "Tríceps Polea (Barra V)", "Curl Araña", "Dips de Tríceps"]
    },
    "🥊 CONTACTO": {
        "Potencia Inferior": ["Saltos al Cajón (60cm+)", "Broad Jumps (Salto Longitud)", "Sentadilla con Salto (30% RM)", "Kettlebell Swings Pesados"],
        "Impacto Superior": ["Flexiones Pliométricas (Palmada)", "Medball Wall Ball", "Landmine Press (Punch Tech)", "Slam Ball (Impacto Total)"],
        "Rotación Core": ["Woodchoppers en Cable", "Rotación Landmine", "Medball Rotational Throw", "Russian Twist con Peso"]
    }
}

# --- 3. LÓGICA DE NAVEGACIÓN (SIDEBAR) ---
with st.sidebar:
    st.markdown('<h1 style="color:#00ff88; font-family:Orbitron; text-align:center;">MORPHAI</h1>', unsafe_allow_html=True)
    st.markdown("---")
    usuario = st.text_input("👤 IDENTIFICACIÓN ATLETA:", value="OPERADOR_ALPHA").strip().upper()
    st.markdown("---")
    modalidad = st.radio("📡 MÓDULO ACTIVO:", ["POWER & HYPERTRAPHY", "ENDURANCE TECH", "COMBAT EXPLOSIVITY"])
    st.markdown("---")
    if st.button("🚨 FORMATEAR SESIÓN"):
        st.session_state['historial_sesion'] = []
        st.rerun()
    st.success(f"Conectado: {usuario}")

# --- 4. CABECERA DINÁMICA ---
st.markdown('<h1 class="main-title">MORPHAI SYSTEM</h1>', unsafe_allow_html=True)
frases = [
    "EL SUDOR ES LA GRASA LLORANDO.",
    "LA MENTE FALLA MIL VECES ANTES QUE EL CUERPO.",
    "NO ENTRENAS PARA SER MEJOR QUE ELLOS, SINO MEJOR QUE AYER.",
    "DISCIPLINA SOBRE MOTIVACIÓN. SIEMPRE."
]
st.markdown(f'<p class="quote-style">"{frases[int(time.time()/5) % len(frases)]}"</p>', unsafe_allow_html=True)

tabs = st.tabs(["⚡ ENTRENAMIENTO", "🧠 PLANIFICACIÓN IA", "📊 ANALÍTICA", "🧮 MÓDULO 1RM", "🏆 HALL OF FAME"])

# --- TAB 1: ENTRENAMIENTO (LÓGICA LARGA) ---
with tabs[0]:
    if modalidad == "POWER & HYPERTRAPHY":
        st.subheader("🛠️ Registro de Cargas Dinámicas")
        with st.form("form_gym", clear_on_submit=True):
            col1, col2 = st.columns(2)
            grupo = col1.selectbox("Grupo Muscular Focus", list(DATA_MASTER["🏋️ PESAS"].keys()))
            ejer = col2.selectbox("Ejercicio (Base de Datos)", DATA_MASTER["🏋️ PESAS"][grupo])
            
            c3, c4, c5 = st.columns(3)
            peso = c3.number_input("Carga (kg)", 0.0, 600.0, 60.0, step=2.5)
            reps = c4.number_input("Reps Logradas", 1, 100, 10)
            rpe = c5.select_slider("RPE (Intensidad)", options=list(range(1, 11)), value=8)
            
            tempo = st.text_input("Tempo de Ejecución (Excéntrica-Isométrica-Concéntrica)", "3-1-1-0")
            
            if st.form_submit_button("REGISTRAR SET"):
                vol = peso * reps
                st.session_state['historial_sesion'].append({
                    "Usuario": usuario, "Tipo": "Pesas", "Actividad": ejer, 
                    "Dato": f"{peso}kg x {reps}", "Meta": f"RPE {rpe}", 
                    "Extra": f"Tempo {tempo}", "Valor": vol, "Timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.toast("Serie guardada en el núcleo.")

    elif modalidad == "ENDURANCE TECH":
        st.subheader("🏃 Monitor de Resistencia")
        with st.form("form_run", clear_on_submit=True):
            c_r1, c_r2 = st.columns(2)
            dist = c_r1.number_input("Distancia Total (km)", 0.1, 150.0, 5.0)
            objetivo_r = c_r2.selectbox("Tipo de Estímulo", ["Z2 (Quema Grasa)", "Umbral Lactato", "Series VO2 Max", "Tempo Run"])
            
            c_r3, c_r4, c_r5 = st.columns(3)
            m = c_r3.number_input("Minutos", 0, 600, 25)
            s = c_r4.number_input("Segundos", 0, 59, 0)
            bpm = c_r5.number_input("Promedio BPM", 40, 220, 145)
            
            if st.form_submit_button("GUARDAR SESIÓN CARDIO"):
                t_dec = m + (s/60)
                ritmo = t_dec / dist
                ritmo_str = f"{int(ritmo)}:{int((ritmo%1)*60):02d} min/km"
                st.session_state['historial_sesion'].append({
                    "Usuario": usuario, "Tipo": "Running", "Actividad": f"Run {objetivo_r}", 
                    "Dato": f"{dist}km @ {ritmo_str}", "Meta": f"{bpm} BPM", 
                    "Extra": f"Pace: {ritmo_str}", "Valor": dist, "Timestamp": datetime.now().strftime("%H:%M:%S")
                })

    elif modalidad == "COMBATE EXPLOSIVITY":
        st.subheader("🥊 Temporizador de Rounds Pro (Green Mode)")
        tc1, tc2, tc3 = st.columns(3)
        rounds = tc1.number_input("Cantidad de Rounds", 1, 20, 3)
        t_w = tc2.number_input("Tiempo Trabajo (min)", 1, 10, 3)
        t_r = tc3.number_input("Tiempo Descanso (seg)", 10, 120, 30)
        
        if st.button("🔥 ACTIVAR CAMPANA"):
            timer_ph = st.empty()
            for r in range(1, rounds + 1):
                # TRABAJO
                for t in range(t_w * 60, 0, -1):
                    timer_ph.markdown(f'<div class="timer-display work-mode">ROUND {r}<br>{t//60:02d}:{t%60:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
                # DESCANSO
                if r < rounds:
                    st.toast("¡DESCANSO! RECUPERA.")
                    for t in range(t_r, 0, -1):
                        timer_ph.markdown(f'<div class="timer-display">DESCANSANDO<br>00:{t:02d}</div>', unsafe_allow_html=True)
                        time.sleep(1)
            timer_ph.success("✅ MISIÓN CUMPLIDA, GUERRERO.")

        st.divider()
        st.subheader("⚡ Registro de Potencia Pliométrica")
        with st.form("form_combat", clear_on_submit=True):
            cat_ex = st.selectbox("Categoría Explosiva", list(DATA_MASTER["🥊 CONTACTO"].keys()))
            ejer_ex = st.selectbox("Ejercicio Potencia", DATA_MASTER["🥊 CONTACTO"][cat_ex])
            c_ex1, c_ex2 = st.columns(2)
            peso_ex = c_ex1.number_input("Peso/Lastre (kg)", 0, 200, 0)
            reps_ex = c_ex2.number_input("Reps (Explosión)", 1, 30, 5)
            if st.form_submit_button("REGISTRAR POTENCIA"):
                st.session_state['historial_sesion'].append({
                    "Usuario": usuario, "Tipo": "Contacto", "Actividad": ejer_ex, 
                    "Dato": f"{peso_ex}kg - {reps_ex} reps", "Meta": "Máxima Velocidad", 
                    "Extra": "Foco S.N.C.", "Valor": peso_ex if peso_ex > 0 else reps_ex, "Timestamp": datetime.now().strftime("%H:%M:%S")
                })

    # VISUALIZACIÓN DE TABLA DE PROGRESO INMEDIATA
    if st.session_state['historial_sesion']:
        st.markdown("### 📊 BITÁCORA DE ESTA SESIÓN")
        df_sesion = pd.DataFrame(st.session_state['historial_sesion'])
        st.dataframe(df_sesion[df_sesion["Usuario"] == usuario], use_container_width=True)

# --- TAB 2: PLANIFICACIÓN IA (MÓDULO LARGO) ---
with tabs[1]:
    st.subheader("🧠 Generador de Ciclos de Entrenamiento")
    col_p1, col_p2 = st.columns(2)
    objetivo = col_p1.selectbox("¿Cuál es tu meta principal?", ["Hipertrofia Estética", "Fuerza Absoluta", "Potencia para Ring/Octágono", "Acondicionamiento Híbrido"])
    frecuencia = col_p2.select_slider("Días por semana", options=[3, 4, 5, 6])
    
    if st.button("🧬 GENERAR MICRO-CICLO"):
        config_ia = {
            "Hipertrofia Estética": {"Metodología": "Arnold Split / PPL", "Rango": "8-12 reps", "Descanso": "90s", "Técnica": "Sobrecarga Progresiva"},
            "Fuerza Absoluta": {"Metodología": "5/3/1 o Starting Strength", "Rango": "1-5 reps", "Descanso": "3-5 min", "Técnica": "Cargas Submáximas"},
            "Potencia para Ring/Octágono": {"Metodología": "Pliometría + Pesas", "Rango": "3-6 reps", "Descanso": "2 min", "Técnica": "Velocidad de Ejecución"},
            "Acondicionamiento Híbrido": {"Metodología": "AMRAP / EMOM", "Rango": "Variable", "Descanso": "30-60s", "Técnica": "Densidad de Trabajo"}
        }
        res = config_ia[objetivo]
        st.success(f"Plan de {objetivo} generado con éxito.")
        
        c_p1, c_p2, c_p3, c_p4 = st.columns(4)
        c_p1.metric("SISTEMA", res["Metodología"])
        c_p2.metric("REPS", res["Rango"])
        c_p3.metric("REST", res["Descanso"])
        c_p4.metric("FOCO", res["Técnica"])
        
        for i in range(1, frecuencia + 1):
            st.markdown(f'<div class="routine-box" style="border-left: 5px solid #00ff88; padding:15px; background:rgba(0,255,136,0.05); margin-top:10px;"><b>DÍA {i}:</b> Entrenamiento enfocado en {res["Metodología"]} - Aplicar {res["Técnica"]}</div>', unsafe_allow_html=True)

# --- TAB 4: MÓDULO 1RM (EL QUE PEDISTE CON COLOR Y STATS) ---
with tabs[3]:
    st.markdown('<div class="rm-display">', unsafe_allow_html=True)
    st.markdown('<p class="rm-label">ANALIZADOR DE FUERZA MÁXIMA</p>', unsafe_allow_html=True)
    
    col_rm1, col_rm2 = st.columns(2)
    p_rm_in = col_rm1.number_input("Peso Movido (kg)", 1.0, 600.0, 100.0, step=1.0)
    r_rm_in = col_rm2.number_input("Repeticiones (1-12)", 1, 12, 5)
    
    # Cálculo Brzycki (Pro)
    rm_final = p_rm_in / (1.0278 - (0.0278 * r_rm_in))
    
    st.markdown(f'<h1 class="rm-val">{round(rm_final, 1)} KG</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #888;">CAPACIDAD NEUROMUSCULAR ESTIMADA</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("📈 Zonas de Entrenamiento Basadas en 1RM")
    z1, z2, z3, z4 = st.columns(4)
    z1.metric("FUERZA EXPLOSIVA (90%)", f"{round(rm_final*0.9, 1)} kg", "Power")
    z2.metric("HIPERTROFIA (80%)", f"{round(rm_final*0.8, 1)} kg", "Muscle")
    z3.metric("POTENCIA (70%)", f"{round(rm_final*0.7, 1)} kg", "Speed")
    z4.metric("RESISTENCIA (60%)", f"{round(rm_final*0.6, 1)} kg", "Endurance")
    
    # Tabla Estadística Pro
    st.markdown("#### 📑 Tabla de Intensidad para Programación")
    stats_rm = {
        "Porcentaje (%)": ["100%", "95%", "85%", "75%", "65%", "55%"],
        "Carga Sugerida (kg)": [f"{round(rm_final*p,1)} kg" for p in [1, 0.95, 0.85, 0.75, 0.65, 0.55]],
        "Rango de Reps": ["1 rep", "2-3 reps", "5-6 reps", "8-10 reps", "12-15 reps", "20+ reps"],
        "Efecto Fisiológico": ["Fuerza Máxima", "Potencia", "Fuerza-Masa", "Hipertrofia", "Resistencia Muscular", "Capilarización"]
    }
    st.table(pd.DataFrame(stats_rm))

# --- TAB 3: ANALÍTICA (GRÁFICOS PRO) ---
with tabs[2]:
    st.subheader("📊 Análisis de Rendimiento Longitudinal")
    if st.session_state['historial_sesion']:
        df_ana = pd.DataFrame(st.session_state['historial_sesion'])
        df_user = df_ana[df_ana["Usuario"] == usuario]
        
        if not df_user.empty:
            # Gráfico de Líneas Evolutivo
            fig_evol = px.line(df_user, x="Timestamp", y="Valor", color="Actividad", markers=True, 
                               template="plotly_dark", title="Evolución de Intensidad por Ejercicio")
            fig_evol.update_traces(line_color='#00ff88', marker=dict(size=10, bordercolor="white", borderwidth=2))
            st.plotly_chart(fig_evol, use_container_width=True)
            
            col_g1, col_g2 = st.columns(2)
            # Distribución de Trabajo
            fig_pie = px.pie(df_user, names='
