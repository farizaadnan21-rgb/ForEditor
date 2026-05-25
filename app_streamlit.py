import streamlit as st
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import io

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FOR Photo Editor",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* === GLOBAL === */
html, body, .stApp {
    background-color: #0f1117 !important;
    color: #e6edf3 !important;
    font-family: 'Segoe UI', system-ui, sans-serif !important;
}
#MainMenu, footer, header { display: none !important; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
}

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    overflow-x: hidden !important;
}
section[data-testid="stSidebar"] * {
    font-family: 'Segoe UI', system-ui, sans-serif !important;
}

/* === SIDEBAR HEADER === */
.sb-header {
    padding: 14px 14px 10px 14px;
    border-bottom: 1px solid #30363d;
}
.sb-header .title {
    font-size: 15px;
    font-weight: 700;
    color: #e6edf3;
    display: flex;
    align-items: center;
    gap: 6px;
}
.sb-header .subtitle {
    font-size: 9px;
    color: #8b949e;
    margin-top: 2px;
}

/* === CARDS === */
.card {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 4px;
    margin: 6px 10px;
    padding: 10px 10px 8px 10px;
}
.card-title {
    font-size: 10px;
    font-weight: 700;
    color: #e6edf3;
    letter-spacing: 0.3px;
    margin-bottom: 8px;
}
.muted {
    font-size: 9px;
    color: #8b949e;
    margin-bottom: 4px;
    line-height: 1.5;
}

/* === BUTTONS === */
.stButton > button {
    width: 100%;
    background-color: #2d333b !important;
    color: #e6edf3 !important;
    border: 1px solid #444c56 !important;
    border-radius: 3px !important;
    font-size: 11px !important;
    font-family: 'Segoe UI', sans-serif !important;
    padding: 5px 6px !important;
    text-align: left !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    background-color: #30363d !important;
    border-color: #768390 !important;
}

