import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import plotly.express as px # Librería para gráficas pro

# Configuración
st.set_page_config(page_title="Gym Pro Ultra", page_icon="🐗", layout="wide")
st.title("🐗 MI GYM IA - MODO PRO")

# 1. CONEXIÓN Y LECTURA
url_base = st.secrets["connections"]["gsheets"]["spreadsheet"].split("/edit")[0]

def leer_csv(pestana):
    url_csv = f"{url_base}/gviz/tq?tqx=out:csv&sheet={pestana}"
    try:
        response = requests.get(url_csv)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            return df.dropna(axis=1, how='all')
        return None
    except:
        return None

df_ejercicios = leer_csv("EJERCICIOS")
df_historial = leer_csv("DATOS")

# 2. PANEL LATERAL (Filtros)
st.sidebar.header("Configuración")
if st.sidebar.button("🔄 Actualizar Datos"):
    st.cache_data.clear()
    st.rerun()

# 3. REGISTRO DE ENTRENAMIENTO
if df_ejercicios is not None:
    with st.expander("➕ REGISTRAR NUEVA SERIE", expanded=True):
        musculos = df_ejercicios.iloc[:, 0].unique()
        musculo = st.selectbox("Grupo Muscular", musculos)
        
        ejercicios = df_ejercicios[df_ejercicios.iloc[:, 0] == musculo].iloc[:, 1].unique()
        ejercicio = st.selectbox("Ejercicio", ejercicios)
        
        c1, c2 = st.columns(2)
        peso = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 0.5)
        reps = c2.number_input("Reps", 1, 100, 10)

        if st.button("💾 GUARDAR"):
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                nueva_fila = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y"), 
                                            "Ejercicio": ejercicio, "Peso": peso, "Reps": reps}])
                df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
                conn.update(worksheet="DATOS", data=df_final)
                st.balloons()
                st.success("¡Guardado!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# 4. GRÁFICAS DE PROGRESO
st.divider()
st.subheader("📈 Mi Progreso")

if df_historial is not None and not df_historial.empty:
    # Filtro para la gráfica
    ejer_grafica = st.selectbox("Ver evolución de:", df_historial["Ejercicio"].unique())
    df_filtrado = df_historial[df_historial["Ejercicio"] == ejer_grafica]
    
    # Crear gráfica
    fig = px.line(df_filtrado, x="Fecha", y="Peso", 
                 title=f"Evolución de Carga: {ejer_grafica}",
                 markers=True, line_shape="spline",
                 color_discrete_sequence=['#FF4B4B'])
    
    st.plotly_chart(fig, use_container_width=True)

    # 5. TABLA DE HISTORIAL
    with st.expander("📊 Ver Historial Completo"):
        st.table(df_historial.tail(10))
else:
    st.info("Aún no hay datos para mostrar gráficas. ¡Empieza a entrenar!")
