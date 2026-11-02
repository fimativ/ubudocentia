"""UBU-Docentia, herramienta no oficial. Streamlit app: ubudocentia.streamlit.app"""
import json
from pathlib import Path

import streamlit as st

from encuestas import leer_informe, media_items
from textos import ELEMENTOS_EXPERTO, ELEMENTOS_NOVEL, prompt_reflexion

VERSION = "2.3"
HERE = Path(__file__).parent
st.set_page_config(page_title="UBU-Docentia (no oficial)", page_icon="🌡️", layout="wide",
                   initial_sidebar_state="collapsed")

# ------------------------------------------------------------------ baremo (manual v4.07, anexo 5)
# (key, label, points per unit, own cap or None, advanced-only)
EJES = {
    "e1": ("Eje 1 · Coordinación y planificación", 10, {
        "b11": ("Comisiones y órganos", 8, [
            ("1.1", "Comisión de título (años)", 1.25, None, False),
            ("1.2", "Comisiones docentes (años)", 1, None, False),
            ("1.3", "Plan de estudios / verificación (años)", 1, None, True),
            ("1.4", "Comisiones SGIC (años)", 0.5, None, True),
            ("1.5", "Coordinación de curso (años)", 1, None, False),
            ("1.6", "Coordinación de asignatura (años)", 0.3, None, True),
            ("1.7", "Coordinación PAT / Mentor (años)", 1, None, True),
            ("1.8", "Dirección de área (años)", 1, None, True),
            ("1.9", "Comisiones de selección (años)", 1, None, True)]),
        "b12": ("Movilidad", 6, [
            ("1.10", "Coordinación de movilidad (años; 0.5 si sin estudiantes)", 1, None, False),
            ("1.11", "Coordinación ERASMUS / SICUE (años)", 1, None, True),
            ("1.12", "Misiones docentes (n.º)", 0.25, None, True)]),
        "b13": ("Otras", 3, [
            ("1.13", "Otras comisiones y representación (puntos)", 1, None, True)])}),
    "e2": ("Eje 2 · Desarrollo de la docencia", 20, {
        "b21": ("Docencia impartida", 16, [
            ("2.1", "Docencia sobre referencia (6–12 puntos)", 1, 12, False),
            ("2.2", "Variedad y primer curso (años)", 1, 5, False),
            ("2.3", "Planes a extinguir (puntos)", 1, None, True),
            ("2.4", "Estudiantes atendidos (0–4 puntos)", 1, 4, False)]),
        "b22": ("Atención personalizada", 6, [
            ("2.5", "PAT (años)", 0.6, None, False),
            ("2.6", "Programa Mentor (años)", 0.6, None, True)]),
        "b23": ("Recursos y actividades", 8, [
            ("2.7", "Uso de UBUVirtual (0–6 puntos)", 1, 6, False),
            ("2.8", "Visitas, talleres, seminarios (n.º)", 0.5, None, True),
            ("2.9", "Tribunales TFG/TFM/tesis (n.º)", 2, None, False),
            ("2.10", "Dirección de TFG/TFM (n.º)", 0.5, None, False),
            ("2.10b", "Dirección de tesis (n.º)", 1, None, True),
            ("2.11", "TFG/TFM en repositorio (n.º)", 0.5, None, True)]),
        "b24": ("Otras", 3, [
            ("2.12", "Otras actividades (puntos)", 1, None, True)])}),
    "e3": ("Eje 3 · Actividades complementarias", 15, {
        "b31": ("Transición secundaria-universidad", 6, [
            ("2.13", "Jornadas de puertas abiertas (años)", 1, None, False),
            ("2.14", "Olimpiadas (n.º)", 0.75, None, True),
            ("2.15", "Tutela de trabajos de secundaria (n.º)", 1, None, True),
            ("2.16", "Prácticas o talleres para secundaria (n.º)", 1, None, True),
            ("2.17", "Jornadas de titulación para secundaria (n.º)", 1, None, True),
            ("2.18", "Semana de la Ciencia (años)", 1, None, False),
            ("2.19", "Cursos cero (n.º)", 1.5, None, True)]),
        "b32": ("Formación", 10, [
            ("2.20", "Formación docente recibida (horas)", 0.08, 6, False),
            ("2.21", "Formación en docencia online, PFEV (horas)", 0.08, 6, True),
            ("2.22", "Cursos docentes impartidos (n.º)", 2, None, False),
            ("2.23", "Cursos de docencia online impartidos (n.º)", 2, None, True),
            ("2.24", "Congresos científicos con ponencia (n.º)", 0.75, None, False),
            ("2.25", "Jornadas de innovación en docencia online (n.º)", 0.75, None, True),
            ("2.26", "Jornadas de innovación docente (n.º)", 0.75, None, True),
            ("2.27", "Tesis en curso (años)", 0.5, 1.5, True),
            ("2.28", "Tesis defendida (2 cum laude, 1 apto)", 1, 2, True)]),
        "b33": ("Innovación", 10, [
            ("3.1", "Libro o manual universitario (puntos)", 1, 10, False),
            ("3.2", "Libro o manual de docencia online (puntos)", 1, 10, True),
            ("3.3", "Capítulo de libro (puntos)", 1, 4, True),
            ("3.4", "Capítulo sobre docencia online (puntos)", 1, 4, True),
            ("3.5", "Artículos docentes (n.º)", 2, None, False),
            ("3.6", "Artículos sobre docencia online (n.º)", 2, None, True),
            ("3.7", "Dirección de proyecto de innovación UBU (años)", 1.5, None, False),
            ("3.8", "Participación en proyecto UBU (años)", 0.75, None, False),
            ("3.9", "Dirección de proyecto externo (años)", 2, None, True),
            ("3.10", "Participación en proyecto externo (años)", 1, None, True),
            ("3.11", "Materiales abiertos (puntos)", 1, 10, False),
            ("3.12", "Materiales abiertos de docencia online (puntos)", 1, 10, True)]),
        "b34": ("Otras", 3, [
            ("3.13", "Otros materiales (puntos)", 1, None, True)])}),
}
ALL_KEYS = [it[0] for e in EJES.values() for b in e[2].values() for it in b[2]]

