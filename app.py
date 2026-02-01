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
st.set_page_config(page_title="Gym IA Master Split", page_icon="🐗", layout="wide")

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
st.title("🐗 GYM IA: COMMAND CENTER")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏋️ Entrenar", "📈 Progreso", "📋 Plan Dividido IA", "🧮 1RM", "⏱️ Descanso"
])

# --- TAB 1: REGISTRO ---
with tab1:
    if df_ejercicios is not None:
        with st.form("reg_form"):
            st.subheader("Registrar Serie")
            f_fecha = st.date_input("Fecha", datetime.now())
            f_musculo = st.selectbox("Músculo", df_ejercicios.iloc[:, 0].unique())
            f_ejer = st.selectbox("Ejercicio", df_ejercicios[df_ejercicios.iloc[:, 0] == f_musculo].iloc[:, 1].unique())
            c1, c2 = st.columns(2)
            f_peso = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 0.5)
            f_reps = c2.number_input("Reps", 1, 100, 10)
            if st.form_submit_button("💾 GUARDAR"):
                conn = st.connection("gsheets", type=GSheetsConnection)
                nueva_fila = pd.DataFrame([{"Fecha": f_fecha.strftime("%d/%m/%Y"), "Ejercicio": f_ejer, "Peso": f_peso, "Reps": f_reps}])
                df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
                conn.update(worksheet="DATOS", data=df_final)
                st.success("Guardado!"); time.sleep(1); st.rerun()

# --- TAB 3: PLANIFICADOR DIVIDIDO (LA CLAVE) ---
with tab3:
    st.subheader("🤖 Planificación Dividida Inteligente")
    col1, col2 = st.columns(2)
    perfil = col1.selectbox("Tu contextura", ["Delgado (Ectomorfo)", "Sobrepeso (Endomorfo)", "Fuerte (Mesomorfo)"])
    dias = col2.select_slider("Días de entreno", options=[3, 4, 5])

    if st.button("✨ GENERAR RUTINA DIVIDIDA"):
        st.write("---")
        
        if dias == 3:
            st.info("💡 **Esquema PPL (Push/Pull/Legs):** Ideal para recuperación total.")
            rutina = {
                "Día 1: Empuje (Pecho/Hombro/Tríceps)": ["Press Banca (3x8)", "Press Militar (3x10)", "Fondos (3x12)"],
                "Día 2: Tracción (Espalda/Bíceps/Posterior)": ["Remo con barra (3x8)", "Dominadas (3xMax)", "Curl Martillo (3x12)"],
                "Día 3: Pierna Completa": ["Sentadillas (4x8)", "Peso Muerto Rumano (3x10)", "Extensiones (3x15)"]
            }
        elif dias == 4:
            st.info("💡 **Esquema Torso/Pierna:** Máxima frecuencia para ganar músculo.")
            rutina = {
                "Lunes: Torso Pesado": ["Press Inclinado", "Remo Kroc", "Press Arnold"],
                "Martes: Pierna Pesada": ["Prensa 45°", "Curl Femoral", "Zancadas"],
                "Jueves: Torso Hipertrofia": ["Aperturas", "Jalón al pecho", "Elevaciones laterales"],
                "Viernes: Pierna Hipertrofia": ["Sentadilla Búlgara", "Extensiones", "Gemelos"]
            }
        else:
            st.info("💡 **Esquema Weider (Dividido por Músculo):** Volumen extremo por zona.")
            rutina = {
                "Día 1": "Pecho y Abdominales",
                "Día 2": "Espalda y lumbares",
                "Día 3": "Pierna (Énfasis Cuádriceps)",
                "Día 4": "Hombros y Trapecio",
                "Día 5": "Bíceps, Tríceps y Pierna (Énfasis Isquios)"
            }

        for dia, ejer in rutina.items():
            with st.expander(f"📍 {dia}"):
                if isinstance(ejer, list):
                    for e in ejer: st.write(f"- {e}")
                else: st.write(f"Enfoque: {ejer}")
        
        st.caption("Nota: Ajusta el peso según tu calculadora de 1RM.")

# --- TAB 2, 4, 5 (MANTENIENDO EL RESTO) ---
with tab2:
    if df_historial is not None and not df_historial.empty:
        ejer_sel = st.selectbox("Evolución de:", df_historial["Ejercicio"].unique())
        st.plotly_chart(px.line(df_historial[df_historial["Ejercicio"] == ejer_sel], x="Fecha", y="Peso", markers=True), use_container_width=True)

with tab4:
    p = st.number_input("Peso", 1.0, 500.0, 60.0); r = st.number_input("Reps", 1, 20, 5)
    st.metric("1RM Estimado", f"{round(p * (1 + r/30), 1)} kg")

with tab5:
    t = st.select_slider("Descanso (s)", [30, 60, 90, 120])
    if st.button("EMPEZAR"):
        b = st.progress(0)
        for i in range(t): time.sleep(1); b.progress((i+1)/t)
        st.success("¡LISTO!"); st.balloons()
