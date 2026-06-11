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
# ── CSS mínimo por tipo de módulo (se incluye solo si el módulo está en uso) ──
LIMIT = 5000

CSS_BASE = "*{box-sizing:border-box;margin:0;padding:0}body{font-family:Arial,sans-serif;color:#111;background:#fff;max-width:970px;margin:auto}img{max-width:100%;display:block}"

CSS_POR_TIPO = {
    "header":    ".ap-header{display:flex;flex-direction:column}.ap-header-img{width:100%;overflow:hidden;max-height:480px}.ap-header-img img{width:100%;height:100%;object-fit:cover}.ap-header-text{background:#141413;color:#FAF9F5;padding:32px 36px}.ap-header-text h1{font-size:1.5rem;font-weight:700;line-height:1.3;margin-bottom:12px;color:#FAF9F5}.ap-header-text p{font-size:.95rem;line-height:1.7;color:#c8c8c0}",
    "modulo":    ".ap-module{display:flex;align-items:stretch;border-top:3px solid #3EB1C8;height:340px}.ap-module-rev{flex-direction:row-reverse}.ap-module-img{width:45%;overflow:hidden;flex-shrink:0}.ap-module-img img{width:100%;height:100%;object-fit:cover}.ap-module-text{flex:1;padding:32px 36px;display:flex;flex-direction:column;justify-content:center}.ap-module-text h2{font-size:1.1rem;font-weight:700;color:#141413;margin-bottom:12px}.ap-module-text p{font-size:.92rem;line-height:1.75;color:#444}.ap-accent{width:36px;height:3px;background:#3EB1C8;margin-bottom:14px}",
    "carrusel":  ".ap-carousel{position:relative;border-top:3px solid #3EB1C8;overflow:hidden}.ap-carousel-track{display:flex;transition:transform .35s ease}.ap-carousel-slide{min-width:100%;position:relative}.ap-carousel-slide img{width:100%;height:420px;object-fit:cover}.ap-carousel-caption{position:absolute;bottom:0;left:0;right:0;background:rgba(20,20,19,.72);color:#FAF9F5;padding:18px 28px}.ap-carousel-caption h3{font-size:1rem;font-weight:700;margin-bottom:6px}.ap-carousel-caption p{font-size:.85rem;color:#ddd}.ap-carousel-btn{position:absolute;top:50%;transform:translateY(-50%);background:rgba(62,177,200,.85);border:none;color:#fff;width:44px;height:44px;border-radius:50%;cursor:pointer;z-index:10}.ap-carousel-prev{left:14px}.ap-carousel-next{right:14px}.ap-carousel-dots{display:flex;justify-content:center;gap:8px;padding:14px 0}.ap-carousel-dot{width:8px;height:8px;border-radius:50%;background:#ccc;cursor:pointer;border:none}.ap-carousel-dot.active{background:#3EB1C8}",
    "tabs":      ".ap-tabs{border-top:3px solid #3EB1C8}.ap-tabs-nav{display:flex;background:#141413;overflow-x:auto}.ap-tabs-nav-btn{flex:1;padding:16px 20px;background:none;border:none;color:#c8c8c0;font-size:.88rem;font-weight:600;cursor:pointer;border-bottom:3px solid transparent}.ap-tabs-nav-btn.active{color:#FAF9F5;border-bottom-color:#3EB1C8}.ap-tab-panel{display:none;flex-direction:row;min-height:300px}.ap-tab-panel.active{display:flex}.ap-tab-panel-img{width:45%;overflow:hidden;flex-shrink:0}.ap-tab-panel-img img{width:100%;height:100%;object-fit:cover}.ap-tab-panel-text{flex:1;padding:32px 36px;display:flex;flex-direction:column;justify-content:center}.ap-tab-panel-text h3{font-size:1.1rem;font-weight:700;margin-bottom:12px;color:#141413}.ap-tab-panel-text p{font-size:.92rem;line-height:1.75;color:#444}",
    "accordion": ".ap-accordion{border-top:3px solid #3EB1C8}.ap-accordion-item{border-bottom:1px solid #e0e0d8}.ap-accordion-btn{width:100%;background:#fff;border:none;padding:20px 24px;text-align:left;font-size:.95rem;font-weight:700;color:#141413;cursor:pointer;display:flex;justify-content:space-between;align-items:center}.ap-accordion-icon{font-size:1.2rem;color:#3EB1C8;transition:transform .25s}.ap-accordion-panel{max-height:0;overflow:hidden;transition:max-height .3s ease}.ap-accordion-panel.open{max-height:600px}.ap-accordion-body{padding:0 24px 20px;font-size:.9rem;line-height:1.75;color:#444}",
    "grid":      ".ap-grid{border-top:3px solid #3EB1C8;padding:40px 36px;background:#FAF9F5}.ap-grid h2{font-size:1rem;font-weight:700;text-transform:uppercase;color:#141413;margin-bottom:28px;text-align:center}.ap-grid-items{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:24px}.ap-grid-item{text-align:center;padding:20px 12px;background:#fff;border-radius:10px;border:1px solid #e8e8e0}.ap-grid-icon{font-size:2rem;margin-bottom:12px}.ap-grid-item h4{font-size:.82rem;font-weight:700;color:#141413;margin-bottom:6px}.ap-grid-item p{font-size:.78rem;color:#666;line-height:1.5}",
    "video":     ".ap-video{border-top:3px solid #3EB1C8;background:#141413}.ap-video-embed{position:relative;padding-bottom:56.25%;height:0;overflow:hidden}.ap-video-embed iframe,.ap-video-embed video{position:absolute;top:0;left:0;width:100%;height:100%;border:none;object-fit:cover}.ap-video-caption{padding:20px 36px;background:#1a1a18}.ap-video-caption p{font-size:.9rem;color:#c8c8c0}",
    "compare":   ".ap-compare{border-top:3px solid #3EB1C8;padding:40px 36px;overflow-x:auto}.ap-compare h2{font-size:1rem;font-weight:700;text-transform:uppercase;color:#141413;margin-bottom:24px}.ap-compare table{width:100%;border-collapse:collapse;min-width:500px}.ap-compare th{background:#141413;color:#FAF9F5;padding:14px 18px;text-align:left;font-size:.85rem;font-weight:700}.ap-compare th:first-child{background:#3EB1C8;color:#141413}.ap-compare td{padding:12px 18px;font-size:.85rem;color:#333;border-bottom:1px solid #eee}.ap-compare tr:nth-child(even) td{background:#f9f9f7}.ap-compare td:first-child{font-weight:700;color:#141413}",
    "specs":     ".ap-specs{background:#FAF9F5;padding:40px 36px;border-top:3px solid #3EB1C8}.ap-specs h2{font-size:1rem;font-weight:700;text-transform:uppercase;color:#141413;margin-bottom:24px}.ap-specs-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}.ap-spec-item{padding:14px 16px;border-bottom:1px solid #e0e0d8;display:flex;align-items:baseline;gap:10px}.ap-spec-item:nth-child(odd){background:#fff}.ap-spec-bullet{width:6px;height:6px;border-radius:50%;background:#3EB1C8;flex-shrink:0;margin-top:6px}.ap-spec-text{font-size:.88rem;color:#333;line-height:1.5}",
}

