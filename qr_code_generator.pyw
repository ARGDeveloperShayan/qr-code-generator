import os
import re
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import qrcode
    from PIL import Image, ImageTk
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Dependency Missing",
        "qrcode or Pillow is not installed.\n"
        "Please run: pip install qrcode pillow")
    sys.exit(1)

FONT   = ("Tahoma", 10)
FONT_B = ("Tahoma", 10, "bold")

def sanitize_filename(data):
    return re.sub(r'[\\/*?:"<>|]', '_', data)

class QRCodeGeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("🔳  QR Code Generator")
        root.geometry("1100x700")
        root.minsize(900, 550)

        self.data_var = tk.StringVar()
        self.filename_var = tk.StringVar(value="qrcode.png")
        self.save_dir = tk.StringVar(value=os.getcwd())
        self._tk_img = None

        self._build_ui()

    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TLabel", font=FONT)
        style.configure("TLabelframe.Label", font=FONT_B)
        style.configure("TButton", font=FONT, padding=6)
        style.configure("Accent.TButton", font=FONT_B, padding=8)

        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        prev_box = ttk.LabelFrame(main, text=" Preview ", padding=6)
        prev_box.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(prev_box, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._redraw_preview())

        side = ttk.Frame(main, width=400)
        side.pack(side="right", fill="y", padx=(12, 0))
        side.pack_propagate(False)

        s1 = ttk.LabelFrame(side, text=" 1) Content ", padding=10)
        s1.pack(fill="x", pady=(0, 8))
        ttk.Label(s1, text="Data (URL, text, etc.):").pack(anchor="w")
        ttk.Entry(s1, textvariable=self.data_var).pack(fill="x", pady=(2, 0))

        s2 = ttk.LabelFrame(side, text=" 2) Output ", padding=10)
        s2.pack(fill="x", pady=(0, 8))
        ttk.Label(s2, text="Filename:").pack(anchor="w")
        r = ttk.Frame(s2); r.pack(fill="x", pady=(2, 6))
        ttk.Entry(r, textvariable=self.filename_var).pack(
            side="left", fill="x", expand=True)
        ttk.Button(r, text="📂", width=3,
                   command=self._browse_save).pack(side="right", padx=(6, 0))

        self.lbl_dir = ttk.Label(
            s2, text=f"Folder: {os.getcwd()}",
            anchor="w", foreground="#7f8c8d", wraplength=340)
        self.lbl_dir.pack(fill="x")

        s3 = ttk.LabelFrame(side, text=" 3) Run ", padding=10)
        s3.pack(fill="x", pady=(0, 8))

        ttk.Button(s3, text="✨  Generate QR Code",
                   style="Accent.TButton",
                   command=self._generate).pack(fill="x")
        ttk.Button(s3, text="✖  Quit",
                   command=self.root.destroy).pack(fill="x", pady=(6, 0))

        self.status_lbl = ttk.Label(
            s3, text="Ready", anchor="w",
            foreground="#2c3e50", wraplength=340)
        self.status_lbl.pack(fill="x", pady=(10, 0))

    def _browse_save(self):
        path = filedialog.asksaveasfilename(
            title="Save QR Code As",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"),
                       ("JPEG files", "*.jpg"),
                       ("All files", "*.*")])
        if path:
            self.filename_var.set(os.path.basename(path))
            self.save_dir.set(os.path.dirname(path))
            self.lbl_dir.config(text=f"Folder: {self.save_dir.get()}")

    def _redraw_preview(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 20 or h < 20:
            return
        if self._tk_img is None:
            self.canvas.create_text(
                w // 2, h // 2,
                text="QR preview will appear here",
                fill="#666666", font=FONT)
        else:
            self.canvas.create_image(w // 2, h // 2, image=self._tk_img)

    def _generate(self):
        data = self.data_var.get().strip()
        if not data:
            messagebox.showerror("Error", "Please enter data for the QR code.")
            return

        fname = self.filename_var.get().strip()
        if not fname:
            fname = sanitize_filename(data) + "_qrcode.png"
            self.filename_var.set(fname)

        save_path = os.path.join(self.save_dir.get(), fname)

        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4)
            qr.add_data(data)
            qr.make(fit=True)

            try:
                qr_img = qr.make_image(fill_color="black",
                                       back_color="white")
            except TypeError:
                qr_img = qr.make_image(fill="black",
                                       back_color="white")

            qr_img = qr_img.convert("RGB")
            qr_img.save(save_path)

            preview = qr_img.copy()
            preview.thumbnail((600, 600))
            self._tk_img = ImageTk.PhotoImage(preview)
            self._redraw_preview()

            self.status_lbl.config(
                text=f"✔  Saved: {save_path}", foreground="#27ae60")
            messagebox.showinfo(
                "Success", f"QR code saved successfully:\n{save_path}")
        except Exception as e:
            self.status_lbl.config(
                text=f"Error: {e}", foreground="#c0392b")
            messagebox.showerror(
                "Error", f"Failed to generate QR code:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeGeneratorApp(root)
    root.mainloop()