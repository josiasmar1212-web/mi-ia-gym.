import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import plotly.express as px
import time
import random

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Gym IA Elite Master", page_icon="🐗", layout="wide")

# --- CONEXIÓN ---
url_base = st.secrets["connections"]["gsheets"]["spreadsheet"].split("/edit")[0]

@st.cache_data(ttl=5)
def leer_csv(pestana):
    url_csv = f"{url_base}/gviz/tq?tqx=out:csv&sheet={pestana}"
    try:
        response = requests.get(url_csv)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            return df.dropna(axis=1, how='all')
        return None
    except:
        return None

df_ejercicios = leer_csv("EJERCICIOS")
df_historial = leer_csv("DATOS")

# --- INTERFAZ ---
st.title("🐗 GYM IA: ELITE COMMAND CENTER")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏋️ Entrenar", "📈 Progreso", "📋 Planificador", "🧮 1RM", "⏱️ Descanso"
])

# --- TAB 1: REGISTRO ---
with tab1:
    if df_ejercicios is not None:
        with st.form("reg_form"):
            st.subheader("Registrar Serie")
            f_fecha = st.date_input("Fecha", datetime.now())
            f_musculo = st.selectbox("Músculo", df_ejercicios.iloc[:, 0].unique())
            f_ejer = st.selectbox("Ejercicio", df_ejercicios[df_ejercicios.iloc[:, 0] == f_musculo].iloc[:, 1].unique())
            
            c1, c2, c3 = st.columns(3)
            f_peso = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 0.5)
            f_reps = c2.number_input("Reps", 1, 100, 10)
            f_sentir = c3.selectbox("Estado", ["🔥 Fuerte", "⚡ Normal", "😴 Cansado", "🤕 Molestia"])
            
            if st.form_submit_button("💾 GUARDAR REGISTRO"):
                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    nueva_fila = pd.DataFrame([{"Fecha": f_fecha.strftime("%d/%m/%Y"), "Ejercicio": f_ejer, "Peso": f_peso, "Reps": f_reps, "Estado": f_sentir}])
                    df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
                    conn.update(worksheet="DATOS", data=df_final)
                    st.balloons(); st.success("¡Guardado!"); time.sleep(1); st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# --- TAB 2: PROGRESO ---
with tab2:
    if df_historial is not None and not df_historial.empty:
        ejer_sel = st.selectbox("Evolución de:", df_historial["Ejercicio"].unique())
        df_f = df_historial[df_historial["Ejercicio"] == ejer_sel].copy()
        color_col = "Estado" if "Estado" in df_f.columns else None
        fig = px.line(df_f, x="Fecha", y="Peso", markers=True, color=color_col, title=f"Progreso en {ejer_sel}")
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 3: PLANIFICADOR (IA + MANUAL) ---
with tab3:
    st.subheader("📋 Gestión de Rutinas")
    
    sub_tab1, sub_tab2 = st.tabs(["🤖 Generador IA", "📝 Creador Manual"])
    
    with sub_tab1:
        perfil = st.selectbox("Contextura", ["Delgado", "Ancho", "Atlético"])
        frecuencia = st.select_slider("Días", options=[3, 4, 5])
        if st.button("✨ GENERAR PLAN IA"):
            st.info("Plan sugerido basado en tu perfil...")
            # (Lógica simplificada de rutina)
            st.write("**Lunes:** Empuje | **Miércoles:** Tracción | **Viernes:** Pierna")

    with sub_tab2:
        st.write("Escribe tu propia rutina. Se guardará localmente en tu navegador.")
        # Usamos st.text_area para que pueda escribir mucho
        user_routine = st.text_area("Tu Rutina Personalizada", 
                                   value=st.session_state.get('my_routine', 'Ejemplo:\nLunes: Pecho y Tríceps\n- Press Banca 4x10\n- Fondos 3x12'),
                                   height=300)
        if st.button("💾 GUARDAR MI RUTINA"):
            st.session_state['my_routine'] = user_routine
            st.success("¡Rutina guardada en la sesión!")

# --- TAB 4 Y 5 (1RM Y TIMER) ---
with tab4:
    p = st.number_input("Peso", 1.0, 500.0, 60.0, key="p_c"); r = st.number_input("Reps", 1, 20, 5, key="r_c")
    st.metric("1RM Estimado", f"{round(p * (1 + r/30), 1)} kg")

with tab5:
    seg = st.slider("Segundos", 30, 180, 90, 30)
    if st.button("INICIAR"):
        prog = st.progress(0)
        for i in range(seg): time.sleep(1); prog.progress((i+1)/seg)
        st.success("¡VAMOS!")