JS_POR_TIPO = {
    "carrusel":  "function apC(id){var t=document.querySelector('#'+id+' .ap-carousel-track'),s=t.querySelectorAll('.ap-carousel-slide'),d=document.querySelectorAll('#'+id+' .ap-carousel-dot'),c=0;function g(n){c=(n+s.length)%s.length;t.style.transform='translateX(-'+c*100+'%)';d.forEach(function(x,i){x.classList.toggle('active',i===c)})}document.querySelector('#'+id+' .ap-carousel-prev').onclick=function(){g(c-1)};document.querySelector('#'+id+' .ap-carousel-next').onclick=function(){g(c+1)};d.forEach(function(x,i){x.onclick=function(){g(i)}})}",
    "tabs":      "function apT(id){var b=document.querySelectorAll('#'+id+' .ap-tabs-nav-btn'),p=document.querySelectorAll('#'+id+' .ap-tab-panel');b.forEach(function(btn,i){btn.onclick=function(){b.forEach(function(x){x.classList.remove('active')});p.forEach(function(x){x.classList.remove('active')});btn.classList.add('active');p[i].classList.add('active')}})}",
    "accordion": "function apA(id){document.querySelectorAll('#'+id+' .ap-accordion-btn').forEach(function(btn){btn.onclick=function(){var p=btn.nextElementSibling,ic=btn.querySelector('.ap-accordion-icon'),o=p.classList.toggle('open');ic.style.transform=o?'rotate(45deg)':''}})}",
}

