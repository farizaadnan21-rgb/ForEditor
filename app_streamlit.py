import streamlit as st
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import io

st.set_page_config(
    page_title="FOR Photo Editor",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── EXACT MATCH CSS to original Tkinter theme ─────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;700&display=swap');

/* ── Global Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.stApp {
    background-color: #0f1117 !important;
    font-family: 'Segoe UI', sans-serif !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Sidebar: exactly bg_sidebar #161b22, width 280px ── */
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    min-width: 260px !important;
    max-width: 260px !important;
    border-right: 1px solid #30363d !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* ── Hide sidebar collapse button ── */
[data-testid="collapsedControl"] { display: none !important; }

/* ── Typography in sidebar ── */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: #e6edf3 !important;
    font-family: 'Segoe UI', sans-serif !important;
}

/* ── Sliders ── */
[data-testid="stSlider"] .stSlider { padding: 2px 0 !important; }
[data-testid="stSlider"] label { font-size: 11px !important; color: #8b949e !important; }

/* ── Buttons generic ── */
.stButton > button {
    background-color: #2d333b !important;
    color: #e6edf3 !important;
    border: 1px solid #444c56 !important;
    border-radius: 3px !important;
    font-family: 'Segoe UI', sans-serif !important;
    font-size: 12px !important;
    padding: 5px 10px !important;
    cursor: pointer !important;
    width: 100% !important;
    text-align: left !important;
    transition: background 0.15s !important;
}
.stButton > button:hover {
    background-color: #30363d !important;
    border-color: #8b949e !important;
}

/* ── Radio buttons ── */
[data-testid="stRadio"] label { font-size: 11px !important; color: #e6edf3 !important; }
[data-testid="stRadio"] { flex-direction: row !important; }

/* ── Selectbox ── */
[data-testid="stSelectbox"] select,
[data-baseweb="select"] {
    background-color: #21262d !important;
    color: #e6edf3 !important;
    border-color: #444c56 !important;
    font-size: 12px !important;
}

/* ── Main area background ── */
[data-testid="stMain"] {
    background-color: #0f1117 !important;
    padding: 0 !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background-color: #238636 !important;
    color: white !important;
    border: none !important;
    border-radius: 3px !important;
    font-size: 12px !important;
    width: 100% !important;
}

/* ── Card Style (matches _make_card) ── */
.for-card {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 3px;
    padding: 10px 12px;
    margin: 0 10px 8px 10px;
}
.for-card-title {
    font-size: 11px;
    font-weight: bold;
    color: #e6edf3;
    margin-bottom: 8px;
    border-bottom: 1px solid #30363d;
    padding-bottom: 5px;
}
.for-header {
    padding: 14px 14px 8px 14px;
    border-bottom: 1px solid #30363d;
    margin-bottom: 8px;
}
.for-header h2 {
    font-size: 16px !important;
    font-weight: bold !important;
    color: #e6edf3 !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}
.for-header p {
    font-size: 10px !important;
    color: #8b949e !important;
    margin: 2px 0 0 0 !important;
}
.for-muted {
    font-size: 10px !important;
    color: #8b949e !important;
    margin-bottom: 6px !important;
    line-height: 1.4 !important;
}

/* ── Status Bar fixed bottom ── */
.status-bar {
    position: fixed;
    bottom: 0; left: 0;
    width: 100%;
    background-color: #0d1117;
    color: #8b949e;
    font-size: 11px;
    font-family: 'Segoe UI', sans-serif;
    padding: 4px 14px;
    border-top: 1px solid #30363d;
    z-index: 9999;
}

/* ── Color button (orange like original) ── */
.btn-color > button { background-color: #e67e22 !important; color: white !important; text-align: center !important; }
.btn-eraser > button { background-color: #b91c1c !important; color: white !important; text-align: center !important; }
.btn-blue > button { background-color: #1f6feb !important; color: white !important; text-align: center !important; }
.btn-green > button { background-color: #238636 !important; color: white !important; text-align: center !important; }
.btn-active > button { background-color: #1f6feb !important; color: white !important; }

/* Canvas wrapper */
.canvas-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #0f1117;
    min-height: calc(100vh - 30px);
    padding: 20px;
}
.canvas-border {
    border: 2px solid #30363d;
    box-shadow: 0 4px 30px rgba(0,0,0,0.8), inset 0 0 0 1px #000;
    background: white;
    display: inline-block;
}

/* Before/After popup style */
.ba-popup {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 20px;
    margin-top: 10px;
}
.ba-label-before { font-size: 11px; font-weight: bold; color: #8b949e; text-align: center; margin-bottom: 6px; }
.ba-label-after  { font-size: 11px; font-weight: bold; color: #2ea043; text-align: center; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# ── Helper Funcs ───────────────────────────────────────────────────────────────
def pil_to_cv(img): return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
def cv_to_pil(img): return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

def adjust_brightness(img, v): return ImageEnhance.Brightness(img).enhance(float(v))
def adjust_contrast(img, v):   return ImageEnhance.Contrast(img).enhance(float(v))
def adjust_saturation(img, v): return ImageEnhance.Color(img).enhance(float(v))

def adjust_temperature(img, v):
    val = int(v)
    if val == 0: return img
    cv = pil_to_cv(img)
    b, g, r = cv2.split(cv)
    r = cv2.add(r, val); b = cv2.subtract(b, val)
    return cv_to_pil(cv2.merge((b, g, r)))

def apply_denoise(img, v):
    k = int(v)
    if k == 0: return img
    if k % 2 == 0: k += 1
    return cv_to_pil(cv2.medianBlur(pil_to_cv(img), k))

def effect_sketch(img):
    cv = pil_to_cv(img)
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    inv  = cv2.bitwise_not(gray)
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sk   = cv2.divide(gray, 255 - blur, scale=256)
    return cv_to_pil(cv2.cvtColor(sk, cv2.COLOR_GRAY2BGR))

def effect_neon(img):
    cv = pil_to_cv(img)
    edges = cv2.dilate(cv2.Canny(cv, 100, 200), None)
    mask = np.zeros_like(cv)
    mask[edges > 0] = [255, 0, 255]
    return cv_to_pil(cv2.add((cv * 0.3).astype(np.uint8), mask))

def effect_sepia(img):
    cv = pil_to_cv(img)
    k  = np.array([[0.272,0.534,0.131],[0.349,0.686,0.168],[0.393,0.769,0.189]])
    s  = cv2.transform(cv, k)
    n  = np.random.normal(0, 15, s.shape).astype(np.uint8)
    return cv_to_pil(cv2.add(s, n))

# ── Session State Init ─────────────────────────────────────────────────────────
def init_state():
    defaults = dict(
        brightness=1.0, contrast=1.0, saturation=1.0, temp=0, denoise=0,
        effect="Normal", show_ba=False, orig_image=None, status="Siap — Load gambar atau ambil foto kamera"
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Header (matches "🖌  FOR Editor" + "by Fariza · Ocid · Rasya")
    st.markdown("""
    <div class="for-header">
        <h2>✏️ FOR Editor</h2>
        <p>by Fariza · Ocid · Rasya</p>
    </div>
    """, unsafe_allow_html=True)

    # ── CARD: Drawing Tools ──────────────────────────────────────────────────
    st.markdown('<div class="for-card"><div class="for-card-title">🛠 Drawing Tools</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="btn-color">', unsafe_allow_html=True)
        choose_color = st.button("🎨 Color", key="btn_color")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        clear_btn = st.button("🧹 Clear", key="btn_clear")

    st.markdown('<div class="btn-eraser">', unsafe_allow_html=True)
    eraser_btn = st.button("🧽  Eraser", key="btn_eraser")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<p class="for-muted" style="margin-top:8px;">Brush Shape</p>', unsafe_allow_html=True)
    brush_shape = st.radio("Brush Shape", ["● Round", "◆ Flat", "✦ Spray"], horizontal=True, label_visibility="collapsed")

    st.markdown('<p class="for-muted" style="margin-top:6px;">Brush Size</p>', unsafe_allow_html=True)
    brush_size = st.slider("Brush Size", 1, 50, 5, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── CARD: Image Adjustments ──────────────────────────────────────────────
    st.markdown('<div class="for-card"><div class="for-card-title">🎛 Image Adjustments</div>', unsafe_allow_html=True)

    b_val = st.slider("☀️ Brightness", 0.0, 2.0, st.session_state.brightness, 0.05)
    c_val = st.slider("🌓 Contrast",   0.0, 2.0, st.session_state.contrast,   0.05)
    s_val = st.slider("🎨 Saturation", 0.0, 3.0, st.session_state.saturation, 0.05)
    t_val = st.slider("🌡️ Temperature", -100, 100, st.session_state.temp, 5)
    d_val = st.slider("✨ Denoise",    0,   20,  st.session_state.denoise, 2)

    st.session_state.brightness = b_val
    st.session_state.contrast   = c_val
    st.session_state.saturation = s_val
    st.session_state.temp       = t_val
    st.session_state.denoise    = d_val

    st.markdown('</div>', unsafe_allow_html=True)

    # ── CARD: Special Effects ────────────────────────────────────────────────
    st.markdown('<div class="for-card"><div class="for-card-title">✨ Special Effects</div>', unsafe_allow_html=True)
    st.markdown('<p class="for-muted">Click again to toggle off</p>', unsafe_allow_html=True)

    cur_fx = st.session_state.effect

    sketch_cls = "btn-active" if cur_fx == "sketch" else ""
    neon_cls   = "btn-active" if cur_fx == "neon"   else ""
    sepia_cls  = "btn-active" if cur_fx == "sepia"  else ""

    st.markdown(f'<div class="{sketch_cls}">', unsafe_allow_html=True)
    if st.button("✏️  Pencil Sketch",  key="fx_sketch"): st.session_state.effect = "Normal" if cur_fx == "sketch" else "sketch"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="{neon_cls}">', unsafe_allow_html=True)
    if st.button("🌆  Cyberpunk Neon", key="fx_neon"):   st.session_state.effect = "Normal" if cur_fx == "neon"   else "neon";   st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="{sepia_cls}">', unsafe_allow_html=True)
    if st.button("📜  Sepia Vintage",  key="fx_sepia"):  st.session_state.effect = "Normal" if cur_fx == "sepia"  else "sepia";  st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── CARD: Before / After ─────────────────────────────────────────────────
    st.markdown('<div class="for-card"><div class="for-card-title">🔍 Before / After</div>', unsafe_allow_html=True)
    st.markdown('<p class="for-muted">Load an image first, then apply effects and compare.</p>', unsafe_allow_html=True)

    st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
    if st.button("⚡  Compare Before / After", key="btn_ba"):
        st.session_state.show_ba = not st.session_state.show_ba
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── BOTTOM FILE DOCK (Load / Save / Undo / Redo + Camera) ────────────────
    st.markdown('<div style="border-top:1px solid #30363d; padding: 8px 10px 4px 10px;">', unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        load_btn = st.button("📂 Load", key="btn_load")
    with d2:
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        save_btn = st.button("💾 Save", key="btn_save")
        st.markdown('</div>', unsafe_allow_html=True)
    with d3:
        undo_btn = st.button("↩ Undo", key="btn_undo")
    with d4:
        redo_btn = st.button("↪ Redo", key="btn_redo")

    st.markdown('<div class="btn-blue" style="margin-top:4px;">', unsafe_allow_html=True)
    cam_toggle = st.button("📷  Camera", key="btn_cam")
    st.markdown('</div>', unsafe_allow_html=True)

    # Upload / Camera input (hidden behind buttons, shown conditionally)
    uploaded_file = st.file_uploader("Load Image", type=["png","jpg","jpeg","webp","bmp"], label_visibility="collapsed")
    camera_photo  = st.camera_input("Camera", label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

# ── LOAD IMAGE ─────────────────────────────────────────────────────────────────
base_image = None
if uploaded_file is not None:
    base_image = Image.open(uploaded_file).convert("RGB")
    st.session_state.orig_image = base_image.copy()
    st.session_state.status = f"Loaded: {uploaded_file.name}"
elif camera_photo is not None:
    base_image = Image.open(camera_photo).convert("RGB")
    st.session_state.orig_image = base_image.copy()
    st.session_state.status = "Loaded from Camera"
elif st.session_state.orig_image is not None:
    base_image = st.session_state.orig_image.copy()

is_blank = base_image is None
if is_blank:
    base_image = Image.new("RGB", (860, 650), "white")

# ── APPLY FILTERS ──────────────────────────────────────────────────────────────
processed = base_image.copy()
if d_val > 0:        processed = apply_denoise(processed, d_val)
if t_val != 0:       processed = adjust_temperature(processed, t_val)
if b_val != 1.0:     processed = adjust_brightness(processed, b_val)
if c_val != 1.0:     processed = adjust_contrast(processed, c_val)
if s_val != 1.0:     processed = adjust_saturation(processed, s_val)

fx = st.session_state.effect
if fx == "sketch":   processed = effect_sketch(processed); st.session_state.status = "Effect active: sketch"
elif fx == "neon":   processed = effect_neon(processed);   st.session_state.status = "Effect active: neon"
elif fx == "sepia":  processed = effect_sepia(processed);  st.session_state.status = "Effect active: sepia"

if clear_btn:
    base_image = Image.new("RGB", (860, 650), "white")
    st.session_state.orig_image = None
    st.session_state.effect = "Normal"
    st.session_state.status = "Canvas cleared"
    processed = base_image.copy()
    st.rerun()

# ── MAIN CANVAS AREA ───────────────────────────────────────────────────────────
st.markdown('<div class="canvas-wrap">', unsafe_allow_html=True)
st.markdown('<div class="canvas-border">', unsafe_allow_html=True)
st.image(processed, use_column_width=False, width=860 if not is_blank else 700,
         caption=None)
st.markdown('</div></div>', unsafe_allow_html=True)

# ── BEFORE / AFTER POPUP (Matches original Toplevel window style) ──────────────
if st.session_state.show_ba and not is_blank and st.session_state.orig_image is not None:
    st.markdown("""
    <div style="
        position:fixed; top:0; left:0; width:100%; height:100%;
        background:rgba(0,0,0,0.6); z-index:1000;
        display:flex; align-items:center; justify-content:center;">
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="ba-popup">', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; margin-bottom:14px; color:#e6edf3; font-size:13px; font-weight:bold; border-bottom:1px solid #30363d; padding-bottom:8px;">
            Before / After Comparison
        </div>
        """, unsafe_allow_html=True)

        col_b, col_div, col_a = st.columns([10, 1, 10])
        with col_b:
            st.markdown('<div class="ba-label-before">BEFORE</div>', unsafe_allow_html=True)
            before_thumb = st.session_state.orig_image.resize((500, 400))
            st.image(before_thumb, use_column_width=True)
        with col_div:
            st.markdown('<div style="border-left:2px solid #30363d; height:100%; margin:auto;"></div>', unsafe_allow_html=True)
        with col_a:
            st.markdown('<div class="ba-label-after">AFTER</div>', unsafe_allow_html=True)
            after_thumb = processed.resize((500, 400))
            st.image(after_thumb, use_column_width=True)

        _, close_col, _ = st.columns([2, 1, 2])
        with close_col:
            if st.button("✕  Close", key="close_ba"):
                st.session_state.show_ba = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ── SAVE DOWNLOAD ──────────────────────────────────────────────────────────────
if save_btn:
    buf = io.BytesIO()
    processed.save(buf, format="PNG")
    st.sidebar.download_button(
        "⬇️ Download PNG", buf.getvalue(),
        file_name="foreditor_export.png", mime="image/png", use_container_width=True
    )

# ── STATUS BAR ─────────────────────────────────────────────────────────────────
status_msg = st.session_state.status
st.markdown(f'<div class="status-bar">{status_msg}</div>', unsafe_allow_html=True)
