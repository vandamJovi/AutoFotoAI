import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

import config
import api

SUPPORTED = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AutoFotoAI")
        self.geometry("820x560")
        self.resizable(False, False)

        self.api_key = config.load_key()
        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.image_vars: dict[str, tk.BooleanVar] = {}

        self._build_ui()

    # ── UI Construction ──────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_left()
        self._build_right()

    def _build_header(self):
        header = ctk.CTkFrame(self, height=48, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")

        ctk.CTkLabel(header, text="AutoFotoAI", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=16, pady=10)
        ctk.CTkButton(header, text="⚙ API Key", width=100, command=self._set_api_key).pack(side="right", padx=12, pady=8)

    def _build_left(self):
        left = ctk.CTkFrame(self, corner_radius=0)
        left.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=8)
        # Source folder
        ctk.CTkLabel(left, text="Quellordner").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))
        src_row = ctk.CTkFrame(left, fg_color="transparent")
        src_row.grid(row=1, column=0, sticky="ew", padx=10)
        ctk.CTkEntry(src_row, textvariable=self.source_folder, width=240).pack(side="left")
        ctk.CTkButton(src_row, text="...", width=32, command=self._pick_source).pack(side="left", padx=(4, 0))

        # Dest folder
        ctk.CTkLabel(left, text="Zielordner").grid(row=2, column=0, sticky="w", padx=10, pady=(8, 2))
        dst_row = ctk.CTkFrame(left, fg_color="transparent")
        dst_row.grid(row=3, column=0, sticky="new", padx=10)
        ctk.CTkEntry(dst_row, textvariable=self.dest_folder, width=240).pack(side="left")
        ctk.CTkButton(dst_row, text="...", width=32, command=self._pick_dest).pack(side="left", padx=(4, 0))

        # Image list
        ctk.CTkLabel(left, text="Bilder").grid(row=4, column=0, sticky="w", padx=10, pady=(12, 2))
        self.scroll_frame = ctk.CTkScrollableFrame(left, width=300, height=300)
        self.scroll_frame.grid(row=5, column=0, sticky="nsew", padx=10, pady=(0, 6))
        left.grid_rowconfigure(5, weight=1)

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.grid(row=6, column=0, sticky="ew", padx=10, pady=(0, 10))
        ctk.CTkButton(btn_row, text="Alle", width=80, command=self._select_all).pack(side="left")
        ctk.CTkButton(btn_row, text="Keine", width=80, command=self._select_none).pack(side="left", padx=(8, 0))

    def _build_right(self):
        right = ctk.CTkFrame(self, corner_radius=0)
        right.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=8)
        right.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(right, text="Prompt (Bearbeitungsanweisung)").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))
        self.prompt_box = ctk.CTkTextbox(right, width=360, height=100)
        self.prompt_box.grid(row=1, column=0, sticky="ew", padx=10)

        self.run_btn = ctk.CTkButton(right, text="▶  Verarbeiten", height=40, command=self._start_processing)
        self.run_btn.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(right, text="Status").grid(row=3, column=0, sticky="w", padx=10)
        self.log_box = ctk.CTkTextbox(right, width=360, height=280, state="disabled")
        self.log_box.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))
        right.grid_rowconfigure(4, weight=1)

    # ── Actions ──────────────────────────────────────────────────

    def _set_api_key(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("API Key")
        dialog.geometry("480x160")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="OpenAI API Key:").pack(anchor="w", padx=20, pady=(20, 4))
        entry = ctk.CTkEntry(dialog, width=440, show="*")
        entry.pack(padx=20)
        entry.insert(0, self.api_key)

        def save():
            key = entry.get().strip()
            if key:
                self.api_key = key
                config.save_key(key)
            dialog.destroy()

        ctk.CTkButton(dialog, text="Speichern", command=save).pack(pady=16)

    def _pick_source(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_folder.set(folder)
            self._load_images(folder)

    def _pick_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_folder.set(folder)

    def _load_images(self, folder: str):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.image_vars.clear()

        files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in SUPPORTED]
        files.sort()

        for fname in files:
            var = tk.BooleanVar(value=True)
            self.image_vars[fname] = var
            ctk.CTkCheckBox(self.scroll_frame, text=fname, variable=var).pack(anchor="w", pady=2)

        if not files:
            ctk.CTkLabel(self.scroll_frame, text="Keine Bilder gefunden").pack(pady=10)

    def _select_all(self):
        for var in self.image_vars.values():
            var.set(True)

    def _select_none(self):
        for var in self.image_vars.values():
            var.set(False)

    def _log(self, msg: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _start_processing(self):
        if not self.api_key:
            messagebox.showerror("Fehler", "Kein API Key gesetzt. Bitte zuerst ⚙ API Key eingeben.")
            return

        prompt = self.prompt_box.get("1.0", "end").strip()
        if not prompt:
            messagebox.showerror("Fehler", "Bitte einen Prompt eingeben.")
            return

        selected = [name for name, var in self.image_vars.items() if var.get()]
        if not selected:
            messagebox.showerror("Fehler", "Keine Bilder ausgewählt.")
            return

        dest = self.dest_folder.get()
        if not dest:
            messagebox.showerror("Fehler", "Kein Zielordner ausgewählt.")
            return

        self.run_btn.configure(state="disabled")
        threading.Thread(target=self._process, args=(selected, prompt, dest), daemon=True).start()

    def _process(self, files: list[str], prompt: str, dest: str):
        source = self.source_folder.get()
        total = len(files)

        for i, fname in enumerate(files, 1):
            self._log(f"[{i}/{total}] {fname} …")
            try:
                result = api.edit_image(self.api_key, os.path.join(source, fname), prompt)
                out = api.save_result(result, dest, fname)
                self._log(f"  ✓ gespeichert: {os.path.basename(out)}")
            except Exception as e:
                self._log(f"  ✗ Fehler: {e}")

        self._log("─── Fertig ───")
        self.run_btn.configure(state="normal")
