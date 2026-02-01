import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Gym Pro", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🐗 MI GYM IA")

try:
    # 2. LEER DATOS
    # Lee la pestaña EJERCICIOS para el menú
    df_menu = conn.read(worksheet="EJERCICIOS", ttl=0)
    
    # 3. INTERFAZ DE USUARIO
    musculo = st.selectbox("¿Qué entrenamos?", df_menu.iloc[:, 0].unique())
    ejer_filtrados = df_menu[df_menu.iloc[:, 0] == musculo]
    ejercicio = st.selectbox("Selecciona ejercicio", ejer_filtrados.iloc[:, 1].unique())
    
    col1, col2 = st.columns(2)
    with col1:
        peso = st.number_input("Peso (kg)", 0.0, step=2.5)
    with col2:
        reps = st.number_input("Reps", 1, 100, 10)

    # 4. BOTÓN DE GUARDAR (Aquí estaba el error)
    if st.button("💾 GUARDAR ENTRENAMIENTO"):
        # Creamos la nueva fila
        nueva_fila = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%d/%m/%Y"),
            "Ejercicio": ejercicio,
            "Peso": peso,
            "Reps": reps
        }])

        # Leemos la pestaña DATOS y añadimos la fila
        df_historial = conn.read(worksheet="DATOS", ttl=0)
        df_actualizado = pd.concat([df_historial, nueva_fila], ignore_index=True)
        
        # Guardamos en el Excel
        conn.update(worksheet="DATOS", data=df_actualizado)
        
        st.balloons()
        st.success(f"¡Guardado! {ejercicio} con {peso}kg")

except Exception as e:
    st.error(f"Error técnico: {e}")
    st.info("Revisa que tengas las pestañas EJERCICIOS y DATOS en tu Excel.")
