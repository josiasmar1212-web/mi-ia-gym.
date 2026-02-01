import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Configuración básica
st.set_page_config(page_title="Gym Pro", page_icon="🐗")
st.title("🐗 MI GYM IA")

# 2. Conexión manual forzada
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 3. Leer Ejercicios (Intentamos sin especificar worksheet primero)
    # Si esto falla, el problema es el Link en Secrets
    df_ejercicios = conn.read(worksheet="EJERCICIOS", ttl=0)
    
    st.subheader("🏋️ Registrar Entrenamiento")
    
    # Selectores
    musculo = st.selectbox("Músculo", df_ejercicios.iloc[:, 0].unique())
    ejer_lista = df_ejercicios[df_ejercicios.iloc[:, 0] == musculo].iloc[:, 1].unique()
    ejercicio = st.selectbox("Ejercicio", ejer_lista)
    
    c1, c2 = st.columns(2)
    peso = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 2.5)
    reps = c2.number_input("Reps", 1, 100, 10)

    if st.button("💾 GUARDAR"):
        # Crear datos nuevos
        nueva_fila = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%d/%m/%Y"),
            "Ejercicio": ejercicio,
            "Peso": peso,
            "Reps": reps
        }])
        
        # Leer DATOS (si falla, empezamos de cero)
        try:
            df_historial = conn.read(worksheet="DATOS", ttl=0)
            df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
        except:
            df_final = nueva_fila

        # Actualizar
        conn.update(worksheet="DATOS", data=df_final)
        st.balloons()
        st.success("¡Guardado!")
        st.rerun()

except Exception as e:
    st.error("❌ Fallo de comunicación con el Excel")
    st.write("Casi siempre es por el Link en Secrets. Mira abajo:")
    st.code("Asegúrate de que en Secrets el link NO tenga nada después de 'edit?usp=sharing'")
    
# Mostrar historial si existe
st.divider()
try:
    df_ver = conn.read(worksheet="DATOS", ttl=0)
    st.dataframe(df_ver.tail(5), use_container_width=True)
except:
    st.write("Historial no disponible.")
