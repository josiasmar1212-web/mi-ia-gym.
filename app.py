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
    "🏋️ Entrenar", "📈 Progreso", "📋 Plan Dividido IA", "🧮 1RM", "⏱️ Descanso"
])

# --- TAB 1: REGISTRO ---
with tab1:
    if df_ejercicios is not None:
        with st.form("reg_form"):
            st.subheader("Registrar Serie y Sensaciones")
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
                    nueva_fila = pd.DataFrame([{
                        "Fecha": f_fecha.strftime("%d/%m/%Y"), 
                        "Ejercicio": f_ejer, 
                        "Peso": f_peso, 
                        "Reps": f_reps,
                        "Estado": f_sentir
                    }])
                    # Combinar con historial existente
                    df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
                    conn.update(worksheet="DATOS", data=df_final)
                    st.balloons()
                    st.success("¡Datos guardados!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# --- TAB 2: PROGRESO (CORREGIDO) ---
with tab2:
    if df_historial is not None and not df_historial.empty:
        ejer_sel = st.selectbox("Evolución de:", df_historial["Ejercicio"].unique())
        df_f = df_historial[df_historial["Ejercicio"] == ejer_sel].copy()
        
        # Validar si existe la columna Estado para evitar el ValueError
        color_col = "Estado" if "Estado" in df_f.columns else None
        
        fig = px.line(df_f, x="Fecha", y="Peso", markers=True, 
                     color=color_col, 
                     title=f"Progreso en {ejer_sel}",
                     color_discrete_map={"🔥 Fuerte": "green", "⚡ Normal": "blue", "😴 Cansado": "orange", "🤕 Molestia": "red"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Registra tu primer entrenamiento para ver la gráfica.")

# --- TAB 3: PLAN IA ---
with tab3:
    st.subheader("🤖 Tu Rutina Dividida")
    col1, col2 = st.columns(2)
    perfil = col1.selectbox("Contextura", ["Ectomorfo (Delgado)", "Endomorfo (Ancho)", "Mesomorfo (Atlético)"])
    frecuencia = col2.select_slider("Días", options=[3, 4, 5])

    if st.button("✨ GENERAR"):
        if frecuencia == 3:
            rutina = {"Día 1: Empuje": ["Banca", "Militar"], "Día 2: Tracción": ["Remo", "Bíceps"], "Día 3: Pierna": ["Sentadilla"]}
        else:
            rutina = {"Lunes: Pecho": ["Inclinado", "Plano"], "Martes: Espalda": ["Remo", "Jalón"], "Jueves: Pierna": ["Sentadilla"], "Viernes: Hombro": ["Militar"]}
        
        for dia, ejercicios in rutina.items():
            with st.expander(f"📅 {dia}"):
                for e in ejercicios: st.write(f"- {e}")

# --- TAB 4: 1RM ---
with tab4:
    st.subheader("Calculadora 1RM")
    c1, c2 = st.columns(2)
    p = c1.number_input("Peso", 1.0, 500.0, 60.0, key="p_calc")
    r = c2.number_input("Reps", 1, 20, 5, key="r_calc")
    rm = p * (1 + r/30)
    st.metric("1RM Estimado", f"{round(rm, 1)} kg")

# --- TAB 5: TIMER ---
with tab5:
    seg = st.slider("Segundos", 30, 180, 90, 30)
    if st.button("INICIAR"):
        prog = st.progress(0)
        for i in range(seg):
            time.sleep(1)
            prog.progress((i+1)/seg)
        st.success("¡VAMOS!")
