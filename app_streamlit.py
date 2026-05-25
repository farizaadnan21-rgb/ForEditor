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

# ─────────────────────────────────────────────────────────────────────────────
# CSS  —  exact dark theme from original Tkinter app + accordion animation
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, .stApp {
    background-color: #0f1117 !important;
    color: #e6edf3 !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}
#MainMenu, footer, header { display:none !important; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    overflow-x: hidden !important;
}

/* ── SIDEBAR HEADER ── */
.sb-header {
    padding: 14px 14px 10px 14px;
    border-bottom: 1px solid #30363d;
    margin-bottom: 6px;
}
.sb-title { font-size: 15px; font-weight: 700; color: #e6edf3; }
.sb-sub   { font-size: 9px;  color: #8b949e; margin-top: 2px; }

/* ── COMPACT CARD ── */
.card {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 5px;
    margin: 4px 8px;
    padding: 8px 10px;
}
.card-title {
    font-size: 10px; font-weight: 700;
    color: #8b949e; letter-spacing: .5px;
    text-transform: uppercase;
    margin-bottom: 7px;
}
.muted { font-size: 9px; color: #8b949e; margin-bottom: 3px; }

/* ── ALL BUTTONS — compact & elegant ── */
.stButton > button {
    width: 100%;
    background: #2d333b !important;
    color: #e6edf3 !important;
    border: 1px solid #3d444d !important;
    border-radius: 4px !important;
    font-size: 11px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    padding: 4px 8px !important;
    margin-bottom: 2px !important;
    cursor: pointer !important;
    transition: background .15s, border-color .15s, transform .08s !important;
    text-align: left !important;
    line-height: 1.4 !important;
}
.stButton > button:hover {
    background: #373e47 !important;
    border-color: #6e7681 !important;
}
.stButton > button:active {
    transform: scale(0.97) !important;
}

/* ── ACCORDION BUTTON (active state) ── */
.acc-open .stButton > button {
    background: #1c2d3d !important;
    border-color: #1f6feb !important;
    color: #58a6ff !important;
}
.acc-open .stButton > button::after {
    content: ' ▲';
    float: right;
    font-size: 8px;
    opacity: 0.7;
}
.acc-closed .stButton > button::after {
    content: ' ▼';
    float: right;
    font-size: 8px;
    opacity: 0.4;
}

/* ── SLIDER inside accordion — fade-in animation ── */
.slider-panel {
    background: #1c2128;
    border: 1px solid #1f6feb44;
    border-radius: 4px;
    padding: 6px 8px 4px 8px;
    margin: 2px 0 4px 0;
    animation: fadeSlide .18s ease-out;
}
@keyframes fadeSlide {
    from { opacity: 0; transform: translateY(-6px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── BUTTON VARIANTS ── */
.btn-orange .stButton > button {
    background: #b45309 !important;
    border-color: #d97706 !important;
    color: #fef3c7 !important;
    text-align: center !important;
}
.btn-red .stButton > button {
    background: #7f1d1d !important;
    border-color: #b91c1c !important;
    color: #fecaca !important;
    text-align: center !important;
}
.btn-blue .stButton > button {
    background: #1d4ed8 !important;
    border-color: #3b82f6 !important;
    color: #eff6ff !important;
    text-align: center !important;
}
.btn-green .stButton > button {
    background: #166534 !important;
    border-color: #16a34a !important;
    color: #dcfce7 !important;
    text-align: center !important;
}
.fx-active .stButton > button {
    background: #1c3a5c !important;
    border-color: #1f6feb !important;
    color: #58a6ff !important;
}

/* ── RADIO ── */
[data-testid="stRadio"] label span { font-size: 10px !important; color: #e6edf3 !important; }
[data-testid="stRadio"] > div { gap: 4px !important; }

/* ── SLIDER ── */
[data-testid="stSlider"] label, [data-testid="stSlider"] p {
    font-size: 9px !important;
    color: #8b949e !important;
}
[data-testid="stSlider"] { padding: 2px 0 !important; }

/* ── FILE UPLOADER compact ── */
[data-testid="stFileUploader"] { padding: 0 !important; }
[data-testid="stFileUploader"] section {
    padding: 6px 8px !important;
    background: #21262d !important;
    border: 1px dashed #3d444d !important;
    border-radius: 4px !important;
}
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] p { font-size: 9px !important; color: #8b949e !important; }

/* ── CAMERA ── */
[data-testid="stCameraInput"] video {
    border-radius: 4px !important;
    border: 1px solid #30363d !important;
    max-height: 130px !important;
    object-fit: cover !important;
}

/* ── DOCK (bottom) ── */
.dock {
    border-top: 1px solid #30363d;
    padding: 6px 8px 6px 8px;
    margin-top: auto;
}

/* ── MAIN CANVAS ── */
.canvas-wrap {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    background: #0f1117;
    padding: 24px;
    min-height: calc(100vh - 28px);
}
.canvas-box {
    border: 2px solid #30363d;
    box-shadow: 0 8px 40px rgba(0,0,0,.9), 0 0 0 1px #000;
    background: white;
}

/* ── BEFORE/AFTER MODAL ── */
.ba-modal {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 16px;
    margin-top: 12px;
    animation: fadeSlide .2s ease-out;
}
.ba-title {
    text-align: center; font-size: 12px; font-weight: 700;
    color: #e6edf3; border-bottom: 1px solid #30363d;
    padding-bottom: 8px; margin-bottom: 12px;
}
.ba-b { font-size: 10px; font-weight: 700; color: #8b949e; text-align:center; padding-bottom:4px; }
.ba-a { font-size: 10px; font-weight: 700; color: #2ea043; text-align:center; padding-bottom:4px; }

/* ── STATUS BAR ── */
.status-bar {
    position: fixed; bottom: 0; left: 0;
    width: 100%; background: #0d1117;
    color: #8b949e; font-size: 9px;
    font-family: 'Inter', sans-serif;
    padding: 3px 14px;
    border-top: 1px solid #30363d;
    z-index: 9999;
}
</style>
""", unsafe_allow_html=True)

# ── Image Processing Helpers ───────────────────────────────────────────────────
def pil_to_cv(img): return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
def cv_to_pil(img): return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

def apply_brightness(img, v):  return ImageEnhance.Brightness(img).enhance(float(v))
def apply_contrast(img, v):    return ImageEnhance.Contrast(img).enhance(float(v))
def apply_saturation(img, v):  return ImageEnhance.Color(img).enhance(float(v))
def apply_sharpness(img, v):   return ImageEnhance.Sharpness(img).enhance(float(v))

def apply_temperature(img, v):
    val = int(v)
    if val == 0: return img
    c = pil_to_cv(img); b, g, r = cv2.split(c)
    r = cv2.add(r, val); b = cv2.subtract(b, val)
    return cv_to_pil(cv2.merge((b, g, r)))

def apply_denoise(img, v):
    k = int(v)
    if k == 0: return img
    if k % 2 == 0: k += 1
    return cv_to_pil(cv2.medianBlur(pil_to_cv(img), k))

def fx_sketch(img):
    c = pil_to_cv(img)
    gray = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)
    inv = cv2.bitwise_not(gray)
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sk = cv2.divide(gray, 255 - blur, scale=256)
    return cv_to_pil(cv2.cvtColor(sk, cv2.COLOR_GRAY2BGR))

def fx_neon(img):
    c = pil_to_cv(img)
    edges = cv2.dilate(cv2.Canny(c, 100, 200), None)
    mask = np.zeros_like(c); mask[edges > 0] = [255, 0, 255]
    return cv_to_pil(cv2.add((c * 0.3).astype(np.uint8), mask))

def fx_sepia(img):
    c = pil_to_cv(img)
    k = np.array([[0.272,0.534,0.131],[0.349,0.686,0.168],[0.393,0.769,0.189]])
    s = cv2.transform(c, k)
    n = np.random.normal(0, 15, s.shape).astype(np.uint8)
    return cv_to_pil(cv2.add(s, n))

# ── Session State Init ─────────────────────────────────────────────────────────
DEFAULTS = dict(
    brightness=1.0, contrast=1.0, saturation=1.0,
    temp=0, denoise=0, sharpness=1.0,
    effect="Normal", active_adj=None,
    orig_image=None, show_ba=False,
    input_mode="upload",
    status="Siap — Load gambar atau ambil foto"
)
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Accordion config: (label, key, min, max, default, step, format)
ADJ = [
    ("☀️  Brightness", "brightness", 0.0,  2.0,  1.0, 0.05, "%.2f"),
    ("🌓  Contrast",   "contrast",   0.0,  2.0,  1.0, 0.05, "%.2f"),
    ("🎨  Saturation", "saturation", 0.0,  3.0,  1.0, 0.05, "%.2f"),
    ("🌡️  Temperature","temp",       -100, 100,  0,   5,    "%d"),
    ("✨  Denoise",    "denoise",    0,    20,   0,   2,    "%d"),
]

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:

    # Header
    st.markdown("""
    <div class="sb-header">
        <div class="sb-title">✏️ FOR Editor</div>
        <div class="sb-sub">by Fariza · Ocid · Rasya</div>
    </div>""", unsafe_allow_html=True)

    # ── CARD: Drawing Tools ──────────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">🛠  Drawing Tools</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="btn-orange">', unsafe_allow_html=True)
        st.button("🎨  Color", key="btn_color")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.button("🧹  Clear", key="btn_clear")

    st.markdown('<div class="btn-red">', unsafe_allow_html=True)
    st.button("🧽  Eraser", key="btn_eraser")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="muted" style="margin-top:6px">Brush Shape</div>', unsafe_allow_html=True)
    st.radio("", ["● Round", "◆ Flat", "✦ Spray"],
             horizontal=True, key="brush_shape", label_visibility="collapsed")

    st.markdown('<div class="muted" style="margin-top:4px">Brush Size</div>', unsafe_allow_html=True)
    st.slider("", 1, 50, 5, key="brush_size", label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── CARD: Image Adjustments (Accordion) ──────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">🎛  Image Adjustments</div>', unsafe_allow_html=True)

    for (label, key, mn, mx, dflt, step, fmt) in ADJ:
        is_open = st.session_state.active_adj == key
        css_cls = "acc-open" if is_open else "acc-closed"

        st.markdown(f'<div class="{css_cls}">', unsafe_allow_html=True)
        if st.button(label, key=f"acc_{key}"):
            st.session_state.active_adj = None if is_open else key
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Slider — only show for the open accordion item
        if is_open:
            current = st.session_state.get(key, dflt)
            st.markdown('<div class="slider-panel">', unsafe_allow_html=True)
            # Use float or int slider depending on type
            if isinstance(dflt, float):
                new_val = st.slider(
                    label, float(mn), float(mx), float(current), float(step),
                    key=f"sl_{key}", label_visibility="collapsed"
                )
            else:
                new_val = st.slider(
                    label, int(mn), int(mx), int(current), int(step),
                    key=f"sl_{key}", label_visibility="collapsed"
                )
            st.session_state[key] = new_val
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── CARD: Special Effects ─────────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">✨  Special Effects</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Click again to toggle off</div>', unsafe_allow_html=True)

    cur_fx = st.session_state.effect
    for (lbl, fx_key) in [
        ("✏️  Pencil Sketch", "sketch"),
        ("🌆  Cyberpunk Neon", "neon"),
        ("📜  Sepia Vintage",  "sepia"),
    ]:
        css = "fx-active" if cur_fx == fx_key else ""
        st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
        if st.button(lbl, key=f"fx_{fx_key}"):
            st.session_state.effect = "Normal" if cur_fx == fx_key else fx_key
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── CARD: Before / After ──────────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">🔍  Before / After</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Load an image first, then apply effects and compare.</div>', unsafe_allow_html=True)

    st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
    if st.button("⚡  Compare Before / After", key="btn_ba"):
        st.session_state.show_ba = not st.session_state.show_ba
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

    # ── DOCK: Load / Save / Undo / Redo / Camera ─────────────────────────────
    st.markdown('<div class="dock">', unsafe_allow_html=True)
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        load_clicked = st.button("📂 Load", key="d_load")
    with d2:
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        save_clicked = st.button("💾 Save", key="d_save")
        st.markdown('</div>', unsafe_allow_html=True)
    with d3:
        st.button("↩ Undo", key="d_undo")
    with d4:
        st.button("↪ Redo", key="d_redo")

    st.markdown('<div class="btn-blue" style="margin-top:3px">', unsafe_allow_html=True)
    cam_clicked = st.button("📷  Camera", key="d_cam")
    st.markdown('</div>', unsafe_allow_html=True)

    # Toggle input mode
    if cam_clicked:
        st.session_state.input_mode = "camera"
        st.rerun()
    if load_clicked:
        st.session_state.input_mode = "upload"
        st.rerun()

    # Show only the active input widget (compact)
    if st.session_state.input_mode == "upload":
        uploaded = st.file_uploader("", type=["png","jpg","jpeg","webp","bmp"],
                                    label_visibility="collapsed")
        cam_img = None
    else:
        uploaded = None
        cam_img = st.camera_input("", label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

# ── Load Image ─────────────────────────────────────────────────────────────────
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

is_blank = base is None
if is_blank:
    base = Image.new("RGB", (860, 650), "white")

if st.session_state.get("btn_clear"):
    base = Image.new("RGB", (860, 650), "white")
    st.session_state.orig_image = None
    st.session_state.effect     = "Normal"
    st.session_state.active_adj = None
    st.session_state.status     = "Canvas cleared"

# ── Apply Filters ──────────────────────────────────────────────────────────────
out = base.copy()
if st.session_state.denoise > 0:    out = apply_denoise(out,     st.session_state.denoise)
if st.session_state.temp    != 0:   out = apply_temperature(out, st.session_state.temp)
if st.session_state.brightness != 1.0: out = apply_brightness(out, st.session_state.brightness)
if st.session_state.contrast   != 1.0: out = apply_contrast(out,   st.session_state.contrast)
if st.session_state.saturation != 1.0: out = apply_saturation(out, st.session_state.saturation)

fx = st.session_state.effect
if   fx == "sketch": out = fx_sketch(out); st.session_state.status = "Effect active: sketch"
elif fx == "neon":   out = fx_neon(out);   st.session_state.status = "Effect active: neon"
elif fx == "sepia":  out = fx_sepia(out);  st.session_state.status = "Effect active: sepia"

# ── CANVAS ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="canvas-wrap"><div class="canvas-box">', unsafe_allow_html=True)
st.image(out, use_column_width=False, width=860)
st.markdown('</div></div>', unsafe_allow_html=True)

# ── Before / After ─────────────────────────────────────────────────────────────
if st.session_state.show_ba and not is_blank and st.session_state.orig_image is not None:
    st.markdown('<div class="ba-modal">', unsafe_allow_html=True)
    st.markdown('<div class="ba-title">Before / After Comparison</div>', unsafe_allow_html=True)
    cb, ca = st.columns(2)
    with cb:
        st.markdown('<div class="ba-b">BEFORE</div>', unsafe_allow_html=True)
        st.image(st.session_state.orig_image.resize((480, 380)), use_column_width=True)
    with ca:
        st.markdown('<div class="ba-a">AFTER</div>', unsafe_allow_html=True)
        st.image(out.resize((480, 380)), use_column_width=True)
    _, cc, _ = st.columns([2,1,2])
    with cc:
        if st.button("✕  Close", key="close_ba"):
            st.session_state.show_ba = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Save / Download ────────────────────────────────────────────────────────────
if save_clicked:
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    st.sidebar.download_button(
        "⬇️ Download PNG", buf.getvalue(),
        file_name="foreditor_export.png", mime="image/png",
        use_container_width=True
    )

# ── Status Bar ─────────────────────────────────────────────────────────────────
st.markdown(f'<div class="status-bar">{st.session_state.status}</div>', unsafe_allow_html=True)
