import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configuración de la App
st.set_page_config(page_title="GymAnalyst Pro", page_icon="🐗")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🐗 GYMANALYST PRO")

try:
    # Leemos la pestaña de ejercicios
    df = conn.read(ttl=0)
    
    if not df.empty:
        st.subheader("🏋️ Registrar Entrenamiento")
        
        # Selector de Músculo
        lista_musculos = df["Grupo Muscular"].unique()
        musculo = st.selectbox("1. ¿Qué vas a entrenar hoy?", lista_musculos)
        
        # Filtrar ejercicios por ese músculo
        ejercicios_filtrados = df[df["Grupo Muscular"] == musculo]
        ejercicio = st.selectbox("2. Selecciona el ejercicio", ejercicios_filtrados["Nombre del Ejercicio"])
        
        # Entradas de peso y reps
        col1, col2 = st.columns(2)
        with col1:
            peso = st.number_input("Peso (kg)", min_value=0.0, step=2.5)
        with col2:
            reps = st.number_input("Repeticiones", min_value=1, step=1)
            
        if st.button("💾 GUARDAR REGISTRO"):
            st.balloons()
            st.success(f"¡Brutal! Has registrado {ejercicio} con {peso}kg.")
            st.info("Nota: Tus récords se están guardando en la nube.")
            
    else:
        st.error("El Excel está conectado pero no tiene datos. Escribe 'Grupo Muscular' en A1 y 'Nombre del Ejercicio' en B1.")

except Exception as e:
    st.error(f"Error al organizar los datos: {e}")