# ------------------------------------------------------------------ palette (UBU web) and colour scale
BLUE, NAVY, LIGHT, WINE, PINK, GREY, RULE = "#006DB3", "#002E4B", "#E6F0F7", "#470E19", "#F7E9EC", "#55565B", "#D1D5DB"
RED = "#C0392B"
RAINBOW = ["#7c2790", "#4b3ada", "#4766f2", "#2e86ea", "#1fa9da", "#00afaf", "#3bc09f", "#5ecc7a",
           "#9dca40", "#dcb935", "#ffba4b", "#f8d82f", "#efec21"]


def hex2rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def scale_colour(t):
    t = max(0.0, min(1.0, t)) * (len(RAINBOW) - 1)
    i = min(int(t), len(RAINBOW) - 2)
    f = t - i
    a, b = hex2rgb(RAINBOW[i]), hex2rgb(RAINBOW[i + 1])
    return tuple(round(a[k] + f * (b[k] - a[k])) for k in range(3))


def mix(rgb, white=0.86):
    return "#%02x%02x%02x" % tuple(round(c + (255 - c) * white) for c in rgb)


# ------------------------------------------------------------------ state
DEFAULTS = {**{f"k_{k}": 0.0 for k in ALL_KEYS}, "novel": True, "avanzado": False, "refl": 0,
            "mpve_manual": 12.0, "theta": 1.0, "delta": 1.0, "asig": []}
if "pending" in st.session_state:
    for k, v in st.session_state.pop("pending").items():
        st.session_state[k] = v
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


