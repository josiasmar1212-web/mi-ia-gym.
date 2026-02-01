import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Gym Pro", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🐗 MI GYM IA v100")

try:
    # 1. Intentamos leer la pestaña EJERCICIOS
    df_ejercicios = conn.read(worksheet="EJERCICIOS", ttl=0)
    
    st.subheader("🏋️ Registrar Entreno")
    
    # Selector de músculo
    grupo = st.selectbox("Músculo", df_ejercicios["Grupo Muscular"].unique())
    
    # Selector de ejercicio
    ejer_filtrados = df_ejercicios[df_ejercicios["Grupo Muscular"] == grupo]
    ejercicio = st.selectbox("Ejercicio", ejer_filtrados["Nombre del Ejercicio"])
    
    peso = st.number_input("Peso (kg)", 0.0)
    
    if st.button("💾 GUARDAR"):
        st.balloons()
        st.success(f"¡Guardado! {ejercicio} con {peso}kg.")

except Exception as e:
    st.error("❌ ERROR DE CONEXIÓN")
    st.write("Asegúrate de que la primera pestaña se llame EJERCICIOS")
    st.info(f"Nota: {e}")
