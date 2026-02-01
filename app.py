import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gym Pro", page_icon="🐗")
st.title("🐗 MI GYM IA")

conn = st.connection("gsheets", type=GSheetsConnection)

# Intentamos leer la primera pestaña disponible si fallan los nombres
try:
    df_ejercicios = conn.read(worksheet="EJERCICIOS", ttl=0)
    st.success("✅ Conexión establecida")
except Exception:
    st.error("❌ No encuentro la pestaña 'EJERCICIOS'.")
    st.info("Asegúrate de que el nombre sea EJERCICIOS (en mayúsculas) y el link en Secrets esté bien.")
    st.stop()

# Si llegamos aquí, es que leyó bien los ejercicios
grupos = df_ejercicios.iloc[:, 0].unique()
musculo = st.selectbox("Músculo", grupos)

ejercicios = df_ejercicios[df_ejercicios.iloc[:, 0] == musculo].iloc[:, 1].unique()
ejercicio = st.selectbox("Ejercicio", ejercicios)

col1, col2 = st.columns(2)
peso = col1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 2.5)
reps = col2.number_input("Reps", 1, 100, 10)

if st.button("💾 GUARDAR ENTRENAMIENTO"):
    try:
        nueva_fila = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%d/%m/%Y"),
            "Ejercicio": ejercicio,
            "Peso": peso,
            "Reps": reps
        }])
        
        # Intentamos leer DATOS, si no existe la creamos
        try:
            df_historial = conn.read(worksheet="DATOS", ttl=0)
            df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
        except:
            df_final = nueva_fila

        conn.update(worksheet="DATOS", data=df_final)
        st.balloons()
        st.success("¡Guardado!")
        st.rerun()
    except Exception as e:
        st.error(f"Error al guardar: {e}")