def val(k):
    return float(st.session_state.get(f"k_{k}", 0) or 0)


def export_json():
    return json.dumps({k: st.session_state[k] for k in DEFAULTS}, ensure_ascii=False, indent=1)


# ------------------------------------------------------------------ scoring
ejes, bloques = {}, {}
for e, (name, emax, blocks) in EJES.items():
    tot = 0.0
    for b, (bname, bcap, items) in blocks.items():
        s = 0.0
        for key, label, pts, cap, _ in items:
            v = val(key) * pts
            s += min(v, cap) if cap else v
        bloques[b] = (s, bcap)
        tot += min(s, bcap)
    ejes[e] = min(tot, emax)
act = sum(ejes.values())
actW = act * 35 / 45
refl = float(st.session_state["refl"])
reflW = refl * 30 / 35
asig = st.session_state["asig"]
usable = [a for a in asig if a.get("media") and (a.get("part") or 0) >= 25]
media_pond = sum(a["part"] * a["media"] for a in usable) / sum(a["part"] for a in usable) if usable else None
if media_pond is not None:
    mpve = max(12.0, min(35.0, 1.10 * float(st.session_state["theta"]) * float(st.session_state["delta"]) * 7 * media_pond))
else:
    mpve = float(st.session_state["mpve_manual"])

total = actW + reflW + mpve
ok = act >= 12 and mpve >= 12
if not ok:
    grade, gtxt = "D", "umbral no superado: " + ", ".join(
        x for x, bad in (("actividad docente", act < 12), ("encuestas", mpve < 12)) if bad)
elif total < 50:
    grade, gtxt = "D", "deficiente"
elif total < 65:
    grade, gtxt = "C", "correcto"
elif total < 85:
    grade, gtxt = "B", "destacado"
else:
    grade, gtxt = "A", "excelente (orientativo)"
rgb = scale_colour(total / 100)
col_full = "#%02x%02x%02x" % rgb
col_bg, col_card = mix(rgb, 0.55), mix(rgb, 0.85)
col_dark = "#%02x%02x%02x" % tuple(round(c * 0.55) for c in rgb)

