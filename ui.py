import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import os
from converter import convert_to_pdf, get_image_info, is_image, SUPPORTED_FORMATS

BG = "#0d0d1a"
BG2 = "#12122a"
BG3 = "#1a1a3e"
BG4 = "#222244"
FG = "#e8e8ff"
FG2 = "#8888aa"
ACCENT = "#7c4dff"
ACCENT2 = "#651fff"
GREEN = "#00e676"
ERROR = "#ff5252"
WARNING = "#ffab40"
FONT_UI = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI", 15, "bold")

THUMB_SIZE = (80, 80)


class SnapToPDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SnapToPDF")
        self.root.geometry("700x650")
        self.root.configure(bg=BG)
        self.root.minsize(550, 450)

        self.images = []
        self.thumbnails = {}

        self._build_header()
        self._build_dropzone()
        self._build_list()
        self._build_footer()
        self._build_statusbar()

    def _build_header(self):
        header = tk.Frame(self.root, bg=BG3, pady=14)
        header.pack(fill=tk.X)
        tk.Label(header, text="🖼️ SnapToPDF", bg=BG3, fg=FG, font=FONT_TITLE).pack(side=tk.LEFT, padx=16)
        tk.Label(header, text="  —  Image to PDF Converter", bg=BG3, fg=FG2, font=FONT_UI).pack(side=tk.LEFT)

    def _build_dropzone(self):
        outer = tk.Frame(self.root, bg=BG, pady=16)
        outer.pack(fill=tk.X, padx=24)

        self.dropzone = tk.Frame(outer, bg=BG2, height=100, highlightbackground=ACCENT,
                                  highlightthickness=2)
        self.dropzone.pack(fill=tk.X)
        self.dropzone.pack_propagate(False)

        label = tk.Label(
            self.dropzone, text="📥  Arrastra imágenes aquí o haz clic para seleccionar",
            bg=BG2, fg=FG2, font=FONT_UI, cursor="hand2"
        )
        label.pack(expand=True)

        for widget in (self.dropzone, label):
            widget.bind("<Button-1>", lambda e: self._select_files())
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_drop)

    def _build_list(self):
        outer = tk.Frame(self.root, bg=BG, pady=8)
        outer.pack(fill=tk.BOTH, expand=True, padx=24)

        header = tk.Frame(outer, bg=BG)
        header.pack(fill=tk.X, pady=(0, 8))

        self.count_label = tk.Label(header, text="0 imágenes", bg=BG, fg=FG2, font=("Segoe UI", 9, "bold"))
        self.count_label.pack(side=tk.LEFT)

        tk.Button(
            header, text="🗑 Limpiar todo", bg=BG3, fg=ERROR,
            font=("Segoe UI", 9), relief=tk.FLAT,
            padx=8, pady=3, cursor="hand2",
            activebackground=BG4, activeforeground=ERROR,
            command=self._clear_all
        ).pack(side=tk.RIGHT)

        canvas_frame = tk.Frame(outer, bg=BG2)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg=BG2, highlightthickness=0)
        scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.list_frame = tk.Frame(self.canvas, bg=BG2)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def _build_footer(self):
        frame = tk.Frame(self.root, bg=BG, pady=12)
        frame.pack(fill=tk.X, padx=24)

        self.convert_btn = tk.Button(
            frame, text="📄 Convertir a PDF", bg=ACCENT, fg="white",
            font=("Segoe UI", 11, "bold"), relief=tk.FLAT,
            padx=24, pady=10, cursor="hand2",
            activebackground=ACCENT2, activeforeground="white",
            command=self._convert
        )
        self.convert_btn.pack(fill=tk.X)

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=BG3, pady=5)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(bar, text="Listo", bg=BG3, fg=FG2, font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT, padx=12)
        tk.Label(bar, text="SnapToPDF v1.0", bg=BG3, fg=FG2, font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=12)

    def _set_status(self, text, color=None):
        self.status_label.config(text=text, fg=color or FG2)

    def _select_files(self):
        files = filedialog.askopenfilenames(
            title="Selecciona imágenes",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff")]
        )
        if files:
            self._add_images(files)

    def _on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        valid = [f for f in files if is_image(f)]
        if valid:
            self._add_images(valid)
        else:
            self._set_status("⚠ Ningún archivo válido", WARNING)

    def _add_images(self, paths):
        added = 0
        for path in paths:
            if path not in self.images and is_image(path):
                self.images.append(path)
                added += 1
        self._refresh_list()
        if added:
            self._set_status(f"✓ {added} imágenes añadidas", GREEN)

    def _refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.count_label.config(text=f"{len(self.images)} imágenes")

        if not self.images:
            tk.Label(self.list_frame, text="No hay imágenes añadidas", bg=BG2, fg=FG2, font=FONT_UI).pack(pady=40)
            return

        for i, path in enumerate(self.images):
            self._build_image_row(i, path)

    def _build_image_row(self, index, path):
        row = tk.Frame(self.list_frame, bg=BG3, pady=6, padx=10)
        row.pack(fill=tk.X, padx=4, pady=3)

        thumb = self._get_thumbnail(path)
        if thumb:
            img_label = tk.Label(row, image=thumb, bg=BG3)
            img_label.image = thumb
            img_label.pack(side=tk.LEFT, padx=(0, 10))

        info_frame = tk.Frame(row, bg=BG3)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        filename = os.path.basename(path)
        tk.Label(info_frame, text=f"{index + 1}. {filename}", bg=BG3, fg=FG, font=FONT_UI, anchor="w").pack(fill=tk.X)

        info = get_image_info(path)
        if info:
            tk.Label(
                info_frame,
                text=f"{info['width']}x{info['height']} px — {info['size']} — {info['format']}",
                bg=BG3, fg=FG2, font=("Segoe UI", 8), anchor="w"
            ).pack(fill=tk.X)

        actions = tk.Frame(row, bg=BG3)
        actions.pack(side=tk.RIGHT)

        tk.Button(
            actions, text="▲", bg=BG3, fg=FG2 if index > 0 else BG4,
            font=("Segoe UI", 9), relief=tk.FLAT, padx=6, cursor="hand2",
            activebackground=BG4, activeforeground=ACCENT,
            command=lambda i=index: self._move_up(i),
            state=tk.NORMAL if index > 0 else tk.DISABLED
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            actions, text="▼", bg=BG3, fg=FG2 if index < len(self.images) - 1 else BG4,
            font=("Segoe UI", 9), relief=tk.FLAT, padx=6, cursor="hand2",
            activebackground=BG4, activeforeground=ACCENT,
            command=lambda i=index: self._move_down(i),
            state=tk.NORMAL if index < len(self.images) - 1 else tk.DISABLED
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            actions, text="✕", bg=BG3, fg=ERROR,
            font=("Segoe UI", 9), relief=tk.FLAT, padx=6, cursor="hand2",
            activebackground=BG4, activeforeground=ERROR,
            command=lambda i=index: self._remove(i)
        ).pack(side=tk.LEFT, padx=2)

    def _get_thumbnail(self, path):
        if path in self.thumbnails:
            return self.thumbnails[path]
        try:
            img = Image.open(path)
            img.thumbnail(THUMB_SIZE)
            thumb = ImageTk.PhotoImage(img)
            self.thumbnails[path] = thumb
            return thumb
        except Exception:
            return None

    def _move_up(self, index):
        if index > 0:
            self.images[index - 1], self.images[index] = self.images[index], self.images[index - 1]
            self._refresh_list()

    def _move_down(self, index):
        if index < len(self.images) - 1:
            self.images[index + 1], self.images[index] = self.images[index], self.images[index + 1]
            self._refresh_list()

    def _remove(self, index):
        self.images.pop(index)
        self._refresh_list()

    def _clear_all(self):
        self.images = []
        self._refresh_list()
        self._set_status("Lista limpiada")

    def _convert(self):
        if not self.images:
            self._set_status("⚠ Añade al menos una imagen", WARNING)
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile="documento.pdf"
        )
        if not output_path:
            return

        self._set_status("Convirtiendo...", ACCENT)
        self.convert_btn.config(state=tk.DISABLED, text="Convirtiendo...")
        self.root.update()

        success, error = convert_to_pdf(self.images, output_path)

        self.convert_btn.config(state=tk.NORMAL, text="📄 Convertir a PDF")

        if success:
            self._set_status(f"✅ PDF guardado en {output_path}", GREEN)
            messagebox.showinfo("Éxito", f"PDF creado correctamente:\n{output_path}")
        else:
            self._set_status(f"❌ Error: {error}", ERROR)
            messagebox.showerror("Error", f"No se pudo crear el PDF:\n{error}")