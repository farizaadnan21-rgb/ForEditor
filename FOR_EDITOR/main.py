import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, Scale, HORIZONTAL, StringVar, ttk
from PIL import Image, ImageTk, ImageDraw

import filters
import tools

# ─── WARNA TEMA ─────────────────────────────────────────────────────────────
C = {
    "bg":        "#0f1117",
    "sidebar":   "#161b22",
    "card":      "#21262d",
    "card2":     "#2d333b",
    "hover":     "#30363d",
    "accent":    "#238636",
    "accent2":   "#2ea043",
    "blue":      "#1f6feb",
    "blue2":     "#388bfd",
    "danger":    "#b91c1c",
    "danger2":   "#ef4444",
    "border":    "#30363d",
    "text":      "#e6edf3",
    "muted":     "#8b949e",
    "canvas_bg": "#ffffff",
}

FONT_TITLE  = ("Segoe UI", 15, "bold")
FONT_LABEL  = ("Segoe UI", 9, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 8)

def make_btn(parent, text, cmd, bg=None, hover=None, fg=None, **kw):
    bg    = bg    or C["card2"]
    hover = hover or C["hover"]
    fg    = fg    or C["text"]
    b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                  activebackground=hover, activeforeground=fg,
                  relief="flat", bd=0, padx=8, pady=6,
                  font=FONT_BODY, cursor="hand2", **kw)
    b.bind("<Enter>", lambda _: b.config(bg=hover))
    b.bind("<Leave>", lambda _: b.config(bg=bg))
    return b

class PFOREditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FOR Photo Editor")
        self.root.geometry("1280x780")
        self.root.configure(bg=C["bg"])
        self.root.minsize(960, 640)

        # ── State ────────────────────────────────────────────────────────────
        self.default_color   = "black"
        self.brush_color     = self.default_color
        self.brush_size      = 5
        self.brush_type      = "round"
        self.is_eraser       = False
        self.is_drawing      = False
        self.last_x          = None
        self.last_y          = None
        self.image_cache     = None
        self.active_effect_name = None
        self.pre_effect_image   = None
        self.original_image     = None   # untuk before/after
        self.history         = []
        self.redo_stack      = []
        self.max_history     = 20

        # ── Canvas / Image ───────────────────────────────────────────────────
        self.canvas_w, self.canvas_h = 860, 650
        self.image = Image.new("RGB", (self.canvas_w, self.canvas_h), "white")
        self.draw  = ImageDraw.Draw(self.image)

        self._build_layout()
        self._build_sidebar()
        self._build_canvas_area()
        self._build_statusbar()

        self.root.bind("<Control-z>", self.undo_shortcut)
        self.root.bind("<Control-y>", self.redo_shortcut)

        self.update_canvas()
        self._update_status("Siap — Ctrl+Z Undo  ·  Ctrl+Y Redo")

    # ══════════════════════════════════════════════════════════════════════════
    # LAYOUT
    # ══════════════════════════════════════════════════════════════════════════
    def _build_layout(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.frm_sidebar  = tk.Frame(self.root, bg=C["sidebar"], width=300)
        self.frm_sidebar.grid(row=0, column=0, sticky="ns")
        self.frm_sidebar.grid_propagate(False)

        self.frm_workspace = tk.Frame(self.root, bg=C["bg"])
        self.frm_workspace.grid(row=0, column=1, sticky="nsew")
        self.frm_workspace.grid_rowconfigure(0, weight=1)
        self.frm_workspace.grid_columnconfigure(0, weight=1)

    def _build_statusbar(self):
        self.status_var = tk.StringVar()
        bar = tk.Label(self.root, textvariable=self.status_var,
                       bg="#0d1117", fg=C["muted"], font=FONT_SMALL,
                       anchor="w", padx=14, pady=5)
        bar.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _update_status(self, msg):
        self.status_var.set(msg)

    # ── Canvas area ───────────────────────────────────────────────────────────
    def _build_canvas_area(self):
        outer = tk.Frame(self.frm_workspace, bg=C["border"], padx=2, pady=2)
        outer.grid(row=0, column=0, padx=28, pady=28, sticky="nsew")

        inner = tk.Frame(outer, bg="#000000", padx=1, pady=1)
        inner.pack(expand=True)

        self.canvas = tk.Canvas(inner, width=self.canvas_w, height=self.canvas_h,
                                bg=C["canvas_bg"], cursor="crosshair",
                                highlightthickness=0, bd=0)
        self.canvas.pack()

        self.canvas.bind("<Button-1>",        lambda e: tools.start_draw(self, e))
        self.canvas.bind("<B1-Motion>",       lambda e: tools.draw_brush(self, e))
        self.canvas.bind("<ButtonRelease-1>", lambda e: tools.stop_draw(self, e))

    # ══════════════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ══════════════════════════════════════════════════════════════════════════
    def _build_sidebar(self):
        panel = self.frm_sidebar

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(panel, bg=C["sidebar"])
        hdr.pack(fill="x", padx=16, pady=(18, 10))
        tk.Label(hdr, text="🖌  FOR Editor", bg=C["sidebar"],
                 fg=C["text"], font=FONT_TITLE).pack(anchor="w")
        tk.Label(hdr, text="by Fariza · Ocid · Rasya", bg=C["sidebar"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(2, 0))

        sep = tk.Frame(panel, bg=C["border"], height=1)
        sep.pack(fill="x", padx=12, pady=(0, 8))

        # ── Scroll area ───────────────────────────────────────────────────────
        wrap = tk.Frame(panel, bg=C["sidebar"])
        wrap.pack(fill="both", expand=True)

        sc = tk.Canvas(wrap, bg=C["sidebar"], highlightthickness=0, width=286)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=sc.yview)
        sc.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        sc.pack(side="left", fill="both", expand=True)

        self._sc_inner = tk.Frame(sc, bg=C["sidebar"])
        win = sc.create_window((0, 0), window=self._sc_inner, anchor="nw")

        def _sync(e=None):
            sc.configure(scrollregion=sc.bbox("all"))
            sc.itemconfig(win, width=sc.winfo_width())
        self._sc_inner.bind("<Configure>", _sync)
        sc.bind("<Configure>", _sync)

        for w in (panel, wrap, sc, self._sc_inner):
            w.bind("<MouseWheel>",  lambda e: sc.yview_scroll(int(-1*(e.delta/120)), "units"))
            w.bind("<Button-4>",    lambda e: sc.yview_scroll(-1, "units"))
            w.bind("<Button-5>",    lambda e: sc.yview_scroll(1, "units"))

        self._build_tools_card()
        self._build_adjustments_card()
        self._build_effects_card()
        self._build_before_after_card()
        self._build_file_bar()

    # ── Card helper ───────────────────────────────────────────────────────────
    def _card(self, title, icon=""):
        outer = tk.Frame(self._sc_inner, bg=C["sidebar"])
        outer.pack(fill="x", padx=10, pady=(0, 8))
        card = tk.Frame(outer, bg=C["card"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="x")
        hdr = tk.Frame(card, bg=C["card"])
        hdr.pack(fill="x", padx=12, pady=(8, 4))
        lbl = (icon + "  " + title).strip()
        tk.Label(hdr, text=lbl, bg=C["card"], fg=C["text"],
                 font=FONT_LABEL).pack(side="left")
        body = tk.Frame(card, bg=C["card"])
        body.pack(fill="x", padx=12, pady=(0, 10))
        return body

    # ── Drawing Tools ─────────────────────────────────────────────────────────
    def _build_tools_card(self):
        body = self._card("Drawing Tools", "🛠️")

        # Color row
        row = tk.Frame(body, bg=C["card"])
        row.pack(fill="x", pady=(0, 6))
        self.color_swatch = tk.Canvas(row, width=28, height=28,
                                      bg=self.default_color,
                                      highlightbackground=C["border"],
                                      highlightthickness=1, cursor="hand2")
        self.color_swatch.pack(side="left", padx=(0, 8))
        self.color_swatch.bind("<Button-1>", lambda _: self.choose_color())

        r2 = tk.Frame(row, bg=C["card"])
        r2.pack(side="left", fill="x", expand=True)
        make_btn(r2, "🎨 Color", self.choose_color,
                 bg=C["blue"], hover=C["blue2"]).pack(side="left", fill="x",
                                                      expand=True, padx=(0, 4))
        make_btn(r2, "🧹 Clear", lambda: tools.clear_canvas(self),
                 bg=C["card2"]).pack(side="left", fill="x", expand=True)

        # Eraser
        self.btn_eraser = make_btn(body, "🧽  Eraser", self.activate_eraser,
                                   bg=C["danger"], hover=C["danger2"])
        self.btn_eraser.pack(fill="x", pady=3)

        # Brush shape
        tk.Label(body, text="Brush Shape", bg=C["card"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(8, 3))
        self.brush_var = StringVar(value="round")
        f = tk.Frame(body, bg=C["card"])
        f.pack(fill="x")
        style = ttk.Style()
        style.configure("B.TRadiobutton", background=C["card"],
                        foreground=C["text"])
        for val, lbl in [("round","● Round"),("flat","■ Flat"),("spray","✦ Spray")]:
            ttk.Radiobutton(f, text=lbl, variable=self.brush_var,
                            value=val, style="B.TRadiobutton",
                            command=self.change_brush_type).pack(side="left", padx=(0, 8))

        # Brush size
        tk.Label(body, text="Brush Size", bg=C["card"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(8, 2))
        self.slider = Scale(body, from_=1, to=50, orient=HORIZONTAL,
                            bg=C["card"], fg=C["text"],
                            troughcolor=C["card2"], highlightthickness=0,
                            activebackground=C["blue"])
        self.slider.set(5)
        self.slider.pack(fill="x")

    # ── Image Adjustments ─────────────────────────────────────────────────────
    def _build_adjustments_card(self):
        self.pcd_container = self._card("Image Adjustments", "🎛️")

        for label, func in [
            ("☀️  Brightness",   self._setup_brightness),
            ("🌓  Contrast",     self._setup_contrast),
            ("🎨  Saturation",   self._setup_saturation),
            ("🌡️  Temperature",  self._setup_temperature),
            ("✨  Denoise",      self._setup_denoise),
        ]:
            self._accordion(self.pcd_container, label, func)

    def _accordion(self, parent, text, setup_fn):
        frm = tk.Frame(parent, bg=C["card"])
        frm.pack(fill="x", pady=2)
        btn = make_btn(frm, text, lambda f=frm, s=setup_fn: self.toggle_slider(f, s),
                       bg=C["card2"])
        btn.config(anchor="w")
        btn.pack(fill="x")
        frm.accordion_btn = btn
        frm.slider_area = tk.Frame(frm, bg=C["card2"])
        frm.is_open = False

    def _build_effects_card(self):
        body = self._card("Special Effects", "✨")
        tk.Label(body, text="Click again to toggle off",
                 bg=C["card"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(0,6))
        for lbl, name, fn in [
            ("✏️  Pencil Sketch", "sketch", filters.effect_sketch),
            ("🌆  Cyberpunk Neon","neon",   filters.effect_neon),
            ("📜  Sepia Vintage", "sepia",  filters.effect_sepia),
        ]:
            self._effect_btn(body, lbl, name, fn)

    def _effect_btn(self, parent, text, name, fn):
        b = make_btn(parent, text,
                     lambda n=name, f=fn: self.toggle_special_effect(n, f),
                     bg=C["card2"])
        b.config(anchor="w")
        b.pack(fill="x", pady=2)
        if not hasattr(self, "_effect_btns"):
            self._effect_btns = {}
        self._effect_btns[name] = b

    # ── Before / After ────────────────────────────────────────────────────────
    def _build_before_after_card(self):
        body = self._card("Before / After", "🔍")
        tk.Label(body,
                 text="Load an image first, then apply\neffects and compare.",
                 bg=C["card"], fg=C["muted"], font=FONT_SMALL,
                 justify="left").pack(anchor="w", pady=(0, 8))
        make_btn(body, "⚡  Compare Before / After",
                 self.show_before_after,
                 bg=C["blue"], hover=C["blue2"]).pack(fill="x", pady=2)

    def show_before_after(self):
        if self.original_image is None:
            messagebox.showinfo("Before / After",
                                "Belum ada gambar asli.\nLoad gambar terlebih dahulu.")
            return

        win = tk.Toplevel(self.root)
        win.title("Before / After Comparison")
        win.configure(bg=C["bg"])
        win.resizable(False, False)

        thumb_w, thumb_h = 500, 400

        before_img = self.original_image.resize((thumb_w, thumb_h))
        after_img  = self.image.resize((thumb_w, thumb_h))

        before_tk = ImageTk.PhotoImage(before_img)
        after_tk  = ImageTk.PhotoImage(after_img)

        frm = tk.Frame(win, bg=C["bg"])
        frm.pack(padx=20, pady=20)

        # Before
        col_b = tk.Frame(frm, bg=C["bg"])
        col_b.grid(row=0, column=0, padx=12)
        tk.Label(col_b, text="BEFORE", bg=C["bg"], fg=C["muted"],
                 font=FONT_LABEL).pack(pady=(0, 6))
        lbl_b = tk.Label(col_b, image=before_tk,
                         highlightbackground=C["border"], highlightthickness=2)
        lbl_b.image = before_tk
        lbl_b.pack()

        # Divider
        tk.Frame(frm, bg=C["border"], width=2).grid(row=0, column=1, sticky="ns", padx=4)

        # After
        col_a = tk.Frame(frm, bg=C["bg"])
        col_a.grid(row=0, column=2, padx=12)
        tk.Label(col_a, text="AFTER", bg=C["bg"], fg=C["accent2"],
                 font=FONT_LABEL).pack(pady=(0, 6))
        lbl_a = tk.Label(col_a, image=after_tk,
                         highlightbackground=C["accent"], highlightthickness=2)
        lbl_a.image = after_tk
        lbl_a.pack()

        make_btn(win, "✕  Close", win.destroy,
                 bg=C["card2"]).pack(pady=12)

    # ── File bar ──────────────────────────────────────────────────────────────
    def _build_file_bar(self):
        f = tk.Frame(self.frm_sidebar, bg=C["sidebar"])
        f.pack(side="bottom", fill="x", padx=10, pady=(6, 12))
        tk.Frame(f, bg=C["border"], height=1).pack(fill="x", pady=(0, 8))
        g = tk.Frame(f, bg=C["sidebar"])
        g.pack(fill="x")
        for i, (txt, cmd, bg, hov) in enumerate([
            ("📂 Load",  self.load_image, C["card2"],  C["hover"]),
            ("💾 Save",  self.save_image, C["accent"], C["accent2"]),
            ("↩ Undo",  self.undo,        C["card2"],  C["hover"]),
            ("↪ Redo",  self.redo,        C["card2"],  C["hover"]),
        ]):
            b = make_btn(g, txt, cmd, bg=bg, hover=hov)
            b.grid(row=0, column=i, sticky="ew", padx=2)
            g.grid_columnconfigure(i, weight=1)

        make_btn(f, "📷  Camera", lambda: tools.open_camera(self),
                 bg=C["blue"], hover=C["blue2"]).pack(fill="x", pady=(6, 0))

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDER ACCORDIONS
    # ══════════════════════════════════════════════════════════════════════════
    def toggle_slider(self, frm, setup_fn):
        if self.active_effect_name:
            self.active_effect_name = None
            self.pre_effect_image   = None
        if frm.is_open:
            self.close_all_sliders()
            return
        self.close_all_sliders()
        self.save_state()
        self.image_cache = self.image.copy()
        setup_fn(frm.slider_area)
        frm.slider_area.pack(fill="x", pady=2, padx=4)
        frm.is_open = True
        if hasattr(frm, "accordion_btn"):
            frm.accordion_btn.config(bg=C["blue"], fg="#ffffff")

    def close_all_sliders(self):
        self.image_cache = None
        for child in self.pcd_container.winfo_children():
            if isinstance(child, tk.Frame) and hasattr(child, "slider_area"):
                for w in child.slider_area.winfo_children():
                    w.destroy()
                child.slider_area.pack_forget()
                child.is_open = False
                if hasattr(child, "accordion_btn"):
                    child.accordion_btn.config(bg=C["card2"], fg=C["text"])

    def _slider_row(self, parent, frm_=0, to_=100, res=1, default=50, cmd=None):
        s = Scale(parent, from_=frm_, to=to_, resolution=res,
                  orient=HORIZONTAL, command=cmd,
                  bg=C["card2"], fg=C["text"], troughcolor=C["card"],
                  highlightthickness=0, activebackground=C["blue"])
        s.set(default)
        s.pack(fill="x", padx=6, pady=4)
        return s

    def _setup_brightness(self, p):
        self._slider_row(p, 0.0, 2.0, 0.1, 1.0, self._live_brightness)
    def _live_brightness(self, v):
        if self.image_cache:
            self.image = filters.adjust_brightness(self.image_cache, v)
            self.draw   = ImageDraw.Draw(self.image)
            self.update_canvas()

    def _setup_contrast(self, p):
        self._slider_row(p, 0.0, 2.0, 0.1, 1.0, self._live_contrast)
    def _live_contrast(self, v):
        if self.image_cache:
            self.image = filters.adjust_contrast(self.image_cache, v)
            self.draw   = ImageDraw.Draw(self.image)
            self.update_canvas()

    def _setup_saturation(self, p):
        self._slider_row(p, 0.0, 3.0, 0.1, 1.0, self._live_saturation)
    def _live_saturation(self, v):
        if self.image_cache:
            self.image = filters.adjust_saturation(self.image_cache, v)
            self.draw   = ImageDraw.Draw(self.image)
            self.update_canvas()

    def _setup_temperature(self, p):
        self._slider_row(p, -100, 100, 1, 0, self._live_temperature)
    def _live_temperature(self, v):
        if self.image_cache:
            self.image = filters.adjust_temperature(self.image_cache, v)
            self.draw   = ImageDraw.Draw(self.image)
            self.update_canvas()

    def _setup_denoise(self, p):
        self._slider_row(p, 0, 20, 1, 0, self._live_denoise)
    def _live_denoise(self, v):
        if self.image_cache:
            self.image = filters.apply_denoise(self.image_cache, v)
            self.draw   = ImageDraw.Draw(self.image)
            self.update_canvas()

    # ══════════════════════════════════════════════════════════════════════════
    # SPECIAL EFFECTS TOGGLE
    # ══════════════════════════════════════════════════════════════════════════
    def toggle_special_effect(self, name, fn):
        self.close_all_sliders()
        if self.active_effect_name == name:
            if self.pre_effect_image:
                self.image = self.pre_effect_image.copy()
                self.draw  = ImageDraw.Draw(self.image)
                self.update_canvas()
            self.active_effect_name = None
            self.pre_effect_image   = None
            self._highlight_effect(None)
            self._update_status(f"Effect '{name}' removed.")
            return
        if self.active_effect_name is not None:
            self.image = self.pre_effect_image.copy()
        else:
            self.pre_effect_image = self.image.copy()
            self.save_state()
        self.image = fn(self.image)
        self.draw  = ImageDraw.Draw(self.image)
        self.update_canvas()
        self.active_effect_name = name
        self._highlight_effect(name)
        self._update_status(f"Effect active: {name}")

    def _highlight_effect(self, name):
        if not hasattr(self, "_effect_btns"):
            return
        for k, b in self._effect_btns.items():
            if k == name:
                b.config(bg=C["accent"], fg="#ffffff")
            else:
                b.config(bg=C["card2"], fg=C["text"])

    # ══════════════════════════════════════════════════════════════════════════
    # TOOL ACTIONS
    # ══════════════════════════════════════════════════════════════════════════
    def activate_eraser(self):
        if self.active_effect_name:
            self.active_effect_name = None
            self.pre_effect_image   = None
        self.is_eraser  = True
        self.brush_color = "white"
        self.brush_type  = "round"
        self.btn_eraser.config(bg=C["danger2"])
        self._update_status("Mode: Eraser")

    def change_brush_type(self):
        self.is_eraser  = False
        self.brush_type  = self.brush_var.get()
        self.brush_color = self.default_color
        self.btn_eraser.config(bg=C["danger"])
        self._update_status(f"Brush: {self.brush_type}")

    def choose_color(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.default_color = c
            self.brush_color   = c
            self.is_eraser     = False
            self.color_swatch.config(bg=c)
            self.btn_eraser.config(bg=C["danger"])

    def update_canvas(self):
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")

    def save_state(self):
        self.history.append(self.image.copy())
        self.redo_stack.clear()
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def undo(self):
        self.active_effect_name = None
        self._highlight_effect(None)
        if self.history:
            self.redo_stack.append(self.image.copy())
            self.image = self.history.pop()
            self.draw  = ImageDraw.Draw(self.image)
            self.update_canvas()
            self._update_status("Undo")

    def redo(self):
        if self.redo_stack:
            self.history.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.draw  = ImageDraw.Draw(self.image)
            self.update_canvas()
            self._update_status("Redo")

    def undo_shortcut(self, _): self.undo()
    def redo_shortcut(self, _): self.redo()

    def load_image(self):
        p = filedialog.askopenfilename(
            filetypes=[("Image files","*.png *.jpg *.jpeg *.bmp *.gif *.webp"), ("All","*.*")])
        if p:
            self.save_state()
            img = Image.open(p).convert("RGB")
            img = img.resize((self.canvas_w, self.canvas_h))
            self.image          = img.copy()
            self.original_image = img.copy()   # simpan untuk before/after
            self.draw           = ImageDraw.Draw(self.image)
            self.update_canvas()
            self._update_status(f"Loaded: {p.split('/')[-1]}")

    def save_image(self):
        p = filedialog.asksaveasfilename(defaultextension=".png",
            filetypes=[("PNG","*.png"),("JPEG","*.jpg"),("All","*.*")])
        if p:
            self.image.save(p)
            self._update_status(f"Saved: {p.split('/')[-1]}")
            messagebox.showinfo("Saved", "Image saved successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app  = PFOREditorApp(root)
    root.mainloop()