# ------------------------------------------------------------------ CSS
st.markdown(f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
html,body,.stApp,[data-testid="stAppViewContainer"]{{font-family:Inter,Arial,Helvetica,sans-serif}}
.stApp,[data-testid="stAppViewContainer"]{{background:{col_bg} !important;transition:background .6s}}
[data-testid="stHeader"]{{background:transparent}}
.block-container{{padding-top:1rem;padding-bottom:2rem;max-width:1280px}}
.hero{{display:grid;grid-template-columns:auto 1fr;gap:18px;align-items:center;background:{col_card};
  border:1px solid {RULE};border-radius:14px;padding:14px 20px;margin:4px 0 12px}}
.hero .letter{{font-size:84px;font-weight:800;line-height:1;color:{col_dark}}}
.hero .value{{font-size:22px;font-weight:700;color:{NAVY}}}
.hero .txt{{font-size:13px;color:{GREY}}}
.scale{{position:relative;height:18px;border-radius:9px;margin:10px 0 22px;
  background:linear-gradient(90deg,{','.join(RAINBOW)})}}
.scale .tick{{position:absolute;top:0;width:2px;height:18px;background:rgba(0,0,0,.4)}}
.scale .lab{{position:absolute;top:20px;font-size:11px;color:{GREY};transform:translateX(-50%)}}
.scale .mark{{position:absolute;top:-6px;width:4px;height:30px;background:{NAVY};border-radius:2px;transform:translateX(-2px)}}
.topbar{{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-bottom:4px}}
.topbar h1{{font-size:26px;font-weight:800;color:{NAVY};margin:0}}
.pill{{display:inline-block;padding:3px 12px;border-radius:999px;font-size:12px;font-weight:600;background:{PINK};color:{WINE}}}
.pill.blue{{background:{LIGHT};color:{NAVY}}}
.card-h{{display:flex;justify-content:space-between;align-items:baseline;font-weight:700;color:{NAVY};font-size:15px;margin-bottom:2px}}
.card-h em{{font-style:normal;font-weight:600;color:{GREY};font-size:12px}}
.bar{{position:relative;height:9px;border-radius:5px;background:#e8eaed;margin:3px 0 8px}}
.bar i{{display:block;height:100%;border-radius:5px}}
.bar s{{position:absolute;top:-4px;width:2px;height:17px;background:{WINE};text-decoration:none}}
.card-h .sat{{color:{RED} !important}}
.foot{{font-size:11.5px;color:{GREY};border-top:1px solid {RULE};margin-top:14px;padding-top:10px;line-height:1.5}}
.st-key-grid [data-testid="stHorizontalBlock"]{{flex-wrap:wrap;gap:14px}}
.st-key-grid [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{{flex:0 0 calc(33.333% - 10px);min-width:calc(33.333% - 10px)}}
.st-key-grid [data-testid="stVerticalBlockBorderWrapper"]{{background:{col_card}}}
@media (max-width:860px){{
  .st-key-grid [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{{flex:0 0 100%;min-width:100%}}
  .topbar h1{{font-size:20px}} .hero .letter{{font-size:60px}}
}}
[data-testid="stNumberInput"] label p,[data-testid="stSlider"] label p,[data-testid="stCheckbox"] p{{font-size:12px}}
.st-key-grid [data-testid="stMarkdownContainer"] ol li, .st-key-grid [data-testid="stMarkdownContainer"] p{{font-size:13px}}
[data-testid="stExpander"] summary p{{font-size:13px;font-weight:600}}
[data-testid="stFileUploaderDropzone"]{{padding:4px 10px;min-height:0}}
[data-testid="stFileUploaderDropzoneInstructions"] span{{display:none}}
[data-testid="stFileUploaderDropzone"] button{{font-size:0 !important}}
[data-testid="stFileUploaderDropzone"] button > *{{display:none !important}}
[class*="st-key-jsonup"] [data-testid="stFileUploaderDropzone"] button::after{{content:"Cargar JSON";font:400 14px Inter,Arial,sans-serif}}
[class*="st-key-pdfs"] [data-testid="stFileUploaderDropzone"] button::after{{content:"Subir informes PDF";font:400 14px Inter,Arial,sans-serif}}
[data-testid="stFileUploader"] section,[data-testid="stFileUploaderDropzone"]{{background:transparent !important;border:none !important;padding:0 !important}}
[data-testid="stFileUploaderDropzone"] button{{width:100%;height:2.5rem;background:#fff;border:1px solid {RULE};border-radius:.5rem;color:{NAVY}}}
[data-testid="stFileUploaderDropzone"] button:hover{{border-color:{BLUE};color:{BLUE}}}
[data-testid="stFileUploaderDropzone"]>div:first-child:not(:has(button)){{display:none}}
[data-testid="stFileUploaderFile"],[data-testid="stFileUploaderPagination"],[data-testid="stFileUploader"] [data-testid="stFileUploaderDeleteBtn"]{{display:none !important}}
[data-testid="stFileUploader"] ul,[data-testid="stFileUploader"] section+div{{display:none !important}}
button,button p{{font-family:Inter,Arial,sans-serif !important}}
[data-testid="stFileUploader"]{{margin:0 !important}} [data-testid="stFileUploaderDropzone"]{{min-height:0 !important}}
.stButton button,.stDownloadButton button{{height:2.5rem;border-radius:.5rem;color:{NAVY};border-color:{RULE};white-space:nowrap}}
.stButton button:hover,.stDownloadButton button:hover{{border-color:{BLUE};color:{BLUE}}}
label p,[data-testid="stWidgetLabel"] p{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
[data-testid="stTabs"] button p{{font-size:13px;font-weight:600}}
.sub{{font-size:12.5px;color:{GREY};font-weight:600;margin:4px 0 2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.els{{margin:2px 0 8px 0;padding:0;font-size:13px;line-height:1.7;list-style-position:inside}}
.els li{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.tb{{width:100%;font-size:12.5px;border-collapse:collapse;margin:4px 0}}
.tb th{{color:{GREY};font-weight:600;text-align:left;border-bottom:1px solid {RULE}}}
.tb td,.tb th{{padding:3px 4px;white-space:nowrap}}
.tb td+td,.tb th+th{{text-align:right}}
.topbar{{margin:0 !important}}
[data-testid="stFileUploaderDropzone"]{{display:block !important;width:100%}}
[data-testid="stFileUploaderDropzone"]>div,[data-testid="stFileUploaderDropzone"] button{{width:100% !important}}
@media (max-width:640px){{
  .st-key-top [data-testid="stHorizontalBlock"]{{flex-wrap:wrap !important;flex-direction:row !important;gap:8px}}
  .st-key-top [data-testid="stColumn"]{{flex:0 0 calc(50% - 4px) !important;min-width:calc(50% - 4px) !important;width:calc(50% - 4px) !important}}
  .st-key-top [data-testid="stColumn"]:first-child{{flex:0 0 100% !important;min-width:100% !important;width:100% !important}}
}}
.topbar h1{{white-space:nowrap}}
</style>""", unsafe_allow_html=True)

# ------------------------------------------------------------------ top bar (one line)
top = st.container(key="top")
t0, t1, t2, t3, t4, t5 = top.columns([2.6, 0.9, 1, 1, 1, 0.9], vertical_alignment="center")
with t0:
    st.markdown(f'<div class="topbar"><h1>UBU-Docentia</h1><span class="pill">NO OFICIAL · v{VERSION}</span></div>',
                unsafe_allow_html=True)
with t1:
    st.toggle("Avanzado", key="avanzado")
with t2:
    st.download_button("Guardar JSON", export_json(), "docentia.json", "application/json", use_container_width=True)
with t3:
    up = st.file_uploader("Cargar JSON", type="json", label_visibility="collapsed", key=f"jsonup_{st.session_state.get('json_v', 0)}")
    if up is not None:
        try:
            d = json.loads(up.read().decode("utf-8"))
            pend = {k: d[k] for k in DEFAULTS if k in d}
            pend["json_v"] = st.session_state.get("json_v", 0) + 1
            st.session_state["pending"] = pend
            st.rerun()
        except Exception:
            st.warning("No se pudo leer el JSON.")
with t4:
    html_local = HERE / "docentia_ubu.html"
    if html_local.exists():
        st.download_button("Copia local", html_local.read_bytes(), "docentia_ubu.html", "text/html",
                           use_container_width=True, help="Versión ligera que funciona sin conexión.")
with t5:
    if st.button("Borrar", use_container_width=True):
        st.session_state["pending"] = dict(DEFAULTS)
        st.rerun()

# ------------------------------------------------------------------ hero: letter, value, colour scale
ticks = "".join(f'<span class="tick" style="left:{s}%"></span>' for s in (50, 65, 85))
labs = "".join(f'<span class="lab" style="left:{x}%">{g}</span>' for g, x in (("D", 25), ("C", 57.5), ("B", 75), ("A", 92.5)))
st.markdown(f"""<div class="hero">
<div class="letter">{grade}</div>
<div><div class="value">{total:.1f} / 100 <span class="txt">· {gtxt}</span></div>
<div class="scale">{ticks}{labs}<span class="mark" style="left:{max(0,min(100,total)):.1f}%"></span></div>
<div class="txt">Actividad docente {actW:.1f} / 35 · Reflexión {reflW:.1f} / 30 · Encuestas {mpve:.1f} / 35</div></div>
</div>""", unsafe_allow_html=True)


def bar(v, mx, color, thr=None):
    s = f'<s style="left:{100*thr/mx:.1f}%"></s>' if thr is not None else ""
    return f'<div class="bar"><i style="width:{100*min(v,mx)/mx:.1f}%;background:{color}"></i>{s}</div>'


def header(title, right, saturated=False):
    cls = ' class="sat"' if saturated else ""
    st.markdown(f'<div class="card-h"><span{cls}>{title}</span><em{cls}>{right}</em></div>', unsafe_allow_html=True)


def red(text, on):
    return f":red[{text}]" if on else text


SHORT_NOVEL = ["Encargo docente", "Materiales y capturas de UBUVirtual", "Desarrollo profesional",
               "Reflexión sobre las encuestas", "Evaluación y retroalimentación", "Innovación y reconocimientos"]
SHORT_EXPERTO = ["Encargo docente", "Esfuerzo de desarrollo y mejora", "Reflexión sobre las encuestas",
                 "Evaluación y retroalimentación", "Innovación y reconocimientos"]
H = 560
colors = {"e1": "#00afaf", "e2": "#4faa5e", "e3": "#d99a1f"}
with st.container(key="grid"):
    c1, c2, c3 = st.columns(3)

    with c1, st.container(border=True, height=H):
        header("Actividad docente", f"{act:.1f} / 45 · umbral 12")
        st.markdown(bar(act, 45, BLUE, 12), unsafe_allow_html=True)
        satcss = "".join(f'.st-key-tabs_ejes [role="tab"]:nth-of-type({i}) p{{color:{RED} !important}}'
                         for i, e in enumerate(EJES, 1) if ejes[e] >= EJES[e][1] - 1e-9)
        if satcss:
            st.markdown(f"<style>{satcss}</style>", unsafe_allow_html=True)
        tabs = st.tabs([f"Eje {i}" for i in range(1, len(EJES) + 1)], key="tabs_ejes")
        for tab, (e, (name, emax, blocks)) in zip(tabs, EJES.items()):
            with tab:
                sat = ejes[e] >= emax - 1e-9
                st.markdown(f'<div class="card-h" style="font-size:13px"><span{" class=sat" if sat else ""}>{name.split("· ")[1]}</span>'
                            f'<em{" class=sat" if sat else ""}>{ejes[e]:.1f} / {emax}</em></div>' + bar(ejes[e], emax, colors[e]),
                            unsafe_allow_html=True)
                for b, (bname, bcap, items) in blocks.items():
                    shown = [it for it in items if st.session_state["avanzado"] or not it[4]]
                    if not shown:
                        continue
                    s_, cap = bloques[b]
                    with st.expander(red(f"{bname} · {min(s_, cap):g}/{cap}", s_ >= cap), key=f"exp_{b}"):
                        for key, label, pts, cap_i, _ in shown:
                            st.number_input(f"{key} {label}", min_value=0.0, step=1.0 if pts >= 1 else 0.5,
                                            key=f"k_{key}", format="%g")

    with c2, st.container(border=True, height=H):
        header("Reflexión sobre la práctica", f"{refl:.0f} / 35")
        st.markdown(bar(refl, 35, "#7c2790"), unsafe_allow_html=True)
        st.slider("Autoevaluación", 0, 35, key="refl")
        st.toggle("Profesorado novel", key="novel")
        novel = bool(st.session_state["novel"])
        items = "".join(f"<li>{x}</li>" for x in (SHORT_NOVEL if novel else SHORT_EXPERTO))
        st.markdown(f'<div class="sub">Elementos del informe</div><ol class="els">{items}</ol>', unsafe_allow_html=True)
        prompt = prompt_reflexion(novel)
        with st.expander("Prompt de revisión con IA", key="exp_prompt"):
            st.code(prompt, language="text")
        st.download_button("Descargar prompt", prompt, "prompt_reflexion_docentia.txt", use_container_width=True)

    with c3, st.container(border=True, height=H):
        header("Encuestas del estudiantado", f"MPVE {mpve:.1f} / 35")
        st.markdown(bar(mpve - 12, 23, BLUE), unsafe_allow_html=True)
        if media_pond is None:
            st.slider("MPVE manual", 12.0, 35.0, step=0.1, key="mpve_manual")
        files = st.file_uploader("Informes de encuesta (PDF)", type="pdf", accept_multiple_files=True,
                                 key=f"pdfs_{st.session_state.get('pdfs_v', 0)}", label_visibility="collapsed")
        if files:
            names = {a.get("file") for a in asig}
            nuevo = False
            for f in files:
                if f.name in names:
                    continue
                try:
                    inf = leer_informe(f.read())
                    med, n = media_items(inf)
                    asig.append({"file": f.name, "asignatura": inf["asignatura"], "curso": inf["curso"],
                                 "media": med, "n_items": n, "part": inf["participacion"], "modalidad": inf["modalidad"]})
                    nuevo = True
                except Exception:
                    st.warning(f"No se pudo leer {f.name}.")
            st.session_state["asig"] = asig
            st.session_state["pdfs_v"] = st.session_state.get("pdfs_v", 0) + 1
            st.rerun()
        if asig:
            rows = "".join(f'<tr><td>{x["asignatura"].title()[:24]}</td><td>{x["media"]:.2f}</td><td>{x["part"]:.0f} %</td></tr>'
                           for x in asig if x["media"])
            st.markdown(f'<table class="tb"><tr><th>Asignatura</th><th>Media</th><th>Part.</th></tr>{rows}</table>',
                        unsafe_allow_html=True)
            if media_pond is not None:
                st.markdown(f'<div class="sub">Media ponderada {media_pond:.2f} / 5 · MPVE estimado {mpve:.1f}</div>',
                            unsafe_allow_html=True)
            if st.button("Quitar informes", use_container_width=True):
                st.session_state["asig"] = []
                st.session_state["pdfs_v"] = st.session_state.get("pdfs_v", 0) + 1
                st.rerun()
        k1, k2 = st.columns(2)
        with k1:
            st.number_input("θ asignaturas", 0.9, 1.1, step=0.01, key="theta", format="%.3f",
                            help="1 si ≤ 4 asignaturas; 1.01 si 5–10; 1.02 si ≥ 11.")
        with k2:
            st.number_input("δ créditos", 0.9, 1.1, step=0.005, key="delta", format="%.3f",
                            help="1 bajo el primer tercil; 1.015 entre terciles; 1.030 sobre el segundo.")

st.markdown(f"""<div class="foot">
<b>HERRAMIENTA NO OFICIAL · versión {VERSION} · usar bajo propia responsabilidad.</b>
Cálculo orientativo según el <a href="https://www.ubu.es/sites/default/files/portal_page/files/Manual%20de%20evaluaci%C3%B3n%20de%20la%20actividad%20docente%20del%20profesorado%20-%20version%204.07.pdf">Manual de evaluación de la actividad docente, v4.07</a>:
global ≈ actividad × 35/45 + reflexión × 30/35 + MPVE; bandas D &lt; 50, C 50–65, B 65–85, A ≥ 85 (el manual no fija el corte de A).
El MPVE estimado desde los PDF (1,10 · θ · δ · 7 · media ponderada por participación, tope 35) es una reconstrucción, no la fórmula oficial.
No se almacena ninguna información personal en el servidor: los datos viven sólo en su navegador durante la sesión y en los JSON que usted descargue.
Puede descargar una copia local de esta herramienta con el botón «Copia local».<br>
Código abierto bajo licencia MIT · © 2026 Sinuhé Perea Puente · Universidad de Burgos.
</div>""", unsafe_allow_html=True)
