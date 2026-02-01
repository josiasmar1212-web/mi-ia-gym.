import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Gym Pro Precision", page_icon="🐗", layout="wide")

st.title("🐗 CONTROL DE ENTRENAMIENTO PRO")

# Función para limpiar la URL del Secret y evitar el Error 400
def get_clean_url():
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        return url.split("?")[0].split("#")[0] # Deja solo el ID base
    except:
        return None

# Inicializar conexión
conn = st.connection("gsheets", type=GSheetsConnection)

def main():
    clean_url = get_clean_url()
    if not clean_url:
        st.error("❌ No se encontró la URL en los Secrets.")
        return

    try:
        # LECTURA DE DATOS
        df_ejercicios = conn.read(worksheet="EJERCICIOS", ttl=0)
        
        st.subheader("🏋️ Nuevo Registro")
        
        # Selectores usando posiciones de columna para evitar errores de nombres
        col_musculo = df_ejercicios.iloc[:, 0].unique()
        musculo = st.selectbox("Grupo Muscular", col_musculo)
        
        ejer_filtrados = df_ejercicios[df_ejercicios.iloc[:, 0] == musculo].iloc[:, 1].unique()
        ejercicio = st.selectbox("Ejercicio", ejer_filtrados)
        
        c1, c2 = st.columns(2)
        peso = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 0.5)
        reps = c2.number_input("Reps", 1, 100, 10)

        if st.button("💾 GUARDAR ENTRENAMIENTO"):
            # Crear nueva fila
            nueva_data = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Ejercicio": ejercicio,
                "Peso": peso,
                "Reps": reps
            }])

            # Leer historial actual
            try:
                historial = conn.read(worksheet="DATOS", ttl=0)
                # Limpiar columnas fantasma que causan Error 400
                historial = historial.loc[:, ~historial.columns.str.contains('^Unnamed')]
                df_final = pd.concat([historial, nueva_data], ignore_index=True)
            except:
                df_final = nueva_data

            # GUARDAR - La parte crítica
            conn.update(worksheet="DATOS", data=df_final)
            st.balloons()
            st.success("¡Guardado con éxito!")
            st.rerun()

    except Exception as e:
        st.error(f"⚠️ Error de Precisión: {e}")
        st.info("Revisa que el nombre de la pestaña sea EXACTAMENTE 'EJERCICIOS' (en mayúsculas).")

    # Mostrar Historial
    st.divider()
    st.subheader("📊 Últimos Registros")
    try:
        df_ver = conn.read(worksheet="DATOS", ttl=0)
        # Mostrar solo las 4 columnas reales
        st.dataframe(df_ver[["Fecha", "Ejercicio", "Peso", "Reps"]].tail(5), use_container_width=True)
    except:
        st.write("Sin datos previos.")

if __name__ == "__main__":
    main()
