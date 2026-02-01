import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests
from io import StringIO

# Configuración de página
st.set_page_config(page_title="Gym Pro Ultra", page_icon="🐗")
st.title("🐗 MI GYM IA - VERSIÓN FINAL")

# 1. OBTENER URL LIMPIA
try:
    url_base = st.secrets["connections"]["gsheets"]["spreadsheet"].split("/edit")[0]
except:
    st.error("Revisa el link en los Secrets.")
    st.stop()

# 2. FUNCIÓN DE LECTURA POR FUERZA BRUTA (CSV)
def leer_csv(pestana):
    # Esta URL descarga la pestaña directamente sin pasar por la API compleja
    url_csv = f"{url_base}/gviz/tq?tqx=out:csv&sheet={pestana}"
    try:
        response = requests.get(url_csv)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            # Eliminamos columnas vacías que causan el Error 400
            df = df.dropna(axis=1, how='all')
            return df
        else:
            return None
    except:
        return None

# 3. CARGAR DATOS
df_ejercicios = leer_csv("EJERCICIOS")

if df_ejercicios is not None and not df_ejercicios.empty:
    st.subheader("🏋️ Registrar Entrenamiento")
    
    # Selectores por posición para evitar errores de nombres de columna
    musculos = df_ejercicios.iloc[:, 0].unique()
    musculo = st.selectbox("Grupo Muscular", musculos)
    
    ejercicios = df_ejercicios[df_ejercicios.iloc[:, 0] == musculo].iloc[:, 1].unique()
    ejercicio = st.selectbox("Ejercicio", ejercicios)
    
    c1, c2 = st.columns(2)
    peso = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 0.5)
    reps = c2.number_input("Reps", 1, 100, 10)

    # 4. GUARDAR (Usamos el conector solo para escribir)
    if st.button("💾 GUARDAR"):
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            
            nueva_fila = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Ejercicio": ejercicio,
                "Peso": peso,
                "Reps": reps
            }])

            # Leemos el historial actual
            df_historial = leer_csv("DATOS")
            
            if df_historial is not None:
                df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
            else:
                df_final = nueva_fila

            # Enviamos al Excel
            conn.update(worksheet="DATOS", data=df_final)
            st.balloons()
            st.success("¡Guardado!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Error al escribir: {e}")
else:
    st.error("No se pudo conectar con la pestaña EJERCICIOS.")
    st.info("Verifica que el link en Secrets sea correcto y la pestaña sea pública (Editor).")

# 5. MOSTRAR HISTORIAL
st.divider()
st.subheader("📊 Historial")
df_ver = leer_csv("DATOS")
if df_ver is not None:
    st.table(df_ver.tail(5))
