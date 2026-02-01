import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configuración básica
st.set_page_config(page_title="GymAnalyst Pro", layout="wide")

# Conexión con tu Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🐗 GYMANALYST PRO")

try:
    # Intentamos leer la pestaña EJERCICIOS de tu Excel
    df_ejercicios = conn.read(worksheet="EJERCICIOS")
     #    Esto lee tus récords pasados
df_historial = conn.read(worksheet="Hoja 1")
    if not df_ejercicios.empty:
        st.subheader("🏋️ Nuevo Registro")
        # Menú para elegir el músculo
        grupo = st.selectbox("1. Elige Músculo", df_ejercicios["Grupo Muscular"].unique())
        
        # Filtramos los ejercicios de ese músculo
        ejer_filtrados = df_ejercicios[df_ejercicios["Grupo Muscular"] == grupo]
        ejercicio = st.selectbox("2. Elige Ejercicio", ejer_filtrados["Nombre del Ejercicio"])
        
        peso = st.number_input("3. Peso (kg)", 0.0)
        
        if st.button("GUARDAR ENTRENAMIENTO"):
            st.balloons()
            st.success(f"¡Brutal! Has guardado {ejercicio}")
except Exception as e:
    st.error("⚠️ Error: No encuentro la pestaña 'EJERCICIOS' en tu Excel.")
    st.info("Asegúrate de que en tu Google Sheets la pestaña de abajo se llame EJERCICIOS (en mayúsculas).")

