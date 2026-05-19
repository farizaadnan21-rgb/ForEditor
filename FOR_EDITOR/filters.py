import cv2
import numpy as np
from PIL import Image, ImageEnhance

# --- HELPER (KONVERSI) ---
def pil_to_cv(pil_image):
    # Mengubah format gambar dari Pillow ke OpenCV
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

def cv_to_pil(cv_image):
    # Mengubah format gambar dari OpenCV kembali ke Pillow
    return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

# --- EFEK SPESIAL (INI YANG SEBELUMNYA HILANG) ---
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
    neon_mask[edges > 0] = [255, 0, 255] # Warna Magenta
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

# --- PENYESUAIAN GAMBAR (SLIDER) ---
def adjust_brightness(pil_image, val):
    return ImageEnhance.Brightness(pil_image).enhance(float(val))

def adjust_contrast(pil_image, val):
    return ImageEnhance.Contrast(pil_image).enhance(float(val))

def adjust_saturation(pil_image, val):
    return ImageEnhance.Color(pil_image).enhance(float(val))

def adjust_temperature(pil_image, val):
    value = int(val)
    if value == 0: return pil_image
    img = pil_to_cv(pil_image)
    b, g, r = cv2.split(img)
    if value > 0: # Hangat (Kuning)
        r = cv2.add(r, value); b = cv2.subtract(b, value)
    else: # Dingin (Biru)
        r = cv2.add(r, value); b = cv2.subtract(b, value)
    return cv_to_pil(cv2.merge((b, g, r)))

def apply_denoise(pil_image, val):
    k = int(val)
    if k == 0: return pil_image
    if k % 2 == 0: k += 1
    img = pil_to_cv(pil_image)
    res = cv2.medianBlur(img, k)
    return cv_to_pil(res)