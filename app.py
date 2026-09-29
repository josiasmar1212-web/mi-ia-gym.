# ============================================================
# ESTILOS (CSS) · tema "Ember"
# ============================================================

def apply_custom_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    :root {
        --bg-0:#07060d; --bg-1:#0d0b17; --panel:#121022; --panel-2:#181530;
        --line:rgba(255,140,90,0.16);
        --signal:#ff6b35; --signal-2:#22d3ee; --signal-soft:rgba(255,107,53,0.14);
        --amber:#ffb703; --amber-soft:rgba(255,183,3,0.12);
        --ok:#3ddc97; --red:#ff4d6d; --violet:#8b5cf6; --pink:#ff3d81;
        --text-hi:#f6f3fb; --text-mid:#a9a3c2; --text-low:#67617f;
    }
    * { scrollbar-width: thin; scrollbar-color: var(--signal) var(--bg-1); }
    ::-webkit-scrollbar { width:8px; height:8px; } ::-webkit-scrollbar-track { background:var(--bg-1); }
    ::-webkit-scrollbar-thumb { background:var(--signal); border-radius:8px; }
    .stApp {
        background:
            radial-gradient(circle at 8% 8%, rgba(255,107,53,0.13) 0%, transparent 42%),
            radial-gradient(circle at 92% 18%, rgba(139,92,246,0.13) 0%, transparent 40%),
            radial-gradient(circle at 50% 105%, rgba(34,211,238,0.08) 0%, transparent 45%),
            var(--bg-0);
        color: var(--text-hi); font-family:'Inter',sans-serif;
    }
    h1,h2,h3,h4 { font-family:'Space Grotesk',sans-serif; }

    .hero-card { position:relative; overflow:hidden;
        background:linear-gradient(135deg, rgba(24,21,48,0.95) 0%, rgba(13,11,23,0.97) 100%);
        border:1px solid var(--line); border-radius:22px; padding:30px 34px; margin-bottom:26px;
        display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px;
        box-shadow:0 14px 44px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.05); }
    .hero-card::before { content:""; position:absolute; top:-70%; right:-12%; width:440px; height:440px;
        background:radial-gradient(circle, rgba(255,107,53,0.22) 0%, transparent 70%);
        animation:floatGlow 8s ease-in-out infinite alternate; pointer-events:none; }
    @keyframes floatGlow { from { transform:translate(0,0) scale(1);} to { transform:translate(-30px,30px) scale(1.15);} }
    .hero-eyebrow { font-family:'JetBrains Mono',monospace; color:var(--signal); font-size:0.74rem;
        letter-spacing:3px; text-transform:uppercase; margin-bottom:8px; }
    .hero-title { font-family:'Space Grotesk',sans-serif; font-size:2.1rem; font-weight:800; margin:0;
        background:linear-gradient(90deg,#f6f3fb 35%, var(--signal) 100%);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
    .hero-sub { color:var(--text-mid); font-size:0.94rem; margin-top:6px; max-width:480px; }
    .hero-stats { display:flex; gap:12px; flex-wrap:wrap; z-index:1; }
    .stat-chip { font-family:'JetBrains Mono',monospace; background:rgba(255,255,255,0.03);
        border:1px solid var(--line); padding:10px 18px; border-radius:14px; text-align:center;
        min-width:100px; transition:all .2s ease; }
    .stat-chip:hover { border-color:var(--signal); transform:translateY(-2px); box-shadow:0 6px 18px rgba(255,107,53,0.2); }
    .stat-chip .num { font-size:1.3rem; font-weight:700; color:var(--signal); display:block; }
    .stat-chip .lbl { font-size:0.65rem; color:var(--text-mid); letter-spacing:1px; text-transform:uppercase; }
    .stat-chip.chip-cyan { border-color:rgba(34,211,238,0.35);} .stat-chip.chip-cyan .num { color:var(--signal-2);}
    .stat-chip.chip-amber { border-color:rgba(255,183,3,0.35);} .stat-chip.chip-amber .num { color:var(--amber);}

    .section-title { display:flex; align-items:center; gap:10px; font-family:'Space Grotesk',sans-serif;
        font-size:1.15rem; font-weight:700; margin:4px 0 18px 0; padding-bottom:10px; border-bottom:1px solid var(--line); }
    .timer-display { font-family:'JetBrains Mono',monospace; font-weight:800; font-size:5.5rem; text-align:center;
        padding:44px; border-radius:22px; border:2px solid var(--amber); color:var(--amber);
        background:radial-gradient(circle at 50% 0%, var(--amber-soft), transparent 70%);
        letter-spacing:4px; animation:pulseGlow 1.4s ease-in-out infinite; }
    .work-active { border-color:var(--signal) !important; color:var(--signal) !important;
        background:radial-gradient(circle at 50% 0%, var(--signal-soft), transparent 70%) !important; }
    @keyframes pulseGlow { 0%,100% { box-shadow:0 0 25px rgba(255,183,3,0.12);} 50% { box-shadow:0 0 45px rgba(255,183,3,0.3);} }

    .ia-card { background:linear-gradient(160deg, var(--panel) 0%, var(--panel-2) 100%);
        border:1px solid var(--line); border-left:4px solid var(--signal); border-radius:16px; padding:26px;
        white-space:pre-wrap; line-height:1.7; box-shadow:0 8px 26px rgba(0,0,0,0.3); margin:10px 0; }
    .ia-tag { color:var(--signal); font-family:'JetBrains Mono',monospace; font-size:0.85rem; letter-spacing:1.5px;
        text-transform:uppercase; border-bottom:1px solid var(--line); margin-bottom:14px; padding-bottom:10px; }
    .ia-card.ia-amber { border-left-color:var(--amber);} .ia-card.ia-amber .ia-tag { color:var(--amber);}
    .ia-card.ia-cyan { border-left-color:var(--signal-2);} .ia-card.ia-cyan .ia-tag { color:var(--signal-2);}
    .ia-card.ia-violet { border-left-color:var(--violet);} .ia-card.ia-violet .ia-tag { color:var(--violet);}

    .rm-giant { font-family:'JetBrains Mono',monospace; font-weight:800; font-size:3.8rem; text-align:center; margin:0;
        background:linear-gradient(90deg,var(--signal),var(--amber)); -webkit-background-clip:text;
        -webkit-text-fill-color:transparent; background-clip:text; }

    .readiness-wrap { display:flex; align-items:center; gap:26px; margin-bottom:10px; flex-wrap:wrap; }
    .readiness-ring { width:140px; height:140px; border-radius:50%; display:flex; align-items:center;
        justify-content:center; position:relative; flex-shrink:0; }
    .readiness-high { background:conic-gradient(var(--ok) calc(var(--pct)*1%), rgba(255,255,255,0.07) 0); }
    .readiness-mid { background:conic-gradient(var(--amber) calc(var(--pct)*1%), rgba(255,255,255,0.07) 0); }
    .readiness-low { background:conic-gradient(var(--red) calc(var(--pct)*1%), rgba(255,255,255,0.07) 0); }
    .readiness-ring::after { content:""; position:absolute; width:112px; height:112px; border-radius:50%; background:var(--panel); }
    .readiness-ring .val { font-family:'JetBrains Mono',monospace; font-weight:800; font-size:1.8rem; z-index:1; }
    .readiness-status { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.05rem; }

    .today-card { border:1px solid var(--line); border-radius:18px; padding:22px 24px;
        background:linear-gradient(135deg, rgba(255,107,53,0.14), rgba(139,92,246,0.10)); white-space:pre-wrap; line-height:1.6; }
    .today-card .day { font-family:'JetBrains Mono',monospace; color:var(--signal); font-size:0.78rem;
        letter-spacing:2px; text-transform:uppercase; margin-bottom:8px; }

    section[data-testid="stSidebar"] { background:linear-gradient(180deg, var(--bg-1) 0%, #050409 100%);
        border-right:1px solid var(--line); }
    section[data-testid="stSidebar"] div[role="radiogroup"] label { border-radius:10px; padding:6px 10px;
        margin-bottom:2px; transition:all .15s ease; }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background:rgba(255,107,53,0.10); }
    .stButton>button { border-radius:12px; font-weight:700; transition:all .18s ease; border:1px solid var(--line); }
    .stButton>button:hover { transform:translateY(-2px); box-shadow:0 8px 20px rgba(255,107,53,0.22); border-color:var(--signal); }
    div[data-testid="stMetric"] { background:var(--panel); border:1px solid var(--line); border-radius:14px;
        padding:14px 18px; box-shadow:0 4px 14px rgba(0,0,0,0.25); }
    div[data-testid="stChatMessage"] { border-radius:14px; border:1px solid var(--line); }
    div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] { border-radius:18px !important; border-color:var(--line) !important; }

    @media (max-width:640px) {
        .hero-card { flex-direction:column; align-items:flex-start; padding:22px 20px; }
        .hero-title { font-size:1.5rem; } .hero-sub { max-width:100%; } .hero-stats { width:100%; }
        .stat-chip { flex:1; min-width:0; padding:8px 6px; } .stat-chip .num { font-size:1.05rem; }
        .timer-display { font-size:2.8rem; padding:26px 16px; } .rm-giant { font-size:2.4rem; }
        .section-title { font-size:1rem; } .readiness-wrap { flex-direction:column; align-items:flex-start; gap:14px; }
        .ia-card { padding:18px; }
    }
    </style>
    """, unsafe_allow_html=True)


def style_fig(fig, **kw):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      colorway=PLOT_COLORS, margin=dict(l=10, r=10, t=50, b=10), **kw)
    return fig


# ============================================================
# INTEGRACIÓN CON IA (Claude)
# ============================================================

def _get_secret(name: str) -> Optional[str]:
    try:
        return st.secrets[name]
    except Exception:
        return None


def get_ai_client() -> Optional["anthropic.Anthropic"]:
    if not ANTHROPIC_AVAILABLE:
        return None
    api_key = _get_secret("ANTHROPIC_API_KEY") or st.session_state.get("manual_api_key")
    return anthropic.Anthropic(api_key=api_key) if api_key else None


def call_ai(client, prompt: str, *, system: Optional[str] = None,
            image_b64: Optional[str] = None, media_type: str = "image/jpeg") -> Optional[str]:
    content = []
    if image_b64:
        content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_b64}})
    content.append({"type": "text", "text": prompt})
    kwargs = dict(model=_get_secret("AI_MODEL") or DEFAULT_AI_MODEL, max_tokens=AI_MAX_TOKENS,
                  messages=[{"role": "user", "content": content}])
    if system:
        kwargs["system"] = system
    try:
        with st.spinner("Consultando a tu entrenador IA..."):
            response = client.messages.create(**kwargs)
        return "".join(b.text for b in response.content if b.type == "text")
    except Exception as exc:
        st.error(f"Error al comunicarse con la IA: {exc}")
        return None


def need_ai_warning(client) -> None:
    if client is None:
        st.warning("Configura el entrenador IA en la barra lateral (🔑 Configurar entrenador IA) para usar este módulo.")


# ============================================================
# UTILIDADES
# ============================================================

def is_trainer_view() -> bool:
    return st.session_state.get("modo_app") == "entrenador"


def compute_streak(df_all: pd.DataFrame) -> int:
    if df_all.empty:
        return 0
    fechas = set(pd.to_datetime(df_all["fecha"]).dt.date.unique())
    racha, dia = 0, datetime.now().date()
    while dia in fechas:
        racha += 1
        dia = date.fromordinal(dia.toordinal() - 1)
    return racha


def week_days_active(df_all: pd.DataFrame) -> int:
    if df_all.empty:
        return 0
    hoy = datetime.now().date()
    return len([d for d in pd.to_datetime(df_all["fecha"]).dt.date.unique() if (hoy - d).days < 7])


def readiness_band(score: float) -> tuple[str, str, str]:
    if score >= 80:
        return ("readiness-high", "🟢 ÓPTIMO PARA ROMPER PRs",
                "Tu sistema nervioso está fresco. Día perfecto para máxima intensidad (RPE 9-10) o cargas pesadas.")
    if score >= 60:
        return ("readiness-mid", "🟡 ESTADO NEUTRO / NORMAL",
                "Entrena según lo planificado (RPE 7-8). Escucha a tu cuerpo.")
    return ("readiness-low", "🔴 ALERTA: FATIGA CENTRAL",
            "Riesgo alto de sobreentrenamiento o lesión. Movilidad, cardio suave Z1 o descanso.")


def suggest_progressive_overload(df_ejer: pd.DataFrame) -> Optional[str]:
    if df_ejer.empty:
        return None
    m = re.match(r"([\d.]+)kg x (\d+) \(RIR (\d+)\)", str(df_ejer.iloc[0]["meta"]))
    if not m:
        return None
    peso, reps, rir = float(m.group(1)), int(m.group(2)), int(m.group(3))
    if rir <= 1:
        return f"💪 **Sube el peso:** llegaste casi al fallo (RIR {rir}). Hoy prueba **{peso + 2.5:.1f} kg × {reps} reps**."
    if rir >= 4:
        return f"⚡ **Te sobró margen** (RIR {rir}). Sube a **{peso + 5:.1f} kg × {reps} reps**, o añade una serie."
    return f"🎯 **Progresión en reps:** buen margen (RIR {rir}). Intenta **{peso:.1f} kg × {reps + 1} reps**."


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> tuple[str, str]:
    with st.sidebar:
        st.markdown('<h1 style="font-family:Space Grotesk,sans-serif;color:#ff6b35;letter-spacing:2px;'
                    'font-size:1.5rem;margin-bottom:0;">MORPHAI OS</h1>', unsafe_allow_html=True)
        st.caption(f"v{APP_VERSION} · Ember Edition")
        st.divider()
        st.markdown(f"👤 **{st.session_state.user['name']}**")

        modules = list(MODULES_BASE)
        if is_trainer_view():
            modules.insert(1, MODULE_FEEDBACK)
            st.caption(f"🧑‍🏫 Entrenador · {st.session_state.get('trainer_name', '')}")
            if st.button("⬅️ Volver a mi cartera", use_container_width=True, type="primary"):
                st.session_state["logged_in"] = False
                st.session_state["login_stage"] = "entrenador_roster"
                st.rerun()

        if st.button("🔓 Cerrar sesión", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k not in ("manual_api_key",):
                    st.session_state.pop(k, None)
            st.rerun()

        st.divider()
        if _get_secret("ANTHROPIC_API_KEY") is None:
            with st.expander("🔑 Configurar entrenador IA", expanded=not bool(st.session_state.get("manual_api_key"))):
                st.caption("Tu key solo vive en esta sesión de navegador.")
                key_input = st.text_input("Anthropic API Key", type="password",
                                          value=st.session_state.get("manual_api_key", ""),
                                          help="Consíguela en console.anthropic.com")
                if key_input:
                    st.session_state["manual_api_key"] = key_input
        else:
            st.success("🟢 Entrenador IA activo")

        st.divider()
        modulo = st.radio("Sistema:", modules, label_visibility="collapsed")
        st.divider()
        st.caption("🔒 Cada operador ve solo su propio historial.")
    return st.session_state.user["id"], modulo


# ============================================================
# MÓDULO: INICIO (NUEVO)
# ============================================================

def render_home(user: str) -> None:
    st.markdown('<div class="section-title">🏠 Tu día de un vistazo</div>', unsafe_allow_html=True)
    df = load_entries(user)
    df_r = load_readiness(user)

    if is_trainer_view():
        row = get_connection().execute(
            "SELECT COALESCE(goal,''), COALESCE(notes,'') FROM clients WHERE trainer_id=? AND client_slug=?",
            (st.session_state["trainer_id"], st.session_state.get("client_slug", ""))).fetchone()
        if row and (row[0] or row[1]):
            st.info(f"🎯 **Objetivo:** {row[0] or '—'}\n\n📝 **Notas del entrenador:** {row[1] or '—'}")

    c1, c2 = st.columns([3, 2])
    with c1:
        hoy_i = datetime.now().weekday()
        plan_hoy = load_plan(user).get(DIAS[hoy_i], "").strip()
        if plan_hoy:
            st.markdown(f'<div class="today-card"><div class="day">📅 Hoy · {DIAS[hoy_i]}</div>{plan_hoy}</div>',
                        unsafe_allow_html=True)
        else:
            st.info(f"No hay plan para hoy ({DIAS[hoy_i]}). Créalo en **📅 Plan Semanal**.")

        st.markdown("&nbsp;")
        if df_r.empty:
            st.warning("Aún no hay check-in de readiness. Hazlo en **🧠 Neural Readiness** antes de entrenar.")
        else:
            score = float(df_r.iloc[0]["score"])
            ring, status, advice = readiness_band(score)
            st.markdown(f'<div class="readiness-wrap"><div class="readiness-ring {ring}" style="--pct:{score:.0f}">'
                        f'<span class="val">{score:.0f}%</span></div><div><div class="readiness-status">{status}</div>'
                        f'<p style="color:var(--text-mid);margin-top:8px;max-width:320px;">{advice}</p></div></div>',
                        unsafe_allow_html=True)
    with c2:
        meta = int(st.session_state.get("meta_semanal", 4))
        activos = week_days_active(df)
        st.metric("🔥 Racha", f"{compute_streak(df)} días")
        st.metric("✅ Días activos (7 d)", f"{activos}/{meta}")
        st.progress(min(activos / meta, 1.0))

    st.divider()
    st.markdown("#### 🕒 Últimos registros")
    if df.empty:
        st.caption("Todavía no hay registros. Empieza en cualquier módulo del menú lateral.")
    else:
        st.dataframe(df[["fecha", "tipo", "actividad", "meta"]].head(6), use_container_width=True, hide_index=True)


# ============================================================
# MÓDULO: PLAN SEMANAL (NUEVO)
# ============================================================

def render_plan(user: str) -> None:
    st.markdown('<div class="section-title">📅 Plan Semanal</div>', unsafe_allow_html=True)
    quien = "de tu cliente" if is_trainer_view() else "tuyo"
    st.caption(f"Define qué toca cada día. El plan {quien} de hoy aparece destacado en 🏠 Inicio.")
    plan = load_plan(user)
    hoy_i = datetime.now().weekday()

    with st.form(f"f_plan_{user}"):
        vals = {}
        cols = st.columns(2)
        for i, d in enumerate(DIAS):
            vals[d] = cols[i % 2].text_area(
                ("👉 " if i == hoy_i else "") + d, plan.get(d, ""), height=100,
                placeholder="Ej: Pecho + tríceps · 60 min · Press banca 4x8 RIR 2...", key=f"plan_{user}_{d}")
        if st.form_submit_button("💾 Guardar plan semanal", type="primary"):
            save_plan(user, vals)
            st.success("Plan guardado.")

    if st.session_state.get("ultimo_plan_ia"):
        with st.expander("📋 Ver último plan generado por la IA (para copiar aquí)"):
            st.markdown(st.session_state["ultimo_plan_ia"])


# ============================================================
# MÓDULO: FEEDBACK DEL ENTRENADOR (NUEVO)
# ============================================================

def render_feedback(user: str) -> None:
    st.markdown('<div class="section-title">💬 Feedback del entrenador</div>', unsafe_allow_html=True)
    st.caption("Deja comentarios fechados sobre la evolución de este cliente. Sirven de bitácora de seguimiento.")
    with st.form(f"f_fb_{user}", clear_on_submit=True):
        texto = st.text_area("Nuevo comentario", placeholder="Ej: Mejoró técnica en sentadilla. Subir carga 2.5 kg.")
        if st.form_submit_button("➕ Guardar comentario", type="primary"):
            if texto.strip():
                save_feedback(user, texto)
                st.rerun()
            else:
                st.warning("Escribe algo antes de guardar.")
    df = load_feedback(user)
    if df.empty:
        st.info("Aún no hay comentarios para este cliente.")
    for _, r in df.iterrows():
        st.markdown(f'<div class="ia-card ia-violet"><div class="ia-tag">🗒️ {r["fecha"]}</div>{r["texto"]}</div>',
                    unsafe_allow_html=True)


# ============================================================
# MÓDULO: NEURAL READINESS
# ============================================================

def render_readiness(user: str) -> None:
    st.markdown('<div class="section-title">🧠 Evaluación Diaria del Sistema Nervioso (Readiness)</div>', unsafe_allow_html=True)
    st.caption("El sobreentrenamiento destruye el progreso. Mide tu fatiga y HRV antes de cargar la barra.")
    c1, c2 = st.columns(2)
    with c1:
        with st.form("f_readiness", clear_on_submit=True):
            sueno = st.number_input("Horas de sueño anoche", 1.0, 14.0, 7.5, 0.5)
            calidad = st.slider("Calidad del sueño (1: Pésimo, 10: Óptimo)", 1, 10, 8)
            doms = st.slider("Dolor muscular / DOMS (1: Ninguno, 10: Extremo)", 1, 10, 3)
            estres = st.slider("Estrés general/mental (1: Relajado, 10: Alto)", 1, 10, 4)
            hrv = st.number_input("HRV matutino (ms, 0 si no lo mides)", 0, 200, 65)
            nota_r = st.text_input("Nota del estado matutino", "Buen descanso")
            if st.form_submit_button("Calcular y guardar readiness"):
                score = (sueno / 8.0 * 30) + (calidad * 3) + ((11 - doms) * 2.5) + ((11 - estres) * 1.5)
                if hrv > 0:
                    score = (score * 0.8) + min(hrv / 80.0 * 20, 20)
                score = min(max(score, 10), 100)
                save_readiness(user, sueno, calidad, doms, estres, hrv, score, nota_r)
                st.success(f"Readiness registrado: {score:.1f}%")
                st.rerun()
    with c2:
        df_r = load_readiness(user)
        if df_r.empty:
            st.info("Registra tu primer check-in matutino para calibrar tu entrenamiento.")
            return
        ring, status, advice = readiness_band(float(df_r.iloc[0]["score"]))
        st.markdown(f'<div class="readiness-wrap"><div class="readiness-ring {ring}" style="--pct:{df_r.iloc[0]["score"]:.0f}">'
                    f'<span class="val">{df_r.iloc[0]["score"]:.0f}%</span></div><div><div class="readiness-status">{status}</div>'
                    f'<p style="color:var(--text-mid);margin-top:8px;max-width:320px;">{advice}</p></div></div>',
                    unsafe_allow_html=True)
        st.divider()
        fig = px.line(df_r.head(14).sort_values("id"), x="fecha", y="score", markers=True,
                      title="Tendencia de Readiness (últimos 14 registros)")
        fig.update_traces(line_color=C_MAIN)
        st.plotly_chart(style_fig(fig), use_container_width=True)


# ============================================================
# MÓDULO: FUERZA
# ============================================================

def render_strength(user: str) -> None:
    st.markdown('<div class="section-title">🏋️ Entrenamiento de Fuerza</div>', unsafe_allow_html=True)
    grupos = ["Pecho", "Espalda", "Piernas", "Glúteos", "Pantorrillas", "Hombros", "Brazos", "Antebrazos", "Core", "Calistenia"]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title">📥 Registro de Set</div>', unsafe_allow_html=True)
        grupo = st.selectbox("Grupo muscular", grupos)
        render_body_diagram(grupo)
        with st.form("f_gym", clear_on_submit=True):
            ejer = st.selectbox("Ejercicio", DB_EXERCISES[grupo])
            c_p, c_r, c_rir = st.columns(3)
            peso = c_p.number_input("Carga (kg)", 0.0, 500.0, 40.0, 2.5)
            reps = c_r.number_input("Reps", 1, 50, 10)
            rir = c_rir.number_input("RIR", 0, 5, 2, help="Repeticiones que te quedaban antes del fallo.")
            if st.form_submit_button("Registrar set"):
                ton = peso * reps
                save_entry(user, f"Fuerza-{grupo}", ejer, ton, f"{peso}kg x {reps} (RIR {rir})", f"RPE {10 - rir}")
                st.session_state["ultimo_peso"], st.session_state["ultimas_reps"] = peso, reps
                st.success(f"Set de {ejer} guardado. Tonelaje: {ton:.0f} kg.")
        info = DB_EXERCISE_INFO.get(ejer)
        if info:
            st.caption(f"💡 **Trabaja:** {info[0]} — {info[1]}")
        st.divider()
        st.markdown(f"#### 📜 Historial — {ejer}")
        df_e = load_entries(user)
        df_e = df_e[df_e["actividad"] == ejer] if not df_e.empty else df_e
        if not df_e.empty:
            pr = df_e["valor"].max()
            st.metric("🏆 Récord de tonelaje", f"{pr:.0f} kg", help=f"Logrado el {df_e[df_e['valor'] == pr].iloc[0]['fecha']}")
            sug = suggest_progressive_overload(df_e)
            if sug:
                st.info(sug)
            st.dataframe(df_e[["fecha", "meta", "extra"]].head(5), use_container_width=True, hide_index=True)
        else:
            st.caption("Aún no hay sets de este ejercicio. Este será tu primer PR.")
    with c2:
        st.markdown('<div class="section-title">🧮 Estimación 1RM (Brzycki)</div>', unsafe_allow_html=True)
        p_rm = st.number_input("Peso para cálculo", 1.0, 500.0, float(st.session_state.get("ultimo_peso", 100.0)))
        r_rm = st.number_input("Reps para cálculo", 1, 12, int(st.session_state.get("ultimas_reps", 5)))
        rm = p_rm / (1.0278 - (0.0278 * r_rm)) if r_rm < 37 else p_rm
        st.markdown(f'<p class="rm-giant">{round(rm, 1)} KG</p>', unsafe_allow_html=True)
        st.divider()
        st.write("**Zonas de intensidad sugeridas:**")
        st.write(f"🔴 **95%:** {round(rm * .95, 1)} kg · 🟠 **85%:** {round(rm * .85, 1)} kg · 🟢 **70%:** {round(rm * .7, 1)} kg")
        st.divider()
        st.markdown("#### 🔥 Series de calentamiento sugeridas")
        st.write("1. Barra vacía / ligero × 12 reps")
        st.write(f"2. {round(rm * .4, 1)} kg × 8 reps")
        st.write(f"3. {round(rm * .6, 1)} kg × 4 reps")
        st.write(f"4. {round(rm * .8, 1)} kg × 1 rep")
        st.caption("Para un calentamiento personalizado ve a 🔥 AI Warm-up & Form Coach.")

    st.divider()
    st.markdown('<div class="section-title">⚖️ Balance Muscular Acumulado</div>', unsafe_allow_html=True)
    df_f = load_entries(user)
    df_f = df_f[df_f["tipo"].str.startswith("Fuerza-")] if not df_f.empty else df_f
    if not df_f.empty:
        df_f = df_f.copy()
        df_f["grupo"] = df_f["tipo"].str.replace("Fuerza-", "", regex=False)
        bal = df_f.groupby("grupo")["valor"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(bal, x="grupo", y="valor", title="Tonelaje total por grupo muscular", color="grupo",
                     color_discrete_sequence=PLOT_COLORS)
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_fig(fig), use_container_width=True)
        if len(bal) > 1:
            st.caption(f"💡 Priorizas **{bal.iloc[0]['grupo']}**; vigila que **{bal.iloc[-1]['grupo']}** no se rezague.")
    else:
        st.caption("Registra tus primeros sets para ver aquí tu balance muscular.")


# ============================================================
# MÓDULO: RUNNING
# ============================================================

def _fmt_pace(p: float) -> str:
    return f"{int(p)}:{int((p % 1) * 60):02d} min/km"


def render_running(user: str) -> None:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title">🏃 Registro de Resistencia</div>', unsafe_allow_html=True)
        with st.form("f_run", clear_on_submit=True):
            tipo = st.selectbox("Tipo de estímulo", DB_EXERCISES["Running"])
            dist = st.number_input("Distancia (km)", 0.1, 100.0, 5.0, 0.5)
            mins = st.number_input("Minutos", 1, 500, 25)
            hr = st.slider("BPM medio", 60, 220, 145)
            if st.form_submit_button("Guardar run"):
                save_entry(user, "Running", tipo, dist, _fmt_pace(mins / dist), f"{hr} BPM")
                st.session_state["ultima_dist"] = dist
                st.success("Carrera guardada.")
        st.divider()
        st.markdown("#### 📜 Últimas carreras")
        df = load_entries(user)
        df = df[df["tipo"] == "Running"] if not df.empty else df
        if not df.empty:
            st.dataframe(df[["fecha", "actividad", "valor", "meta", "extra"]].head(5)
                         .rename(columns={"valor": "km", "meta": "pace", "extra": "BPM"}),
                         use_container_width=True, hide_index=True)
        else:
            st.caption("Aún no registras carreras.")
    with c2:
        st.markdown('<div class="section-title">📐 Zonas de ritmo</div>', unsafe_allow_html=True)
        pb = st.number_input("Tu mejor tiempo en 5K (minutos)", 10.0, 60.0, 25.0, 0.5)
        base = pb / 5.0
        st.write(f"**Pace de referencia (5K):** {_fmt_pace(base)}")
        st.divider()
        for z, k in (("🟢 Z1 Recuperación", 1.4), ("🔵 Z2 Base aeróbica", 1.25), ("🟡 Z3 Tempo", 1.1),
                     ("🟠 Z4 Umbral", 1.03), ("🔴 Z5 VO2 Max", .95)):
            st.write(f"**{z}:** {_fmt_pace(base * k)}")
        st.divider()
        cal = round(st.session_state.get("ultima_dist", 0) * (st.session_state.user.get("weight") or 75) * 1.036)
        st.metric("🔥 Calorías estimadas (última carrera)", f"{cal} kcal")
        st.caption("Estimación aproximada (≈ 1.036 kcal/kg/km).")


# ============================================================
# MÓDULO: COMBATE
# ============================================================

def render_combat(user: str) -> None:
    st.subheader("⏱️ Temporizador Táctico de Combate")
    preset = st.radio("Preset rápido", ["Personalizado", "Tabata Clásico (8x20/10)", "Boxeo Amateur (3x180/60)",
                                        "HIIT Largo (5x240/60)"], horizontal=True)
    presets = {"Tabata Clásico (8x20/10)": (8, 20 / 60, 10), "Boxeo Amateur (3x180/60)": (3, 3.0, 60),
               "HIIT Largo (5x240/60)": (5, 4.0, 60)}
    d_r, d_w, d_d = presets.get(preset, (3, 3.0, 30))
    t1, t2, t3 = st.columns(3)
    rds = t1.number_input("Rounds", 1, 15, d_r, key=f"rds_{preset}")
    w_t = t2.number_input("Trabajo (min)", 0.1, 5.0, float(d_w), key=f"wt_{preset}")
    r_t = t3.number_input("Descanso (seg)", 5, 90, d_d, key=f"rt_{preset}")
    if st.button("🔔 Iniciar rounds"):
        ph = st.empty()
        for r in range(1, rds + 1):
            for t in range(int(w_t * 60), 0, -1):
                ph.markdown(f'<div class="timer-display work-active">ROUND {r}<br>{t // 60:02d}:{t % 60:02d}</div>',
                            unsafe_allow_html=True)
                time.sleep(1)
            if r < rds:
                for t in range(r_t, 0, -1):
                    ph.markdown(f'<div class="timer-display">REST<br>00:{t:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
        ph.success("🔥 Combate finalizado con éxito")
        save_entry(user, "Combate-Rounds", preset, rds, f"{rds} rounds", f"{w_t:.1f}min trabajo / {r_t}s desc.")
    st.divider()
    st.subheader("⚡ Biblioteca de Explosividad y Potencia")
    with st.form("f_ex", clear_on_submit=True):
        ej = st.selectbox("Ejercicio de potencia", DB_EXERCISES["Explosividad"])
        reps = st.slider("Reps explosivas", 1, 30, 6)
        lastre = st.number_input("Lastre extra (kg)", 0, 100, 0)
        if st.form_submit_button("Registrar potencia"):
            save_entry(user, "Combate", ej, reps, f"{reps} reps", f"{lastre}kg lastre")
            st.success("Registro guardado.")
    df = load_entries(user)
    df = df[df["tipo"].str.startswith("Combate")] if not df.empty else df
    if not df.empty:
        st.markdown("#### 📜 Historial reciente")
        st.dataframe(df[["fecha", "actividad", "meta", "extra"]].head(5), use_container_width=True, hide_index=True)


# ============================================================
# MÓDULO: MOVILIDAD
# ============================================================

def render_mobility(user: str) -> None:
    st.markdown('<div class="section-title">🧘 Movilidad y Regeneración</div>', unsafe_allow_html=True)
    st.caption("La recuperación también es entrenamiento.")
    c1, c2 = st.columns(2)
    with c1:
        with st.form("f_mov", clear_on_submit=True):
            mov = st.selectbox("Ejercicio de movilidad", DB_EXERCISES["Movilidad"])
            dur = st.slider("Duración (minutos)", 1, 60, 10)
            sens = st.select_slider("Sensación al terminar", options=["Tenso", "Normal", "Suelto", "Óptimo"])
            if st.form_submit_button("Registrar sesión"):
                save_entry(user, "Movilidad", mov, dur, f"{dur} min", sens)
                st.success(f"Sesión de {mov} guardada.")
        info = DB_EXERCISE_INFO.get(mov)
        if info:
            st.caption(f"💡 **Enfoque:** {info[0]} — {info[1]}")
    with c2:
        st.markdown("#### 🔄 Rutina rápida (5 min)")
        for t in ("**Movilidad de cadera:** 60s por lado", "**Movilidad torácica:** 60s en rodillas",
                  "**Estiramiento isquiotibiales:** 60s por lado", "**Movilidad de hombro:** 60s con banda",
                  "**Respiración diafragmática:** 60s"):
            st.write("• " + t)
        st.info("Ideal antes de entrenar o como cierre de un día de descanso.")


# ============================================================
# MÓDULO: NUTRICIÓN
# ============================================================

def render_nutrition(user: str) -> None:
    st.markdown('<div class="section-title">🍎 Motor Metabólico & Combustible</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    u = st.session_state.user
    with c1:
        st.markdown("#### 🧮 Calculadora TDEE")
        peso = st.number_input("Peso actual (kg)", 40.0, 160.0, min(max(float(u["weight"] or 75), 40.0), 160.0))
        alt = st.number_input("Altura (cm)", 140, 220, min(max(int(u["height"] or 175), 140), 220))
        edad = st.number_input("Edad", 15, 80, min(max(int(u["age"] or 25), 15), 80))
        mult = {"Sedentario (poco o ningún ejercicio)": 1.2, "Ligero (1-3 días/semana)": 1.375,
                "Moderado (3-5 días/semana)": 1.55, "Intenso (6-7 días/semana)": 1.725,
                "Atleta de élite (dobles sesiones)": 1.9}
        act = st.selectbox("Nivel de actividad física", list(mult), index=2)
        tdee = (10 * peso + 6.25 * alt - 5 * edad + 5) * mult[act]
        st.metric("🔥 Calorías de mantenimiento (TDEE)", f"{tdee:.0f} kcal/día")
        st.write(f"📉 **Déficit:** {tdee - 500:.0f} kcal | 📈 **Superávit:** {tdee + 300:.0f} kcal")
        st.write(f"💧 **Hidratación recomendada:** {peso * 0.04:.1f} L/día")
        st.caption("Fórmula Mifflin-St Jeor (base masculina). Orientativa.")
    with c2:
        st.markdown("#### 📥 Registro diario de ingesta")
        with st.form("f_nutricion", clear_on_submit=True):
            cal = st.number_input("Calorías totales", 0, 10000, 2500, 50)
            prot = st.number_input("Proteínas (g)", 0, 500, 160, 5)
            carb = st.number_input("Carbohidratos (g)", 0, 1000, 250, 10)
            fat = st.number_input("Grasas (g)", 0, 300, 70, 5)
            agua = st.number_input("Agua (litros)", 0.0, 10.0, 3.0, 0.25)
            if st.form_submit_button("Guardar macros del día"):
                save_nutrition(user, cal, prot, carb, fat, agua)
                st.success("Ingesta registrada.")
        df = load_nutrition(user)
        if not df.empty:
            st.markdown("#### 📜 Historial reciente")
            st.dataframe(df[["fecha", "calorias", "proteina", "carbs", "grasa", "agua_l"]].head(5)
                         .rename(columns={"calorias": "Kcal", "proteina": "Prot(g)", "carbs": "Carbs(g)",
                                          "grasa": "Grasa(g)", "agua_l": "Agua(L)"}),
                         use_container_width=True, hide_index=True)
