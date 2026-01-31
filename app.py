import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GymAnalyst AI", page_icon="🐗")
st.title("🐗 GymAnalyst AI: Modo Bestia")

# Entrada de datos
with st.sidebar:
    st.header("Entrada de Datos")
    ejercicio = st.selectbox("Ejercicio", ["Press Militar", "Sentadilla", "Press Banca", "Prensa", "Fondos", "Extensiones"])
    peso_anterior = st.number_input("Peso anterior (kg)", min_value=1.0, value=70.0)
    peso_actual = st.number_input("Peso de hoy (kg)", min_value=1.0, value=75.0)
    
    if st.button("Analizar Progreso"):
        mejora = ((peso_actual - peso_anterior) / peso_anterior) * 100
        st.session_state['mejora'] = mejora

# Lógica del Analista
if 'mejora' in st.session_state:
    mejora = st.session_state['mejora']
    if 5 <= mejora <= 7:
        st.balloons()
        st.success(f"🏆 ¡MOMENTO ÉPICO! Has mejorado un {mejora:.1f}%.")
    elif mejora > 7:
        st.warning(f"🐗🔥 NIVEL BESTIA: {mejora:.1f}% de aumento.")
    else:
        st.info(f"Progreso sólido: {mejora:.1f}%.")

    df = pd.DataFrame({"Sesión": ["Anterior", "Actual"], "Peso (kg)": [peso_anterior, peso_actual]})
    fig = px.bar(df, x="Sesión", y="Peso (kg)", color="Sesión", title=f"Evolución en {ejercicio}")
    st.plotly_chart(fig)
