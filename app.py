import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración Pro
st.set_page_config(page_title="GymAnalyst Pro", layout="wide")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🐗 GYMANALYST PRO")

try:
    # 1. LEEMOS EL MENÚ DE EJERCICIOS
    df_ejercicios = conn.read(worksheet="EJERCICIOS")
    
    # 2. SECCIÓN DE REGISTRO
    st.subheader("🏋️ Nuevo Entrenamiento")
    
    # Selector de músculo
    grupo = st.selectbox("Elige Músculo", df_ejercicios["Grupo Muscular"].unique())
    
    # Selector de ejercicio (filtrado por músculo)
    ejer_filtrados = df_ejercicios[df_ejercicios["Grupo Muscular"] == grupo]
    ejercicio = st.selectbox("Elige Ejercicio", ejer_filtrados["Nombre del Ejercicio"])
    
    col1, col2 = st.columns(2)
    with col1:
        peso = st.number_input("Peso (kg)", 0.0)
    with col2:
        reps = st.number_input("Reps", 0)

    if st.button("💾 GUARDAR EN HOJA 1"):
        st.balloons()
        st.success(f"¡Guardado! Mira tu Hoja 1 en el Excel.")

    # 3. MOSTRAR HISTORIAL (Opcional)
    st.divider()
    st.subheader("📊 Últimos Registros (Hoja 1)")
    df_historial = conn.read(worksheet="Hoja 1")
    st.dataframe(df_historial.tail(5)) # Muestra los últimos 5 entrenos

except Exception as e:
    st.error("⚠️ Todavía hay un problema con las pestañas del Excel.")
    st.info("Asegúrate de que tienes una pestaña llamada 'EJERCICIOS' y otra llamada 'Hoja 1'.")