JS_INIT_POR_TIPO = {
    "carrusel":  "document.querySelectorAll('.ap-carousel').forEach(function(el){apC(el.id)});",
    "tabs":      "document.querySelectorAll('.ap-tabs').forEach(function(el){apT(el.id)});",
    "accordion": "document.querySelectorAll('.ap-accordion').forEach(function(el){apA(el.id)});",
}

def css_js_para_bloques(bloques: list) -> str:
    """Genera solo el CSS y JS de los tipos de módulo presentes en el layout."""
    tipos_usados = set(b.get("tipo","") for b in bloques)
    css = "<style>" + CSS_BASE
    for tipo in CSS_POR_TIPO:
        if tipo in tipos_usados:
            css += CSS_POR_TIPO[tipo]
    css += "</style>"
    js_fns   = "".join(JS_POR_TIPO[t]   for t in JS_POR_TIPO if t in tipos_usados)
    js_inits = "".join(JS_INIT_POR_TIPO[t] for t in JS_INIT_POR_TIPO if t in tipos_usados)
    if js_inits:
        js_fns += f"window.addEventListener('load',function(){{{js_inits}}});"
    return css + (f"<script>{js_fns}</script>" if js_fns else "")

def calcular_chars(fila, bloques):
    """Calcula el tamaño real del HTML generado para un producto."""
    html = generar_aplus(fila, bloques)
    return len(html)

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

def _video_embed(url):
    """Genera el embed correcto según el tipo de URL."""
    if not url: return ""
    if "youtube.com/watch" in url or "youtu.be/" in url:
        vid = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1].split("?")[0]
        return f'<iframe src="https://www.youtube.com/embed/{vid}" allowfullscreen></iframe>'
    if "vimeo.com" in url:
        vid = url.rstrip("/").split("/")[-1]
        return f'<iframe src="https://player.vimeo.com/video/{vid}" allowfullscreen></iframe>'
    if url.endswith((".mp4",".webm",".ogg")):
        return f'<video src="{url}" controls playsinline></video>'
    return f'<iframe src="{url}" allowfullscreen></iframe>'

def _val(fila, campo): return str(fila.get(campo, "") or "").strip()
def _img_tag(fila, campo, alt=""):
    u = _url(_val(fila, campo))
    return f'<img src="{u}" alt="{_esc(alt)}" loading="lazy"/>' if u else ""

# ══════════════════════════════════════════════════════════════
# GENERADORES POR TIPO DE MÓDULO
# ══════════════════════════════════════════════════════════════
def gen_header(fila, cfg):
    img = _img_tag(fila, cfg.get("img",""))
    nom = _esc(_val(fila, cfg.get("titulo","")))
    desc= _esc(_val(fila, cfg.get("desc","")))
    return f'<section class="ap-header"><div class="ap-header-img">{img}</div><div class="ap-header-text"><h1>{nom}</h1><p>{desc}</p></div></section>'

def gen_modulo(fila, cfg, idx):
    img  = _img_tag(fila, cfg.get("img",""))
    tit  = _esc(_val(fila, cfg.get("titulo","")))
    txt  = _esc(_val(fila, cfg.get("desc","")))
    rev  = "ap-module-rev" if idx % 2 == 1 else ""
    return f'<section class="ap-module {rev}"><div class="ap-module-img">{img}</div><div class="ap-module-text"><div class="ap-accent"></div><h2>{tit}</h2><p>{txt}</p></div></section>'

def gen_specs(fila, cfg):
    items = ""
    for campo in cfg.get("campos", []):
        v = _val(fila, campo)
        if v and not _es_url(v):
            items += f'<div class="ap-spec-item"><div class="ap-spec-bullet"></div><span class="ap-spec-text">{_esc(v)}</span></div>'
    titulo = _esc(cfg.get("titulo_fijo", "Caractéristiques"))
    return f'<section class="ap-specs"><h2>{titulo}</h2><div class="ap-specs-grid">{items}</div></section>' if items else ""

