import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from io import StringIO

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Gym Pro Ultra", page_icon="🐗", layout="wide")
st.title("🐗 MI GYM IA - MODO ROBUSTO")

# 2. OBTENER URL DE LOS SECRETS
try:
    # Limpiamos la URL para asegurar que sea la de exportación directa
    raw_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    base_url = raw_url.split('/edit')[0]
except Exception as e:
    st.error("Error al leer el Secret. Verifica que esté bien escrito en Streamlit Cloud.")
    st.stop()

# 3. FUNCIONES DE LECTURA Y ESCRITURA ESPECÍFICAS
def leer_pestana(nombre_pestana):
    # Construimos la URL de descarga directa de CSV para evitar el Error 400
    csv_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={nombre_pestana}"
    try:
        response = requests.get(csv_url)
        if response.status_code == 200:
            return pd.read_csv(StringIO(response.text))
        else:
            st.error(f"Error HTTP {response.status_code} en {nombre_pestana}")
            return None
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# 4. CARGAR DATOS
df_ejercicios = leer_pestana("EJERCICIOS")

if df_ejercicios is not None:
    # INTERFAZ
    st.subheader("🏋️ Nuevo Registro")
    
    col_grupos = df_ejercicios.iloc[:, 0].unique()
    musculo = st.selectbox("Grupo Muscular", col_grupos)
    
    ejercicios_filtrados = df_ejercicios[df_ejercicios.iloc[:, 0] == musculo]
    ejercicio = st.selectbox("Ejercicio", ejercicios_filtrados.iloc[:, 1].unique())
    
    c1, c2 = st.columns(2)
    peso = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 2.5)
    reps = c2.number_input("Repeticiones", 1, 100, 10)

    # 5. GUARDAR (Usando el conector oficial para escribir)
    from streamlit_gsheets import GSheetsConnection
    conn = st.connection("gsheets", type=GSheetsConnection)

    if st.button("💾 GUARDAR EN EXCEL"):
        try:
            nueva_fila = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Ejercicio": ejercicio,
                "Peso": peso,
                "Reps": reps
            }])
            
            # Leer DATOS para concatenar
            df_datos = conn.read(worksheet="DATOS", ttl=0)
            df_final = pd.concat([df_datos, nueva_fila], ignore_index=True)
            
            # Actualizar
            conn.update(worksheet="DATOS", data=df_final)
            st.balloons()
            st.success("¡Registro guardado con éxito!")
            st.rerun()
        except Exception as e:
            st.error(f"No se pudo escribir en 'DATOS'. Revisa si la pestaña existe: {e}")

# 6. MOSTRAR HISTORIAL
st.divider()
st.subheader("📊 Historial Reciente")
df_historial = leer_pestana("DATOS")
if df_historial is not None:
    st.dataframe(df_historial.tail(10), use_container_width=True)
