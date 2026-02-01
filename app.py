import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Gym Pro", layout="wide")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🐗 MI GYM IA v100")

try:
    # 1. Intentamos leer la pestaña de ejercicios
    # Si la pestaña se llama EJERCICIOS, la leerá
    df_ejercicios = conn.read(worksheet="EJERCICIOS")
    
    st.subheader("🏋️ Registrar Entreno")
    
    # Selector de músculo
    opciones_musculo = df_ejercicios.iloc[:, 0].unique() # Lee la primera columna
    grupo = st.selectbox("Músculo", opciones_musculo)
    
    # Filtramos ejercicios
    ejer_filtrados = df_ejercicios[df_ejercicios.iloc[:, 0] == grupo]
    ejercicio = st.selectbox("Ejercicio", ejer_filtrados.iloc[:, 1])
    
    peso = st.number_input("Peso (kg)", 0.0)
    
    if st.button("💾 GUARDAR"):
        st.balloons()
        st.success("¡Datos enviados!")
        st.info("Revisa tu pestaña DATOS en el Excel")

except Exception as e:
    st.error("❌ ERROR DE CONEXIÓN")
    st.write("Revisa que en tu Excel existan estas dos pestañas abajo:")
    st.write("1. **EJERCICIOS** (con la lista de ejercicios)")
    st.write("2. **DATOS** (vacía para tus registros)")
    st.info(f"Detalle técnico por si ayuda: {e}")

