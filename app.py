import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gym Pro", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🐗 MI GYM IA")

try:
    # Leer el menú de la pestaña EJERCICIOS
    df_menu = conn.read(worksheet="EJERCICIOS", ttl=0)
    
    # Interfaz
    musculo = st.selectbox("¿Qué entrenamos?", df_menu.iloc[:, 0].unique())
    ejer_filtrados = df_menu[df_menu.iloc[:, 0] == musculo]
    ejercicio = st.selectbox("Selecciona ejercicio", ejer_filtrados.iloc[:, 1].unique())
    
    col1, col2 = st.columns(2)
    with col1:
        peso = st.number_input("Peso (kg)", 0.0, step=2.5)
    with col2:
        reps = st.number_input("Reps", 1, 100, 10)

    if st.button("💾 GUARDAR ENTRENAMIENTO"):
        # Creamos la nueva fila
        nueva_fila = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%d/%m/%Y"),
            "Ejercicio": ejercicio,
            "Peso": peso,
            "Reps": reps
        }])

        # Leemos el historial de la pestaña DATOS
        # Si da error aquí, es que la pestaña DATOS no existe o no tiene los títulos
        df_historial = conn.read(worksheet="DATOS", ttl=0)
        
        # Combinamos
        df_actualizado = pd.concat([df_historial, nueva_fila], ignore_index=True)
        
        # Actualizamos la hoja
        conn.update(worksheet="DATOS", data=df_actualizado)
        
        st.balloons()
        st.success(f"¡Guardado con éxito!")

except Exception as e:
    st.error(f"Error técnico: {e}")
    st.info("Asegúrate de que la pestaña DATOS tenga los títulos: Fecha, Ejercicio, Peso, Reps")
