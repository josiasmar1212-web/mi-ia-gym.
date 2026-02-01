import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración visual
st.set_page_config(page_title="Gym Pro", page_icon="🐗", layout="wide")

st.markdown("# 🐗 MI GIMNASIO IA")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. CARGAR DATOS (EJERCICIOS)
try:
    df_ejercicios = conn.read(worksheet="EJERCICIOS", ttl=0)
    
    st.subheader("🏋️ Nuevo Registro")
    
    # Selectores
    grupos = df_ejercicios.iloc[:, 0].unique()
    musculo = st.selectbox("Grupo Muscular", grupos)
    
    ejer_filtrados = df_ejercicios[df_ejercicios.iloc[:, 0] == musculo]
    ejercicio = st.selectbox("Ejercicio", ejer_filtrados.iloc[:, 1].unique())
    
    col1, col2 = st.columns(2)
    peso = col1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 2.5)
    reps = col2.number_input("Repeticiones", 1, 100, 10)

    # 2. BOTÓN GUARDAR
    if st.button("💾 GUARDAR EN EXCEL"):
        # Creamos la nueva fila
        nueva_fila = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%d/%m/%Y"),
            "Ejercicio": ejercicio,
            "Peso": peso,
            "Reps": reps
        }])

        # Leemos historial y limpiamos columnas vacías
        df_historial = conn.read(worksheet="DATOS", ttl=0)
        df_historial = df_historial.dropna(axis=1, how='all') # Borra columnas fantasma
        
        # Unimos y actualizamos
        df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
        conn.update(worksheet="DATOS", data=df_final)
        
        st.balloons()
        st.success("¡Entrenamiento registrado!")
        st.rerun()

except Exception as e:
    st.error(f"Error: {e}")

# 3. HISTORIAL VISUAL LIMPIO
st.divider()
st.subheader("📊 Historial Reciente")
try:
    df_ver = conn.read(worksheet="DATOS", ttl=0)
    # Seleccionamos solo las 4 columnas que nos importan para que no salgan los "Unnamed"
    df_limpio = df_ver[["Fecha", "Ejercicio", "Peso", "Reps"]].tail(10)
    st.table(df_limpio) # Usamos table para que se vea más estético
except:
    st.write("Aún no hay registros.")
