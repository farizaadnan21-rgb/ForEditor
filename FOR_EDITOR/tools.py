import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageTk
import cv2
import random

# --- LOGIKA KAMERA (WEBCAM) ---
def open_camera(app):
    cam_window = tk.Toplevel(app.root)
    cam_window.title("Ambil Foto dari Kamera")
    cam_window.geometry("640x550")
    
    lbl_video = tk.Label(cam_window)
    lbl_video.pack(pady=10)
    
    # Coba akses kamera (0 atau 1)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        messagebox.showerror("Error", "Kamera tidak terdeteksi!\nCoba cek izin kamera laptop.")
        cam_window.destroy()
        return

    def show_frames():
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            lbl_video.imgtk = imgtk
            lbl_video.configure(image=imgtk)
            lbl_video.after(10, show_frames)

    def capture():
        ret, frame = cap.read()
        if ret:
            app.save_state()
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
            pil_img = pil_img.resize((app.canvas_w, app.canvas_h))
            
            app.image = pil_img
            app.draw = ImageDraw.Draw(app.image)
            app.update_canvas()
            cleanup()

    def cleanup():
        cap.release()
        cam_window.destroy()

    btn_capture = tk.Button(cam_window, text="📸 AMBIL FOTO (CAPTURE)", command=capture, 
                            bg="#3498db", fg="white", font=("Arial", 12, "bold"), pady=10)
    btn_capture.pack(fill="x", padx=20, pady=10)

    show_frames()
    cam_window.protocol("WM_DELETE_WINDOW", cleanup)

# --- LOGIKA GAMBAR ---
def start_draw(app, event):
    if app.active_effect_name: 
        app.active_effect_name = None
        app.pre_effect_image = None
    app.is_drawing = True
    app.last_x, app.last_y = event.x, event.y
    app.save_state()

def stop_draw(app, event):
    app.is_drawing = False
    app.update_canvas()

def draw_brush(app, event):
    if app.is_drawing:
        x, y = event.x, event.y
        r = app.slider.get()
        if app.brush_type == "spray":
            for _ in range(int(r*2)):
                rx = x + random.randint(-r, r); ry = y + random.randint(-r, r)
                app.canvas.create_oval(rx, ry, rx+1, ry+1, fill=app.brush_color, outline=app.brush_color)
                app.draw.point((rx, ry), fill=app.brush_color)
        elif app.brush_type == "flat":
            app.canvas.create_line(app.last_x, app.last_y, x, y, fill=app.brush_color, width=r*2, capstyle=tk.PROJECTING)
            app.draw.line([app.last_x, app.last_y, x, y], fill=app.brush_color, width=r*2)
        else:
            app.canvas.create_line(app.last_x, app.last_y, x, y, fill=app.brush_color, width=r*2, capstyle=tk.ROUND, smooth=True)
            app.draw.line([app.last_x, app.last_y, x, y], fill=app.brush_color, width=r*2, joint="curve")
        app.last_x, app.last_y = x, y

def clear_canvas(app):
    app.save_state()
    app.image = Image.new("RGB", (app.canvas_w, app.canvas_h), "white")
    app.draw = ImageDraw.Draw(app.image)
    app.update_canvas()