/* Color button variants */
.btn-orange  .stButton > button { background-color: #e67e22 !important; color: #fff !important; text-align: center !important; border-color: #e67e22 !important; }
.btn-red     .stButton > button { background-color: #b91c1c !important; color: #fff !important; text-align: center !important; border-color: #b91c1c !important; }
.btn-blue    .stButton > button { background-color: #1f6feb !important; color: #fff !important; text-align: center !important; border-color: #1f6feb !important; }
.btn-green   .stButton > button { background-color: #238636 !important; color: #fff !important; text-align: center !important; border-color: #238636 !important; }
.btn-active  .stButton > button { background-color: #1f6feb !important; color: #fff !important; text-align: left !important; border-color: #1f6feb !important; }
.btn-ghost   .stButton > button { background-color: #21262d !important; }

/* === BOTTOM DOCK === */
.dock {
    border-top: 1px solid #30363d;
    padding: 6px 10px 4px 10px;
}

/* === RADIO / SLIDER labels === */
[data-testid="stRadio"] label span { font-size: 11px !important; color: #e6edf3 !important; }
[data-testid="stRadio"] > div { gap: 6px !important; }
[data-testid="stSlider"] label { font-size: 10px !important; color: #8b949e !important; }
[data-testid="stSlider"] p { font-size: 10px !important; color: #8b949e !important; }

/* Upload widget compact */
[data-testid="stFileUploader"] {
    padding: 0 !important;
}
[data-testid="stFileUploader"] section {
    padding: 6px !important;
    border-radius: 4px !important;
    background-color: #21262d !important;
    border: 1px dashed #444c56 !important;
}
[data-testid="stFileUploader"] label { font-size: 10px !important; color: #8b949e !important; }

/* Camera input compact */
[data-testid="stCameraInput"] video {
    border-radius: 4px !important;
    border: 1px solid #30363d !important;
    max-height: 120px !important;
    object-fit: cover !important;
}
[data-testid="stCameraInput"] label { font-size: 10px !important; color: #8b949e !important; }

/* Select box */
[data-baseweb="select"] > div {
    background-color: #21262d !important;
    border-color: #444c56 !important;
    color: #e6edf3 !important;
    font-size: 11px !important;
}

/* === MAIN CANVAS AREA === */
[data-testid="stMain"] .main-canvas-wrap {
    background-color: #0f1117;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    min-height: 100vh;
    padding: 24px;
}

/* Status bar */
.status-bar {
    position: fixed;
    bottom: 0; left: 0;
    width: 100%;
    background-color: #0d1117;
    color: #8b949e;
    font-size: 10px;
    font-family: 'Segoe UI', sans-serif;
    padding: 3px 14px;
    border-top: 1px solid #30363d;
    z-index: 9999;
}

/* Before/After modal */
.ba-modal {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 16px;
    margin-top: 12px;
}
.ba-title {
    text-align: center;
    font-size: 12px;
    font-weight: bold;
    color: #e6edf3;
    border-bottom: 1px solid #30363d;
    padding-bottom: 8px;
    margin-bottom: 12px;
}
.ba-label-b { font-size: 10px; font-weight: bold; color: #8b949e; text-align: center; padding-bottom: 4px; }
.ba-label-a { font-size: 10px; font-weight: bold; color: #2ea043; text-align: center; padding-bottom: 4px; }

/* Canvas image border (matching canvas_outer shadow in tkinter) */
.canvas-box {
    border: 2px solid #30363d;
    box-shadow: 0 6px 40px rgba(0,0,0,0.85), 0 0 0 1px #000;
    display: inline-block;
    background: white;
}
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
def pil_to_cv(img): return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
def cv_to_pil(img): return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

def apply_brightness(img, v):  return ImageEnhance.Brightness(img).enhance(float(v))
def apply_contrast(img, v):    return ImageEnhance.Contrast(img).enhance(float(v))
def apply_saturation(img, v):  return ImageEnhance.Color(img).enhance(float(v))

def apply_temperature(img, v):
    val = int(v)
    if val == 0: return img
    cv = pil_to_cv(img); b, g, r = cv2.split(cv)
    r = cv2.add(r, val); b = cv2.subtract(b, val)
    return cv_to_pil(cv2.merge((b, g, r)))

def apply_denoise(img, v):
    k = int(v)
    if k == 0: return img
    if k % 2 == 0: k += 1
    return cv_to_pil(cv2.medianBlur(pil_to_cv(img), k))

def fx_sketch(img):
    cv = pil_to_cv(img)
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    inv = cv2.bitwise_not(gray)
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sk = cv2.divide(gray, 255 - blur, scale=256)
    return cv_to_pil(cv2.cvtColor(sk, cv2.COLOR_GRAY2BGR))

def fx_neon(img):
    cv = pil_to_cv(img)
    edges = cv2.dilate(cv2.Canny(cv, 100, 200), None)
    mask = np.zeros_like(cv); mask[edges > 0] = [255, 0, 255]
    return cv_to_pil(cv2.add((cv * 0.3).astype(np.uint8), mask))

def fx_sepia(img):
    cv = pil_to_cv(img)
    k = np.array([[0.272,0.534,0.131],[0.349,0.686,0.168],[0.393,0.769,0.189]])
    s = cv2.transform(cv, k)
    n = np.random.normal(0, 15, s.shape).astype(np.uint8)
    return cv_to_pil(cv2.add(s, n))

# ── Session State ──────────────────────────────────────────────────────────────
for key, val in dict(
    brightness=1.0, contrast=1.0, saturation=1.0, temp=0, denoise=0,
    effect="Normal", orig_image=None, show_ba=False,
    status="Siap — Load gambar atau ambil foto kamera",
    input_mode="📂 Upload File"
).items():
    if key not in st.session_state: st.session_state[key] = val

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Header
    st.markdown("""
    <div class="sb-header">
        <div class="title">✏️ FOR Editor</div>
        <div class="subtitle">by Fariza · Ocid · Rasya</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Card: Drawing Tools ──────────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">🛠 Drawing Tools</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="btn-orange">', unsafe_allow_html=True)
        st.button("🎨 Color", key="btn_color")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.button("🧹 Clear", key="btn_clear")

    st.markdown('<div class="btn-red">', unsafe_allow_html=True)
    st.button("🧽 Eraser", key="btn_eraser")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="muted" style="margin-top:8px">Brush Shape</div>', unsafe_allow_html=True)
    st.radio("shape", ["● Round", "◆ Flat", "✦ Spray"], horizontal=True, key="brush_shape", label_visibility="collapsed")

    st.markdown('<div class="muted" style="margin-top:4px">Brush Size</div>', unsafe_allow_html=True)
    st.slider("Brush Size", 1, 50, 5, key="brush_size", label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)  # end card

    # ── Card: Image Adjustments ──────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">🎛 Image Adjustments</div>', unsafe_allow_html=True)

    st.slider("☀️ Brightness",      0.0,  2.0, key="brightness", step=0.05)
    st.slider("🌓 Contrast",         0.0,  2.0, key="contrast",   step=0.05)
    st.slider("🎨 Saturation",       0.0,  3.0, key="saturation", step=0.05)
    st.slider("🌡️ Temperature",      -100, 100, key="temp",       step=5)
    st.slider("✨ Denoise",          0,    20,  key="denoise",    step=2)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Card: Special Effects ────────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">✨ Special Effects</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Click again to toggle off</div>', unsafe_allow_html=True)

    cur = st.session_state.effect

    sk_c = "btn-active" if cur == "sketch" else ""
    ne_c = "btn-active" if cur == "neon"   else ""
    se_c = "btn-active" if cur == "sepia"  else ""

    st.markdown(f'<div class="{sk_c}">', unsafe_allow_html=True)
    if st.button("✏️  Pencil Sketch",  key="fx_sketch"):
        st.session_state.effect = "Normal" if cur == "sketch" else "sketch"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="{ne_c}">', unsafe_allow_html=True)
    if st.button("🌆  Cyberpunk Neon", key="fx_neon"):
        st.session_state.effect = "Normal" if cur == "neon"   else "neon";   st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="{se_c}">', unsafe_allow_html=True)
    if st.button("📜  Sepia Vintage",  key="fx_sepia"):
        st.session_state.effect = "Normal" if cur == "sepia"  else "sepia";  st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Card: Before / After ─────────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">🔍 Before / After</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Load an image first, then apply effects and compare.</div>', unsafe_allow_html=True)

    st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
    if st.button("⚡  Compare Before / After", key="btn_ba"):
        st.session_state.show_ba = not st.session_state.show_ba
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Bottom File Dock ─────────────────────────────────────────────────────
    st.markdown('<div class="dock">', unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        load_clicked = st.button("📂 Load",  key="d_load")
    with d2:
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        save_clicked = st.button("💾 Save",  key="d_save")
        st.markdown('</div>', unsafe_allow_html=True)
    with d3:
        st.button("↩ Undo", key="d_undo")
    with d4:
        st.button("↪ Redo", key="d_redo")

    st.markdown('<div class="btn-blue" style="margin-top:4px">', unsafe_allow_html=True)
    cam_clicked = st.button("📷  Camera", key="d_cam")
    st.markdown('</div>', unsafe_allow_html=True)

    # Input mode selection (compact, toggled by Load/Camera buttons)
    if cam_clicked:
        st.session_state.input_mode = "📷 Camera"
        st.rerun()
    if load_clicked:
        st.session_state.input_mode = "📂 Upload File"
        st.rerun()

    # Show only the relevant input widget
    if st.session_state.input_mode == "📂 Upload File":
        uploaded = st.file_uploader("", type=["png","jpg","jpeg","webp","bmp"], label_visibility="collapsed")
        cam_img = None
    else:
        uploaded = None
        cam_img = st.camera_input("", label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)  # end dock

# ── Load Base Image ────────────────────────────────────────────────────────────
base = None
if uploaded is not None:
    base = Image.open(uploaded).convert("RGB")
    st.session_state.orig_image = base.copy()
    st.session_state.status = f"Loaded: {uploaded.name}"
elif cam_img is not None:
    base = Image.open(cam_img).convert("RGB")
    st.session_state.orig_image = base.copy()
    st.session_state.status = "Loaded from Camera"
elif st.session_state.orig_image is not None:
    base = st.session_state.orig_image.copy()

is_blank = (base is None)
if is_blank:
    base = Image.new("RGB", (860, 650), "white")

if st.session_state.get("btn_clear"):
    base = Image.new("RGB", (860, 650), "white")
    st.session_state.orig_image = None
    st.session_state.effect = "Normal"
    st.session_state.status = "Canvas cleared"

# ── Apply Filters ──────────────────────────────────────────────────────────────
out = base.copy()
dv = st.session_state.denoise
tv = st.session_state.temp
bv = st.session_state.brightness
cv = st.session_state.contrast
sv = st.session_state.saturation
fx = st.session_state.effect

if dv > 0:    out = apply_denoise(out, dv)
if tv != 0:   out = apply_temperature(out, tv)
if bv != 1.0: out = apply_brightness(out, bv)
if cv != 1.0: out = apply_contrast(out, cv)
if sv != 1.0: out = apply_saturation(out, sv)
if fx == "sketch": out = fx_sketch(out); st.session_state.status = "Effect active: sketch"
elif fx == "neon":  out = fx_neon(out);   st.session_state.status = "Effect active: neon"
elif fx == "sepia": out = fx_sepia(out);  st.session_state.status = "Effect active: sepia"

# ── MAIN AREA: Canvas ──────────────────────────────────────────────────────────
st.markdown('<div style="display:flex;justify-content:center;align-items:flex-start;'
            'background:#0f1117;padding:28px;min-height:calc(100vh - 30px);">', unsafe_allow_html=True)
st.markdown('<div class="canvas-box">', unsafe_allow_html=True)
st.image(out, use_column_width=False, width=860)
st.markdown('</div></div>', unsafe_allow_html=True)

# ── Before / After Comparison ──────────────────────────────────────────────────
if st.session_state.show_ba and not is_blank and st.session_state.orig_image is not None:
    st.markdown('<div class="ba-modal">', unsafe_allow_html=True)
    st.markdown('<div class="ba-title">Before / After Comparison</div>', unsafe_allow_html=True)

    cb, ca = st.columns(2)
    with cb:
        st.markdown('<div class="ba-label-b">BEFORE</div>', unsafe_allow_html=True)
        st.image(st.session_state.orig_image.resize((480, 380)), use_column_width=True)
    with ca:
        st.markdown('<div class="ba-label-a">AFTER</div>', unsafe_allow_html=True)
        st.image(out.resize((480, 380)), use_column_width=True)

    _, cc, _ = st.columns([2, 1, 2])
    with cc:
        if st.button("✕  Close", key="close_ba"):
            st.session_state.show_ba = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Download (Save) ────────────────────────────────────────────────────────────
if save_clicked:
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    st.download_button(
        "⬇️ Download Gambar (PNG)", buf.getvalue(),
        file_name="foreditor_export.png", mime="image/png"
    )

# ── Status Bar ─────────────────────────────────────────────────────────────────
st.markdown(f'<div class="status-bar">{st.session_state.status}</div>', unsafe_allow_html=True)
