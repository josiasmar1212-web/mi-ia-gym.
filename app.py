import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import plotly.express as px
import time

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Gym IA Elite", page_icon="🐗", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .routine-card {
        background-color: #1f2937; border-radius: 15px; padding: 20px;
        border-left: 5px solid #00d4ff; margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #1f2937 0%, #0e1117 100%);
        padding: 15px; border-radius: 10px; border: 1px solid #00d4ff; text-align: center;
    }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: #00d4ff; color: #0E1117; font-weight: bold; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
url_base = st.secrets["connections"]["gsheets"]["spreadsheet"].split("/edit")[0]

@st.cache_data(ttl=5)
def leer_csv(pestana):
    url_csv = f"{url_base}/gviz/tq?tqx=out:csv&sheet={pestana}"
    try:
        response = requests.get(url_csv)
        return pd.read_csv(StringIO(response.text)).dropna(axis=1, how='all') if response.status_code == 200 else None
    except: return None

df_ejercicios = leer_csv("EJERCICIOS")
df_historial = leer_csv("DATOS")

if 'rutina_activa' not in st.session_state:
    st.session_state['rutina_activa'] = "Define tu plan en la pestaña '📋 CONFIGURAR'"

st.title("🐗 GYM IA ELITE")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏋️ ENTRENAR", "📋 CONFIGURAR", "🧮 1RM", "📈 PROGRESO", "⏱️ TIMER"])

# --- TAB 1: ENTRENAR ---
with tab1:
    st.markdown(f'<div class="routine-card"><h3>📅 MI PLAN ACTUAL</h3><p style="color: #00d4ff;">{st.session_state["rutina_activa"]}</p></div>', unsafe_allow_html=True)
    with st.expander("📝 REGISTRAR SERIE"):
        if df_ejercicios is not None:
            with st.form("reg_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                f_musculo = c1.selectbox("Músculo", df_ejercicios.iloc[:, 0].unique())
                f_ejer = c2.selectbox("Ejercicio", df_ejercicios[df_ejercicios.iloc[:, 0] == f_musculo].iloc[:, 1].unique())
                c3, c4 = st.columns(2); f_peso = c3.number_input("Kg", 0.0, 500.0, 20.0); f_reps = c4.number_input("Reps", 1, 100, 10)
                if st.form_submit_button("GUARDAR SERIE"):
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    nueva_fila = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": f_ejer, "Peso": f_peso, "Reps": f_reps, "Estado": "⚡"}])
                    conn.update(worksheet="DATOS", data=pd.concat([df_historial, nueva_fila], ignore_index=True))
                    st.success("¡Registrado!"); time.sleep(1); st.rerun()

# --- TAB 2: CONFIGURAR ---
with tab2:
    opcion = st.radio("Método", ["🤖 IA", "📝 Manual"])
    if opcion == "🤖 IA":
        dias = st.slider("Días", 2, 6, 4)
        if st.button("GENERAR RUTINA"):
            st.session_state['rutina_activa'] = f"Rutina IA para {dias} días generada."
    else:
        st.session_state['rutina_activa'] = st.text_area("Tu plan:", value=st.session_state['rutina_activa'])

# --- TAB 3: CALCULADORA 1RM (LO QUE FALTABA) ---
with tab3:
    st.subheader("🧮 Calculadora de Fuerza Real")
    col_a, col_b = st.columns(2)
    peso_rm = col_a.number_input("Peso levantado (kg)", 1.0, 500.0, 60.0)
    reps_rm = col_b.number_input("Repeticiones máximas", 1, 15, 5)
    
    # Fórmula de Epley
    uno_rm = peso_rm * (1 + 0.0333 * reps_rm)
    
    st.markdown(f"""
    <div class="metric-card">
        <p style='margin:0; font-size: 14px; color: #aaa;'>TU 1RM ESTIMADO</p>
        <h1 style='margin:0; color: #00d4ff;'>{round(uno_rm, 1)} kg</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.write("### 📈 Porcentajes de Carga")
    c1, c2, c3 = st.columns(3)
    c1.metric("Fuerza (90%)", f"{round(uno_rm * 0.9, 1)} kg")
    c2.metric("Hipertrofia (75%)", f"{round(uno_rm * 0.75, 1)} kg")
    c3.metric("Resistencia (60%)", f"{round(uno_rm * 0.6, 1)} kg")

# --- TAB 4: PROGRESO ---
with tab4:
    if df_historial is not None and not df_historial.empty:
        ejer_sel = st.selectbox("Ejercicio:", df_historial["Ejercicio"].unique())
        st.plotly_chart(px.line(df_historial[df_historial["Ejercicio"] == ejer_sel], x="Fecha", y="Peso", markers=True, template="plotly_dark"), use_container_width=True)

# --- TAB 5: TIMER ---
with tab5:
    t = st.number_input("Segundos", 30, 300, 60)
    if st.button("INICIAR"):
        b = st.progress(0)
        for i in range(t): time.sleep(1); b.progress((i+1)/t)
        st.balloons()
