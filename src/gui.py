# src/gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from src.SystemScanEngine import SystemScanEngine
from src.delete import DeleteFiles

class CleanerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧹 PyCleaner - Windows Cleaning Utility")
        self.root.geometry("700x600")
        self.root.configure(bg="#1e1e1e")
        self.style = ttk.Style(self.root)

        # Dark theme setup
        self.set_dark_theme()

        self.scan_running = False
        self.scan_results = {}
        self.result_checkboxes = {}
        self.selected_targets = {}
        self.scan_thread = None

        self.build_gui()

    def set_dark_theme(self):
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TLabel", background="#1e1e1e", foreground="#ffffff")
        self.style.configure("TButton", background="#333", foreground="#ffffff", padding=6)
        self.style.configure("TCheckbutton", background="#1e1e1e", foreground="#ffffff")
        self.style.configure("TLabelframe", background="#2e2e2e", foreground="#ffffff")
        self.style.configure("Vertical.TScrollbar", background="#444", troughcolor="#222", arrowcolor="#fff")

    def build_gui(self):
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Scan button
        self.scan_button = ttk.Button(self.main_frame, text="🔍 Start Scan", command=self.start_scan)
        self.scan_button.grid(row=0, column=0, sticky="w")

        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.grid(row=0, column=1, sticky="ew", padx=10)
        self.main_frame.columnconfigure(1, weight=1)

        # Target selection panel
        self.target_frame = ttk.LabelFrame(self.main_frame, text="Scan Targets", padding=10)
        self.target_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

        self.target_checkboxes = {}
        scan_engine = SystemScanEngine()
        for label in scan_engine.targets:
            var = tk.BooleanVar(value=True)
            chk = ttk.Checkbutton(self.target_frame, text=label, variable=var)
            chk.pack(anchor="w", padx=5, pady=2)
            self.target_checkboxes[label] = var

        # Results panel
        self.result_frame = ttk.LabelFrame(self.main_frame, text="Scan Results", padding=10)
        self.result_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)

        self.result_canvas = tk.Canvas(self.result_frame, bg="#1e1e1e", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.result_canvas.yview)
        self.result_inner = ttk.Frame(self.result_canvas)

        self.result_inner.bind("<Configure>", lambda e: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all")))
        self.result_canvas.create_window((0, 0), window=self.result_inner, anchor="nw")
        self.result_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.result_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Summary
        self.summary_label = ttk.Label(self.main_frame, text="", anchor="w")
        self.summary_label.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

        # Cleanup button
        self.clean_button = ttk.Button(self.main_frame, text="🧼 Delete Selected Items", command=self.clean_selected, state="disabled")
        self.clean_button.grid(row=4, column=0, columnspan=2, pady=10)

    def start_scan(self):
        if self.scan_running:
            messagebox.showinfo("Scan Running", "A scan is already in progress.")
            return

        self.scan_button.config(state="disabled")
        self.clean_button.config(state="disabled")
        self.progress.start()
        self.scan_running = True

        for widget in self.result_inner.winfo_children():
            widget.destroy()
        self.result_checkboxes.clear()
        self.scan_results.clear()
        self.summary_label.config(text="")

        self.scan_thread = threading.Thread(target=self.run_scan)
        self.scan_thread.start()

    def run_scan(self):
        scan_engine = SystemScanEngine()

        # Filter targets based on user selection
        scan_engine.targets = {
            label: path for label, path in scan_engine.targets.items()
            if self.target_checkboxes[label].get()
        }

        self.scan_results = scan_engine.run_scan()

        self.root.after(0, self.display_results)

    def display_results(self):
        total_size = 0
        total_files = 0
        registry_count = 0

        for label, data in self.scan_results.items():
            var = tk.BooleanVar(value=True)
            if label.startswith("Registry:"):
                line = f"🗝️ {label} - {len(data['keys'])} issues"
                registry_count += len(data['keys'])
            else:
                line = f"{label} - {data['file_count']} files, {data['size_human']}"
                total_size += data["size_bytes"]
                total_files += data["file_count"]

            chk = ttk.Checkbutton(self.result_inner, text=line, variable=var)
            chk.pack(anchor="w", pady=2)
            self.result_checkboxes[label] = var

        total_summary = f"🧾 Total: {total_files} files, {self.human_readable_size(total_size)}"
        if registry_count:
            total_summary += f" | 🗝️ {registry_count} registry keys"
        self.summary_label.config(text=total_summary)

        self.clean_button.config(state="normal")
        self.scan_button.config(state="normal")
        self.progress.stop()
        self.scan_running = False

    def clean_selected(self):
        if not self.result_checkboxes:
            messagebox.showwarning("Nothing to Delete", "No items selected for deletion.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected files and registry entries?")
        if not confirm:
            return

        delete = DeleteFiles(self.scan_results, self.result_checkboxes)
        freed = delete.delete_selected()

        summary = f"🧹 Cleaned: {self.human_readable_size(freed)}"
        if delete.registry_cleaned_count:
            summary += f" | 🗝️ {delete.registry_cleaned_count} registry keys deleted"

        messagebox.showinfo("Cleanup Complete", summary)
        self.clean_button.config(state="disabled")
        self.summary_label.config(text=f"✅ {summary}")

    def human_readable_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
