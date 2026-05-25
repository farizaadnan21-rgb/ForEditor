import streamlit as st
from PIL import Image, ImageDraw
import cv2
import numpy as np
import io

# ─── 1. PAGE CONFIGURATION (MATCHING ORIGINAL DESIGN) ───────────────────────
st.set_page_config(
    page_title="ForEditor — Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── 2. INJECT PROFESSIONAL DARK CUSTOM CSS (EXACT COPY OF ORIGINAL THEME) ──
# Match: bg_main (#14161c), bg_sidebar (#1c1f26), bg_card (#252930), text (#e8eaed), accent (#4a8cff)
st.markdown("""
<style>
    /* App background */
    .stApp {
        background-color: #14161c !important;
        color: #e8eaed !important;
        font-family: 'Segoe UI', -apple-system, sans-serif !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1c1f26 !important;
        border-right: 1px solid #3a4049 !important;
        width: 330px !important;
    }
    
    /* Custom Card container (Exactly like original self._make_card) */
    .original-card {
        background-color: #252930;
        border: 1px solid #3a4049;
        border-radius: 4px;
        padding: 14px;
        margin-bottom: 12px;
    }
    
    .original-card-title {
        color: #e8eaed;
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
        font-weight: bold;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Input Elements Dark Styling */
    div[data-baseweb="select"] > div {
        background-color: #1e2229 !important;
        border-color: #3a4049 !important;
        color: #e8eaed !important;
    }
    
    /* White Canvas Border & Shadow Styling (Matches canvas_outer and canvas_inner) */
    .canvas-outer {
        background-color: #0d0e12;
        padding: 4px;
        border-radius: 4px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5);
        display: inline-block;
        margin: auto;
    }
    
    .canvas-inner {
        background-color: #000000;
        padding: 1px;
    }
    
    /* Status bar at the bottom */
    .status-bar {
        background-color: #111318;
        color: #8b929a;
        font-family: 'Segoe UI', sans-serif;
        font-size: 12px;
        padding: 6px 14px;
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        border-top: 1px solid #3a4049;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# ─── 3. CORE PROCESSING LOGIC (PRESERVING ALL ORIGINAL FILTER MATHEMATICS) ───
def pil_to_cv(pil_image):
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

def cv_to_pil(cv_image):
    return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

def adjust_brightness(pil_image, val):
    from PIL import ImageEnhance
    return ImageEnhance.Brightness(pil_image).enhance(float(val))

def adjust_contrast(pil_image, val):
    from PIL import ImageEnhance
    return ImageEnhance.Contrast(pil_image).enhance(float(val))

def adjust_saturation(pil_image, val):
    from PIL import ImageEnhance
    return ImageEnhance.Color(pil_image).enhance(float(val))

def adjust_temperature(pil_image, val):
    value = int(val)
    if value == 0: 
        return pil_image
    img = pil_to_cv(pil_image)
    b, g, r = cv2.split(img)
    if value > 0:  # Hangat (Kuning)
        r = cv2.add(r, value)
        b = cv2.subtract(b, value)
    else:  # Dingin (Biru)
        r = cv2.add(r, value)
        b = cv2.subtract(b, value)
    return cv_to_pil(cv2.merge((b, g, r)))

def apply_denoise(pil_image, val):
    k = int(val)
    if k == 0: 
        return pil_image
    if k % 2 == 0: 
        k += 1
    img = pil_to_cv(pil_image)
    res = cv2.medianBlur(img, k)
    return cv_to_pil(res)

# ─── SPECIAL EFFECTS (EXACT REPLICAS OF ORIGINAL PIPELINES) ──────────────────
def effect_sketch(pil_image):
    img = pil_to_cv(pil_image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv = cv2.bitwise_not(gray)
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    return cv_to_pil(cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR))

def effect_neon(pil_image):
    img = pil_to_cv(pil_image)
    edges = cv2.Canny(img, 100, 200)
    edges = cv2.dilate(edges, None)
    neon_mask = np.zeros_like(img)
    neon_mask[edges > 0] = [255, 0, 255]  # Magenta Neon
    dark_img = (img * 0.3).astype(np.uint8)
    return cv_to_pil(cv2.add(dark_img, neon_mask))

def effect_sepia(pil_image):
    img = pil_to_cv(pil_image)
    kernel = np.array([[0.272, 0.534, 0.131], 
                       [0.349, 0.686, 0.168], 
                       [0.393, 0.769, 0.189]])
    sepia = cv2.transform(img, kernel)
    noise = np.random.normal(0, 15, sepia.shape).astype(np.uint8)
    return cv_to_pil(cv2.add(sepia, noise))

# ─── 4. SIDEBAR BRANDING (EXACTLY MATCHING ORIGINAL TKINTER HEADER) ─────────
st.sidebar.markdown(
    """
    <div style="padding: 10px 0px 20px 0px;">
        <h1 style="margin: 0; font-size: 1.8rem; font-weight: bold; color: #e8eaed;">🖌️ ForEditor</h1>
        <p style="margin: 2px 0 0 0; color: #8b929a; font-size: 0.85rem;">
            Lightweight image editor · portfolio ready
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Initialize states if not present
if "brightness" not in st.session_state: st.session_state.brightness = 1.0
if "contrast" not in st.session_state: st.session_state.contrast = 1.0
if "saturation" not in st.session_state: st.session_state.saturation = 1.0
if "temp" not in st.session_state: st.session_state.temp = 0
if "denoise" not in st.session_state: st.session_state.denoise = 0
if "effect" not in st.session_state: st.session_state.effect = "Normal"
if "brush_color" not in st.session_state: st.session_state.brush_color = "#000000"
if "brush_shape" not in st.session_state: st.session_state.brush_shape = "● Bulat"
if "brush_size" not in st.session_state: st.session_state.brush_size = 5

# ─── 5. CARD 1: ALAT GAMBAR (RESTORING THE SOUL OF ORIGINAL SIDEBAR) ────────
with st.sidebar:
    st.markdown('<div class="original-card">', unsafe_allow_html=True)
    st.markdown('<div class="original-card-title">🛠️ Alat Gambar</div>', unsafe_allow_html=True)
    
    # Grid for Brush Color Swatch and Buttons
    col_swatch, col_buttons = st.columns([1, 2])
    with col_swatch:
        brush_color = st.color_picker("Warna", st.session_state.brush_color, label_visibility="collapsed")
        st.session_state.brush_color = brush_color
    with col_buttons:
        if st.button("🧹 Reset Kanvas", use_container_width=True):
            st.session_state.brightness = 1.0
            st.session_state.contrast = 1.0
            st.session_state.saturation = 1.0
            st.session_state.temp = 0
            st.session_state.denoise = 0
            st.session_state.effect = "Normal"
            st.rerun()
            
    # Eraser mode styling simulation
    if st.button("🧽 Penghapus (Set Putih)", use_container_width=True):
        st.session_state.brush_color = "#FFFFFF"
        st.rerun()
        
    st.markdown("<div style='font-size: 11px; color: #8b929a; margin-top: 8px; margin-bottom: 2px;'>Bentuk kuas</div>", unsafe_allow_html=True)
    brush_shape = st.radio(
        "Bentuk kuas", 
        ["● Bulat", "■ Kotak", "✦ Spray"], 
        index=["● Bulat", "■ Kotak", "✦ Spray"].index(st.session_state.brush_shape),
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.brush_shape = brush_shape
    
    st.markdown("<div style='font-size: 11px; color: #8b929a; margin-top: 8px;'>Ukuran kuas</div>", unsafe_allow_html=True)
    brush_size = st.slider(
        "Ukuran kuas", 1, 50, st.session_state.brush_size,
        label_visibility="collapsed"
    )
    st.session_state.brush_size = brush_size
    
    st.markdown('</div>', unsafe_allow_html=True)

# ─── 6. CARD 2: PENYESUAIAN GAMBAR (ACCORDION STYLE FROM ORIGINAL) ──────────
with st.sidebar:
    st.markdown('<div class="original-card">', unsafe_allow_html=True)
    st.markdown('<div class="original-card-title">🎛️ Penyesuaian Gambar</div>', unsafe_allow_html=True)
    
    # Re-creating Accordion with beautiful clean sliders
    b_val = st.slider("☀️ Kecerahan", 0.0, 2.0, st.session_state.brightness, 0.1)
    st.session_state.brightness = b_val
    
    c_val = st.slider("🌓 Kontras", 0.0, 2.0, st.session_state.contrast, 0.1)
    st.session_state.contrast = c_val
    
    s_val = st.slider("🎨 Saturasi", 0.0, 3.0, st.session_state.saturation, 0.1)
    st.session_state.saturation = s_val
    
    t_val = st.slider("🌡️ Temperatur (Hangat/Dingin)", -100, 100, st.session_state.temp, 5)
    st.session_state.temp = t_val
    
    d_val = st.slider("✨ Hilangkan Noise", 0, 20, st.session_state.denoise, 2)
    st.session_state.denoise = d_val
    
    st.markdown('</div>', unsafe_allow_html=True)

# ─── 7. CARD 3: EFEK SPESIAL (ORIGINAL CHROME INTEGRATION) ───────────────────
with st.sidebar:
    st.markdown('<div class="original-card">', unsafe_allow_html=True)
    st.markdown('<div class="original-card-title">✨ Efek Spesial</div>', unsafe_allow_html=True)
    
    fx_option = st.selectbox(
        "Pilih Efek Spesial:",
        ["Normal", "✏️ Sketsa Pensil", "🌆 Cyberpunk Neon", "📜 Sepia Vintage"],
        index=["Normal", "✏️ Sketsa Pensil", "🌆 Cyberpunk Neon", "📜 Sepia Vintage"].index(st.session_state.effect),
        label_visibility="collapsed"
    )
    st.session_state.effect = fx_option
    st.markdown('</div>', unsafe_allow_html=True)

# ─── 8. BOTTOM OPERATION DOCK (FILE OPS MATCHING ORIGINAL DOCK) ─────────────
with st.sidebar:
    st.markdown('<div class="original-card" style="padding: 10px;">', unsafe_allow_html=True)
    
    # Input selections matching bottom dock
    source_choice = st.radio("Input Sumber:", ["📂 Load File", "📷 Ambil Foto"], horizontal=True, label_visibility="collapsed")
    
    uploaded_file = None
    camera_photo = None
    
    if source_choice == "📂 Load File":
        uploaded_file = st.file_uploader("Load Image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    else:
        camera_photo = st.camera_input("Ambil Foto", label_visibility="collapsed")
        
    st.markdown('</div>', unsafe_allow_html=True)

# ─── 9. MAIN STUDIO CANVAS (RESTORED BEAUTIFUL ORIGINAL WORKSPACE) ───────────
# Load original/uploaded image
base_image = None
if uploaded_file is not None:
    base_image = Image.open(uploaded_file).convert("RGB")
elif camera_photo is not None:
    base_image = Image.open(camera_photo).convert("RGB")

if base_image is None:
    # Blank White Studio Canvas (Exactly 900x750 like original self.canvas_w / self.canvas_h)
    base_image = Image.new("RGB", (900, 750), "white")
    is_blank = True
else:
    # Scale image to match standard studio workspace resolution
    base_image = base_image.resize((900, 750))
    is_blank = False

# Apply all filters reactively in the original chain order
processed_image = base_image.copy()

# 1. Denoise
if st.session_state.denoise > 0:
    processed_image = apply_denoise(processed_image, st.session_state.denoise)
# 2. Temperature
if st.session_state.temp != 0:
    processed_image = adjust_temperature(processed_image, st.session_state.temp)
# 3. Brightness
if st.session_state.brightness != 1.0:
    processed_image = adjust_brightness(processed_image, st.session_state.brightness)
# 4. Contrast
if st.session_state.contrast != 1.0:
    processed_image = adjust_contrast(processed_image, st.session_state.contrast)
# 5. Saturation
if st.session_state.saturation != 1.0:
    processed_image = adjust_saturation(processed_image, st.session_state.saturation)
# 6. Special Effects
if st.session_state.effect == "✏️ Sketsa Pensil":
    processed_image = effect_sketch(processed_image)
elif st.session_state.effect == "🌆 Cyberpunk Neon":
    processed_image = effect_neon(processed_image)
elif st.session_state.effect == "📜 Sepia Vintage":
    processed_image = effect_sepia(processed_image)

# Draw on canvas if a brush size and color are active (Optional Web Drawing simulation)
# Users can interactively see details. We display the canvas in the center.
col_canvas, col_ops = st.columns([3, 1])

with col_canvas:
    # Display Canvas with the original self.canvas_outer and shadow border style
    st.markdown('<div class="canvas-outer"><div class="canvas-inner">', unsafe_allow_html=True)
    st.image(processed_image, use_column_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

with col_ops:
    st.markdown(
        """
        <div class="original-card" style="min-height: 250px;">
            <div class="original-card-title">🔍 Detail & Operasi</div>
            <p style="font-size: 11px; color: #8b929a; margin: 0 0 10px 0;">
                Gunakan tab di bawah untuk melihat perbandingan real-time.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Save/Download Operation (Exactly equivalent to Self.save_image)
    buf = io.BytesIO()
    processed_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="💾 SAVE IMAGE (Unduh PNG)",
        data=byte_im,
        file_name="foreditor_studio_export.png",
        mime="image/png",
        use_container_width=True
    )

# ─── 10. BEFORE / AFTER REAL-TIME ACCORDION COMPARISON ──────────────────────
if not is_blank:
    st.markdown("---")
    st.markdown("### 🔍 Perbandingan Sebelum / Sesudah (Before vs After)")
    col_b, col_a = st.columns(2)
    with col_b:
        st.markdown("<p style='color: #8b929a; font-size: 12px; font-weight: bold;'>BEFORE (Asli)</p>", unsafe_allow_html=True)
        st.image(base_image, use_column_width=True)
    with col_a:
        st.markdown("<p style='color: #4a8cff; font-size: 12px; font-weight: bold;'>AFTER (Edit)</p>", unsafe_allow_html=True)
        st.image(processed_image, use_column_width=True)

# ─── 11. ORIGINAL STATUS BAR (BOTTOM FIXED DOCK) ────────────────────────────
# Matching self.status_var.set("Siap — Ctrl+Z Undo · Ctrl+Y Redo")
st.markdown(
    f"""
    <div class="status-bar">
        🟢 Siap — Warna Kuas: {st.session_state.brush_color} · Ukuran: {st.session_state.brush_size} px · Bentuk: {st.session_state.brush_shape}
    </div>
    """,
    unsafe_allow_html=True
)
