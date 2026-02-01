import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gym Pro", page_icon="🐗", layout="wide")

# CONEXIÓN CON TU EXCEL
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🐗 MI GYM IA - REGISTRO DE ENTRENAMIENTO")

try:
    # 1. LEER LOS EJERCICIOS (De la pestaña EJERCICIOS)
    df_menu = conn.read(worksheet="EJERCICIOS", ttl=0)
    
    # Limpiar espacios en los nombres de las columnas por si acaso
    df_menu.columns = df_menu.columns.str.strip()

    st.subheader("🏋️ Nuevo Registro")
    
    # Selectores dinámicos
    # Usamos iloc para elegir columnas por posición y evitar errores de nombres
    col_grupos = df_menu.iloc[:, 0].unique() 
    musculo = st.selectbox("¿Qué músculo entrenas hoy?", col_grupos)
    
    ejercicios_filtrados = df_menu[df_menu.iloc[:, 0] == musculo]
    ejercicio = st.selectbox("Selecciona el ejercicio", ejercicios_filtrados.iloc[:, 1].unique())
    
    col_a, col_b = st.columns(2)
    with col_a:
        peso = st.number_input("Peso (kg)", min_value=0.0, step=2.5)
    with col_b:
        reps = st.number_input("Repeticiones", min_value=1, step=1, value=10)

    # 2. BOTÓN PARA GUARDAR
    if st.button("💾 GUARDAR EN MI EXCEL"):
        # Creamos la nueva fila de datos
        nueva_fila = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%d/%m/%Y"),
            "Ejercicio": ejercicio,
            "Peso": peso,
            "Reps": reps
        }])

        # Leemos el historial actual de la pestaña DATOS
        df_historial = conn.read(worksheet="DATOS", ttl=0)
        
        # Unimos lo viejo con lo nuevo
        df_actualizado = pd.concat([df_historial, nueva_fila], ignore_index=True)
        
        # ENVIAR AL EXCEL (IMPORTANTE: Requiere permiso de EDITOR en el Excel)
        conn.update(worksheet="DATOS", data=df_actualizado)
        
        st.balloons()
        st.success(f"¡Brutal! Has guardado {ejercicio} con {peso}kg.")

except Exception as e:
    st.error("❌ ERROR DE CONEXIÓN")
    st.write("Causas posibles:")
    st.write("1. El Excel no tiene permiso de **EDITOR** para 'Cualquier persona con el enlace'.")
    st.write("2. No existen las pestañas **EJERCICIOS** y **DATOS** (así en mayúsculas).")
    st.write("3. La pestaña DATOS no tiene los títulos: Fecha, Ejercicio, Peso, Reps en la fila 1.")
    st.info(f"Detalle técnico: {e}")

# MOSTRAR ÚLTIMOS REGISTROS (Opcional)
st.divider()
st.subheader("📊 Mis últimos entrenos")
try:
    historial_visual = conn.read(worksheet="DATOS", ttl=0)
    st.dataframe(historial_visual.tail(5), use_container_width=True)
except:
    st.write("Aún no hay datos registrados.")
