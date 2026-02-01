import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import plotly.express as px
import time

# 1. CONFIGURACIÓN DE INTERFAZ PROFESIONAL
st.set_page_config(page_title="Gym IA Elite", page_icon="🐗", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    /* Tarjetas de Rutina */
    .routine-card {
        background-color: #1f2937; border-radius: 15px; padding: 20px;
        border-left: 5px solid #00d4ff; margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: #00d4ff; color: #0E1117; font-weight: bold; border: none;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1f2937; border-radius: 10px; padding: 12px; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A DATOS ---
url_base = st.secrets["connections"]["gsheets"]["spreadsheet"].split("/edit")[0]

@st.cache_data(ttl=5)
def leer_csv(pestana):
    url_csv = f"{url_base}/gviz/tq?tqx=out:csv&sheet={pestana}"
    try:
        response = requests.get(url_csv)
        return pd.read_csv(StringIO(response.text)).dropna(axis=1, how='all') if response.status_code == 200 else None
    except: return None

df_ejercicios = leer_csv("EJERCICIOS")
df_historial = leer_csv("DATOS")

# --- LÓGICA DE MEMORIA ---
if 'rutina_activa' not in st.session_state:
    st.session_state['rutina_activa'] = "Define tu plan en la pestaña '📋 CONFIGURAR'"

st.title("🐗 GYM IA ELITE")

tab1, tab2, tab3, tab4 = st.tabs(["🏋️ ENTRENAR", "📋 CONFIGURAR", "📈 PROGRESO", "⏱️ TIMER"])

# --- TAB 1: EL PANEL DE CONTROL DEL ATLETA ---
with tab1:
    st.markdown(f"""
    <div class="routine-card">
        <h3 style='margin-top:0;'>📅 MI PLAN ACTUAL</h3>
        <p style='color: #00d4ff;'>{st.session_state['rutina_activa']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📝 REGISTRAR SERIE DE HOY"):
        if df_ejercicios is not None:
            with st.form("reg_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                f_musculo = c1.selectbox("Músculo", df_ejercicios.iloc[:, 0].unique())
                f_ejer = c2.selectbox("Ejercicio", df_ejercicios[df_ejercicios.iloc[:, 0] == f_musculo].iloc[:, 1].unique())
                
                c3, c4, c5 = st.columns(3)
                f_peso = c3.number_input("Kg", 0.0, 500.0, 20.0)
                f_reps = c4.number_input("Reps", 1, 100, 10)
                f_sentir = c5.selectbox("RPE", ["🔥 (Tope)", "⚡ (Bien)", "😴 (Falla)"])
                
                if st.form_submit_button("GUARDAR EN EL DIARIO"):
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    nueva_fila = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": f_ejer, "Peso": f_peso, "Reps": f_reps, "Estado": f_sentir}])
                    df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
                    conn.update(worksheet="DATOS", data=df_final)
                    st.toast("¡Serie guardada con éxito!", icon="✅")
                    time.sleep(1); st.rerun()

# --- TAB 2: CONFIGURACIÓN (IA VS MANUAL) ---
with tab2:
    st.subheader("🛠️ Diseña tu Entrenamiento")
    opcion = st.radio("¿Quién arma el plan?", ["🤖 Generador IA", "📝 Yo mismo (Manual)"])
    
    if opcion == "🤖 Generador IA":
        col1, col2 = st.columns(2)
        dias = col1.slider("¿Cuántos días entrenarás?", 2, 6, 4)
        exp = col2.selectbox("Experiencia", ["Novato (< 6 meses)", "Intermedio (1-2 años)", "Avanzado (> 3 años)"])
        meta = st.selectbox("Objetivo Principal", ["Ganar Músculo (Hipertrofia)", "Fuerza Pura", "Pérdida de Grasa"])
        
        if st.button("✨ GENERAR MI RUTINA CIENTÍFICA"):
            with st.spinner('IA analizando volumen y frecuencia...'):
                time.sleep(1.5)
                # Lógica de generación según días
                if dias <= 3:
                    plan = "**Full Body Elite**: Sentadilla, Banca, Remo (Frecuencia 3)"
                elif dias == 4:
                    plan = "**Torso/Pierna**: L-J: Torso, M-V: Pierna"
                else:
                    plan = "**Push/Pull/Legs**: Rotación continua de empuje, tracción y pierna"
                
                st.session_state['rutina_activa'] = f"{meta} - {plan} ({exp})"
                st.success("¡Rutina generada! Revisa la pestaña 'ENTRENAR'")

    else:
        manual_plan = st.text_area("Escribe tu rutina detallada aquí:", 
                                  value=st.session_state['rutina_activa'], height=300)
        if st.button("💾 GUARDAR MI PLAN MANUAL"):
            st.session_state['rutina_activa'] = manual_plan
            st.success("Plan guardado.")

# --- TAB 3: PROGRESO ---
with tab3:
    if df_historial is not None and not df_historial.empty:
        ejer_sel = st.selectbox("Analizar ejercicio:", df_historial["Ejercicio"].unique())
        df_f = df_historial[df_historial["Ejercicio"] == ejer_sel]
        fig = px.line(df_f, x="Fecha", y="Peso", markers=True, template="plotly_dark", title=f"Progreso en {ejer_sel}")
        fig.update_traces(line_color='#00d4ff')
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 4: TIMER ---
with tab4:
    t = st.number_input("Descanso (segundos)", 30, 300, 90)
    if st.button("INICIAR DESCANSO"):
        b = st.progress(0)
        for i in range(t):
            time.sleep(1)
            b.progress((i+1)/t)
        st.balloons()