def gen_carrusel(fila, cfg):
    slides_cfg = cfg.get("slides", [])
    if not slides_cfg: return ""
    uid = _uid()
    slides_html = dots_html = ""
    for i, s in enumerate(slides_cfg):
        img = _img_tag(fila, s.get("img",""))
        tit = _esc(_val(fila, s.get("titulo","")) or s.get("titulo_fijo",""))
        txt = _esc(_val(fila, s.get("desc","")) or s.get("desc_fija",""))
        cap = f'<div class="ap-carousel-caption"><h3>{tit}</h3><p>{txt}</p></div>' if tit or txt else ""
        slides_html += f'<div class="ap-carousel-slide">{img}{cap}</div>'
        dots_html   += f'<button class="ap-carousel-dot {"active" if i==0 else ""}"></button>'
    return f'''<div class="ap-carousel" id="{uid}">
  <div class="ap-carousel-track">{slides_html}</div>
  <button class="ap-carousel-btn ap-carousel-prev">&#8592;</button>
  <button class="ap-carousel-btn ap-carousel-next">&#8594;</button>
  <div class="ap-carousel-dots">{dots_html}</div>
</div>'''

def gen_tabs(fila, cfg):
    tabs_cfg = cfg.get("tabs", [])
    if not tabs_cfg: return ""
    uid = _uid()
    nav = content = ""
    for i, t in enumerate(tabs_cfg):
        label = _esc(_val(fila, t.get("label","")) or t.get("label_fijo", f"Tab {i+1}"))
        img   = _img_tag(fila, t.get("img",""))
        tit   = _esc(_val(fila, t.get("titulo","")) or t.get("titulo_fijo",""))
        txt   = _esc(_val(fila, t.get("desc","")) or t.get("desc_fija",""))
        nav     += f'<button class="ap-tabs-nav-btn {"active" if i==0 else ""}">{label}</button>'
        content += f'<div class="ap-tab-panel {"active" if i==0 else ""}"><div class="ap-tab-panel-img">{img}</div><div class="ap-tab-panel-text"><h3>{tit}</h3><p>{txt}</p></div></div>'
    return f'<div class="ap-tabs" id="{uid}"><div class="ap-tabs-nav">{nav}</div><div class="ap-tabs-content">{content}</div></div>'

def gen_accordion(fila, cfg):
    items_cfg = cfg.get("items", [])
    if not items_cfg: return ""
    uid = _uid()
    items_html = ""
    for item in items_cfg:
        tit = _esc(_val(fila, item.get("titulo","")) or item.get("titulo_fijo",""))
        txt = _esc(_val(fila, item.get("desc","")) or item.get("desc_fija",""))
        img = _img_tag(fila, item.get("img",""))
        img_html = f'<div>{img}</div>' if img else ""
        items_html += f'''<div class="ap-accordion-item">
  <button class="ap-accordion-btn">{tit}<span class="ap-accordion-icon">+</span></button>
  <div class="ap-accordion-panel"><div class="ap-accordion-body">{img_html}<p>{txt}</p></div></div>
</div>'''
    return f'<div class="ap-accordion" id="{uid}">{items_html}</div>'

def gen_grid(fila, cfg):
    items_cfg = cfg.get("items", [])
    if not items_cfg: return ""
    titulo = _esc(cfg.get("titulo_fijo","Características destacadas"))
    items_html = ""
    for item in items_cfg:
        img  = _img_tag(fila, item.get("img",""))
        icon = item.get("icon_fijo","")
        tit  = _esc(_val(fila, item.get("titulo","")) or item.get("titulo_fijo",""))
        txt  = _esc(_val(fila, item.get("desc","")) or item.get("desc_fija",""))
        icono_html = img or (f'<div class="ap-grid-icon">{icon}</div>' if icon else "")
        items_html += f'<div class="ap-grid-item">{icono_html}<h4>{tit}</h4><p>{txt}</p></div>'
    return f'<section class="ap-grid"><h2>{titulo}</h2><div class="ap-grid-items">{items_html}</div></section>'

def gen_video(fila, cfg):
    url_campo = _val(fila, cfg.get("url_campo",""))
    url_fija  = cfg.get("url_fija","")
    url = url_fija or url_campo
    if not url: return ""
    embed = _video_embed(url)
    caption = _esc(_val(fila, cfg.get("caption","")) or cfg.get("caption_fija",""))
    cap_html = f'<div class="ap-video-caption"><p>{caption}</p></div>' if caption else ""
    return f'<section class="ap-video"><div class="ap-video-embed">{embed}</div>{cap_html}</section>'

