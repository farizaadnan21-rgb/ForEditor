import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, Scale, HORIZONTAL, Radiobutton, StringVar
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageOps, ImageEnhance
import cv2
import numpy as np
import random 

class JawirPaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jawir Paint — Studio")
        self.root.geometry("1280x850")
        self.root.minsize(960, 640)

        # --- STYLING: palet dark profesional (mini Photoshop ringan) ---
        self._init_theme()
        self.root.configure(bg=self.c["bg_main"])

        # --- VARIABEL ---
        self.default_color = "black"
        self.brush_color = self.default_color
        self.brush_size = 5
        self.brush_type = "round"
        self.is_eraser = False
        self.active_tool = "brush"  # untuk highlight tool aktif di sidebar
        
        self.is_drawing = False
        self.last_x, self.last_y = None, None
        
        # Variabel Filter Live Preview (Slider)
        self.image_cache = None 
        
        # Variabel Toggle Efek Spesial (Anti-Tumpuk)
        self.active_effect_name = None  # Nama efek yang sedang aktif
        self.pre_effect_image = None    # Backup gambar sebelum kena efek
        
        # --- UNDO/REDO ---
        self.history = []      
        self.redo_stack = []   
        self.max_history = 20  
        
        # --- KANVAS ---
        self.canvas_w, self.canvas_h = 900, 750
        
        # 1. Backend (PIL)
        self.image = Image.new("RGB", (self.canvas_w, self.canvas_h), "white")
        self.draw = ImageDraw.Draw(self.image)
        
        # --- LAYOUT: grid responsif (sidebar | workspace + status bar) ---
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.sidebar = tk.Frame(self.root, bg=self.c["bg_sidebar"], width=300)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.workspace = tk.Frame(self.root, bg=self.c["bg_main"])
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=0)
        self.workspace.grid_rowconfigure(0, weight=1)
        self.workspace.grid_columnconfigure(0, weight=1)

        # Bingkai fokus di sekitar canvas (area kerja terpusat saat resize)
        self.canvas_outer = tk.Frame(
            self.workspace, bg=self.c["canvas_border"], padx=2, pady=2
        )
        self.canvas_outer.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)

        self.canvas_inner = tk.Frame(self.canvas_outer, bg=self.c["canvas_shadow"], padx=1, pady=1)
        self.canvas_inner.pack(expand=True)

        # 2. Frontend (Tkinter) — ukuran gambar tetap; hanya layout yang menyesuaikan
        self.canvas = tk.Canvas(
            self.canvas_inner,
            width=self.canvas_w,
            height=self.canvas_h,
            bg="white",
            cursor="cross",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()
        
        # Binding Mouse & Keyboard
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_brush)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.root.bind('<Control-z>', self.undo_shortcut)
        self.root.bind('<Control-y>', self.redo_shortcut)
        self.root.bind("<Configure>", self._on_root_configure)

        self.status_var = tk.StringVar(value="Siap — Ctrl+Z Undo · Ctrl+Y Redo")
        self.status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg=self.c["bg_status"],
            fg=self.c["text_muted"],
            font=self.font_small,
            anchor="w",
            padx=14,
            pady=6,
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.setup_ui()
        self._center_canvas()
        self.update_canvas()

    # ==========================
    # STYLING & UI HELPERS (tampilan saja, tidak mengubah logika gambar)
    # ==========================
    def _init_theme(self):
        """Palet warna & font — satu tempat agar konsisten di seluruh UI."""
        self.c = {
            "bg_main": "#14161c",
            "bg_sidebar": "#1c1f26",
            "bg_card": "#252930",
            "bg_card_alt": "#2a2f38",
            "bg_hover": "#323842",
            "bg_active": "#3d6df0",
            "bg_active_dim": "#2f5299",
            "bg_btn": "#2e333d",
            "bg_btn_danger": "#4a2c2c",
            "bg_btn_danger_active": "#c0392b",
            "bg_slider": "#1e2229",
            "bg_status": "#111318",
            "canvas_border": "#0d0e12",
            "canvas_shadow": "#000000",
            "text": "#e8eaed",
            "text_muted": "#8b929a",
            "text_accent": "#6ea8fe",
            "border": "#3a4049",
            "accent": "#4a8cff",
        }
        self.font_title = ("Segoe UI", 18, "bold")
        self.font_section = ("Segoe UI", 9, "bold")
        self.font_body = ("Segoe UI", 10)
        self.font_small = ("Segoe UI", 9)
        self._tool_buttons = {}
        self._effect_buttons = {}

    def _configure_ttk(self, parent):
        """ttk Scale/Radiobutton agar selaras dengan tema gelap."""
        style = ttk.Style(parent)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Dark.TRadiobutton",
            background=self.c["bg_card"],
            foreground=self.c["text"],
            font=self.font_small,
            indicatorcolor=self.c["accent"],
        )
        style.map(
            "Dark.TRadiobutton",
            background=[("active", self.c["bg_card"])],
            foreground=[("active", self.c["text_accent"])],
        )

    def _update_status(self, msg):
        self.status_var.set(msg)

    def _make_card(self, parent, title, icon=""):
        """Panel kartu untuk mengelompokkan kontrol di sidebar."""
        outer = tk.Frame(parent, bg=self.c["bg_sidebar"])
        outer.pack(fill="x", padx=12, pady=(0, 10))
        card = tk.Frame(outer, bg=self.c["bg_card"], highlightbackground=self.c["border"], highlightthickness=1)
        card.pack(fill="x")
        header = tk.Frame(card, bg=self.c["bg_card"])
        header.pack(fill="x", padx=12, pady=(10, 6))
        lbl = icon + " " + title if icon else title
        tk.Label(
            header, text=lbl.strip(), bg=self.c["bg_card"],
            fg=self.c["text"], font=self.font_section, anchor="w",
        ).pack(side="left")
        body = tk.Frame(card, bg=self.c["bg_card"])
        body.pack(fill="x", padx=12, pady=(0, 12))
        return body

    def _make_btn(self, parent, text, command, variant="default", tool_key=None, full_width=False):
        """Tombol custom dengan hover; tool_key dipakai untuk highlight tool aktif."""
        palettes = {
            "default": (self.c["bg_btn"], self.c["bg_hover"]),
            "primary": (self.c["accent"], "#5c9bff"),
            "danger": (self.c["bg_btn_danger"], self.c["bg_btn_danger_active"]),
            "ghost": (self.c["bg_card_alt"], self.c["bg_hover"]),
        }
        normal_bg, hover_bg = palettes.get(variant, palettes["default"])
        btn = tk.Button(
            parent, text=text, command=command,
            bg=normal_bg, fg=self.c["text"], activebackground=hover_bg,
            activeforeground=self.c["text"], font=self.font_body,
            relief="flat", bd=0, padx=10, pady=8, cursor="hand2",
            highlightthickness=0,
        )
        if full_width:
            btn.pack(fill="x", pady=3)
        btn._jp_normal_bg = normal_bg
        btn._jp_hover_bg = hover_bg
        btn._jp_variant = variant
        btn._jp_tool_key = tool_key

        def on_enter(_e):
            if not getattr(btn, "_jp_active", False):
                btn.config(bg=hover_bg)
        def on_leave(_e):
            if getattr(btn, "_jp_active", False):
                btn.config(bg=self.c["bg_active"])
            else:
                btn.config(bg=normal_bg)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        if tool_key:
            self._tool_buttons[tool_key] = btn
        return btn

    def _set_active_tool(self, tool_key):
        """Highlight tool yang sedang dipakai (brush / eraser)."""
        self.active_tool = tool_key
        for key, btn in self._tool_buttons.items():
            active = key == tool_key
            btn._jp_active = active
            if active:
                btn.config(bg=self.c["bg_active"], fg="#ffffff")
            else:
                normal = btn._jp_normal_bg
                btn.config(bg=normal, fg=self.c["text"])
        if tool_key == "eraser":
            self._update_status("Mode: Penghapus")
        else:
            self._update_status(f"Mode: Kuas ({self.brush_var.get()}) · {self.brush_color}")

    def _center_canvas(self):
        """Pusatkan canvas di workspace saat jendela di-resize."""
        self.workspace.update_idletasks()
        ow = self.canvas_outer.winfo_width()
        oh = self.canvas_outer.winfo_height()
        if ow < 10 or oh < 10:
            return
        # canvas_inner tetap di tengah area kerja
        self.canvas_inner.pack_forget()
        self.canvas_inner.pack(expand=True)

    def _on_root_configure(self, event):
        if event.widget == self.root:
            self._center_canvas()

    def _slider_parent_bg(self):
        return self.c["bg_slider"]

    def setup_ui(self):
        panel = self.sidebar
        self._configure_ttk(panel)

        # --- Header branding ---
        header = tk.Frame(panel, bg=self.c["bg_sidebar"])
        header.pack(fill="x", padx=14, pady=(16, 8))
        tk.Label(
            header, text="🖌️ JAWIR PAINT", bg=self.c["bg_sidebar"],
            font=self.font_title, fg=self.c["text"],
        ).pack(anchor="w")
        tk.Label(
            header, text="Mini studio · portfolio ready", bg=self.c["bg_sidebar"],
            font=self.font_small, fg=self.c["text_muted"],
        ).pack(anchor="w", pady=(2, 0))

        # Scroll area sidebar (rapi saat banyak filter)
        scroll_wrap = tk.Frame(panel, bg=self.c["bg_sidebar"])
        scroll_wrap.pack(fill="both", expand=True, padx=0, pady=0)
        self._sidebar_canvas = tk.Canvas(
            scroll_wrap, bg=self.c["bg_sidebar"], highlightthickness=0, width=288,
        )
        sb = ttk.Scrollbar(scroll_wrap, orient="vertical", command=self._sidebar_canvas.yview)
        self._sidebar_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._sidebar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        panel_inner = tk.Frame(self._sidebar_canvas, bg=self.c["bg_sidebar"])
        self._sidebar_win = self._sidebar_canvas.create_window((0, 0), window=panel_inner, anchor="nw")

        def _sync_scroll_region(_e=None):
            self._sidebar_canvas.configure(scrollregion=self._sidebar_canvas.bbox("all"))
            self._sidebar_canvas.itemconfig(self._sidebar_win, width=self._sidebar_canvas.winfo_width())
        panel_inner.bind("<Configure>", _sync_scroll_region)
        self._sidebar_canvas.bind("<Configure>", _sync_scroll_region)

        def _on_mousewheel(event):
            # Linux: Button-4/5 · Windows/macOS: MouseWheel + delta
            if getattr(event, "num", None) == 5:
                self._sidebar_canvas.yview_scroll(1, "units")
            elif getattr(event, "num", None) == 4:
                self._sidebar_canvas.yview_scroll(-1, "units")
            else:
                d = getattr(event, "delta", 0)
                if d > 0:
                    self._sidebar_canvas.yview_scroll(-1, "units")
                elif d < 0:
                    self._sidebar_canvas.yview_scroll(1, "units")
        for w in (panel, scroll_wrap, self._sidebar_canvas, panel_inner):
            w.bind("<MouseWheel>", _on_mousewheel)
            w.bind("<Button-4>", _on_mousewheel)
            w.bind("<Button-5>", _on_mousewheel)

        # --- CARD: Alat Gambar ---
        frame_tools = self._make_card(panel_inner, "Alat Gambar", "🛠️")

        row_color = tk.Frame(frame_tools, bg=self.c["bg_card"])
        row_color.pack(fill="x", pady=(0, 6))
        self.color_swatch = tk.Canvas(
            row_color, width=28, height=28, bg=self.default_color,
            highlightbackground=self.c["border"], highlightthickness=1, cursor="hand2",
        )
        self.color_swatch.pack(side=tk.LEFT, padx=(0, 8))
        self.color_swatch.bind("<Button-1>", lambda _e: self.choose_color())

        btn_row = tk.Frame(row_color, bg=self.c["bg_card"])
        btn_row.pack(side=tk.LEFT, fill="x", expand=True)
        self._make_btn(btn_row, "🎨 Warna", self.choose_color, variant="primary", tool_key="brush").pack(
            side=tk.LEFT, fill="x", expand=True, padx=(0, 4)
        )
        self._make_btn(btn_row, "🧹 Reset", self.clear_canvas, variant="ghost").pack(
            side=tk.LEFT, fill="x", expand=True
        )

        self.btn_eraser = self._make_btn(
            frame_tools, "🧽 Penghapus", self.activate_eraser,
            variant="danger", tool_key="eraser", full_width=True,
        )

        tk.Label(
            frame_tools, text="Bentuk kuas", bg=self.c["bg_card"],
            fg=self.c["text_muted"], font=self.font_small,
        ).pack(anchor="w", pady=(8, 4))

        self.brush_var = StringVar(value="round")
        f_style = tk.Frame(frame_tools, bg=self.c["bg_card"])
        f_style.pack(fill="x")
        for val, label in [("round", "● Bulat"), ("flat", "■ Kotak"), ("spray", "✦ Spray")]:
            ttk.Radiobutton(
                f_style, text=label, variable=self.brush_var, value=val,
                style="Dark.TRadiobutton", command=self.change_brush_type,
            ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(
            frame_tools, text="Ukuran kuas", bg=self.c["bg_card"],
            fg=self.c["text_muted"], font=self.font_small,
        ).pack(anchor="w", pady=(10, 4))
        self.slider = Scale(
            frame_tools, from_=1, to=50, orient=HORIZONTAL,
            bg=self.c["bg_card"], fg=self.c["text"], troughcolor=self.c["bg_slider"],
            highlightthickness=0, sliderrelief="flat", activebackground=self.c["accent"],
            command=lambda v: self._update_status(f"Ukuran kuas: {int(float(v))}"),
        )
        self.slider.set(5)
        self.slider.pack(fill="x")

        # --- CONTAINER FILTER (accordion di dalam card) ---
        self.pcd_container = self._make_card(panel_inner, "Penyesuaian Gambar", "🎛️")

        self.create_accordion_item("☀️ Kecerahan", self.setup_brightness_slider)
        self.create_accordion_item("🌓 Kontras", self.setup_contrast_slider)
        self.create_accordion_item("🎨 Saturasi", self.setup_saturation_slider)
        self.create_accordion_item("🌡️ Temperatur (Biru/Kuning)", self.setup_temperature_slider)
        self.create_accordion_item("✨ Hilangkan Noise", self.setup_denoise_slider)

        fx_body = self._make_card(panel_inner, "Efek Spesial", "✨")
        tk.Label(
            fx_body, text="Klik 2× pada efek aktif untuk menonaktifkan",
            bg=self.c["bg_card"], fg=self.c["text_muted"], font=self.font_small, wraplength=240,
        ).pack(anchor="w", pady=(0, 8))

        self.create_special_effect_btn("✏️ Sketsa Pensil", "sketch", self.effect_sketch, parent=fx_body)
        self.create_special_effect_btn("🌆 Cyberpunk Neon", "neon", self.effect_neon, parent=fx_body)
        self.create_special_effect_btn("📜 Sepia Vintage", "sepia", self.effect_sepia, parent=fx_body)

        # --- FILE OPS (dock bawah sidebar, di luar scroll) ---
        f_file = tk.Frame(panel, bg=self.c["bg_sidebar"])
        f_file.pack(side=tk.BOTTOM, fill="x", padx=12, pady=(8, 12))
        sep = tk.Frame(f_file, bg=self.c["border"], height=1)
        sep.pack(fill="x", pady=(0, 10))
        grid_file = tk.Frame(f_file, bg=self.c["bg_sidebar"])
        grid_file.pack(fill="x")
        for col, (txt, cmd, var) in enumerate([
            ("📂 Load", self.load_image, "ghost"),
            ("💾 Save", self.save_image, "primary"),
            ("↩ Undo", self.undo, "ghost"),
            ("↪ Redo", self.redo, "ghost"),
        ]):
            b = self._make_btn(grid_file, txt, cmd, variant=var)
            b.grid(row=0, column=col, sticky="ew", padx=3)
            grid_file.grid_columnconfigure(col, weight=1)

        self._set_active_tool("brush")

    # =========================================
    # LOGIKA BARU: TOGGLE EFEK SPESIAL
    # =========================================
    
    def create_special_effect_btn(self, text, name, func, parent=None):
        """Membuat tombol efek yang bisa di-toggle on/off"""
        container = parent if parent is not None else self.pcd_container
        btn = self._make_btn(
            container, text,
            lambda: self.toggle_special_effect(name, func),
            variant="ghost", full_width=True,
        )
        btn.config(anchor="w")
        self._effect_buttons[name] = btn

    def toggle_special_effect(self, name, func):
        self.close_all_sliders() # Tutup slider jika ada yang buka
        
        # 1. JIKA KLIK EFEK YANG SAMA -> NONAKTIFKAN (RESET)
        if self.active_effect_name == name:
            if self.pre_effect_image:
                self.image = self.pre_effect_image.copy() # Balikin gambar
                self.draw = ImageDraw.Draw(self.image)
                self.update_canvas()
            
            # Reset Status
            self.active_effect_name = None
            self.pre_effect_image = None
            self._highlight_effect_btn(None)
            self._update_status(f"Efek {name} dinonaktifkan")
            messagebox.showinfo("Info", f"Efek {name} dinonaktifkan.")
            return

        # 2. JIKA GANTI EFEK (ATAU BARU PERTAMA KALI)
        
        # Kalau sebelumnya sudah ada efek lain, reset dulu ke gambar bersih
        if self.active_effect_name is not None:
            self.image = self.pre_effect_image.copy()
        else:
            # Kalau ini efek pertama, simpan gambar asli sebagai backup
            self.pre_effect_image = self.image.copy()
            # Simpan state ke History Undo (supaya Undo Ctrl+Z tetap jalan normal)
            self.save_state()

        # Terapkan Efek Baru
        func() 
        self.active_effect_name = name # Tandai efek ini aktif
        self._highlight_effect_btn(name)
        self._update_status(f"Efek aktif: {name}")

    # =========================================
    # FUNGSI EFEK SPESIAL (IMPLEMENTASI)
    # =========================================
    def effect_sketch(self):
        img = self.pil_to_cv()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv = cv2.bitwise_not(gray)
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        self.cv_to_pil(cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR))

    def effect_neon(self):
        img = self.pil_to_cv()
        edges = cv2.Canny(img, 100, 200)
        edges = cv2.dilate(edges, None)
        neon_mask = np.zeros_like(img)
        neon_mask[edges > 0] = [255, 0, 255] # Magenta Neon
        dark_img = (img * 0.3).astype(np.uint8)
        self.cv_to_pil(cv2.add(dark_img, neon_mask))

    def effect_sepia(self):
        img = self.pil_to_cv()
        kernel = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
        sepia = cv2.transform(img, kernel)
        noise = np.random.normal(0, 15, sepia.shape).astype(np.uint8)
        self.cv_to_pil(cv2.add(sepia, noise))

    # ==========================
    # LOGIKA UI SLIDER (ACCORDION)
    # ==========================
    def _highlight_effect_btn(self, name):
        """Highlight tombol efek spesial yang sedang aktif."""
        for key, btn in self._effect_buttons.items():
            active = key == name
            btn._jp_active = active
            if active:
                btn.config(bg=self.c["bg_active"], fg="#ffffff")
            else:
                btn.config(bg=btn._jp_normal_bg, fg=self.c["text"])

    def create_accordion_item(self, text, setup_func):
        frame = tk.Frame(self.pcd_container, bg=self.c["bg_card"])
        frame.pack(fill="x", pady=2)
        btn = self._make_btn(
            frame, text,
            lambda: self.toggle_slider(frame, setup_func),
            variant="ghost", full_width=True,
        )
        btn.config(anchor="w")
        frame.accordion_btn = btn
        slider_area = tk.Frame(frame, bg=self._slider_parent_bg())
        frame.slider_area = slider_area
        frame.setup_func = setup_func
        frame.is_open = False

    def toggle_slider(self, frame, setup_func):
        # Jika user buka slider, kita anggap dia "Commit" efek spesial sebelumnya (jika ada)
        if self.active_effect_name:
            self.active_effect_name = None
            self.pre_effect_image = None
        
        if frame.is_open:
            self.close_all_sliders()
            return
        
        self.close_all_sliders()
        self.save_state() 
        self.image_cache = self.image.copy() 
        setup_func(frame.slider_area)
        frame.slider_area.pack(fill="x", pady=2, padx=4) 
        frame.is_open = True
        if hasattr(frame, "accordion_btn"):
            frame.accordion_btn._jp_active = True
            frame.accordion_btn.config(bg=self.c["bg_active"], fg="#ffffff")
            self._update_status(f"Panel: {frame.accordion_btn.cget('text')}")

    def close_all_sliders(self):
        self.image_cache = None 
        for child in self.pcd_container.winfo_children():
            if isinstance(child, tk.Frame) and hasattr(child, 'slider_area'):
                for w in child.slider_area.winfo_children(): w.destroy()
                child.slider_area.pack_forget() 
                child.is_open = False
                if hasattr(child, "accordion_btn"):
                    child.accordion_btn._jp_active = False
                    child.accordion_btn.config(
                        bg=child.accordion_btn._jp_normal_bg, fg=self.c["text"]
                    )

    # ==========================
    # LOGIKA FILTER BARU (TEMPERATUR & LAINNYA)
    # ==========================
    
    # --- TEMPERATUR (BIRU <-> KUNING) ---
    def setup_temperature_slider(self, parent):
        sb = self._slider_parent_bg()
        tk.Label(parent, text="Dingin (Biru) <---> Hangat (Kuning)", bg=sb, fg=self.c["text_muted"], font=self.font_small).pack(anchor="w", padx=5)
        # Range -100 (Sangat Biru) sampai +100 (Sangat Kuning)
        s = Scale(parent, from_=-100, to=100, orient=HORIZONTAL, command=self.live_temperature,
                  bg=sb, fg=self.c["text"], troughcolor=self.c["bg_card"], highlightthickness=0)
        s.set(0)
        s.pack(fill="x", padx=5, pady=5)

    def live_temperature(self, val):
        value = int(val)
        if value == 0:
            if self.image_cache:
                self.image = self.image_cache.copy()
                self.draw = ImageDraw.Draw(self.image)
                self.update_canvas()
            return

        if self.image_cache:
            # Kita pakai OpenCV untuk manipulasi channel B (Blue) dan R (Red)
            img = cv2.cvtColor(np.array(self.image_cache), cv2.COLOR_RGB2BGR)
            b, g, r = cv2.split(img)

            if value > 0: # Hangat (Kuning/Merah naik, Biru turun)
                r = cv2.add(r, value)
                b = cv2.subtract(b, value)
            else: # Dingin (Biru naik, Merah turun)
                r = cv2.add(r, value) # Value negatif, jadi otomatis berkurang
                b = cv2.subtract(b, value) # Subtract negatif = bertambah

            merged = cv2.merge((b, g, r))
            self.cv_to_pil(merged)

    # --- KECERAHAN ---
    def setup_brightness_slider(self, parent):
        sb = self._slider_parent_bg()
        tk.Label(parent, text="Intensitas (0.0 - 2.0):", bg=sb, fg=self.c["text_muted"], font=self.font_small).pack(anchor="w", padx=5)
        s = Scale(parent, from_=0.0, to=2.0, resolution=0.1, orient=HORIZONTAL, command=self.live_brightness,
                  bg=sb, fg=self.c["text"], troughcolor=self.c["bg_card"], highlightthickness=0)
        s.set(1.0)
        s.pack(fill="x", padx=5, pady=5)

    def live_brightness(self, val):
        if self.image_cache:
            enhancer = ImageEnhance.Brightness(self.image_cache)
            self.image = enhancer.enhance(float(val))
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas()

    # --- KONTRAS ---
    def setup_contrast_slider(self, parent):
        sb = self._slider_parent_bg()
        tk.Label(parent, text="Intensitas (0.0 - 2.0):", bg=sb, fg=self.c["text_muted"], font=self.font_small).pack(anchor="w", padx=5)
        s = Scale(parent, from_=0.0, to=2.0, resolution=0.1, orient=HORIZONTAL, command=self.live_contrast,
                  bg=sb, fg=self.c["text"], troughcolor=self.c["bg_card"], highlightthickness=0)
        s.set(1.0)
        s.pack(fill="x", padx=5, pady=5)

    def live_contrast(self, val):
        if self.image_cache:
            enhancer = ImageEnhance.Contrast(self.image_cache)
            self.image = enhancer.enhance(float(val))
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas()

    # --- SATURASI ---
    def setup_saturation_slider(self, parent):
        sb = self._slider_parent_bg()
        tk.Label(parent, text="Warna (0.0 = BW, 2.0 = Tajam):", bg=sb, fg=self.c["text_muted"], font=self.font_small).pack(anchor="w", padx=5)
        s = Scale(parent, from_=0.0, to=3.0, resolution=0.1, orient=HORIZONTAL, command=self.live_saturation,
                  bg=sb, fg=self.c["text"], troughcolor=self.c["bg_card"], highlightthickness=0)
        s.set(1.0)
        s.pack(fill="x", padx=5, pady=5)

    def live_saturation(self, val):
        if self.image_cache:
            enhancer = ImageEnhance.Color(self.image_cache)
            self.image = enhancer.enhance(float(val))
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas()

    # --- DENOISE ---
    def setup_denoise_slider(self, parent):
        sb = self._slider_parent_bg()
        tk.Label(parent, text="Kekuatan:", bg=sb, fg=self.c["text_muted"], font=self.font_small).pack(anchor="w", padx=5)
        s = Scale(parent, from_=0, to=20, orient=HORIZONTAL, command=self.live_denoise,
                  bg=sb, fg=self.c["text"], troughcolor=self.c["bg_card"], highlightthickness=0)
        s.set(0)
        s.pack(fill="x", padx=5, pady=5)

    def live_denoise(self, val):
        k = int(val)
        if k == 0: 
            self.image = self.image_cache.copy(); self.draw = ImageDraw.Draw(self.image); self.update_canvas(); return
        if k % 2 == 0: k += 1 
        if self.image_cache:
            cv_img = cv2.cvtColor(np.array(self.image_cache), cv2.COLOR_RGB2BGR)
            res = cv2.medianBlur(cv_img, k)
            self.cv_to_pil(res)

    # --- SYSTEM & UTILS ---
    def pil_to_cv(self): return cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)
    def cv_to_pil(self, cv_img): self.image = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)); self.draw = ImageDraw.Draw(self.image); self.update_canvas()
    
    def activate_eraser(self): 
        # Jika lagi mode efek, matikan dulu
        if self.active_effect_name: self.active_effect_name = None; self.pre_effect_image = None
        self.is_eraser = True; self.brush_color = "white"; self.brush_type = "round"
        self._set_active_tool("eraser")
    
    def change_brush_type(self):
        self.is_eraser = False
        self.brush_type = self.brush_var.get()
        self.brush_color = self.default_color
        self._set_active_tool("brush")

    def choose_color(self): 
        c = colorchooser.askcolor()[1]
        if c:
            self.default_color = c
            self.brush_color = c
            self.is_eraser = False
            self.color_swatch.config(bg=c)
            self._set_active_tool("brush")
    
    def start_draw(self, event): 
        # Jika menggambar, efek spesial dianggap 'apply' permanen (tidak bisa di-toggle off lagi lewat tombol)
        if self.active_effect_name:
            self.active_effect_name = None
            self.pre_effect_image = None
            self._highlight_effect_btn(None)
        self.is_drawing = True; self.last_x, self.last_y = event.x, event.y; self.save_state()

    def draw_brush(self, event):
        if self.is_drawing:
            x, y = event.x, event.y; r = self.slider.get()
            if self.brush_type == "spray":
                for _ in range(int(r*2)):
                    rx, ry = x + random.randint(-r, r), y + random.randint(-r, r)
                    self.canvas.create_oval(rx, ry, rx+1, ry+1, fill=self.brush_color, outline=self.brush_color)
                    self.draw.point((rx, ry), fill=self.brush_color)
            elif self.brush_type == "flat":
                self.canvas.create_line(self.last_x, self.last_y, x, y, fill=self.brush_color, width=r*2, capstyle=tk.PROJECTING)
                self.draw.line([self.last_x, self.last_y, x, y], fill=self.brush_color, width=r*2)
            else:
                self.canvas.create_line(self.last_x, self.last_y, x, y, fill=self.brush_color, width=r*2, capstyle=tk.ROUND, smooth=True)
                self.draw.line([self.last_x, self.last_y, x, y], fill=self.brush_color, width=r*2, joint="curve")
            self.last_x, self.last_y = x, y
    def stop_draw(self, event): self.is_drawing = False; self.update_canvas()
    def update_canvas(self): self.tk_image = ImageTk.PhotoImage(self.image); self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")
    
    def save_state(self):
        self.history.append(self.image.copy())
        self.redo_stack.clear()
        if len(self.history) > self.max_history: 
            self.history.pop(0)

    def undo(self): 
        self.active_effect_name = None # Reset toggle status jika undo
        self._highlight_effect_btn(None)
        if self.history:
            self.redo_stack.append(self.image.copy())
            self.image = self.history.pop()
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas()
            self._update_status("Undo")
    def redo(self):
        if self.redo_stack:
            self.history.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas()
            self._update_status("Redo")
    def undo_shortcut(self, event): self.undo()
    def redo_shortcut(self, event): self.redo()
    def clear_canvas(self):
        self.save_state()
        self.image = Image.new("RGB", (self.canvas_w, self.canvas_h), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.update_canvas()
        self._update_status("Kanvas direset")

    def load_image(self):
        p = filedialog.askopenfilename()
        if p:
            self.save_state()
            img = Image.open(p).convert("RGB")
            self.image = img.resize((self.canvas_w, self.canvas_h))
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas()
            self._update_status(f"Dimuat: {p.split('/')[-1]}")

    def save_image(self):
        p = filedialog.asksaveasfilename(defaultextension=".png")
        if p:
            self.image.save(p)
            self._update_status(f"Tersimpan: {p.split('/')[-1]}")
            messagebox.showinfo("Saved", "Gambar berhasil disimpan!")

if __name__ == "__main__":
    root = tk.Tk()
    app = JawirPaintApp(root)
    root.mainloop()