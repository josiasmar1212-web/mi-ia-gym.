import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="GymAnalyst AI v3.0", page_icon="🐗")

st.title("🐗 GymAnalyst AI: Modo Memoria")

# --- ENTRADA DE DATOS ---
with st.container():
    ejercicio = st.selectbox("Selecciona Ejercicio", ["Press Militar", "Sentadilla", "Press Banca", "Prensa", "Laterales"])
    peso_ant = st.number_input("Peso anterior (kg)", value=60.0)
    peso_act = st.number_input("Peso de hoy (kg)", value=60.0)
    
    if st.button("💾 GUARDAR Y ANALIZAR"):
        mejora = ((peso_act - peso_ant) / peso_ant) * 100
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Crear una nueva fila de datos
        nueva_fila = pd.DataFrame([[fecha, ejercicio, peso_ant, peso_act, f"{mejora:.1f}%"]], 
                                  columns=["Fecha", "Ejercicio", "Peso_Anterior", "Peso_Actual", "Progreso"])
        
        # Mostrar resultado inmediato
        if 5 <= mejora <= 7:
            st.balloons()
            st.success(f"🏆 ¡ÉPICO! +{mejora:.1f}%")
        else:
            st.info(f"Registro guardado: +{mejora:.1f}%")
            
        # AQUÍ SE MOSTRARÍA TU HISTORIAL
        st.write("### 📝 Tu Historial Reciente")
        st.table(nueva_fila) 
        
        st.warning("⚠️ Nota: Para guardar permanentemente en la nube, necesitamos configurar los 'Secrets' en Streamlit. ¿Quieres hacerlo?")
