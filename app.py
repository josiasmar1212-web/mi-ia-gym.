import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Gym Pro", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🐗 MI GYM IA")

try:
    # Leemos los datos (ttl=0 para que no guarde errores viejos)
    df = conn.read(ttl=0)
    
    # Limpiamos los nombres de las columnas por si acaso hay espacios
    df.columns = df.columns.str.strip()

    if not df.empty:
        # Usamos la posición de la columna en vez del nombre exacto
        col_musculo = df.columns[0] # La primera columna
        col_ejercicio = df.columns[1] # La segunda columna

        musculo = st.selectbox("¿Qué entrenamos?", df[col_musculo].unique())
        
        ejer_filtrados = df[df[col_musculo] == musculo]
        ejercicio = st.selectbox("Selecciona ejercicio", ejer_filtrados[col_ejercicio].unique())
        
        peso = st.number_input("Peso (kg)", 0.0, step=2.5)
        
        if st.button("💾 GUARDAR"):
            st.balloons()
            st.success(f"¡Brutal! {ejercicio} guardado.")
    else:
        st.warning("Escribe tus ejercicios en el Excel.")

except Exception as e:
    st.error(f"Aún no leo bien las columnas. Error: {e}")
    st.info("Revisa que en el Excel la columna B se llame: Nombre del Ejercicio")
