import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, Scale, HORIZONTAL, Radiobutton, StringVar
from PIL import Image, ImageTk, ImageDraw

import filters
import tools

class PFOREditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FOR Photo Editor (Fariza, Ocid, Rasya)") 
        
        # --- PERBAIKAN UKURAN WINDOW ---
        # Mengubah tinggi dari 850 menjadi 700 agar tombol bawah tidak hilang di laptop
        self.root.geometry("1200x700") 
        self.root.configure(bg="#2c3e50")

        # VARIABEL
        self.default_color = "black"
        self.brush_color = self.default_color
        self.brush_size = 5
        self.brush_type = "round"
        self.is_eraser = False
        self.is_drawing = False
        self.last_x, self.last_y = None, None
        self.image_cache = None 
        self.active_effect_name = None  
        self.pre_effect_image = None    
        self.history = []      
        self.redo_stack = []   
        self.max_history = 20  
        
        # KANVAS
        self.canvas_w, self.canvas_h = 850, 650 # Disesuaikan sedikit
        self.image = Image.new("RGB", (self.canvas_w, self.canvas_h), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.canvas = tk.Canvas(root, width=self.canvas_w, height=self.canvas_h, bg="white", cursor="cross")
        self.canvas.place(x=340, y=20) 
        
        # BINDING
        self.canvas.bind("<Button-1>", lambda e: tools.start_draw(self, e))
        self.canvas.bind("<B1-Motion>", lambda e: tools.draw_brush(self, e))
        self.canvas.bind("<ButtonRelease-1>", lambda e: tools.stop_draw(self, e))
        self.root.bind('<Control-z>', self.undo_shortcut)
        self.root.bind('<Control-y>', self.redo_shortcut)
        
        self.setup_ui()

    def setup_ui(self):
        panel = tk.Frame(self.root, bg="#ecf0f1", width=320, height=850)
        panel.place(x=0, y=0)
        
        # HEADER
        tk.Label(panel, text="FOR EDITOR", bg="#ecf0f1", font=("Segoe UI", 24, "bold"), fg="#2c3e50").pack(pady=(15, 5))
        tk.Label(panel, text="By: Fariza, Ocid, Rasya", bg="#ecf0f1", font=("Segoe UI", 9, "italic"), fg="#7f8c8d").pack(pady=(0, 15))
        
        # TOOLS
        frame_tools = tk.LabelFrame(panel, text="Drawing Tools", bg="#ecf0f1", font=("Arial", 10, "bold"))
        frame_tools.pack(fill="x", padx=10, pady=5)
        
        btn_frame = tk.Frame(frame_tools, bg="#ecf0f1")
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="🎨 Color", command=self.choose_color, width=10, bg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🧹 Clear", command=lambda: tools.clear_canvas(self), width=10, bg="white").pack(side=tk.LEFT, padx=5)
        self.btn_eraser = tk.Button(frame_tools, text="🧽 ERASER", command=self.activate_eraser, bg="#ffcccc")
        self.btn_eraser.pack(fill="x", padx=10, pady=5)
        
        self.brush_var = StringVar(value="round")
        f_style = tk.Frame(frame_tools, bg="#ecf0f1")
        f_style.pack(fill="x", padx=5)
        Radiobutton(f_style, text="Round", variable=self.brush_var, value="round", bg="#ecf0f1", command=self.change_brush_type).pack(side=tk.LEFT)
        Radiobutton(f_style, text="Flat", variable=self.brush_var, value="flat", bg="#ecf0f1", command=self.change_brush_type).pack(side=tk.LEFT)
        Radiobutton(f_style, text="Spray", variable=self.brush_var, value="spray", bg="#ecf0f1", command=self.change_brush_type).pack(side=tk.LEFT)
        self.slider = Scale(frame_tools, from_=1, to=50, orient=HORIZONTAL, bg="#ecf0f1")
        self.slider.set(5)
        self.slider.pack(fill="x", padx=10, pady=5)

        # FILTER
        self.pcd_container = tk.Frame(panel, bg="#ecf0f1")
        self.pcd_container.pack(fill="x", padx=10, pady=5)

        tk.Label(self.pcd_container, text="Image Adjustments", bg="#ecf0f1", font=("Arial", 9, "bold")).pack(pady=(10,5), anchor="w")
        self.create_accordion_item("☀️ Brightness", self.setup_brightness_slider)
        self.create_accordion_item("🌓 Contrast", self.setup_contrast_slider)
        self.create_accordion_item("🎨 Saturation", self.setup_saturation_slider)
        self.create_accordion_item("🌡️ Temperature", self.setup_temperature_slider)
        self.create_accordion_item("✨ Denoise", self.setup_denoise_slider)

        tk.Label(self.pcd_container, text="Special Effects (Toggle)", bg="#ecf0f1", fg="#d35400", font=("Arial", 9, "bold")).pack(pady=(10,5), anchor="w")
        self.create_special_effect_btn("✏️ Pencil Sketch", "sketch", filters.effect_sketch)
        self.create_special_effect_btn("🌆 Cyberpunk Neon", "neon", filters.effect_neon)
        self.create_special_effect_btn("📜 Vintage Sepia", "sepia", filters.effect_sepia)

        # --- FOOTER (KAMERA + FILE OPS) ---
        # Kita gunakan container khusus yang menempel di bawah
        f_footer = tk.Frame(panel, bg="#ecf0f1")
        f_footer.pack(side=tk.BOTTOM, fill="x", padx=10, pady=10)

        # 1. TOMBOL LOAD/SAVE/UNDO (Paling Bawah)
        f_actions = tk.Frame(f_footer, bg="#ecf0f1")
        f_actions.pack(side=tk.BOTTOM, fill="x")
        
        tk.Button(f_actions, text="Load", command=self.load_image, width=6).pack(side=tk.LEFT, padx=1)
        tk.Button(f_actions, text="Save", command=self.save_image, width=6).pack(side=tk.LEFT, padx=1)
        tk.Button(f_actions, text="Undo", command=self.undo, width=6, bg="yellow").pack(side=tk.LEFT, padx=1)
        tk.Button(f_actions, text="Redo", command=self.redo, width=6, bg="lightgreen").pack(side=tk.LEFT, padx=1)

        # 2. TOMBOL KAMERA (Di atas tombol Load/Save)
        tk.Button(f_footer, text="📷 CAMERA", command=lambda: tools.open_camera(self), 
                  bg="#3498db", fg="white", font=("Arial", 11, "bold")).pack(side=tk.BOTTOM, fill="x", pady=(0, 5))

    # --- LOGIKA UI (HELPER) ---
    def create_special_effect_btn(self, text, name, func):
        btn = tk.Button(self.pcd_container, text=text, command=lambda: self.toggle_special_effect(name, func), bg="white", anchor="w", padx=10)
        btn.pack(fill="x", pady=2)

    def toggle_special_effect(self, name, func):
        self.close_all_sliders()
        if self.active_effect_name == name:
            if self.pre_effect_image:
                self.image = self.pre_effect_image.copy()
                self.draw = ImageDraw.Draw(self.image)
                self.update_canvas()
            self.active_effect_name = None; self.pre_effect_image = None
            messagebox.showinfo("Info", f"Effect {name} OFF.")
            return
        if self.active_effect_name is not None:
            self.image = self.pre_effect_image.copy()
        else:
            self.pre_effect_image = self.image.copy()
            self.save_state()
        self.image = func(self.image)
        self.draw = ImageDraw.Draw(self.image)
        self.update_canvas()
        self.active_effect_name = name

    def create_accordion_item(self, text, setup_func):
        frame = tk.Frame(self.pcd_container, bg="#ecf0f1")
        frame.pack(fill="x", pady=2)
        btn = tk.Button(frame, text=text, bg="white", anchor="w", padx=10)
        btn.config(command=lambda: self.toggle_slider(frame, setup_func))
        btn.pack(fill="x")
        slider_area = tk.Frame(frame, bg="#dfe6e9")
        frame.slider_area = slider_area
        frame.is_open = False

    def toggle_slider(self, frame, setup_func):
        if self.active_effect_name: self.active_effect_name = None; self.pre_effect_image = None
        if frame.is_open: self.close_all_sliders(); return
        self.close_all_sliders()
        self.save_state()
        self.image_cache = self.image.copy()
        setup_func(frame.slider_area)
        frame.slider_area.pack(fill="x", pady=2)
        frame.is_open = True

    def close_all_sliders(self):
        self.image_cache = None
        for child in self.pcd_container.winfo_children():
            if isinstance(child, tk.Frame) and hasattr(child, 'slider_area'):
                for w in child.slider_area.winfo_children(): w.destroy()
                child.slider_area.pack_forget()
                child.is_open = False

    def setup_brightness_slider(self, p):
        s = Scale(p, from_=0.0, to=2.0, resolution=0.1, orient=HORIZONTAL, command=self.live_brightness); s.set(1.0); s.pack(fill="x", padx=5)
    def live_brightness(self, val):
        if self.image_cache: self.image = filters.adjust_brightness(self.image_cache, val); self.draw = ImageDraw.Draw(self.image); self.update_canvas()
    def setup_contrast_slider(self, p):
        s = Scale(p, from_=0.0, to=2.0, resolution=0.1, orient=HORIZONTAL, command=self.live_contrast); s.set(1.0); s.pack(fill="x", padx=5)
    def live_contrast(self, val):
        if self.image_cache: self.image = filters.adjust_contrast(self.image_cache, val); self.draw = ImageDraw.Draw(self.image); self.update_canvas()
    def setup_saturation_slider(self, p):
        s = Scale(p, from_=0.0, to=3.0, resolution=0.1, orient=HORIZONTAL, command=self.live_saturation); s.set(1.0); s.pack(fill="x", padx=5)
    def live_saturation(self, val):
        if self.image_cache: self.image = filters.adjust_saturation(self.image_cache, val); self.draw = ImageDraw.Draw(self.image); self.update_canvas()
    def setup_temperature_slider(self, p):
        s = Scale(p, from_=-100, to=100, orient=HORIZONTAL, command=self.live_temperature); s.set(0); s.pack(fill="x", padx=5)
    def live_temperature(self, val):
        if self.image_cache: self.image = filters.adjust_temperature(self.image_cache, val); self.draw = ImageDraw.Draw(self.image); self.update_canvas()
    def setup_denoise_slider(self, p):
        s = Scale(p, from_=0, to=20, orient=HORIZONTAL, command=self.live_denoise); s.set(0); s.pack(fill="x", padx=5)
    def live_denoise(self, val):
        if self.image_cache: self.image = filters.apply_denoise(self.image_cache, val); self.draw = ImageDraw.Draw(self.image); self.update_canvas()

    def activate_eraser(self): 
        if self.active_effect_name: self.active_effect_name = None; self.pre_effect_image = None
        self.is_eraser = True; self.brush_color = "white"; self.brush_type = "round"; self.btn_eraser.config(relief="sunken", bg="#ff5555", fg="white")
    def change_brush_type(self): self.is_eraser = False; self.brush_type = self.brush_var.get(); self.brush_color = self.default_color; self.btn_eraser.config(relief="raised", bg="#ffcccc", fg="black")
    def choose_color(self): 
        c = colorchooser.askcolor()[1]
        if c: self.default_color = c; self.brush_color = c; self.is_eraser = False; self.btn_eraser.config(relief="raised", bg="#ffcccc", fg="black")
    def update_canvas(self): self.tk_image = ImageTk.PhotoImage(self.image); self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")
    def save_state(self):
        self.history.append(self.image.copy()); self.redo_stack.clear()
        if len(self.history) > self.max_history: self.history.pop(0)
    def undo(self): 
        self.active_effect_name = None 
        if self.history: self.redo_stack.append(self.image.copy()); self.image = self.history.pop(); self.draw = ImageDraw.Draw(self.image); self.update_canvas()
    def redo(self):
        if self.redo_stack: self.history.append(self.image.copy()); self.image = self.redo_stack.pop(); self.draw = ImageDraw.Draw(self.image); self.update_canvas()
    def undo_shortcut(self, event): self.undo()
    def redo_shortcut(self, event): self.redo()
    def load_image(self):
        p = filedialog.askopenfilename()
        if p: self.save_state(); img = Image.open(p).convert("RGB"); self.image = img.resize((self.canvas_w, self.canvas_h)); self.draw = ImageDraw.Draw(self.image); self.update_canvas()
    def save_image(self):
        p = filedialog.asksaveasfilename(defaultextension=".png")
        if p: self.image.save(p); messagebox.showinfo("Saved", "Gambar berhasil disimpan!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PFOREditorApp(root)
    root.mainloop()