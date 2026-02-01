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
    /* Estilo de Pizarra para la Rutina */
    .pizarra-rutina {
        background-color: #1f2937; 
        border-radius: 15px; 
        padding: 20px;
        border: 2px solid #00d4ff;
        margin-bottom: 25px;
        box-shadow: 0px 4px 15px rgba(0, 212, 255, 0.2);
    }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: #00d4ff; color: #0E1117; font-weight: bold; border: none;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1f2937; border-radius: 10px; padding: 12px; color: white;
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

# --- MEMORIA DE RUTINA ---
if 'rutina_activa' not in st.session_state:
    st.session_state['rutina_activa'] = "⚠️ No hay rutina activa. Configúrala en la pestaña 📋."

st.title("🐗 GYM IA ELITE")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏋️ ENTRENAR", "📋 CONFIGURAR", "🧮 1RM", "📈 PROGRESO", "⏱️ TIMER"])

# --- TAB 1: ENTRENAR (CON RUTINA INTEGRADA) ---
with tab1:
    # LA PIZARRA: Aquí aparece lo que generaste o escribiste
    st.markdown(f"""
    <div class="pizarra-rutina">
        <h4 style='margin-top:0; color: #00d4ff;'>📋 MI RUTINA PARA HOY:</h4>
        <div style='font-size: 16px; line-height: 1.6;'>
            {st.session_state['rutina_activa'].replace(chr(10), '<br>')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ✍️ REGISTRAR SERIE")
    if df_ejercicios is not None:
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            f_musculo = col1.selectbox("Músculo", df_ejercicios.iloc[:, 0].unique())
            f_ejer = col2.selectbox("Ejercicio", df_ejercicios[df_ejercicios.iloc[:, 0] == f_musculo].iloc[:, 1].unique())
            
            col3, col4 = st.columns(2)
            f_peso = col3.number_input("Peso (Kg)", 0.0, 500.0, 20.0, step=0.5)
            f_reps = col4.number_input("Reps", 1, 100, 10)
            
            if st.form_submit_button("💾 GUARDAR SERIE"):
                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    nueva_fila = pd.DataFrame([{
                        "Fecha": datetime.now().strftime("%d/%m/%Y"), 
                        "Ejercicio": f_ejer, "Peso": f_peso, "Reps": f_reps, "Estado": "🔥"
                    }])
                    df_actualizado = pd.concat([df_historial, nueva_fila], ignore_index=True)
                    conn.update(worksheet="DATOS", data=df_actualizado)
                    st.toast("¡Serie guardada!", icon="✅")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

# --- TAB 2: CONFIGURAR (IA O MANUAL) ---
with tab2:
    st.subheader("🛠️ ¿Cómo quieres entrenar?")
    modo = st.radio("Elige método:", ["🤖 Generar con IA", "📝 Escribir mi propia rutina"])
    
    if modo == "🤖 Generar con IA":
        dias = st.slider("Días por semana", 2, 6, 4)
        meta = st.selectbox("Objetivo", ["Masa Muscular", "Fuerza", "Definición"])
        if st.button("✨ GENERAR PLAN INTELIGENTE"):
            # Lógica simple de IA (puedes ampliarla)
            if dias <= 3:
                res = f"**Plan {meta} (Full Body):**<br>- Sentadilla 3x8<br>- Press Banca 3x8<br>- Remo con Barra 3x10"
            else:
                res = f"**Plan {meta} (Split):**<br>- L/J: Pecho, Hombro, Tríceps<br>- M/V: Espalda, Pierna, Bíceps"
            st.session_state['rutina_activa'] = res
            st.success("¡Plan IA Activado! Ve a la pestaña 'ENTRENAR'")
            
    else:
        manual = st.text_area("Escribe tu rutina aquí (ej: Lunes Pecho...):", 
                             value=st.session_state['rutina_activa'].replace('<br>', '\n'), 
                             height=250)
        if st.button("💾 ACTIVAR MI RUTINA"):
            st.session_state['rutina_activa'] = manual
            st.success("¡Rutina Manual Activada!")

# --- TAB 3: 1RM ---
with tab3:
    st.subheader("🧮 Calculadora de RM")
    p = st.number_input("Peso levantado", 1.0, 500.0, 60.0, key="rm_p")
    r = st.number_input("Reps realizadas", 1, 15, 5, key="rm_r")
    rm = p * (1 + 0.0333 * r)
    st.metric("Tu 1RM es de:", f"{round(rm,1)} kg")

# --- TAB 4 Y 5 (PROGRESO Y TIMER) ---
with tab4:
    if df_historial is not None and not df_historial.empty:
        ejer = st.selectbox("Ver evolución:", df_historial["Ejercicio"].unique())
        st.plotly_chart(px.line(df_historial[df_historial["Ejercicio"] == ejer], x="Fecha", y="Peso", markers=True, template="plotly_dark"))

with tab5:
    t = st.number_input("Descanso", 30, 300, 60)
    if st.button("INICIAR TIMER"):
        b = st.progress(0)
        for i in range(t): time.sleep(1); b.progress((i+1)/t)
        st.balloons()
