import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gym Pro", page_icon="🐗")

st.title("🐗 MI GYM IA")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN PARA CARGAR DATOS SEGURO ---
def cargar_datos(pestana):
    try:
        return conn.read(worksheet=pestana, ttl=0)
    except:
        return pd.DataFrame()

# 1. CARGAR MENÚ
df_ejercicios = cargar_datos("EJERCICIOS")

if not df_ejercicios.empty:
    # Interfaz limpia
    grupos = df_ejercicios.iloc[:, 0].unique()
    musculo = st.selectbox("Músculo", grupos)
    
    ejercicios = df_ejercicios[df_ejercicios.iloc[:, 0] == musculo].iloc[:, 1].unique()
    ejercicio = st.selectbox("Ejercicio", ejercicios)
    
    c1, c2 = st.columns(2)
    peso = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 2.5)
    reps = c2.number_input("Reps", 1, 100, 10)

    if st.button("💾 GUARDAR AHORA"):
        try:
            # Crear nueva fila
            nueva_fila = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Ejercicio": ejercicio,
                "Peso": peso,
                "Reps": reps
            }])

            # Leer historial actual
            df_historial = cargar_datos("DATOS")
            
            # Unir (Si el historial falló, usamos solo la nueva fila)
            if df_historial.empty:
                df_final = nueva_fila
            else:
                df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
            
            # GUARDAR
            conn.update(worksheet="DATOS", data=df_final)
            st.balloons()
            st.success("¡Guardado en el Excel!")
            st.rerun()
        except Exception as e:
            st.error(f"Error al guardar: {e}")
else:
    st.warning("No se pudo leer la pestaña 'EJERCICIOS'. Revisa el link en Secrets.")

# --- HISTORIAL ---
st.divider()
st.subheader("📊 Últimos registros")
df_ver = cargar_datos("DATOS")
if not df_ver.empty:
    st.dataframe(df_ver.tail(10), use_container_width=True)
