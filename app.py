import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Gym Pro", page_icon="🐗", layout="wide")

# Conexión con el Excel
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🐗 MI GYM IA")

try:
    # 1. LEER LOS EJERCICIOS
    # Forzamos la lectura de la pestaña EJERCICIOS
    df_menu = conn.read(worksheet="EJERCICIOS", ttl=0)
    
    # 2. INTERFAZ DE USUARIO
    st.subheader("🏋️ Nuevo Registro")
    
    # Selectores basados en tu Excel
    col_grupos = df_menu.iloc[:, 0].unique() 
    musculo = st.selectbox("¿Qué músculo entrenas hoy?", col_grupos)
    
    ejercicios_filtrados = df_menu[df_menu.iloc[:, 0] == musculo]
    ejercicio = st.selectbox("Selecciona el ejercicio", ejercicios_filtrados.iloc[:, 1].unique())
    
    col_a, col_b = st.columns(2)
    with col_a:
        peso = st.number_input("Peso (kg)", min_value=0.0, step=2.5, value=10.0)
    with col_b:
        reps = st.number_input("Repeticiones", min_value=1, step=1, value=10)

    # 3. BOTÓN PARA GUARDAR
    if st.button("💾 GUARDAR ENTRENAMIENTO"):
        # Creamos la nueva fila
        nueva_fila = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%d/%m/%Y"),
            "Ejercicio": ejercicio,
            "Peso": peso,
            "Reps": reps
        }])

        # Leemos el historial de la pestaña DATOS
        df_historial = conn.read(worksheet="DATOS", ttl=0)
        
        # Combinamos y enviamos
        df_actualizado = pd.concat([df_historial, nueva_fila], ignore_index=True)
        conn.update(worksheet="DATOS", data=df_actualizado)
        
        st.balloons()
        st.success(f"¡Guardado correctamente en la pestaña DATOS!")

except Exception as e:
    st.error(f"❌ Error de conexión: {e}")
    st.info("Revisa que los permisos del Excel sigan en 'Editor'.")

# 4. MOSTRAR ÚLTIMOS REGISTROS
st.divider()
st.subheader("📊 Mis últimos entrenos")
try:
    historial = conn.read(worksheet="DATOS", ttl=0)
    if not historial.empty:
        st.dataframe(historial.tail(5), use_container_width=True)
    else:
        st.write("Aún no hay datos registrados.")
except:
    st.write("No se pudo cargar el historial.")
