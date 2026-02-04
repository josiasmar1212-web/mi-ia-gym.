import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import plotly.express as px

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="MorphAI Social Pro", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    .stApp { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; color: #00d4ff; text-align: center; font-size: 3.5rem; letter-spacing: 12px; margin-bottom: 0px; text-shadow: 0px 0px 20px rgba(0, 212, 255, 0.4); }
    .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; margin-bottom: 20px; }
    .record-card { background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 128, 255, 0.1)); border: 1px solid #00d4ff; border-radius: 15px; padding: 20px; text-align: center; }
    .rm-display { background: rgba(0, 212, 255, 0.1); border: 1px solid #00d4ff; padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 30px; }
    .timer-display { font-size: 5rem; text-align: center; font-family: 'Orbitron'; background: rgba(255, 255, 255, 0.05); border-radius: 20px; padding: 20px; margin: 10px 0; border: 2px solid #ff4b4b; color: #ff4b4b; }
    .work-mode { border-color: #00d4ff; color: #00d4ff; box-shadow: 0px 0px 20px rgba(0, 212, 255, 0.3); }
    </style>
""", unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE MEMORIA ---
if 'plan_activo' not in st.session_state: st.session_state['plan_activo'] = "Arnold Split"
if 'historial_sesion' not in st.session_state: st.session_state['historial_sesion'] = []
if 'records_social' not in st.session_state: st.session_state['records_social'] = {}

BIBLIOTECA_GYM = {
    "Pecho/Espalda": ["Press Banca", "Press Inclinado", "Aperturas", "Dominadas", "Remo con Barra", "Jalón al Pecho"],
    "Piernas": ["Sentadilla Barra", "Prensa", "Extensiones", "Curl Femoral", "Peso Muerto Rumano"],
    "Hombros/Brazos": ["Press Militar", "Elevaciones Laterales", "Curl Bíceps", "Tríceps Polea", "Martillo"]
}

EJER_EXPLOSIVOS = {
    "Potencia Piernas": ["Saltos al Cajón", "Broad Jumps", "Sentadilla Explosiva", "Kettlebell Swings"],
    "Empuje/Impacto": ["Flexiones Pliométricas", "Lanzamiento Balón Medicinal", "Landmine Press", "Slam Ball"],
    "Core/Rotación": ["Rotaciones Landmine", "Woodchoppers", "Lanzamiento Lateral Medball"]
}

# --- 3. CONEXIÓN A DATOS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_global = conn.read(worksheet="DATOS", ttl=0)
except:
    df_global = pd.DataFrame(columns=["Usuario", "Fecha", "Actividad", "Dato", "Valor"])

# --- 4. SIDEBAR (PERFIL Y MODALIDAD) ---
with st.sidebar:
    st.markdown('<h2 style="color:#00d4ff;">👤 ATLETA</h2>', unsafe_allow_html=True)
    usuario = st.text_input("Nombre de Perfil:", value="Atleta_Alpha").strip()
    st.divider()
    modalidad = st.radio("Disciplina:", ["🏋️ Pesas", "🏃 Running", "🥊 Contacto"])
    st.divider()
    if st.button("🔄 REINICIAR SESIÓN"):
        st.session_state['historial_sesion'] = []
        st.rerun()

# --- 5. CUERPO PRINCIPAL ---
st.markdown(f'<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; color:#00d4ff;">Perfil: {usuario} | Plan: {st.session_state["plan_activo"]}</p>', unsafe_allow_html=True)

tabs = st.tabs(["⚡ ENTRENAR", "🧠 PLANIFICAR", "🏆 RÉCORDS", "📊 ANALYTICS", "🧮 1RM"])

# --- TAB 1: ENTRENAR ---
with tabs[0]:
    if modalidad == "🏋️ Pesas":
        with st.form("gym_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            grupo = col1.selectbox("Grupo Muscular", list(BIBLIOTECA_GYM.keys()))
            ejer = col2.selectbox("Ejercicio", BIBLIOTECA_GYM[grupo])
            c3, c4 = st.columns(2)
            peso = c3.number_input("Peso (kg)", 0, 500, 60)
            reps = c4.number_input("Reps", 1, 50, 10)
            if st.form_submit_button("REGISTRAR SERIE"):
                key_rec = f"{usuario}_{ejer}"
                if key_rec not in st.session_state['records_social'] or peso > st.session_state['records_social'][key_rec]:
                    st.session_state['records_social'][key_rec] = peso
                    st.toast(f"🏆 ¡Nuevo récord para {usuario}!")
                st.session_state['historial_sesion'].append({"Usuario": usuario, "Fecha": datetime.now().strftime("%d/%m"), "Actividad": ejer, "Dato": f"{peso}kg x {reps}", "Valor": peso})

    elif modalidad == "🏃 Running":
        with st.form("run_form", clear_on_submit=True):
            km = st.number_input("Distancia (km)", 0.1, 100.0, 5.0)
            per = st.selectbox("Periodo", ["Base Aeróbica", "Series/Intervalos", "Tirada Larga", "Fartlek"])
            c_min, c_seg = st.columns(2)
            minutos = c_min.number_input("Minutos", 1, 600, 25)
            segundos = c_seg.number_input("Segundos", 0, 59, 0)
            if st.form_submit_button("GUARDAR RUN"):
                t_total = minutos + (segundos/60)
                ritmo = t_total / km
                ritmo_str = f"{int(ritmo)}:{int((ritmo%1)*60):02d}"
                st.session_state['historial_sesion'].append({"Usuario": usuario, "Fecha": datetime.now().strftime("%d/%m"), "Actividad": f"Run ({per})", "Dato": f"{km}km a {ritmo_str} min/km", "Valor": km})

    elif modalidad == "🥊 Contacto":
        st.subheader("⏱️ Round Timer & Explosividad")
        c_r1, c_r2, c_r3 = st.columns(3)
        n_rounds = c_r1.number_input("Rounds", 1, 15, 3)
        t_work = c_r2.number_input("Min Round", 1, 5, 3)
        t_rest = c_r3.number_input("Seg Descanso", 10, 60, 30)
        
        if st.button("🔔 INICIAR ROUNDS"):
            placeholder = st.empty()
            for r in range(1, n_rounds + 1):
                # Trabajo
                for t in range(t_work * 60, 0, -1):
                    placeholder.markdown(f'<div class="timer-display work-mode">ROUND {r}<br>{t//60:02d}:{t%60:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
                st.toast("🥊 ¡TIEMPO!")
                # Descanso
                if r < n_rounds:
                    for t in range(t_rest, 0, -1):
                        placeholder.markdown(f'<div class="timer-display">DESCANSO<br>00:{t:02d}</div>', unsafe_allow_html=True)
                        time.sleep(1)
            placeholder.success("🔥 Entrenamiento Finalizado")

        with st.form("ex_form", clear_on_submit=True):
            cat_ex = st.selectbox("Categoría Explosiva", list(EJER_EXPLOSIVOS.keys()))
            ejer_ex = st.selectbox("Movimiento de Potencia", EJER_EXPLOSIVOS[cat_ex])
            p_ex = st.number_input("Peso/Carga (kg)", 0, 100, 0)
            if st.form_submit_button("REGISTRAR POTENCIA"):
                st.session_state['historial_sesion'].append({"Usuario": usuario, "Fecha": datetime.now().strftime("%d/%m"), "Actividad": ejer_ex, "Dato": f"Explosivo: {p_ex}kg", "Valor": p_ex})

    if st.session_state['historial_sesion']:
        st.markdown("### 📋 Sesión Actual")
        st.dataframe(pd.DataFrame(st.session_state['historial_sesion']), use_container_width=True)

# --- TAB 2: PLANIFICAR ---
with tabs[1]:
    st.subheader("Seleccionar Estrategia IA")
    col_a, col_b = st.columns(2)
    if col_a.button("⚙️ ACTIVAR ARNOLD SPLIT"):
        st.session_state['plan_activo'] = "Arnold Split (Antagonistas)"
        st.rerun()
    if col_b.button("⚙️ ACTIVAR PUSH/PULL/LEGS"):
        st.session_state['plan_activo'] = "PPL (Frecuencia 2)"
        st.rerun()

# --- TAB 3: RÉCORDS ---
with tabs[2]:
    st.subheader(f"🥇 Hall of Fame: {usuario}")
    mis_recs = {k.split('_')[1]: v for k, v in st.session_state['records_social'].items() if k.startswith(usuario)}
    if mis_recs:
        cols = st.columns(len(mis_recs) if len(mis_recs) < 4 else 4)
        for i, (e, v) in enumerate(mis_recs.items()):
            cols[i % 4].markdown(f'<div class="record-card"><small>{e}</small><h2>{v} kg</h2></div>', unsafe_allow_html=True)
    else:
        st.info("Aún no tienes récords. ¡Es hora de empujar los límites!")

# --- TAB 4: ANALYTICS ---
with tabs[3]:
    st.subheader("Tu Progreso Visual")
    if st.session_state['historial_sesion']:
        df_an = pd.DataFrame(st.session_state['historial_sesion'])
        df_user = df_an[df_an["Usuario"] == usuario]
        if not df_user.empty:
            fig = px.line(df_user, x="Fecha", y="Valor", color="Actividad", markers=True, template="plotly_dark")
            fig.update_traces(line_color='#00d4ff')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sin datos para graficar. Registra tu entrenamiento primero.")

# --- TAB 5: 1RM PRO ---
with tabs[4]:
    st.subheader("Calculadora de Fuerza Máxima")
    c_rm1, c_rm2 = st.columns(2)
    p_rm = c_rm1.number_input("Peso (kg)", 1, 500, 100)
    r_rm = c_rm2.number_input("Repeticiones", 1, 12, 5)
    rm_calc = p_rm * (1 + 0.0333 * r_rm)
    
    st.markdown(f'<div class="rm-display"><h1>{round(rm_calc, 1)} kg</h1><p>TU 1RM ESTIMADO</p></div>', unsafe_allow_html=True)
    
    col_x, col_y, col_z = st.columns(3)
    col_x.metric("90% Fuerza Pura", f"{round(rm_calc*0.9, 1)} kg")
    col_y.metric("80% Hipertrofia", f"{round(rm_calc*0.8, 1)} kg")
    col_z.metric("70% Resistencia Muscular", f"{round(rm_calc*0.7, 1)} kg")
