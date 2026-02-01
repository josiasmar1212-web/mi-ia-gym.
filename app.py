import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Configuración de la App
st.set_page_config(page_title="Gym Pro", page_icon="🐗")
st.title("🐗 MI GYM IA")

# 2. Establecer la conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN DE CARGA ---
@st.cache_data(ttl=0) # Esto obliga a la IA a leer datos nuevos siempre
def obtener_datos(nombre_pestana):
    return conn.read(worksheet=nombre_pestana)

try:
    # 3. Leer Ejercicios
    df_ejercicios = obtener_datos("EJERCICIOS")
    
    # 4. Interfaz de Selección
    # Usamos .iloc para no depender de si los títulos tienen espacios
    grupos = df_ejercicios.iloc[:, 0].unique()
    musculo = st.selectbox("Músculo", grupos)
    
    ejercicios = df_ejercicios[df_ejercicios.iloc[:, 0] == musculo].iloc[:, 1].unique()
    ejercicio = st.selectbox("Ejercicio", ejercicios)
    
    c1, c2 = st.columns(2)
    peso = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 2.5)
    reps = c2.number_input("Reps", 1, 100, 10)

    # 5. Botón Guardar
    if st.button("💾 GUARDAR ENTRENAMIENTO"):
        # Crear fila nueva
        nueva_fila = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%d/%m/%Y"),
            "Ejercicio": ejercicio,
            "Peso": peso,
            "Reps": reps
        }])
        
        # Leer historial y añadir
        try:
            df_historial = conn.read(worksheet="DATOS")
            df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
        except:
            # Si la pestaña DATOS está vacía o da error, empezamos de cero
            df_final = nueva_fila

        # Actualizar Google Sheets
        conn.update(worksheet="DATOS", data=df_final)
        st.balloons()
        st.success("¡Guardado correctamente!")
        st.rerun()

    # 6. Mostrar historial abajo
    st.divider()
    st.subheader("📊 Historial")
    df_ver = conn.read(worksheet="DATOS")
    st.dataframe(df_ver.tail(10), use_container_width=True)

except Exception as e:
    st.error(f"Error de lectura: {e}")
    st.info("💡 Si ves este error, haz clic en los 3 puntitos de arriba a la derecha y selecciona 'Clear Cache'.")
