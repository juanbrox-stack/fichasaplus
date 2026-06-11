import streamlit as st
import pandas as pd
import io
import zipfile
from html import escape
from urllib.parse import urlsplit, urlunsplit, quote

st.set_page_config(page_title="A+ Content Generator", page_icon="🌟", layout="wide")

CC_T = "#3EB1C8"
CC_N = "#141413"
CC_F = "#FAF9F5"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif;background:{CC_N};color:{CC_F}}}
.stApp{{background:{CC_N}}}
#MainMenu,footer,header{{visibility:hidden}}
.block-container{{padding:2rem 2.5rem 3rem!important;max-width:1400px!important}}
.stButton>button{{background:{CC_T}!important;color:{CC_N}!important;border:none!important;border-radius:8px!important;font-weight:700!important;width:100%!important}}
.stButton>button:hover{{background:#2d9db3!important}}
label{{color:#c0c0b8!important;font-size:0.82rem!important;font-weight:600!important}}
[data-baseweb="select"]>div{{background:#1e1e1c!important;border-color:#3a3a38!important;color:{CC_F}!important}}
div[role="radiogroup"] label p{{color:{CC_F}!important}}
.stProgress>div>div>div{{background:{CC_T}!important}}
.section{{background:#1e1e1c;border:1px solid #2e2e2c;border-radius:14px;padding:1.5rem 1.8rem;margin-bottom:1.2rem}}
.section h3{{color:{CC_F}!important;font-size:1rem;font-weight:700;margin:0 0 1rem 0}}
.stat-box{{background:#1a1a1a;border:1px solid #2e2e2c;border-radius:10px;padding:1rem;text-align:center}}
.stat-box .num{{font-size:1.8rem;font-weight:800;color:{CC_T};display:block}}
.stat-box .lbl{{font-size:0.72rem;color:#888;text-transform:uppercase;letter-spacing:1.5px}}
.prev-txt{{font-size:0.8rem;color:#444;background:#eeeee6;border-radius:6px;padding:5px 8px;border-left:3px solid {CC_T};margin-top:5px;font-style:italic}}
.prev-vacio{{font-size:0.78rem;color:#999;margin-top:5px;font-style:italic}}
.mod-badge{{display:inline-block;background:{CC_T};color:{CC_N};font-size:.72rem;font-weight:700;padding:2px 10px;border-radius:20px;margin-bottom:8px}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# CSS + JS GLOBAL DEL HTML GENERADO
# ══════════════════════════════════════════════════════════════
# ── Constante de límite ──────────────────────────────────────
LIMIT = 5000

# Etiquetas prohibidas por Cdiscount: html, head, body, script,
# link, style, iframe, table, a → todo con estilos INLINE, sin JS

# ── Estilos inline compartidos ───────────────────────────────
_S = {
    "wrap":    "max-width:970px;margin:auto;font-family:Arial,sans-serif;color:#111",
    "accent":  "width:36px;height:3px;background:#3EB1C8;margin-bottom:14px",
    "border":  "border-top:3px solid #3EB1C8",
    "turq":    "#3EB1C8",
    "dark":    "#141413",
    "light":   "#FAF9F5",
}

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def _esc(v): return escape(str(v or ""))

def _url(v):
    s = str(v or "").split(" | ")[0].strip()
    if not s.startswith("http"): return ""
    try:
        p = urlsplit(s)
        return urlunsplit((p.scheme, p.netloc, quote(p.path, safe="/:@!$&'()*+,;="), p.query, p.fragment))
    except: return s

def _es_url(v): return str(v or "").strip().startswith("http")

def _uid():
    import random, string
    return "ap" + "".join(random.choices(string.ascii_lowercase, k=6))



def _val(fila, campo): return str(fila.get(campo, "") or "").strip()

# Mapa de clases antiguas → estilos inline (fallback para versión desplegada)
_CLASS_TO_STYLE = {
    "ap-header":       "display:flex;flex-direction:column;max-width:970px;margin:auto;font-family:Arial,sans-serif",
    "ap-header-img":   "width:100%;overflow:hidden;max-height:480px",
    "ap-header-text":  "background:#141413;color:#FAF9F5;padding:32px 36px",
    "ap-module":       "display:flex;align-items:stretch;border-top:3px solid #3EB1C8;min-height:300px;max-width:970px;margin:auto;font-family:Arial,sans-serif",
    "ap-module-rev":   "display:flex;flex-direction:row-reverse;align-items:stretch;border-top:3px solid #3EB1C8;min-height:300px;max-width:970px;margin:auto;font-family:Arial,sans-serif",
    "ap-module-img":   "width:45%;overflow:hidden;flex-shrink:0",
    "ap-module-text":  "flex:1;padding:32px 36px;display:flex;flex-direction:column;justify-content:center",
    "ap-accent":       "width:36px;height:3px;background:#3EB1C8;margin-bottom:14px",
    "ap-specs":        "background:#FAF9F5;padding:40px 36px;border-top:3px solid #3EB1C8;max-width:970px;margin:auto;font-family:Arial,sans-serif",
    "ap-spec-item":    "padding:12px 16px;border-bottom:1px solid #e0e0d8;display:flex;align-items:center;gap:10px",
    "ap-spec-bullet":  "width:6px;height:6px;border-radius:50%;background:#3EB1C8;flex-shrink:0",
    "ap-spec-text":    "font-size:.88rem;color:#333",
    "ap-video":        "border-top:3px solid #3EB1C8;background:#141413;max-width:970px;margin:auto",
    "ap-video-caption":"padding:16px 36px;background:#1a1a18",
    "ap-grid":         "border-top:3px solid #3EB1C8;padding:36px;background:#FAF9F5;max-width:970px;margin:auto;font-family:Arial,sans-serif",
    "ap-grid-items":   "display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:18px",
    "ap-grid-item":    "text-align:center;padding:18px 10px;background:#fff;border-radius:10px;border:1px solid #e8e8e0",
    "ap-compare":      "border-top:3px solid #3EB1C8;padding:36px;overflow-x:auto;max-width:970px;margin:auto;font-family:Arial,sans-serif",
    "ap-carousel":     "border-top:3px solid #3EB1C8;padding:20px;overflow-x:auto;max-width:970px;margin:auto;font-family:Arial,sans-serif",
    "ap-tabs":         "border-top:3px solid #3EB1C8;max-width:970px;margin:auto;font-family:Arial,sans-serif",
    "ap-accordion":    "border-top:3px solid #3EB1C8;max-width:970px;margin:auto;font-family:Arial,sans-serif",
    "ap-accordion-item":"border-bottom:1px solid #e0e0d8",
}

def sanitize_html(html: str) -> str:
    """
    Limpia el HTML para Cdiscount:
    1. Elimina etiquetas prohibidas (style, script, iframe, a)
    2. section → div
    3. Convierte class="ap-*" a estilos inline (compatibilidad con versión antigua)
    """
    import re

    # 1. Eliminar bloques prohibidos
    html = re.sub(r"<style[^>]*>.*?</style>",  "", html, flags=re.DOTALL)
    html = re.sub(r"<script[^>]*>.*?</script>","", html, flags=re.DOTALL)
    html = re.sub(r"<iframe[^>]*>.*?</iframe>","", html, flags=re.DOTALL)
    html = re.sub(r"<iframe[^>]*/>",           "", html)
    html = re.sub(r"<a [^>]*>",  "", html)
    html = re.sub(r"</a>",       "", html)

    # 2. section → div
    html = re.sub(r"<section([^>]*)>", lambda m: "<div" + m.group(1) + ">", html)
    html = re.sub(r"</section>", "</div>", html)

    # 3. class="ap-X ap-Y" → style="..." (convierte clases legacy a inline)
    def reemplazar_clase(m):
        tag    = m.group(1)   # nombre del tag
        attrs  = m.group(2)   # atributos
        clases = re.findall(r'class="([^"]*)"', attrs)
        if not clases:
            return m.group(0)
        nombres = clases[0].split()
        estilos = " ".join(_CLASS_TO_STYLE.get(c, "") for c in nombres if c in _CLASS_TO_STYLE)
        attrs_sin_class = re.sub(r'class="[^"]*"', "", attrs).strip()
        if estilos:
            return "<" + tag + ' style="' + estilos + '" ' + attrs_sin_class + ">"
        return "<" + tag + " " + attrs_sin_class + ">"

    html = re.sub(r"<(div|span|h[1-6]|p|img|figure)(\s[^>]*)?>",
                  lambda m: reemplazar_clase(m) if m.group(2) and "class=" in m.group(2) else m.group(0),
                  html)

    return html.strip()
def _img_tag(fila, campo, alt=""):
    u = _url(_val(fila, campo))
    return f'<img src="{u}" alt="{_esc(alt)}" loading="lazy"/>' if u else ""

# ══════════════════════════════════════════════════════════════
# GENERADORES POR TIPO DE MÓDULO
# ══════════════════════════════════════════════════════════════
def gen_header(fila, cfg):
    u   = _url(_val(fila, cfg.get("img","")))
    nom = _esc(_val(fila, cfg.get("titulo","")))
    dsc = _esc(_val(fila, cfg.get("desc","")))
    img = f'<img src="{u}" style="width:100%;height:100%;object-fit:cover" loading="lazy"/>' if u else ""
    return (
        f'<div style="{_S["wrap"]}">' +
        f'<div style="width:100%;overflow:hidden;max-height:480px">{img}</div>' +
        f'<div style="background:{_S["dark"]};color:{_S["light"]};padding:32px 36px">' +
        f'<h1 style="font-size:1.5rem;font-weight:700;line-height:1.3;margin-bottom:12px;color:{_S["light"]}">{nom}</h1>' +
        f'<p style="font-size:.95rem;line-height:1.7;color:#c8c8c0">{dsc}</p></div></div>'
    )

def gen_modulo(fila, cfg, idx):
    u   = _url(_val(fila, cfg.get("img","")))
    tit = _esc(_val(fila, cfg.get("titulo","")))
    txt = _esc(_val(fila, cfg.get("desc","")))
    img = f'<img src="{u}" style="width:100%;height:100%;object-fit:cover" loading="lazy"/>' if u else ""
    row = "row-reverse" if idx % 2 == 1 else "row"
    return (
        f'<div style="{_S["wrap"]};display:flex;flex-direction:{row};align-items:stretch;{_S["border"]};min-height:300px">' +
        f'<div style="width:45%;overflow:hidden;flex-shrink:0">{img}</div>' +
        f'<div style="flex:1;padding:32px 36px;display:flex;flex-direction:column;justify-content:center">' +
        f'<div style="{_S["accent"]}"></div>' +
        f'<h2 style="font-size:1.1rem;font-weight:700;color:{_S["dark"]};margin-bottom:12px">{tit}</h2>' +
        f'<p style="font-size:.92rem;line-height:1.75;color:#444">{txt}</p></div></div>'
    )

def gen_specs(fila, cfg):
    titulo = _esc(cfg.get("titulo_fijo","Caractéristiques"))
    items  = ""
    for i, campo in enumerate(cfg.get("campos",[])):
        v = _val(fila, campo)
        if not v or _es_url(v): continue
        bg = "#fff" if i%2==0 else "#f9f9f7"
        items += (
            f'<div style="padding:12px 16px;border-bottom:1px solid #e0e0d8;display:flex;align-items:center;gap:10px;background:{bg}">' +
            f'<div style="width:6px;height:6px;border-radius:50%;background:{_S["turq"]};flex-shrink:0"></div>' +
            f'<span style="font-size:.88rem;color:#333">{_esc(v)}</span></div>'
        )
    if not items: return ""
    return (
        f'<div style="{_S["wrap"]};background:{_S["light"]};padding:40px 36px;{_S["border"]}">' +
        f'<h2 style="font-size:1rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:{_S["dark"]};margin-bottom:24px">{titulo}</h2>' +
        f'{items}</div>'
    )

def gen_carrusel(fila, cfg):
    """Sin JS interactivo — muestra slides como grid estático."""
    slides_cfg = cfg.get("slides",[])
    if not slides_cfg: return ""
    items = ""
    for s in slides_cfg:
        u   = _url(_val(fila, s.get("img","")))
        tit = _esc(_val(fila, s.get("titulo","")) or s.get("titulo_fijo",""))
        txt = _esc(_val(fila, s.get("desc","")) or s.get("desc_fija",""))
        img = f'<img src="{u}" style="width:100%;height:240px;object-fit:cover;display:block"/>' if u else ""
        cap = (f'<div style="background:rgba(20,20,19,.8);color:{_S["light"]};padding:14px 20px">' +
               f'<h3 style="font-size:.95rem;font-weight:700;margin-bottom:6px">{tit}</h3>' +
               f'<p style="font-size:.82rem;color:#ddd">{txt}</p></div>') if tit or txt else ""
        items += f'<div style="position:relative;flex:0 0 auto;width:300px;overflow:hidden;border-radius:4px">{img}{cap}</div>'
    return (
        f'<div style="{_S["wrap"]};{_S["border"]};padding:20px;overflow-x:auto">' +
        f'<div style="display:flex;gap:16px;width:max-content">{items}</div></div>'
    )

def gen_tabs(fila, cfg):
    """Sin JS — pestañas como secciones apiladas con título destacado."""
    tabs_cfg = cfg.get("tabs",[])
    if not tabs_cfg: return ""
    out = f'<div style="{_S["wrap"]};{_S["border"]}">'
    for i, t in enumerate(tabs_cfg):
        label = _esc(_val(fila, t.get("label","")) or t.get("label_fijo",f"Tab {i+1}"))
        u     = _url(_val(fila, t.get("img","")))
        tit   = _esc(_val(fila, t.get("titulo","")) or t.get("titulo_fijo",""))
        txt   = _esc(_val(fila, t.get("desc","")) or t.get("desc_fija",""))
        img   = f'<img src="{u}" style="width:45%;height:100%;object-fit:cover;flex-shrink:0"/>' if u else ""
        bt    = "#3EB1C8" if i==0 else "#1e1e1c"
        out  += (
            f'<div style="background:{bt};color:{_S["light"]};padding:10px 20px;font-size:.88rem;font-weight:700">{label}</div>' +
            f'<div style="display:flex;min-height:260px;border-bottom:1px solid #e0e0d8">{img}' +
            f'<div style="flex:1;padding:28px 32px;display:flex;flex-direction:column;justify-content:center">' +
            f'<h3 style="font-size:1.05rem;font-weight:700;margin-bottom:10px;color:{_S["dark"]}">{tit}</h3>' +
            f'<p style="font-size:.9rem;line-height:1.75;color:#444">{txt}</p></div></div>'
        )
    return out + "</div>"

def gen_accordion(fila, cfg):
    """Sin JS — acordeón como lista de secciones colapsadas visualmente."""
    items_cfg = cfg.get("items",[])
    if not items_cfg: return ""
    out = f'<div style="{_S["wrap"]};{_S["border"]}">'
    for item in items_cfg:
        tit = _esc(_val(fila, item.get("titulo","")) or item.get("titulo_fijo",""))
        txt = _esc(_val(fila, item.get("desc","")) or item.get("desc_fija",""))
        u   = _url(_val(fila, item.get("img","")))
        img = f'<img src="{u}" style="max-width:320px;margin-bottom:12px;border-radius:4px"/>' if u else ""
        out += (
            f'<div style="border-bottom:1px solid #e0e0d8">' +
            f'<div style="padding:18px 24px;font-size:.95rem;font-weight:700;color:{_S["dark"]};background:#fff;display:flex;justify-content:space-between">' +
            f'{tit}<span style="color:{_S["turq"]}">+</span></div>' +
            f'<div style="padding:0 24px 18px;font-size:.9rem;line-height:1.75;color:#444;background:#fafaf8">{img}<p>{txt}</p></div>' +
            f'</div>'
        )
    return out + "</div>"

def gen_grid(fila, cfg):
    items_cfg = cfg.get("items",[])
    if not items_cfg: return ""
    titulo    = _esc(cfg.get("titulo_fijo","Características destacadas"))
    items_html = ""
    for item in items_cfg:
        u    = _url(_val(fila, item.get("img","")))
        icon = item.get("icon_fijo","")
        tit  = _esc(_val(fila, item.get("titulo","")) or item.get("titulo_fijo",""))
        txt  = _esc(_val(fila, item.get("desc","")) or item.get("desc_fija",""))
        ico  = (f'<img src="{u}" style="width:60px;height:60px;object-fit:contain;margin:0 auto 12px;display:block"/>' if u
                else f'<div style="font-size:2rem;margin-bottom:12px;text-align:center">{icon}</div>' if icon else "")
        items_html += (
            f'<div style="text-align:center;padding:18px 10px;background:#fff;border-radius:10px;border:1px solid #e8e8e0">' +
            f'{ico}<h4 style="font-size:.82rem;font-weight:700;color:{_S["dark"]};margin-bottom:6px">{tit}</h4>' +
            f'<p style="font-size:.78rem;color:#666;line-height:1.5">{txt}</p></div>'
        )
    return (
        f'<div style="{_S["wrap"]};{_S["border"]};padding:36px;background:{_S["light"]}">' +
        f'<h2 style="font-size:1rem;font-weight:700;text-transform:uppercase;color:{_S["dark"]};margin-bottom:24px;text-align:center">{titulo}</h2>' +
        f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:18px">{items_html}</div></div>'
    )

def gen_video(fila, cfg):
    """Omitido en el HTML exportado (iframe prohibido en Cdiscount)."""
    return ""

def gen_video_preview(fila, cfg):
    """Solo para preview en la app — usa iframe permitido en st.components."""
    url = cfg.get("url_fija","") or _val(fila, cfg.get("url_campo",""))
    if not url: return ""
    caption = _esc(_val(fila, cfg.get("caption","")) or cfg.get("caption_fija",""))
    if "youtube.com" in url or "youtu.be" in url:
        vid = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1].split("?")[0]
        embed = f'<iframe src="https://www.youtube.com/embed/{vid}" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;border:none"></iframe>'
        wrapper = f'<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden">{embed}</div>'
    elif "vimeo.com" in url:
        vid = url.rstrip("/").split("/")[-1]
        embed = f'<iframe src="https://player.vimeo.com/video/{vid}" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;border:none"></iframe>'
        wrapper = f'<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden">{embed}</div>'
    elif url.lower().endswith((".mp4",".webm",".ogg")):
        wrapper = f'<video src="{url}" controls playsinline style="width:100%;display:block"></video>'
    else:
        wrapper = f'<p style="padding:24px;color:{_S["light"]};font-size:.9rem">▶ {url}</p>'
    cap = f'<p style="padding:16px 36px;background:#1a1a18;color:#c8c8c0;font-size:.9rem">{caption}</p>' if caption else ""
    return f'<div style="{_S["wrap"]};{_S["border"]};background:{_S["dark"]}">{wrapper}{cap}</div>'

def gen_compare(fila, cfg):
    """Sin <table>: comparativa con divs en grid."""
    cols_cfg  = cfg.get("columnas",[])
    filas_cfg = cfg.get("filas",[])
    if not cols_cfg and not filas_cfg: return ""
    titulo = _esc(cfg.get("titulo_fijo","Comparaison"))
    n      = len(cols_cfg)+1
    head   = f'<div style="background:{_S["turq"]};color:{_S["dark"]};padding:11px 14px;font-size:.82rem;font-weight:700">Caractéristique</div>'
    head  += "".join(f'<div style="background:{_S["dark"]};color:{_S["light"]};padding:11px 14px;font-size:.82rem;font-weight:700">{_esc(c.get("label",""))}</div>' for c in cols_cfg)
    rows = ""
    for ri, f in enumerate(filas_cfg):
        bg = "#fff" if ri%2==0 else "#f9f9f7"
        rows += f'<div style="background:#f0f0ea;padding:10px 14px;font-size:.84rem;font-weight:700;color:{_S["dark"]}">{_esc(f.get("label",""))}</div>'
        for i in range(len(cols_cfg)):
            v   = f.get("valores",[""])[i] if i < len(f.get("valores",[])) else ""
            col = "#27ae60" if v.lower() in ("sí","si","yes","oui","✓") else ("#aaa" if v.lower() in ("no","non","✗") else "#333")
            rows += f'<div style="background:{bg};padding:10px 14px;font-size:.84rem;color:{col}">{_esc(v)}</div>'
    return (
        f'<div style="{_S["wrap"]};{_S["border"]};padding:36px">' +
        f'<h2 style="font-size:1rem;font-weight:700;text-transform:uppercase;color:{_S["dark"]};margin-bottom:18px">{titulo}</h2>' +
        f'<div style="display:grid;grid-template-columns:repeat({n},1fr);border:1px solid #e0e0d8;border-radius:6px;overflow:hidden">{head}{rows}</div></div>'
    )

# ── Dispatcher ────────────────────────────────────────────────
GENERADORES = {
    "header":    gen_header,
    "modulo":    gen_modulo,
    "specs":     gen_specs,
    "carrusel":  gen_carrusel,
    "tabs":      gen_tabs,
    "accordion": gen_accordion,
    "grid":      gen_grid,
    "video":     gen_video,
    "compare":   gen_compare,
}

def generar_aplus(fila: dict, bloques: list, preview: bool = False) -> str:
    partes = []
    mod_idx = 0
    for b in bloques:
        tipo = b.get("tipo","")
        cfg  = b.get("cfg", {})
        if tipo == "video":
            partes.append(gen_video_preview(fila, cfg) if preview else gen_video(fila, cfg))
            continue
        fn = GENERADORES.get(tipo)
        if not fn: continue
        if tipo == "modulo":
            partes.append(fn(fila, cfg, mod_idx))
            mod_idx += 1
        else:
            partes.append(fn(fila, cfg))
    return "\n".join(p for p in partes if p)

def generar_zip(df, bloques):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for _, fila in df.iterrows():
            sku  = str(fila.get("SKU","sin_sku")).strip().replace("/","_").replace(" ","_")
            html = sanitize_html(generar_aplus(fila.to_dict(), bloques, preview=False))
            zf.writestr(f"{sku}_aplus.html", html.encode("utf-8"))
    buf.seek(0)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════
# UI — HELPERS
# ══════════════════════════════════════════════════════════════
def _prev(col, muestra, es_imagen=False):
    if not col or col == "(ninguno)":
        st.markdown('<div class="prev-vacio">↳ sin campo</div>', unsafe_allow_html=True); return
    if col not in muestra:
        st.markdown(f'<div class="prev-vacio">⚠️ "{col}" no está en el fichero</div>', unsafe_allow_html=True); return
    val = str(muestra.get(col,"") or "").strip()
    if not val:
        st.markdown('<div class="prev-vacio">↳ vacío en este producto</div>', unsafe_allow_html=True); return
    url = _url(val)
    if es_imagen and url: st.image(url, width=130)
    elif _es_url(val): st.markdown(f'<div class="prev-txt" style="font-size:.7rem;word-break:break-all">↳ {val[:90]}</div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="prev-txt">↳ {val[:100]}</div>', unsafe_allow_html=True)

def _sel(label, key, opc, muestra, es_imagen=False):
    lst = ["(ninguno)"] + opc
    actual = st.session_state.get(key, "(ninguno)")
    if actual not in lst: actual = "(ninguno)"
    v = st.selectbox(label, lst, index=lst.index(actual), key=key, label_visibility="visible")
    _prev(v if v != "(ninguno)" else None, muestra, es_imagen)
    return v if v != "(ninguno)" else ""

def _txt_fijo(label, key, placeholder=""):
    return st.text_input(label, key=key, placeholder=placeholder)


# ══════════════════════════════════════════════════════════════
# UI — CONSTRUCTOR DE BLOQUES
# ══════════════════════════════════════════════════════════════
TIPOS = {
    "header":    "🖼 Hero",
    "modulo":    "📐 Texto·Imagen",
    "specs":     "📋 Specs",
    "grid":      "⬡ Grid iconos",
    "compare":   "📊 Comparativa",
    "carrusel":  "🎠 Carrusel*",
    "tabs":      "📑 Pestañas*",
    "accordion": "📂 Acordeón*",
    "video":     "▶️ Vídeo*",
}
# * = módulos adaptados (sin JS/iframe por restricciones del marketplace)

def render_bloque_ui(idx, bloque, cols_img, cols_txt, muestra):
    tipo = bloque["tipo"]
    cfg  = bloque.setdefault("cfg", {})
    pfx  = f"b{idx}"

    with st.container(border=True):
        hc1, hc2, hc3, hc4 = st.columns([4, 1, 1, 1])
        badge_col = {"header":"#3EB1C8","modulo":"#5bbf3e","carrusel":"#e8a020",
                     "tabs":"#a05ce8","accordion":"#e85c5c","grid":"#3EB1C8",
                     "video":"#e8a020","compare":"#5bbf3e","specs":"#888"}.get(tipo,"#3EB1C8")
        with hc1:
            st.markdown(f'<p style="font-weight:700;color:#FAF9F5"><span style="background:{badge_col};color:#141413;padding:2px 9px;border-radius:20px;font-size:.72rem;margin-right:8px">{tipo}</span>{TIPOS[tipo]}</p>', unsafe_allow_html=True)
        with hc2:
            if idx > 0 and st.button("↑", key=f"{pfx}_up", use_container_width=True):
                return "up"
        with hc3:
            if st.button("↓", key=f"{pfx}_dn", use_container_width=True):
                return "dn"
        with hc4:
            if st.button("🗑", key=f"{pfx}_del", use_container_width=True):
                return "del"

        # ── Config por tipo ──────────────────────────────────
        if tipo == "header":
            c1, c2, c3 = st.columns(3)
            with c1: cfg["img"]    = _sel("Imagen hero", f"{pfx}_img", cols_img, muestra, True)
            with c2: cfg["titulo"] = _sel("Título",      f"{pfx}_tit", cols_txt, muestra)
            with c3: cfg["desc"]   = _sel("Descripción", f"{pfx}_desc",cols_txt, muestra)

        elif tipo == "modulo":
            c1, c2, c3 = st.columns(3)
            with c1: cfg["img"]    = _sel("Imagen",  f"{pfx}_img", cols_img, muestra, True)
            with c2: cfg["titulo"] = _sel("Título",  f"{pfx}_tit", cols_txt, muestra)
            with c3: cfg["desc"]   = _sel("Texto",   f"{pfx}_desc",cols_txt, muestra)

        elif tipo == "specs":
            cfg["titulo_fijo"] = _txt_fijo("Título sección", f"{pfx}_tit_fijo", "Caractéristiques")
            cfg["campos"] = st.multiselect("Campos:", ["(ninguno)"] + cols_txt,
                default=[c for c in cfg.get("campos",[]) if c in cols_txt],
                key=f"{pfx}_campos")

        elif tipo == "video":
            c1, c2 = st.columns(2)
            with c1: cfg["url_campo"] = _sel("Campo URL vídeo", f"{pfx}_url_campo", cols_txt+cols_img, muestra)
            with c2: cfg["url_fija"]  = _txt_fijo("O URL fija (YouTube/Vimeo/mp4)", f"{pfx}_url_fija", "https://youtu.be/...")
            cfg["caption"] = _sel("Texto caption (opcional)", f"{pfx}_cap", cols_txt, muestra)

        elif tipo == "carrusel":
            n = st.number_input("Número de slides", 2, 8, max(2, len(cfg.get("slides",[]))), key=f"{pfx}_n")
            slides = cfg.setdefault("slides", [{}]*int(n))
            while len(slides) < int(n): slides.append({})
            cfg["slides"] = slides[:int(n)]
            for si, slide in enumerate(cfg["slides"]):
                st.markdown(f'<p style="font-size:.8rem;color:#888;margin-top:8px">Slide {si+1}</p>', unsafe_allow_html=True)
                sc1, sc2, sc3 = st.columns(3)
                with sc1: slide["img"]        = _sel("Imagen",  f"{pfx}_s{si}_img", cols_img, muestra, True)
                with sc2: slide["titulo_fijo"]= _txt_fijo("Título fijo", f"{pfx}_s{si}_tit", "")
                with sc3: slide["desc_fija"]  = _txt_fijo("Texto fijo",  f"{pfx}_s{si}_desc","")

        elif tipo == "tabs":
            n = st.number_input("Número de pestañas", 2, 6, max(2, len(cfg.get("tabs",[]))), key=f"{pfx}_n")
            tabs = cfg.setdefault("tabs", [{}]*int(n))
            while len(tabs) < int(n): tabs.append({})
            cfg["tabs"] = tabs[:int(n)]
            for ti, tab in enumerate(cfg["tabs"]):
                st.markdown(f'<p style="font-size:.8rem;color:#888;margin-top:8px">Pestaña {ti+1}</p>', unsafe_allow_html=True)
                tc1, tc2, tc3, tc4 = st.columns(4)
                with tc1: tab["label_fijo"] = _txt_fijo("Etiqueta",f"{pfx}_t{ti}_label","Pestaña")
                with tc2: tab["img"]        = _sel("Imagen", f"{pfx}_t{ti}_img", cols_img, muestra, True)
                with tc3: tab["titulo"]     = _sel("Título", f"{pfx}_t{ti}_tit", cols_txt, muestra)
                with tc4: tab["desc"]       = _sel("Texto",  f"{pfx}_t{ti}_desc",cols_txt, muestra)

        elif tipo == "accordion":
            n = st.number_input("Número de items", 2, 8, max(2, len(cfg.get("items",[]))), key=f"{pfx}_n")
            items = cfg.setdefault("items", [{}]*int(n))
            while len(items) < int(n): items.append({})
            cfg["items"] = items[:int(n)]
            for ai, item in enumerate(cfg["items"]):
                st.markdown(f'<p style="font-size:.8rem;color:#888;margin-top:8px">Item {ai+1}</p>', unsafe_allow_html=True)
                ac1, ac2, ac3, ac4 = st.columns(4)
                with ac1: item["titulo_fijo"] = _txt_fijo("Título fijo", f"{pfx}_a{ai}_tit","")
                with ac2: item["titulo"]      = _sel("O campo título", f"{pfx}_a{ai}_tit_c", cols_txt, muestra)
                with ac3: item["desc"]        = _sel("Texto",  f"{pfx}_a{ai}_desc", cols_txt, muestra)
                with ac4: item["img"]         = _sel("Imagen (opcional)", f"{pfx}_a{ai}_img", cols_img, muestra, True)

        elif tipo == "grid":
            cfg["titulo_fijo"] = _txt_fijo("Título sección", f"{pfx}_gtit","Características destacadas")
            n = st.number_input("Número de items", 2, 8, max(2, len(cfg.get("items",[]))), key=f"{pfx}_n")
            items = cfg.setdefault("items", [{}]*int(n))
            while len(items) < int(n): items.append({})
            cfg["items"] = items[:int(n)]
            for gi, item in enumerate(cfg["items"]):
                st.markdown(f'<p style="font-size:.8rem;color:#888;margin-top:8px">Item {gi+1}</p>', unsafe_allow_html=True)
                gc1, gc2, gc3, gc4 = st.columns(4)
                with gc1: item["icon_fijo"]   = _txt_fijo("Emoji/icono", f"{pfx}_g{gi}_ico","⚡")
                with gc2: item["img"]         = _sel("O imagen",  f"{pfx}_g{gi}_img", cols_img, muestra, True)
                with gc3: item["titulo_fijo"] = _txt_fijo("Título fijo", f"{pfx}_g{gi}_tit","")
                with gc4: item["desc_fija"]   = _txt_fijo("Texto fijo",  f"{pfx}_g{gi}_desc","")

        elif tipo == "compare":
            cfg["titulo_fijo"] = _txt_fijo("Título", f"{pfx}_ctit","Comparaison")
            n_cols = st.number_input("Columnas (modelos)", 2, 5, max(2, len(cfg.get("columnas",[]))), key=f"{pfx}_nc")
            n_rows = st.number_input("Filas (características)", 1, 12, max(3, len(cfg.get("filas",[]))), key=f"{pfx}_nr")
            cols_c = cfg.setdefault("columnas", [{}]*int(n_cols))
            while len(cols_c) < int(n_cols): cols_c.append({})
            cfg["columnas"] = cols_c[:int(n_cols)]
            filas_c = cfg.setdefault("filas", [{}]*int(n_rows))
            while len(filas_c) < int(n_rows): filas_c.append({})
            cfg["filas"] = filas_c[:int(n_rows)]
            st.markdown('<p style="font-size:.8rem;color:#888;margin-top:8px">Cabeceras de columnas</p>', unsafe_allow_html=True)
            ccols = st.columns(int(n_cols))
            for ci, col_c in enumerate(cfg["columnas"]):
                with ccols[ci]: col_c["label"] = _txt_fijo(f"Modelo {ci+1}", f"{pfx}_cc{ci}","Modelo")
            st.markdown('<p style="font-size:.8rem;color:#888;margin-top:6px">Filas</p>', unsafe_allow_html=True)
            for ri, fila_c in enumerate(cfg["filas"]):
                rcols = st.columns([2]+[1]*int(n_cols))
                with rcols[0]: fila_c["label"] = _txt_fijo(f"Característica {ri+1}", f"{pfx}_rf{ri}","")
                vals = fila_c.setdefault("valores", [""]*int(n_cols))
                while len(vals) < int(n_cols): vals.append("")
                fila_c["valores"] = vals[:int(n_cols)]
                for ci in range(int(n_cols)):
                    with rcols[ci+1]: fila_c["valores"][ci] = _txt_fijo("", f"{pfx}_rv{ri}_{ci}", "Sí/No/valor")

    return None


# ══════════════════════════════════════════════════════════════
# UI — PRINCIPAL
# ══════════════════════════════════════════════════════════════
st.markdown(f'<h1 style="font-size:2rem;font-weight:800;color:{CC_F};margin-bottom:.3rem">🌟 A+ Content Generator</h1><p style="color:#888;margin-bottom:1.5rem">Marketplaces · Construye módulos y genera HTML listo para pegar</p>', unsafe_allow_html=True)

# ── Paso 1 ────────────────────────────────────────────────────
st.markdown('<div class="section"><h3>📂 Paso 1 — Cargar datos</h3>', unsafe_allow_html=True)
uploaded = st.file_uploader("Excel o CSV exportado desde Plytix", type=["xlsx","xls","csv"])
if uploaded:
    try:
        df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
        col_sku = next((c for c in df.columns if "sku" in c.lower()), None)
        if col_sku and col_sku != "SKU": df = df.rename(columns={col_sku:"SKU"})
        st.session_state["df_aplus"] = df
        st.session_state.setdefault("bloques_aplus", [])
        st.success(f"✅ {len(df)} productos · {len(df.columns)} campos")
    except Exception as e:
        st.error(f"❌ {e}")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get("df_aplus") is None:
    st.info("Carga un fichero para continuar.")
    st.stop()

df      = st.session_state["df_aplus"]
cols    = [c for c in df.columns if c != "SKU"]
cols_img= [c for c in cols if any(k in c.lower() for k in ["foto","photo","image","img","jpg","png","banner","enhanced","gallery"])]
cols_txt= [c for c in cols if c not in cols_img]
skus    = df["SKU"].astype(str).tolist()

sku_sel = st.selectbox("🔍 Producto de muestra para previews:", skus, key="sku_prev_aplus")
muestra = df[df["SKU"].astype(str)==sku_sel].iloc[0].to_dict()

# ── Paso 2 ────────────────────────────────────────────────────
st.markdown('<div class="section"><h3>🧱 Paso 2 — Construye la estructura</h3>', unsafe_allow_html=True)

# Barra de añadir bloques
cols_bar = st.columns(len(TIPOS))
for i, (tipo, label) in enumerate(TIPOS.items()):
    with cols_bar[i]:
        if st.button(f"＋ {label.split(' ')[0]}", key=f"add_{tipo}", use_container_width=True, help=label):
            st.session_state.setdefault("bloques_aplus", []).append({"tipo": tipo, "cfg": {}})
            st.rerun()

bloques = st.session_state.get("bloques_aplus", [])

st.caption("* Carrusel, Pestañas y Acordeón se renderizan como layout estático (sin JS). Vídeo solo admite archivos .mp4 directos (sin YouTube/Vimeo por restricción de iframe).")
if not bloques:
    st.info("Añade bloques desde los botones de arriba.")
else:
    to_del = to_up = to_dn = None
    for i, bloque in enumerate(bloques):
        result = render_bloque_ui(i, bloque, cols_img, cols_txt, muestra)
        if result == "del": to_del = i
        elif result == "up": to_up = i
        elif result == "dn": to_dn = i

    if to_del is not None:
        bloques.pop(to_del); st.rerun()
    if to_up is not None and to_up > 0:
        bloques[to_up], bloques[to_up-1] = bloques[to_up-1], bloques[to_up]; st.rerun()
    if to_dn is not None and to_dn < len(bloques)-1:
        bloques[to_dn], bloques[to_dn+1] = bloques[to_dn+1], bloques[to_dn]; st.rerun()

st.session_state["bloques_aplus"] = bloques
st.markdown('</div>', unsafe_allow_html=True)

# ── Paso 3 ────────────────────────────────────────────────────
def reconstruir_cfg_desde_session(bloques):
    """Lee los valores actuales de los widgets desde st.session_state y los vuelca en cfg."""
    for i, bloque in enumerate(bloques):
        tipo = bloque["tipo"]
        cfg  = bloque.setdefault("cfg", {})
        pfx  = f"b{i}"

        def ss(key, default=""):
            v = st.session_state.get(key, default)
            return "" if v in ("(ninguno)", None) else str(v)

        if tipo == "header":
            cfg["img"]    = ss(f"{pfx}_img")
            cfg["titulo"] = ss(f"{pfx}_tit")
            cfg["desc"]   = ss(f"{pfx}_desc")
        elif tipo == "modulo":
            cfg["img"]    = ss(f"{pfx}_img")
            cfg["titulo"] = ss(f"{pfx}_tit")
            cfg["desc"]   = ss(f"{pfx}_desc")
        elif tipo == "specs":
            cfg["titulo_fijo"] = ss(f"{pfx}_tit_fijo", "Caractéristiques")
            cfg["campos"]      = st.session_state.get(f"{pfx}_campos", [])
        elif tipo == "video":
            cfg["url_campo"]  = ss(f"{pfx}_url_campo")
            cfg["url_fija"]   = ss(f"{pfx}_url_fija")
            cfg["caption"]    = ss(f"{pfx}_cap")
        elif tipo == "carrusel":
            n = int(st.session_state.get(f"{pfx}_n", 2))
            cfg["slides"] = [
                {"img": ss(f"{pfx}_s{si}_img"),
                 "titulo_fijo": ss(f"{pfx}_s{si}_tit"),
                 "desc_fija":   ss(f"{pfx}_s{si}_desc")}
                for si in range(n)
            ]
        elif tipo == "tabs":
            n = int(st.session_state.get(f"{pfx}_n", 2))
            cfg["tabs"] = [
                {"label_fijo": ss(f"{pfx}_t{ti}_label"),
                 "img":        ss(f"{pfx}_t{ti}_img"),
                 "titulo":     ss(f"{pfx}_t{ti}_tit"),
                 "desc":       ss(f"{pfx}_t{ti}_desc")}
                for ti in range(n)
            ]
        elif tipo == "accordion":
            n = int(st.session_state.get(f"{pfx}_n", 2))
            cfg["items"] = [
                {"titulo_fijo": ss(f"{pfx}_a{ai}_tit"),
                 "titulo":      ss(f"{pfx}_a{ai}_tit_c"),
                 "desc":        ss(f"{pfx}_a{ai}_desc"),
                 "img":         ss(f"{pfx}_a{ai}_img")}
                for ai in range(n)
            ]
        elif tipo == "grid":
            cfg["titulo_fijo"] = ss(f"{pfx}_gtit", "Características destacadas")
            n = int(st.session_state.get(f"{pfx}_n", 2))
            cfg["items"] = [
                {"icon_fijo":   ss(f"{pfx}_g{gi}_ico"),
                 "img":         ss(f"{pfx}_g{gi}_img"),
                 "titulo_fijo": ss(f"{pfx}_g{gi}_tit"),
                 "desc_fija":   ss(f"{pfx}_g{gi}_desc")}
                for gi in range(n)
            ]
        elif tipo == "compare":
            cfg["titulo_fijo"] = ss(f"{pfx}_ctit", "Comparaison")
            n_cols = int(st.session_state.get(f"{pfx}_nc", 2))
            n_rows = int(st.session_state.get(f"{pfx}_nr", 3))
            cfg["columnas"] = [{"label": ss(f"{pfx}_cc{ci}")} for ci in range(n_cols)]
            cfg["filas"]    = [
                {"label":   ss(f"{pfx}_rf{ri}"),
                 "valores": [ss(f"{pfx}_rv{ri}_{ci}") for ci in range(n_cols)]}
                for ri in range(n_rows)
            ]
    return bloques

if bloques:
    st.markdown('<div class="section"><h3>👁 Paso 3 — Preview y descarga</h3>', unsafe_allow_html=True)
    bloques_con_cfg = reconstruir_cfg_desde_session(bloques)
    frag         = sanitize_html(generar_aplus(muestra, bloques_con_cfg, preview=False))
    frag_preview = generar_aplus(muestra, bloques_con_cfg, preview=True)

    with st.expander(f"👁 Preview — {sku_sel}", expanded=True):
        st.components.v1.html(
            f"<!DOCTYPE html><html><head><meta charset='UTF-8'/></head><body style='background:#fff'>{frag_preview}</body></html>",
            height=1000, scrolling=True)

    # Contador de caracteres con semáforo de color (sobre el HTML exportado, sin vídeo)
    n_chars = len(frag)
    pct     = n_chars / LIMIT * 100
    color   = "#27ae60" if pct < 75 else "#e8a020" if pct < 95 else "#e85c5c"
    aviso   = "" if pct < 95 else " ⚠️ Cerca del límite" if pct < 100 else " 🚨 LÍMITE SUPERADO"
    st.markdown(
        f'<p style="font-size:.85rem;margin-bottom:6px"><span style="color:{color};font-weight:700">{n_chars:,} / {LIMIT:,} caracteres ({pct:.0f}%)</span>{aviso}</p>',
        unsafe_allow_html=True)
    if n_chars > LIMIT:
        tipos_usados = [t for t in set(b["tipo"] for b in bloques) if t != "video"]
        st.error(f"🚨 Supera el límite en {n_chars-LIMIT:,} chars. Elimina algún módulo.")
    st.markdown("**📋 Código HTML para Cdiscount** (el vídeo solo aparece en el preview):")
    st.text_area("", value=frag, height=220, key="ta_aplus", label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("⚡ Generar ZIP — todos los productos", key="btn_zip"):
        with st.spinner("Generando..."):
            st.session_state["zip_aplus"]   = generar_zip(df, bloques_con_cfg)
            st.session_state["zip_aplus_n"] = len(df)

    if st.session_state.get("zip_aplus"):
        st.success(f"✅ {st.session_state['zip_aplus_n']} ficheros listos")
        st.download_button("⬇️ DESCARGAR ZIP",
            data=st.session_state["zip_aplus"], file_name="aplus.zip",
            mime="application/zip", key="dl_zip")
    st.markdown('</div>', unsafe_allow_html=True)
