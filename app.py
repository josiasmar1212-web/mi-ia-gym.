import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración profesional
st.set_page_config(page_title="Gym Pro", page_icon="🐗", layout="wide")

st.title("🐗 MI GYM IA")

# --- CONEXIÓN ---
# Forzamos una conexión limpia
conn = st.connection("gsheets", type=GSheetsConnection)

def registrar_entreno():
    try:
        # 1. LEER DATOS DE EJERCICIOS
        # Usamos ttl=0 para que siempre lea lo último del Excel
        df_ejercicios = conn.read(worksheet="EJERCICIOS", ttl=0)
        
        if df_ejercicios.empty:
            st.error("La pestaña 'EJERCICIOS' está vacía.")
            return

        # 2. INTERFAZ DE SELECCIÓN
        grupos = df_ejercicios.iloc[:, 0].unique()
        musculo = st.selectbox("¿Qué grupo muscular?", grupos)
        
        ejer_nombres = df_ejercicios[df_ejercicios.iloc[:, 0] == musculo].iloc[:, 1].unique()
        ejercicio = st.selectbox("Selecciona el ejercicio", ejer_nombres)
        
        col1, col2 = st.columns(2)
        with col1:
            peso = st.number_input("Peso (kg)", 0.0, 500.0, 20.0, 2.5)
        with col2:
            reps = st.number_input("Repeticiones", 1, 100, 10)

        # 3. BOTÓN GUARDAR
        if st.button("💾 GUARDAR ENTRENAMIENTO"):
            # Crear la nueva fila
            nueva_fila = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Ejercicio": ejercicio,
                "Peso": peso,
                "Reps": reps
            }])

            # Leer el historial actual de la pestaña DATOS
            df_historial = conn.read(worksheet="DATOS", ttl=0)
            
            # Unir y actualizar
            df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
            conn.update(worksheet="DATOS", data=df_final)
            
            st.balloons()
            st.success("¡Entrenamiento guardado con éxito!")
            st.rerun()

    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.info("💡 CONSEJO: Ve a los Secrets de Streamlit y asegúrate de que el link termine en '/edit?usp=sharing' y no tenga #gid al final.")

# Ejecutar la función
registrar_entreno()

# 4. MOSTRAR HISTORIAL ABAJO
st.divider()
st.subheader("📊 Historial Reciente")
try:
    df_ver = conn.read(worksheet="DATOS", ttl=0)
    st.dataframe(df_ver.tail(10), use_container_width=True)
except:
    st.write("No hay datos para mostrar todavía.")
