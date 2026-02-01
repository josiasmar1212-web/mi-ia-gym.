import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gym Pro", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🐗 MI GYM IA - REGISTRO REAL")

try:
    # 1. LEER LOS EJERCICIOS (Menú)
    df_menu = conn.read(worksheet="EJERCICIOS", ttl=0)
    df_menu.columns = df_menu.columns.str.strip()

    # 2. INTERFAZ
    musculo = st.selectbox("¿Qué entrenamos?", df_menu.iloc[:, 0].unique())
    ejer_filtrados = df_menu[df_menu.iloc[:, 0] == musculo]
    ejercicio = st.selectbox("Selecciona ejercicio", ejer_filtrados.iloc[:, 1].unique())
    
    peso = st.number_input("Peso (kg)", 0.0, step=2.5)
    reps = st.number_input("Repeticiones", 1, 100, 10)

    if st.button("💾 GUARDAR ENTRENAMIENTO"):
        # 3. CREAR LA NUEVA FILA
        nueva_fila = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%d/%m/%Y"),
            "Ejercicio": ejercicio,
            "Peso": peso,
            "Reps": reps
        }])

        # 4. LEER HISTORIAL Y PEGAR LA NUEVA FILA
        df_historial = conn.read(worksheet="DATOS", ttl=0)
        df_actualizado = pd.concat([df_historial, nueva_fila], ignore_index=True)
        
        # 5. MANDAR AL EXCEL (LA MAGIA)
        conn.update(worksheet="DATOS", data=df_actualizado)
        
        st.balloons()
        st.success(f"¡Guardado en el Excel! {ejercicio} - {peso}kg")

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Asegúrate de tener una pestaña llamada 'DATOS' con los títulos: Fecha, Ejercicio, Peso, Reps")