def gen_compare(fila, cfg):
    cols_cfg = cfg.get("columnas", [])  # [{label, campos:[campo1,campo2,...]}]
    filas_cfg = cfg.get("filas", [])    # [{label, valores:[val1,val2,...]}]
    if not cols_cfg and not filas_cfg: return ""
    titulo = _esc(cfg.get("titulo_fijo","Comparaison des modèles"))
    # Cabecera
    ths = "<th>Característica</th>" + "".join(f'<th>{_esc(c.get("label",""))}</th>' for c in cols_cfg)
    # Filas de datos
    rows = ""
    for f in filas_cfg:
        tds = f'<td>{_esc(f.get("label",""))}</td>'
        for i, c in enumerate(cols_cfg):
            val_campo = _val(fila, c.get("campos",[])[i]) if i < len(c.get("campos",[])) else ""
            val_fijo  = f.get("valores",[""])[i] if i < len(f.get("valores",[])) else ""
            v = val_fijo or val_campo
            cls = "yes" if v.lower() in ("sí","si","yes","oui","✓","✔") else ("no" if v.lower() in ("no","non","✗","✘") else "")
            tds += f'<td class="{cls}">{_esc(v)}</td>'
        rows += f'<tr>{tds}</tr>'
    return f'<section class="ap-compare"><h2>{titulo}</h2><table><thead><tr>{ths}</tr></thead><tbody>{rows}</tbody></table></section>'

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

def generar_aplus(fila: dict, bloques: list) -> str:
    partes = [css_js_para_bloques(bloques)]
    mod_idx = 0
    for b in bloques:
        tipo = b.get("tipo","")
        cfg  = b.get("cfg", {})
        fn   = GENERADORES.get(tipo)
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
            html = generar_aplus(fila.to_dict(), bloques)
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
    "header":    "🖼 Hero (imagen + título + desc)",
    "modulo":    "📐 Texto · Imagen (alternado)",
    "carrusel":  "🎠 Carrusel de imágenes",
    "tabs":      "📑 Pestañas",
    "accordion": "📂 Acordeón",
    "grid":      "⬡ Grid de iconos",
    "video":     "▶️ Vídeo",
    "compare":   "📊 Comparativa",
    "specs":     "📋 Especificaciones",
}

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
if bloques:
    st.markdown('<div class="section"><h3>👁 Paso 3 — Preview y descarga</h3>', unsafe_allow_html=True)
    frag = generar_aplus(muestra, bloques)

    with st.expander(f"👁 Preview — {sku_sel}", expanded=True):
        st.components.v1.html(
            f"<!DOCTYPE html><html><head><meta charset='UTF-8'/></head><body style='background:#fff'>{frag}</body></html>",
            height=1000, scrolling=True)

    # Contador de caracteres con semáforo de color
    n_chars = len(frag)
    pct     = n_chars / LIMIT * 100
    color   = "#27ae60" if pct < 75 else "#e8a020" if pct < 95 else "#e85c5c"
    aviso   = "" if pct < 95 else " ⚠️ Cerca del límite" if pct < 100 else " 🚨 LÍMITE SUPERADO"
    st.markdown(
        f'<p style="font-size:.85rem;margin-bottom:6px"><span style="color:{color};font-weight:700">{n_chars:,} / {LIMIT:,} caracteres ({pct:.0f}%)</span>{aviso}</p>',
        unsafe_allow_html=True)
    if n_chars > LIMIT:
        tipos_con_peso = sorted(
            [(t, len(CSS_POR_TIPO.get(t,"")) + len(JS_POR_TIPO.get(t,"")))
             for t in set(b["tipo"] for b in bloques)],
            key=lambda x: -x[1])
        st.error(
            f"🚨 El HTML supera el límite de {LIMIT:,} caracteres en {n_chars-LIMIT:,} chars. "
            f"Módulos más pesados: " +
            ", ".join(f"**{t}** ({w} chars CSS/JS)" for t,w in tipos_con_peso[:3]))
    st.markdown("**📋 Código HTML:**")
    st.text_area("", value=frag, height=220, key="ta_aplus", label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("⚡ Generar ZIP — todos los productos", key="btn_zip"):
        with st.spinner("Generando..."):
            st.session_state["zip_aplus"]   = generar_zip(df, bloques)
            st.session_state["zip_aplus_n"] = len(df)

    if st.session_state.get("zip_aplus"):
        st.success(f"✅ {st.session_state['zip_aplus_n']} ficheros listos")
        st.download_button("⬇️ DESCARGAR ZIP",
            data=st.session_state["zip_aplus"], file_name="aplus.zip",
            mime="application/zip", key="dl_zip")
    st.markdown('</div>', unsafe_allow_html=True)
