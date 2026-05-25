import streamlit as st
from PIL import Image
import cv2
import numpy as np
import io
import os

# Set page config for a professional dark-themed web app
st.set_page_config(
    page_title="ForEditor Studio — Web App",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling (Glassmorphism & Sleek Dark Theme)
st.markdown("""
<style>
    /* Dark Mode aesthetic overrides */
    .stApp {
        background-color: #0f1117;
        color: #e6edf3;
    }
    
    /* Header style */
    .header-container {
        padding: 20px;
        background: linear-gradient(135deg, #161b22 0%, #0f1117 100%);
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    /* Card panel styling */
    .custom-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Highlight labels */
    .accent-text {
        color: #58a6ff;
        font-weight: bold;
    }
    
    /* Title typography */
    h1, h2, h3 {
        font-family: 'Outfit', 'Inter', sans-serif !important;
        color: #e6edf3 !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions to convert between Pillow and OpenCV
def pil_to_cv(pil_image):
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

def cv_to_pil(cv_image):
    return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

# ─── CORE FILTERS (PORTED FROM FILTERS.PY FOR STABILITY) ───────────────────
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
    if value > 0:  # Hangat (Kuning/Merah naik, Biru turun)
        r = cv2.add(r, value)
        b = cv2.subtract(b, value)
    else:  # Dingin (Biru naik, Merah turun)
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

# ─── SPECIAL EFFECTS (PORTED FROM FILTERS.PY FOR STABILITY) ────────────────
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
    neon_mask[edges > 0] = [255, 0, 255]  # Magenta neon
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

# ─── APP HEADER ────────────────────────────────────────────────────────────
st.markdown("""
    <div class="header-container">
        <h1 style="margin: 0; font-size: 2.5rem;">🎨 ForEditor Studio</h1>
        <p style="margin: 5px 0 0 0; color: #8b949e; font-size: 1.1rem;">
            Professional Lightweight Image Editor — Web Demo Version
        </p>
    </div>
""", unsafe_allow_html=True)

# ─── SIDEBAR: UPLOADS & CONTROLS ────────────────────────────────────────────
st.sidebar.markdown("### 📥 Input Sumber Foto")
source_option = st.sidebar.radio("Pilih input:", ["Upload File", "Ambil Foto (Kamera)"])

uploaded_file = None
camera_photo = None

if source_option == "Upload File":
    uploaded_file = st.sidebar.file_uploader(
        "Upload gambar Anda:", 
        type=["png", "jpg", "jpeg", "webp", "bmp"]
    )
else:
    camera_photo = st.sidebar.camera_input("Ambil gambar dari kamera laptop/HP")

# Load image based on choice
image_to_process = None
if uploaded_file is not None:
    image_to_process = Image.open(uploaded_file).convert("RGB")
elif camera_photo is not None:
    image_to_process = Image.open(camera_photo).convert("RGB")

# ─── CONTROLS SIDEBAR ───────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Penyesuaian Gambar")

# Reset button in sidebar
if st.sidebar.button("🧹 Reset Semua Penyesuaian", use_container_width=True):
    st.session_state.brightness = 1.0
    st.session_state.contrast = 1.0
    st.session_state.saturation = 1.0
    st.session_state.temp = 0
    st.session_state.denoise = 0
    st.session_state.effect = "Normal"
    st.rerun()

# Initialize session states for sliders if they don't exist
if "brightness" not in st.session_state: st.session_state.brightness = 1.0
if "contrast" not in st.session_state: st.session_state.contrast = 1.0
if "saturation" not in st.session_state: st.session_state.saturation = 1.0
if "temp" not in st.session_state: st.session_state.temp = 0
if "denoise" not in st.session_state: st.session_state.denoise = 0
if "effect" not in st.session_state: st.session_state.effect = "Normal"

# Sliders
b_val = st.sidebar.slider(
    "☀️ Kecerahan (Brightness)", 
    0.0, 2.0, st.session_state.brightness, 0.1, key="brightness"
)
c_val = st.sidebar.slider(
    "🌓 Kontras (Contrast)", 
    0.0, 2.0, st.session_state.contrast, 0.1, key="contrast"
)
s_val = st.sidebar.slider(
    "🎨 Saturasi (Saturation)", 
    0.0, 3.0, st.session_state.saturation, 0.1, key="saturation"
)
t_val = st.sidebar.slider(
    "🌡️ Temperatur (Hangat/Dingin)", 
    -100, 100, st.session_state.temp, 5, key="temp"
)
d_val = st.sidebar.slider(
    "✨ Hilangkan Noise (Denoise)", 
    0, 20, st.session_state.denoise, 2, key="denoise"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ✨ Efek Spesial")
fx_option = st.sidebar.selectbox(
    "Terapkan Efek:",
    ["Normal", "✏️ Sketsa Pensil", "🌆 Cyberpunk Neon", "📜 Sepia Vintage"],
    index=["Normal", "✏️ Sketsa Pensil", "🌆 Cyberpunk Neon", "📜 Sepia Vintage"].index(st.session_state.effect),
    key="effect"
)

# ─── MAIN WEB WORKSPACE ─────────────────────────────────────────────────────
if image_to_process is None:
    # Beautiful welcome screen when no image is loaded
    st.markdown("""
        <div class="custom-card" style="text-align: center; padding: 50px 20px;">
            <div style="font-size: 80px; margin-bottom: 20px;">🖼️</div>
            <h2 style="margin-top: 0;">Silakan Upload atau Ambil Foto untuk Memulai</h2>
            <p style="color: #8b949e; max-width: 600px; margin: 0 auto 30px auto; font-size: 1.1rem;">
                Gunakan menu di sebelah kiri untuk mengunggah gambar dari komputer Anda atau mengambil foto langsung menggunakan kamera.
            </p>
            <div style="display: flex; justify-content: center; gap: 15px;">
                <span style="background-color: #21262d; border: 1px solid #30363d; padding: 10px 20px; border-radius: 8px; font-weight: 500;">
                    ✓ 5 Image Filters
                </span>
                <span style="background-color: #21262d; border: 1px solid #30363d; padding: 10px 20px; border-radius: 8px; font-weight: 500;">
                    ✓ 3 Special Effects
                </span>
                <span style="background-color: #21262d; border: 1px solid #30363d; padding: 10px 20px; border-radius: 8px; font-weight: 500;">
                    ✓ Before / After Comparison
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    # Apply processing reactively
    processed_image = image_to_process.copy()
    
    # 1. Apply Denoise
    if d_val > 0:
        processed_image = apply_denoise(processed_image, d_val)
        
    # 2. Apply Temperature
    if t_val != 0:
        processed_image = adjust_temperature(processed_image, t_val)
        
    # 3. Apply Brightness
    if b_val != 1.0:
        processed_image = adjust_brightness(processed_image, b_val)
        
    # 4. Apply Contrast
    if c_val != 1.0:
        processed_image = adjust_contrast(processed_image, c_val)
        
    # 5. Apply Saturation
    if s_val != 1.0:
        processed_image = adjust_saturation(processed_image, s_val)
        
    # 6. Apply Special Effects
    if fx_option == "✏️ Sketsa Pensil":
        processed_image = effect_sketch(processed_image)
    elif fx_option == "🌆 Cyberpunk Neon":
        processed_image = effect_neon(processed_image)
    elif fx_option == "📜 Sepia Vintage":
        processed_image = effect_sepia(processed_image)

    # Display Options (Tabs)
    tab1, tab2 = st.tabs(["⚡ Editor & Hasil", "🔍 Bandingkan Sebelum / Sesudah"])
    
    with tab1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        col_main, col_stats = st.columns([3, 1])
        
        with col_main:
            st.image(
                processed_image, 
                caption="Gambar Hasil Edit (Real-time Preview)", 
                use_column_width=True
            )
        
        with col_stats:
            st.markdown("### 📊 Status Gambar")
            st.markdown(f"**Ukuran Asli:** {image_to_process.size[0]} x {image_to_process.size[1]} px")
            st.markdown(f"**Format:** RGB Color Mode")
            
            st.markdown("---")
            st.markdown("### 🛠️ Pengaturan Aktif")
            st.write(f"- Brightness: `{b_val}`")
            st.write(f"- Contrast: `{c_val}`")
            st.write(f"- Saturation: `{s_val}`")
            st.write(f"- Temperature: `{t_val}`")
            st.write(f"- Denoise: `{d_val}`")
            st.write(f"- Effect: `{fx_option}`")
            
            # Conversion for download button
            buf = io.BytesIO()
            processed_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.markdown("---")
            st.download_button(
                label="💾 DOWNLOAD FOTO SEKARANG",
                data=byte_im,
                file_name="foreditor_studio_export.png",
                mime="image/png",
                use_container_width=True
            )
            
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Perbandingan Berdampingan (Side-by-Side)")
        col_before, col_after = st.columns(2)
        
        with col_before:
            st.markdown("#### BEFORE (Gambar Asli)")
            st.image(image_to_process, use_column_width=True)
            
        with col_after:
            st.markdown("#### AFTER (Gambar Hasil Edit)")
            st.image(processed_image, use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ─── FOOTER ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #8b949e; font-size: 0.9rem;'>"
    "ForEditor Studio Web App • Dibuat oleh Fariza, Ocid, & Rasya • "
    "Konsep Portfolio Ready"
    "</p>", 
    unsafe_allow_html=True
)
