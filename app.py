import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import plotly.express as px

# Configuración
st.set_page_config(page_title="Gym Pro Ultra", page_icon="🐗", layout="wide")

# --- CONEXIÓN Y LECTURA ---
url_base = st.secrets["connections"]["gsheets"]["spreadsheet"].split("/edit")[0]

@st.cache_data(ttl=10) # Cache corta para que refresque rápido
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

# --- INTERFAZ ---
st.title("🐗 GYM COMMAND CENTER")

# Creamos pestañas para que la App sea cómoda
tab1, tab2, tab3 = st.tabs(["🏋️ Entrenar", "📈 Progreso", "🧮 Calculadora 1RM"])

with tab1:
    st.subheader("Registrar Serie")
    if df_ejercicios is not None:
        musculo = st.selectbox("Grupo Muscular", df_ejercicios.iloc[:, 0].unique())
        ejer_lista = df_ejercicios[df_ejercicios.iloc[:, 0] == musculo].iloc[:, 1].unique()
        ejercicio = st.selectbox("Ejercicio", ejer_lista)
        
        c1, c2 = st.columns(2)
        peso_reg = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 0.5, key="peso_reg")
        reps_reg = c2.number_input("Reps", 1, 100, 10, key="reps_reg")

        if st.button("💾 GUARDAR ENTRENAMIENTO"):
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                nueva_fila = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y"), 
                                            "Ejercicio": ejercicio, "Peso": peso_reg, "Reps": reps_reg}])
                df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
                conn.update(worksheet="DATOS", data=df_final)
                st.balloons()
                st.success("¡Datos enviados al Excel!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.subheader("Análisis de Fuerza")
    if df_historial is not None and not df_historial.empty:
        ejer_sel = st.selectbox("Selecciona Ejercicio para analizar:", df_historial["Ejercicio"].unique())
        df_filtrado = df_historial[df_historial["Ejercicio"] == ejer_sel]
        
        fig = px.line(df_filtrado, x="Fecha", y="Peso", markers=True, 
                     title=f"Progreso en {ejer_sel}", color_discrete_sequence=['#FF4B4B'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Registra tu primer entreno para ver la gráfica.")

with tab3:
    st.subheader("Calculadora de Repetición Máxima")
    col_calc1, col_calc2 = st.columns(2)
    p = col_calc1.number_input("Peso levantado (kg)", 1.0, 500.0, 60.0)
    r = col_calc2.number_input("Repeticiones hechas", 1, 20, 5)
    
    # Fórmula de Epley
    one_rm = p * (1 + r/30)
    
    st.metric(label="Tu 1RM Estimado", value=f"{round(one_rm, 1)} kg")
    
    st.info("💡 Tu 1RM es el máximo peso que podrías levantar una sola vez.")
    
    # Tabla de porcentajes basada en el 1RM
    st.write("### 📊 Tus zonas de entrenamiento:")
    porcentajes = [0.95, 0.90, 0.85, 0.80, 0.75, 0.70]
    labels = ["Fuerza Máxima (95%)", "Potencia (90%)", "Fuerza-Hipertrofia (85%)", 
              "Hipertrofia (80%)", "Hipertrofia (75%)", "Resistencia (70%)"]
    
    tabla_zonas = pd.DataFrame({
        "Objetivo": labels,
        "Peso Sugerido": [f"{round(one_rm * pct, 1)} kg" for pct in porcentajes]
    })
    st.table(tabla_zonas)
