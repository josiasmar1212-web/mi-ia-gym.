import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import plotly.express as px
import time

# 1. CONFIGURACIÓN ESTILO "APP ELITE"
st.set_page_config(page_title="Gym IA Elite", page_icon="🐗", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: #1f2937; color: #00d4ff; border: 1px solid #00d4ff;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1f2937; border-radius: 10px; padding: 10px; color: white; font-size: 12px;
    }
    div[data-testid="stExpander"] { background-color: #1f2937; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
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

st.title("🐗 GYM IA ELITE")

# --- MENÚ TÁCTIL PRINCIPAL ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏋️ ENTRENO", "📈 PROGRESO", "📋 RUTINA IA", "📝 MANUAL", "⏱️ TIMER"])

# --- TAB 1: REGISTRO ---
with tab1:
    if df_ejercicios is not None:
        with st.form("reg_form", clear_on_submit=True):
            st.subheader("Registrar Serie")
            f_musculo = st.selectbox("Grupo", df_ejercicios.iloc[:, 0].unique())
            f_ejer = st.selectbox("Ejercicio", df_ejercicios[df_ejercicios.iloc[:, 0] == f_musculo].iloc[:, 1].unique())
            c1, c2 = st.columns(2)
            f_peso = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0)
            f_reps = c2.number_input("Reps", 1, 100, 10)
            f_sentir = st.select_slider("Estado", options=["😴", "⚡", "🔥"])
            
            if st.form_submit_button("GUARDAR EN DIARIO"):
                conn = st.connection("gsheets", type=GSheetsConnection)
                nueva_fila = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": f_ejer, "Peso": f_peso, "Reps": f_reps, "Estado": f_sentir}])
                df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
                conn.update(worksheet="DATOS", data=df_final)
                st.balloons(); st.success("¡Hecho!"); time.sleep(1); st.rerun()

# --- TAB 2: PROGRESO ---
with tab2:
    if df_historial is not None and not df_historial.empty:
        ejer_sel = st.selectbox("Evolución de:", df_historial["Ejercicio"].unique())
        df_f = df_historial[df_historial["Ejercicio"] == ejer_sel]
        color_col = "Estado" if "Estado" in df_f.columns else None
        fig = px.line(df_f, x="Fecha", y="Peso", markers=True, template="plotly_dark", color=color_col)
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 3: GENERADOR IA (EL QUE QUERÍAS RECUPERAR) ---
with tab3:
    st.subheader("🤖 Planificador por Biotipo")
    perfil = st.selectbox("Tu contextura", ["Ectomorfo (Delgado)", "Endomorfo (Sobrepeso)", "Mesomorfo (Atlético)"])
    dias = st.select_slider("Días de entreno", options=[3, 4, 5])
    
    if st.button("GENERAR RUTINA INTELIGENTE"):
        if "Delgado" in perfil:
            st.info("Foco: Hipertrofia y pocas repeticiones (Fuerza).")
            rutina = {"Día 1: Empuje": ["Banca 3x8", "Militar 3x10"], "Día 2: Tracción": ["Dominadas 3x10", "Remo 3x8"], "Día 3: Pierna": ["Sentadilla 4x8"]}
        elif "Sobrepeso" in perfil:
            st.warning("Foco: Gasto calórico y alta densidad.")
            rutina = {"Día 1: Fullbody A": ["Prensa 3x15", "Flexiones 3x20"], "Día 2: Cardio": ["30 min HIIT"], "Día 3: Fullbody B": ["Burpees 3x15", "Remo 3x15"]}
        else:
            rutina = {"Día 1: Torso": ["Banca", "Remo"], "Día 2: Pierna": ["Sentadilla"], "Día 3: Hombro/Brazo": ["Curl", "Press"]}
        
        for d, ejs in rutina.items():
            with st.expander(f"📍 {d}"):
                for ej in ejs: st.write(f"- {ej}")

# --- TAB 4: MANUAL ---
with tab4:
    st.subheader("📝 Tu Propio Diseño")
    custom = st.text_area("Escribe aquí tu rutina personalizada:", value=st.session_state.get('c', ''), height=250)
    if st.button("GUARDAR MI DISEÑO"):
        st.session_state['c'] = custom
        st.success("Guardado en esta sesión.")

# --- TAB 5: TIMER ---
with tab5:
    st.subheader("⏱️ Descanso Inteligente")
    seg = st.number_input("Segundos", 30, 300, 90)
    if st.button("INICIAR"):
        bar = st.progress(0)
        for i in range(seg):
            time.sleep(1)
            bar.progress((i+1)/seg)
        st.write("¡SIGUIENTE SERIE! 🔥")
