import streamlit as st
import pandas as pd
import io
import zipfile
from html import escape

st.set_page_config(page_title="A+ Content Generator · Amazon FR", page_icon="🌟", layout="wide")

# ── Colores Cecotec ───────────────────────────────────────────
CC_TURQUESA = "#3EB1C8"
CC_NEGRO    = "#141413"
CC_FONDO    = "#FAF9F5"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background: {CC_NEGRO}; color: {CC_FONDO}; }}
.stApp {{ background: {CC_NEGRO}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 2rem 2.5rem 3rem !important; max-width: 1400px !important; }}
.stButton > button {{ background: {CC_TURQUESA} !important; color: {CC_NEGRO} !important; border: none !important; border-radius: 8px !important; font-weight: 700 !important; width: 100% !important; }}
.stButton > button:hover {{ background: #2d9db3 !important; }}
label {{ color: #c0c0b8 !important; font-size: 0.82rem !important; font-weight: 600 !important; }}
[data-baseweb="select"] > div {{ background: #1e1e1c !important; border-color: #3a3a38 !important; color: {CC_FONDO} !important; }}
div[role="radiogroup"] label p {{ color: {CC_FONDO} !important; }}
.stProgress > div > div > div {{ background: {CC_TURQUESA} !important; }}
.section-dark {{ background: #1e1e1c; border: 1px solid #2e2e2c; border-radius: 14px; padding: 1.5rem 1.8rem; margin-bottom: 1.2rem; }}
.section-dark h3 {{ color: {CC_FONDO} !important; font-size: 1rem; font-weight: 700; margin: 0 0 1rem 0; }}
.stat-box {{ background: #1e1e1c; border: 1px solid #2e2e2c; border-radius: 10px; padding: 1rem; text-align: center; }}
.stat-box .num {{ font-size: 1.8rem; font-weight: 800; color: {CC_TURQUESA}; display: block; }}
.stat-box .lbl {{ font-size: 0.72rem; color: #888; text-transform: uppercase; letter-spacing: 1.5px; }}
</style>
""", unsafe_allow_html=True)

# ── CSS del HTML A+ generado ──────────────────────────────────
CSS_APLUS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,sans-serif;color:#111;background:#fff;max-width:970px;margin:auto}
img{max-width:100%;display:block;object-fit:contain}

/* HEADER */
.ap-header{display:flex;gap:0;align-items:stretch;margin-bottom:0;min-height:320px}
.ap-header-img{width:45%;background:#f5f5f5;overflow:hidden}
.ap-header-img img{width:100%;height:100%;object-fit:cover}
.ap-header-text{flex:1;background:#141413;color:#FAF9F5;padding:40px 36px;display:flex;flex-direction:column;justify-content:center}
.ap-header-text h1{font-size:1.6rem;font-weight:700;line-height:1.3;margin-bottom:16px;color:#FAF9F5}
.ap-header-text p{font-size:0.95rem;line-height:1.7;color:#c8c8c0}

/* MÓDULOS TEXTO+IMAGEN */
.ap-module{display:flex;gap:0;align-items:stretch;border-top:3px solid #3EB1C8;min-height:260px}
.ap-module-rev{flex-direction:row-reverse}
.ap-module-img{width:42%;background:#f8f8f8;overflow:hidden;flex-shrink:0}
.ap-module-img img{width:100%;height:100%;object-fit:cover}
.ap-module-text{flex:1;padding:36px 32px;display:flex;flex-direction:column;justify-content:center;background:#fff}
.ap-module-text h2{font-size:1.1rem;font-weight:700;color:#141413;margin-bottom:12px;text-transform:uppercase;letter-spacing:.06em}
.ap-module-text p{font-size:0.92rem;line-height:1.75;color:#444}
.ap-accent{width:36px;height:3px;background:#3EB1C8;margin-bottom:14px}

/* SPECS */
.ap-specs{background:#FAF9F5;padding:40px 36px;border-top:3px solid #3EB1C8}
.ap-specs h2{font-size:1rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#141413;margin-bottom:24px}
.ap-specs-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:0}
.ap-spec-item{padding:14px 16px;border-bottom:1px solid #e0e0d8;display:flex;align-items:baseline;gap:10px}
.ap-spec-item:nth-child(odd){background:#fff}
.ap-spec-bullet{width:6px;height:6px;border-radius:50%;background:#3EB1C8;flex-shrink:0;margin-top:6px}
.ap-spec-text{font-size:0.88rem;color:#333;line-height:1.5}
"""


def _esc(v):
    return escape(str(v or ""))


def _url(fila, campo):
    """Primera URL válida de un campo."""
    v = str(fila.get(campo, "") or "").split(" | ")[0].strip()
    if v.startswith("http"):
        from urllib.parse import urlsplit, urlunsplit, quote
        parts = urlsplit(v)
        path_enc = quote(parts.path, safe="/:@!$&'()*+,;=")
        return urlunsplit((parts.scheme, parts.netloc, path_enc, parts.query, parts.fragment))
    return ""


def generar_aplus(fila: dict) -> str:
    sku    = _esc(fila.get("SKU", ""))
    nombre = _esc(fila.get("nombre_producto__modelo_fr", "") or fila.get("nombre_producto__modelo", "") or sku)
    desc_h = _esc(fila.get("descripcion_larga_del_producto_fr", "") or fila.get("descripcion_larga_del_producto", ""))

    img_hero = _url(fila, "foto_master_producto_main_image_1000x1000_png_01")
    hero_img_tag = f'<img src="{img_hero}" alt="{nombre}"/>' if img_hero else ""

    # ── Header ────────────────────────────────────────────────
    header = f"""
<section class="ap-header">
  <div class="ap-header-img">{hero_img_tag}</div>
  <div class="ap-header-text">
    <h1>{nombre}</h1>
    <p>{desc_h}</p>
  </div>
</section>"""

    # ── 4 módulos texto+imagen ────────────────────────────────
    modulos = ""
    for n in range(1, 5):
        titulo = _esc(fila.get(f"descripcion_larga_del_producto_fr", ""))
        desc   = _esc(fila.get(f"descripcion_highlight_{n}_fr", "") or fila.get(f"descripcion_highlight_{n}", ""))
        img_u  = _url(fila, f"foto_enriquecida_0{n}")
        img_tag = f'<img src="{img_u}" alt="{titulo}"/>' if img_u else ""
        rev    = "ap-module-rev" if n % 2 == 0 else ""
        modulos += f"""
<section class="ap-module {rev}">
  <div class="ap-module-img">{img_tag}</div>
  <div class="ap-module-text">
    <div class="ap-accent"></div>
    <h2>{titulo}</h2>
    <p>{desc}</p>
  </div>
</section>"""

    # ── Specs ─────────────────────────────────────────────────
    spec_items = ""
    # Highlights cortos
    for n in range(1, 7):
        v = str(fila.get(f"highlight_corto_producto_{n}", "") or "").strip()
        if v:
            spec_items += f'<div class="ap-spec-item"><div class="ap-spec-bullet"></div><span class="ap-spec-text">{_esc(v)}</span></div>'
    # Datos técnicos
    tech = [
        ("Puissance", "watts", "W"),
        ("Tension", "voltaje", "V"),
        ("Poids", "product_weight", "kg"),
        ("Largeur", "product_width", "cm"),
        ("Hauteur", "product_height", "cm"),
        ("Profondeur", "product_depth", "cm"),
    ]
    for label, campo, unidad in tech:
        v = str(fila.get(campo, "") or "").strip()
        if v and v != "nan":
            spec_items += f'<div class="ap-spec-item"><div class="ap-spec-bullet"></div><span class="ap-spec-text"><strong>{label} :</strong> {_esc(v)} {unidad}</span></div>'

    specs = f"""
<section class="ap-specs">
  <h2>Caractéristiques techniques</h2>
  <div class="ap-specs-grid">{spec_items}</div>
</section>""" if spec_items else ""

    return f"""<style>{CSS_APLUS}</style>
{header}
{modulos}
{specs}"""


def generar_zip_aplus(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for _, fila in df.iterrows():
            sku  = str(fila.get("SKU", "sin_sku")).strip().replace("/", "_").replace(" ", "_")
            html = generar_aplus(fila.to_dict())
            zf.writestr(f"{sku}_aplus_fr.html", html.encode("utf-8"))
    buf.seek(0)
    return buf.getvalue()


# ── UI ────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.5rem">
  <h1 style="font-size:2rem;font-weight:800;color:#FAF9F5;margin:0">🌟 A+ Content Generator</h1>
  <p style="color:#888;margin-top:6px">Amazon FR · Genera contenido A+ desde el Excel de Plytix</p>
</div>
""", unsafe_allow_html=True)

# ── Carga de Excel ────────────────────────────────────────────
st.markdown('<div class="section-dark"><h3>📂 Paso 1 — Cargar Excel de Plytix</h3>', unsafe_allow_html=True)
uploaded = st.file_uploader(
    "Sube el Excel descargado desde Plytix (modo Híbrido o PIM directo)",
    type=["xlsx", "xls", "csv"]
)
df = None
if uploaded:
    try:
        df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
        col_sku = next((c for c in df.columns if "sku" in c.lower()), None)
        if col_sku and col_sku != "SKU":
            df = df.rename(columns={col_sku: "SKU"})
        n_prods = len(df)
        campos_utiles = [c for c in df.columns if any(k in c.lower() for k in
            ["highlight","descripcion","nombre","foto","titulo","watts","weight","width","height","depth","voltaje"])]
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="stat-box"><span class="num">{n_prods}</span><span class="lbl">Productos</span></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-box"><span class="num">{len(df.columns)}</span><span class="lbl">Campos totales</span></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="stat-box"><span class="num">{len(campos_utiles)}</span><span class="lbl">Campos A+</span></div>', unsafe_allow_html=True)
        st.success(f"✅ {n_prods} productos cargados")
        st.session_state["df_aplus"] = df
    except Exception as e:
        st.error(f"❌ Error: {e}")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get("df_aplus") is not None:
    df = st.session_state["df_aplus"]

    # ── Preview ───────────────────────────────────────────────
    st.markdown('<div class="section-dark"><h3>👁 Paso 2 — Preview y generación</h3>', unsafe_allow_html=True)

    skus = df["SKU"].astype(str).tolist()
    sku_sel = st.selectbox("Producto de preview:", skus, key="sku_prev_aplus")
    fila_prev = df[df["SKU"].astype(str) == sku_sel].iloc[0].to_dict()

    with st.expander("👁 Preview A+ — " + sku_sel, expanded=True):
        fragmento = generar_aplus(fila_prev)
        html_completo = f"""<!DOCTYPE html><html lang="fr"><head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
</head><body style="background:#fff">{fragmento}</body></html>"""
        st.components.v1.html(html_completo, height=800, scrolling=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Código copiable del producto seleccionado
    st.markdown("**📋 Código HTML — copia y pega en Amazon A+ Content Manager:**")
    st.text_area("", value=fragmento, height=280, key="ta_aplus_copia",
                 label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    # Generar ZIP con todos
    if st.button("⚡ Generar ZIP — todos los productos", use_container_width=True, key="btn_aplus_zip"):
        with st.spinner("Generando A+ para todos los productos..."):
            zip_bytes = generar_zip_aplus(df)
            st.session_state["zip_aplus"] = zip_bytes
            st.session_state["zip_aplus_n"] = len(df)

    if st.session_state.get("zip_aplus"):
        st.success(f"✅ {st.session_state['zip_aplus_n']} ficheros A+ listos")
        st.download_button(
            label="⬇️ DESCARGAR ZIP (A+ FR)",
            data=st.session_state["zip_aplus"],
            file_name="aplus_fr_cecotec.zip",
            mime="application/zip",
            key="dl_aplus_zip"
        )

    st.markdown('</div>', unsafe_allow_html=True)
