import streamlit as st
import pandas as pd
import io
import zipfile
from html import escape
from urllib.parse import urlsplit, urlunsplit, quote

st.set_page_config(page_title="A+ Content Generator · Amazon", page_icon="🌟", layout="wide")

CC_TURQUESA = "#3EB1C8"
CC_NEGRO    = "#141413"
CC_FONDO    = "#FAF9F5"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif;background:{CC_NEGRO};color:{CC_FONDO}}}
.stApp{{background:{CC_NEGRO}}}
#MainMenu,footer,header{{visibility:hidden}}
.block-container{{padding:2rem 2.5rem 3rem!important;max-width:1400px!important}}
.stButton>button{{background:{CC_TURQUESA}!important;color:{CC_NEGRO}!important;border:none!important;border-radius:8px!important;font-weight:700!important;width:100%!important}}
.stButton>button:hover{{background:#2d9db3!important}}
label{{color:#c0c0b8!important;font-size:0.82rem!important;font-weight:600!important}}
[data-baseweb="select"]>div{{background:#1e1e1c!important;border-color:#3a3a38!important;color:{CC_FONDO}!important}}
div[role="radiogroup"] label p{{color:{CC_FONDO}!important}}
.stProgress>div>div>div{{background:{CC_TURQUESA}!important}}
.section{{background:#1e1e1c;border:1px solid #2e2e2c;border-radius:14px;padding:1.5rem 1.8rem;margin-bottom:1.2rem}}
.section h3{{color:{CC_FONDO}!important;font-size:1rem;font-weight:700;margin:0 0 1rem 0}}
.stat-box{{background:#1a1a1a;border:1px solid #2e2e2c;border-radius:10px;padding:1rem;text-align:center}}
.stat-box .num{{font-size:1.8rem;font-weight:800;color:{CC_TURQUESA};display:block}}
.stat-box .lbl{{font-size:0.72rem;color:#888;text-transform:uppercase;letter-spacing:1.5px}}
.prev-txt{{font-size:0.8rem;color:#444;background:#eeeee6;border-radius:6px;padding:5px 8px;border-left:3px solid {CC_TURQUESA};margin-top:5px;font-style:italic}}
.prev-vacio{{font-size:0.78rem;color:#999;margin-top:5px;font-style:italic}}
</style>
""", unsafe_allow_html=True)

# ── CSS del A+ ────────────────────────────────────────────────
CSS_APLUS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,sans-serif;color:#111;background:#fff;max-width:970px;margin:auto}
img{max-width:100%;display:block;object-fit:contain}
.ap-header{display:flex;align-items:stretch;min-height:320px}
.ap-header-img{width:45%;background:#f5f5f5;overflow:hidden}
.ap-header-img img{width:100%;height:100%;object-fit:cover}
.ap-header-text{flex:1;background:#141413;color:#FAF9F5;padding:40px 36px;display:flex;flex-direction:column;justify-content:center}
.ap-header-text h1{font-size:1.6rem;font-weight:700;line-height:1.3;margin-bottom:16px;color:#FAF9F5}
.ap-header-text p{font-size:0.95rem;line-height:1.7;color:#c8c8c0}
.ap-module{display:flex;align-items:stretch;border-top:3px solid #3EB1C8;min-height:260px}
.ap-module-rev{flex-direction:row-reverse}
.ap-module-img{width:42%;background:#f8f8f8;overflow:hidden;flex-shrink:0}
.ap-module-img img{width:100%;height:100%;object-fit:cover}
.ap-module-text{flex:1;padding:36px 32px;display:flex;flex-direction:column;justify-content:center}
.ap-module-text h2{font-size:1.1rem;font-weight:700;color:#141413;margin-bottom:12px;text-transform:uppercase;letter-spacing:.06em}
.ap-module-text p{font-size:0.92rem;line-height:1.75;color:#444}
.ap-accent{width:36px;height:3px;background:#3EB1C8;margin-bottom:14px}
.ap-specs{background:#FAF9F5;padding:40px 36px;border-top:3px solid #3EB1C8}
.ap-specs h2{font-size:1rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#141413;margin-bottom:24px}
.ap-specs-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
.ap-spec-item{padding:14px 16px;border-bottom:1px solid #e0e0d8;display:flex;align-items:baseline;gap:10px}
.ap-spec-item:nth-child(odd){background:#fff}
.ap-spec-bullet{width:6px;height:6px;border-radius:50%;background:#3EB1C8;flex-shrink:0;margin-top:6px}
.ap-spec-text{font-size:0.88rem;color:#333;line-height:1.5}
"""

# ── Helpers ───────────────────────────────────────────────────
def _esc(v): return escape(str(v or ""))

def _url(v):
    s = str(v or "").split(" | ")[0].strip()
    if not s.startswith("http"): return ""
    try:
        p = urlsplit(s)
        return urlunsplit((p.scheme, p.netloc, quote(p.path, safe="/:@!$&'()*+,;="), p.query, p.fragment))
    except: return s

def _es_url(v):
    return str(v or "").strip().startswith("http")

def _preview(col, muestra, es_imagen=False):
    """Renderiza preview con valor real de la muestra."""
    if not col or col == "(ninguno)":
        st.markdown('<div class="prev-vacio">↳ sin campo seleccionado</div>', unsafe_allow_html=True)
        return
    if col not in muestra:
        st.markdown(f'<div class="prev-vacio">⚠️ "{col}" no está en el fichero</div>', unsafe_allow_html=True)
        return
    val = str(muestra.get(col, "") or "").strip()
    if not val:
        st.markdown('<div class="prev-vacio">↳ campo vacío en este producto</div>', unsafe_allow_html=True)
        return
    url = _url(val)
    if es_imagen and url:
        st.image(url, width=150)
    elif _es_url(val):
        st.markdown(f'<div class="prev-txt" style="font-size:0.7rem;word-break:break-all">↳ {val[:100]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="prev-txt">↳ {val[:120]}</div>', unsafe_allow_html=True)

def _campo_sel(label, key, cols, muestra, es_imagen=False, default="(ninguno)"):
    """Selectbox + preview integrado."""
    opc = ["(ninguno)"] + cols
    actual = st.session_state.get(key, default)
    if actual not in opc: actual = "(ninguno)"
    sel = st.selectbox(label, opc, index=opc.index(actual), key=key)
    _preview(sel, muestra, es_imagen)
    return sel

# ── Generador HTML ────────────────────────────────────────────
def generar_aplus(fila: dict, layout: dict) -> str:
    """
    layout = {
      "header": {"img": campo, "titulo": campo, "desc": campo},
      "modulos": [{"img": campo, "titulo": campo, "desc": campo}, ...],
      "specs":   [campo, campo, ...]
    }
    """
    def val(campo): return str(fila.get(campo, "") or "").strip()
    def img(campo):
        u = _url(val(campo))
        return f'<img src="{u}" alt="" loading="lazy"/>' if u else ""

    # Header
    nom  = _esc(val(layout["header"].get("titulo","")))
    desc = _esc(val(layout["header"].get("desc","")))
    hi   = img(layout["header"].get("img",""))
    header = f"""
<section class="ap-header">
  <div class="ap-header-img">{hi}</div>
  <div class="ap-header-text"><h1>{nom}</h1><p>{desc}</p></div>
</section>"""

    # Módulos
    modulos_html = ""
    for i, m in enumerate(layout.get("modulos", [])):
        tit  = _esc(val(m.get("titulo","")))
        txt  = _esc(val(m.get("desc","")))
        mi   = img(m.get("img",""))
        rev  = "ap-module-rev" if i % 2 == 1 else ""
        modulos_html += f"""
<section class="ap-module {rev}">
  <div class="ap-module-img">{mi}</div>
  <div class="ap-module-text">
    <div class="ap-accent"></div>
    <h2>{tit}</h2>
    <p>{txt}</p>
  </div>
</section>"""

    # Specs
    spec_items = ""
    for campo in layout.get("specs", []):
        v = val(campo)
        if v and not _es_url(v):
            spec_items += f'<div class="ap-spec-item"><div class="ap-spec-bullet"></div><span class="ap-spec-text">{_esc(v)}</span></div>'
    specs_html = f"""
<section class="ap-specs">
  <h2>Caractéristiques</h2>
  <div class="ap-specs-grid">{spec_items}</div>
</section>""" if spec_items else ""

    return f"<style>{CSS_APLUS}</style>{header}{modulos_html}{specs_html}"


def generar_zip(df, layout):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for _, fila in df.iterrows():
            sku  = str(fila.get("SKU","sin_sku")).strip().replace("/","_").replace(" ","_")
            html = generar_aplus(fila.to_dict(), layout)
            zf.writestr(f"{sku}_aplus.html", html.encode("utf-8"))
    buf.seek(0)
    return buf.getvalue()


# ── UI ────────────────────────────────────────────────────────
st.markdown(f"""
<h1 style="font-size:2rem;font-weight:800;color:{CC_FONDO};margin-bottom:.3rem">🌟 A+ Content Generator</h1>
<p style="color:#888;margin-bottom:1.5rem">Amazon · Mapea los campos del fichero Plytix a cada módulo</p>
""", unsafe_allow_html=True)

# ── Paso 1: cargar fichero ─────────────────────────────────────
st.markdown('<div class="section"><h3>📂 Paso 1 — Cargar fichero de datos</h3>', unsafe_allow_html=True)
uploaded = st.file_uploader("Excel o CSV exportado desde Plytix", type=["xlsx","xls","csv"])
if uploaded:
    try:
        df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
        col_sku = next((c for c in df.columns if "sku" in c.lower()), None)
        if col_sku and col_sku != "SKU":
            df = df.rename(columns={col_sku: "SKU"})
        st.session_state["df_aplus"] = df
        st.success(f"✅ {len(df)} productos · {len(df.columns)} campos")
    except Exception as e:
        st.error(f"❌ {e}")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get("df_aplus") is None:
    st.info("Carga un fichero para continuar.")
    st.stop()

df   = st.session_state["df_aplus"]
cols = [c for c in df.columns if c != "SKU"]
cols_img  = [c for c in cols if any(k in c.lower() for k in ["foto","photo","image","img","jpg","png","banner","enhanced","gallery"])]
cols_txt  = [c for c in cols if c not in cols_img]

# Producto de muestra para preview
skus    = df["SKU"].astype(str).tolist()
sku_sel = st.selectbox("Producto de muestra para preview:", skus, key="sku_prev_aplus")
muestra = df[df["SKU"].astype(str) == sku_sel].iloc[0].to_dict()

# ── Paso 2: mapear campos ──────────────────────────────────────
st.markdown('<div class="section"><h3>🗂 Paso 2 — Diseña la estructura A+</h3>', unsafe_allow_html=True)

# Header
st.markdown("**Header**")
hc1, hc2, hc3 = st.columns(3)
with hc1: h_img   = _campo_sel("Imagen hero",    "h_img",   cols_img, muestra, es_imagen=True)
with hc2: h_tit   = _campo_sel("Título",          "h_tit",   cols_txt, muestra)
with hc3: h_desc  = _campo_sel("Descripción",     "h_desc",  cols_txt, muestra)

st.divider()

# Módulos
n_mod = st.number_input("Número de módulos texto+imagen", min_value=1, max_value=8, value=4, step=1, key="n_mod")
modulos_layout = []
for i in range(int(n_mod)):
    st.markdown(f"**Módulo {i+1}** {'(foto izq · texto dcha)' if i%2==1 else '(texto izq · foto dcha)'}")
    mc1, mc2, mc3 = st.columns(3)
    with mc1: m_img = _campo_sel("Imagen",   f"m{i}_img",  cols_img, muestra, es_imagen=True)
    with mc2: m_tit = _campo_sel("Título",   f"m{i}_tit",  cols_txt, muestra)
    with mc3: m_desc= _campo_sel("Texto",    f"m{i}_desc", cols_txt, muestra)
    modulos_layout.append({"img": m_img, "titulo": m_tit, "desc": m_desc})

st.divider()

# Specs
st.markdown("**Módulo de especificaciones** — selecciona los campos que aparecerán como bullets")
specs_sel = st.multiselect(
    "Campos de especificaciones:",
    options=cols,
    default=[c for c in ["highlight_corto_producto_1","highlight_corto_producto_2",
                          "highlight_corto_producto_3","highlight_corto_producto_4",
                          "highlight_corto_producto_5","highlight_corto_producto_6",
                          "watts","voltaje","product_weight","product_width",
                          "product_height","product_depth"] if c in cols],
    key="specs_sel"
)
st.markdown('</div>', unsafe_allow_html=True)

# ── Paso 3: preview y descarga ────────────────────────────────
st.markdown('<div class="section"><h3>👁 Paso 3 — Preview y descarga</h3>', unsafe_allow_html=True)

layout = {
    "header":  {"img": h_img, "titulo": h_tit, "desc": h_desc},
    "modulos": modulos_layout,
    "specs":   specs_sel,
}

with st.expander(f"👁 Preview — {sku_sel}", expanded=True):
    frag = generar_aplus(muestra, layout)
    st.components.v1.html(
        f"<!DOCTYPE html><html><head><meta charset='UTF-8'/></head><body style='background:#fff'>{frag}</body></html>",
        height=900, scrolling=True
    )

st.markdown("**📋 Código HTML — copia y pega en Amazon A+ Content Manager:**")
st.text_area("", value=frag, height=260, key="ta_aplus", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("⚡ Generar ZIP — todos los productos", key="btn_zip_aplus"):
    with st.spinner("Generando A+ para todos los productos..."):
        st.session_state["zip_aplus"]   = generar_zip(df, layout)
        st.session_state["zip_aplus_n"] = len(df)

if st.session_state.get("zip_aplus"):
    st.success(f"✅ {st.session_state['zip_aplus_n']} ficheros A+ listos")
    st.download_button(
        label="⬇️ DESCARGAR ZIP (A+)",
        data=st.session_state["zip_aplus"],
        file_name="aplus_amazon.zip",
        mime="application/zip",
        key="dl_zip_aplus"
    )

st.markdown('</div>', unsafe_allow_html=True)
