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

# --- TAB 1: REGISTRO CON DIARIO DE SENSACIONES ---
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
            f_sentir = c3.selectbox("Estado", ["🔥 Fuerte", "⚡ Normal", "😴 Cansado", "🤕 Lesión/Molestia"])
            
            if st.form_submit_button("💾 GUARDAR REGISTRO"):
                conn = st.connection("gsheets", type=GSheetsConnection)
                # Nota: Asegúrate de tener la columna 'Estado' en tu pestaña 'DATOS' del Excel
                nueva_fila = pd.DataFrame([{
                    "Fecha": f_fecha.strftime("%d/%m/%Y"), 
                    "Ejercicio": f_ejer, 
                    "Peso": f_peso, 
                    "Reps": f_reps,
                    "Estado": f_sentir
                }])
                df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
                conn.update(worksheet="DATOS", data=df_final)
                st.balloons()
                st.success(f"¡Guardado con éxito! Te sentiste {f_sentir}")
                time.sleep(1)
                st.rerun()

# --- TAB 3: PLANIFICACIÓN DIVIDIDA INTELIGENTE ---
with tab3:
    st.subheader("🤖 Tu Rutina Dividida Personalizada")
    
    col1, col2 = st.columns(2)
    perfil = col1.selectbox("Tu objetivo principal", ["Ganar Masa (Volumen)", "Perder Grasa (Definición)", "Fuerza Pura"])
    frecuencia = col2.select_slider("Días disponibles a la semana", options=[3, 4, 5, 6])

    if st.button("✨ GENERAR PLAN DE ATAQUE"):
        st.write("---")
        if frecuencia == 3:
            st.info("💡 **Esquema PPL (Empuje/Tracción/Pierna)**")
            rutina = {
                "Día 1: Empuje": ["Press Banca 3x8", "Press Militar 3x10", "Extensiones Tríceps 3x12"],
                "Día 2: Tracción": ["Remo con Barra 3x8", "Dominadas/Jalones 3x10", "Curl Bíceps 3x12"],
                "Día 3: Pierna": ["Sentadilla 4x8", "Prensa 3x12", "Gemelos 4x15"]
            }
        elif frecuencia >= 5:
            st.info("💡 **Esquema Weider Modificado (Día por Músculo)**")
            rutina = {
                "Lunes: Pecho": ["Inclinado 4x10", "Plano 3x8", "Aperturas 3x15"],
                "Martes: Espalda": ["Remo 4x8", "Jalón 3x10", "Pull-over 3x12"],
                "Miércoles: Pierna": ["Sentadilla 4x8", "Extensiones 3x15", "Femoral 3x12"],
                "Jueves: Hombro": ["Press Militar 4x10", "Laterales 4x15", "Pájaros 3x12"],
                "Viernes: Brazo/Core": ["Curl Barra 3x10", "Press Francés 3x10", "Plancha 3x1min"]
            }
        else:
            st.info("💡 **Esquema Torso/Pierna (Frecuencia 2)**")
            rutina = {
                "Día 1: Torso": ["Press Banca", "Remo", "Press Militar"],
                "Día 2: Pierna": ["Sentadilla", "Peso Muerto Rumano", "Prensa"],
                "Día 3: Torso": ["Dominadas", "Fondos", "Elevaciones Laterales"],
                "Día 4: Pierna": ["Zancadas", "Curl Femoral", "Extensiones"]
            }

        for dia, ejercicios in rutina.items():
            with st.expander(f"📅 {dia}"):
                for e in ejercicios if isinstance(ejercicios, list) else [ejercicios]:
                    st.write(f"- {e}")

# --- RESTO DE TABS (PROGRESO, 1RM, DESCANSO) ---
with tab2:
    if df_historial is not None and not df_historial.empty:
        ejer_sel = st.selectbox("Evolución de:", df_historial["Ejercicio"].unique())
        df_f = df_historial[df_historial["Ejercicio"] == ejer_sel]
        st.plotly_chart(px.line(df_f, x="Fecha", y="Peso", markers=True, color="Estado"), use_container_width=True)

with tab4:
    st.subheader("Calculadora 1RM (Fórmula de Epley)")
    

[Image of RPE scale for resistance training]

    c1, c2 = st.columns(2)
    p = c1.number_input("Peso", 1.0, 500.0, 60.0)
    r = c2.number_input("Reps", 1, 20, 5)
    rm = p * (1 + r/30)
    st.metric("Tu Máximo Teórico", f"{round(rm, 1)} kg")

with tab5:
    seg = st.slider("Tiempo de descanso", 30, 180, 90, 30)
    if st.button("INICIAR"):
        prog = st.progress(0)
        for i in range(seg):
            time.sleep(1)
            prog.progress((i+1)/seg)
        st.success("¡VAMOS!"); st.balloons()
