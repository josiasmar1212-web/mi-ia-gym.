import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import plotly.express as px
import time
import random

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gym IA Master", page_icon="🐗", layout="wide")

# --- CONEXIÓN DIRECTA ---
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

# Cargar datos iniciales
df_ejercicios = leer_csv("EJERCICIOS")
df_historial = leer_csv("DATOS")

# --- TÍTULO Y MOTIVACIÓN ---
st.title("🐗 GYM IA: COMMAND CENTER")
frases = [
    "«La disciplina es el puente entre las metas y los logros.»",
    "«No te detengas hasta que estés orgulloso.»",
    "«El dolor es temporal, el orgullo es para siempre.»"
]
st.caption(random.choice(frases))

# --- TABS PRINCIPALES ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏋️ Entrenar", 
    "📈 Progreso", 
    "📋 Plan IA", 
    "🧮 1RM", 
    "⏱️ Descanso"
])

# --- TAB 1: REGISTRO DE ENTRENAMIENTO ---
with tab1:
    if df_ejercicios is not None:
        with st.form("registro_entreno"):
            st.subheader("Registrar Serie")
            f_fecha = st.date_input("Fecha", datetime.now())
            f_musculo = st.selectbox("Músculo", df_ejercicios.iloc[:, 0].unique())
            f_ejer = st.selectbox("Ejercicio", df_ejercicios[df_ejercicios.iloc[:, 0] == f_musculo].iloc[:, 1].unique())
            
            c1, c2 = st.columns(2)
            f_peso = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 0.5)
            f_reps = c2.number_input("Reps", 1, 100, 10)
            
            submit = st.form_submit_button("💾 GUARDAR SERIE")
            
            if submit:
                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    nueva_fila = pd.DataFrame([{"Fecha": f_fecha.strftime("%d/%m/%Y"), "Ejercicio": f_ejer, "Peso": f_peso, "Reps": f_reps}])
                    df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
                    conn.update(worksheet="DATOS", data=df_final)
                    st.balloons()
                    st.success("¡Guardado!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

# --- TAB 2: PROGRESO VISUAL ---
with tab2:
    if df_historial is not None and not df_historial.empty:
        st.subheader("Análisis de Fuerza")
        ejer_sel = st.selectbox("Selecciona Ejercicio:", df_historial["Ejercicio"].unique())
        df_f = df_historial[df_historial["Ejercicio"] == ejer_sel]
        fig = px.line(df_f, x="Fecha", y="Peso", markers=True, title=f"Evolución {ejer_sel}", color_discrete_sequence=['#FF4B4B'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aún no hay datos registrados.")

# --- TAB 3: PLANIFICADOR IA ---
with tab3:
    st.subheader("🤖 Planificador Inteligente")
    st.write("Configura tu perfil para generar una rutina a medida.")
    
    col_a, col_b = st.columns(2)
    p_estado = col_a.selectbox("Tu estado actual", ["Delgado (Ectomorfo)", "Sobrepeso (Endomorfo)", "Atlético (Mesomorfo)"])
    p_objetivo = col_b.selectbox("Tu meta", ["Ganar Músculo", "Perder Grasa", "Fuerza Máxima"])
    
    if st.button("✨ GENERAR MI RUTINA"):
        st.divider()
        if "Delgado" in p_estado or "Ganar" in p_objetivo:
            st.markdown("### 🔥 PLAN: VOLUMEN LIMPIO")
            
            st.info("Frecuencia: 4 días/semana. Descanso: 90s. Enfoque: Superávit calórico.")
            st.write("- **Lunes:** Pecho/Tríceps (Enfoque press plano)")
            st.write("- **Martes:** Espalda/Bíceps (Enfoque dominadas)")
            st.write("- **Jueves:** Pierna (Enfoque Sentadilla)")
            st.write("- **Viernes:** Hombro/Core (Enfoque Press Militar)")
        elif "Sobrepeso" in p_estado or "Perder" in p_objetivo:
            st.markdown("### 💧 PLAN: DÉFICIT E INTENSIDAD")
            st.info("Frecuencia: 3 días fuerza + 2 días cardio. Enfoque: Proteína alta.")
            st.write("- **Días Fuerza:** Rutina FullBody (3x10 reps)")
            st.write("- **Días Cardio:** 30 min Caminata inclinada o Elíptica")
        else:
            st.markdown("### ⚡ PLAN: RENDIMIENTO ATLÉTICO")
            st.write("- **Rutina:** Empuje/Tracción/Pierna con énfasis en movimientos explosivos.")

# --- TAB 4: CALCULADORA 1RM ---
with tab4:
    st.subheader("Calculadora de Fuerza Real")
    c1, c2 = st.columns(2)
    calc_p = c1.number_input("Peso levantado (kg)", 1.0, 500.0, 60.0, key="c_p")
    calc_r = c2.number_input("Reps logradas", 1, 20, 5, key="c_r")
    
    one_rm = calc_p * (1 + calc_r/30)
    st.metric("Tu 1RM Máximo", f"{round(one_rm, 1)} kg")
    
    st.write("### Porcentajes de Carga")
    zonas = {"Fuerza (90%)": 0.9, "Hipertrofia (80%)": 0.8, "Resistencia (70%)": 0.7}
    for label, pct in zonas.items():
        st.write(f"**{label}:** {round(one_rm * pct, 1)} kg")

# --- TAB 5: TEMPORIZADOR ---
with tab5:
    st.subheader("⏱️ Timer de Descanso")
    t_seg = st.select_slider("Segundos", options=[30, 45, 60, 90, 120, 180], value=90)
    if st.button(f"INICIAR DESCANSO ({t_seg}s)"):
        prog = st.progress(0)
        for s in range(t_seg):
            time.sleep(1)
            prog.progress((s + 1) / t_seg)
        st.success("🔥 ¡A POR LA SIGUIENTE SERIE!")
        st.balloons()
